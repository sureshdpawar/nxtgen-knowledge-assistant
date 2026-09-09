from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_eval_case import AgentEvalCase
from app.models.agent_eval_dataset import AgentEvalDataset
from app.models.user import User
from app.schemas.agent_eval import AgentEvalDatasetImportPayload


class AgentEvalDatasetImportService:
    """
    Transactional import of one Agent Evaluation dataset and all golden cases.

    The whole import succeeds or fails together. This is important for
    regression datasets: a partially imported dataset must never look valid.
    """

    @staticmethod
    def _validate_agent(
        db: Session,
        current_user: User,
        payload: AgentEvalDatasetImportPayload,
    ) -> Agent:
        if current_user.tenant_id is None:
            raise ValueError(
                "Agent Evaluation requires a tenant-scoped admin."
            )

        agent = db.get(Agent, payload.agent_id)

        if (
            agent is None
            or agent.tenant_id != current_user.tenant_id
        ):
            raise ValueError("Agent not found.")

        return agent

    @staticmethod
    def _normalise_expected_tools(
        case_index: int,
        expected_tools,
    ) -> list[dict]:
        result: list[dict] = []
        seen_names: set[str] = set()

        for tool in expected_tools:
            name = tool.name.strip()

            if not name:
                raise ValueError(
                    f"Case {case_index}: expected tool name cannot be empty."
                )

            if name in seen_names:
                raise ValueError(
                    f"Case {case_index}: duplicate expected tool '{name}'."
                )

            seen_names.add(name)
            result.append(
                {
                    "name": name,
                    "input_parameters": tool.input_parameters,
                }
            )

        return result

    @staticmethod
    def _normalise_forbidden_tools(
        case_index: int,
        forbidden_tools: list[str],
    ) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()

        for raw_name in forbidden_tools:
            name = raw_name.strip()

            if not name:
                raise ValueError(
                    f"Case {case_index}: forbidden tool name cannot be empty."
                )

            if name in seen:
                continue

            seen.add(name)
            result.append(name)

        return result

    def import_dataset(
        self,
        db: Session,
        current_user: User,
        payload: AgentEvalDatasetImportPayload,
    ) -> tuple[AgentEvalDataset, int]:
        agent = self._validate_agent(
            db=db,
            current_user=current_user,
            payload=payload,
        )

        if not payload.cases:
            raise ValueError(
                "Agent Evaluation dataset must contain at least one case."
            )

        try:
            dataset = AgentEvalDataset(
                tenant_id=agent.tenant_id,
                agent_id=agent.id,
                name=payload.name.strip(),
                version=payload.version.strip(),
                description=payload.description,
            )

            db.add(dataset)
            db.flush()

            case_count = 0

            for index, case_payload in enumerate(
                payload.cases,
                start=1,
            ):
                name = case_payload.name.strip()
                input_text = case_payload.input.strip()
                expected_outcome = (
                    case_payload.expected_outcome.strip()
                )

                if not name:
                    raise ValueError(
                        f"Case {index}: name cannot be empty."
                    )

                if not input_text:
                    raise ValueError(
                        f"Case {index}: input cannot be empty."
                    )

                if not expected_outcome:
                    raise ValueError(
                        f"Case {index}: expected_outcome cannot be empty."
                    )

                expected_tools = self._normalise_expected_tools(
                    case_index=index,
                    expected_tools=case_payload.expected_tools,
                )

                forbidden_tools = self._normalise_forbidden_tools(
                    case_index=index,
                    forbidden_tools=case_payload.forbidden_tools,
                )

                expected_tool_names = {
                    tool["name"]
                    for tool in expected_tools
                }
                overlap = expected_tool_names.intersection(
                    forbidden_tools
                )

                if overlap:
                    names = ", ".join(sorted(overlap))
                    raise ValueError(
                        f"Case {index}: tool(s) cannot be both expected "
                        f"and forbidden: {names}."
                    )

                eval_case = AgentEvalCase(
                    dataset_id=dataset.id,
                    name=name,
                    input=input_text,
                    expected_outcome=expected_outcome,
                    expected_tools=expected_tools,
                    forbidden_tools=forbidden_tools,
                    enabled=case_payload.enabled,
                )

                db.add(eval_case)
                case_count += 1

            db.commit()
            db.refresh(dataset)

            return dataset, case_count

        except Exception:
            db.rollback()
            raise
