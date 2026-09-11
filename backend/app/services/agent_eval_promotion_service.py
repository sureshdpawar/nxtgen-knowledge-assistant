from sqlalchemy.orm import Session

from app.models.agent_eval_case import AgentEvalCase
from app.models.agent_run import AgentRun
from app.models.user import User
from app.repositories.agent_eval_case_repository import AgentEvalCaseRepository
from app.schemas.agent_eval import AgentEvalCasePromoteRunCreate
from app.services.agent_eval_dataset_service import AgentEvalDatasetService


class AgentEvalPromotionService:
    """
    Promote a real AgentRun into a durable Agent Evaluation regression case.

    The source query is taken from AgentRun. Expected outcome and tool
    expectations are explicitly supplied by the operator so a bad production
    answer is never copied as the new golden answer.
    """

    def __init__(self):
        self.case_repository = AgentEvalCaseRepository()
        self.dataset_service = AgentEvalDatasetService()

    @staticmethod
    def _normalise_expected_tools(
        expected_tools,
    ) -> list[dict]:
        result: list[dict] = []
        seen: set[str] = set()

        for tool in expected_tools:
            name = tool.name.strip()
            if not name:
                raise ValueError(
                    "Expected tool name cannot be empty."
                )
            if name in seen:
                raise ValueError(
                    f"Duplicate expected tool '{name}'."
                )

            seen.add(name)
            result.append({
                "name": name,
                "input_parameters": tool.input_parameters,
            })

        return result

    @staticmethod
    def _normalise_forbidden_tools(
        forbidden_tools: list[str],
    ) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()

        for raw_name in forbidden_tools:
            name = raw_name.strip()
            if not name:
                raise ValueError(
                    "Forbidden tool name cannot be empty."
                )
            if name in seen:
                continue
            seen.add(name)
            result.append(name)

        return result

    def promote_run(
        self,
        db: Session,
        current_user: User,
        dataset_id,
        payload: AgentEvalCasePromoteRunCreate,
    ) -> AgentEvalCase:
        if current_user.tenant_id is None:
            raise ValueError(
                "Agent Evaluation requires a tenant-scoped admin."
            )

        dataset = self.dataset_service.get(
            db=db,
            current_user=current_user,
            dataset_id=dataset_id,
        )
        if dataset is None:
            raise ValueError(
                "Agent Evaluation dataset not found."
            )

        run = db.get(
            AgentRun,
            payload.agent_run_id,
        )

        if (
            run is None
            or run.tenant_id != current_user.tenant_id
        ):
            raise ValueError(
                "Agent run not found."
            )

        if run.agent_id != dataset.agent_id:
            raise ValueError(
                "Agent run belongs to a different agent than the target dataset."
            )

        query = (run.query or "").strip()
        if not query:
            raise ValueError(
                "Agent run does not contain a promotable input query."
            )

        name = payload.name.strip()
        expected_outcome = (
            payload.expected_outcome.strip()
        )

        if not name:
            raise ValueError(
                "Evaluation case name cannot be empty."
            )

        if not expected_outcome:
            raise ValueError(
                "Expected outcome cannot be empty."
            )

        expected_tools = self._normalise_expected_tools(
            payload.expected_tools
        )
        forbidden_tools = self._normalise_forbidden_tools(
            payload.forbidden_tools
        )

        expected_names = {
            item["name"] for item in expected_tools
        }
        overlap = expected_names.intersection(
            forbidden_tools
        )

        if overlap:
            names = ", ".join(sorted(overlap))
            raise ValueError(
                "Tool(s) cannot be both expected and forbidden: "
                f"{names}."
            )

        eval_case = AgentEvalCase(
            dataset_id=dataset.id,
            name=name,
            input=query,
            expected_outcome=expected_outcome,
            expected_tools=expected_tools,
            forbidden_tools=forbidden_tools,
            enabled=payload.enabled,
            source_agent_run_id=run.id,
        )

        eval_case = self.case_repository.create(
            db=db,
            entity=eval_case,
        )

        db.commit()
        db.refresh(eval_case)

        return eval_case
