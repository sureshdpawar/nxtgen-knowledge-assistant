from statistics import mean
from uuid import UUID

from deepeval.metrics import (
    ArgumentCorrectnessMetric,
    GEval,
    ToolCorrectnessMetric,
)
from deepeval.models import OpenAIModel
from deepeval.test_case import (
    LLMTestCase,
    SingleTurnParams,
    ToolCall,
)
from sqlalchemy.orm import Session

from app.models.agent_eval_case import AgentEvalCase
from app.models.agent_eval_result import AgentEvalResult
from app.services.llm_client_factory import LLMClientFactory


class AgentEvalScoringService:
    """
    DeepEval-backed scoring for persisted Agent Evaluation experiments.

    Judge credentials and provider endpoint are resolved from Knowgentiq's
    tenant-managed LLM configuration. The process environment is deliberately
    not mutated and legacy settings.LLM_API / settings.LLM_API_KEY are not used.

    Agent Evaluation currently uses the tenant default LLM profile as its judge
    profile. The experiment's judge_model remains an optional model-name
    override, allowing the evaluator model to differ while still using the
    tenant-managed endpoint and credential.

    knowledge_base_id is supported for callers that evaluate a single KB:
    LLMClientFactory then applies the existing KB override -> tenant default
    resolution rule. Dataset-based Agent Evaluation does not pass a KB id
    because an agent can be attached to multiple knowledge bases.
    """

    def __init__(self):
        self.client_factory = LLMClientFactory()

    def _resolve_judge(
        self,
        *,
        db: Session,
        tenant_id: UUID,
        judge_model: str | None,
        knowledge_base_id: UUID | None = None,
    ) -> tuple[OpenAIModel, dict]:
        if knowledge_base_id is not None:
            _, configuration = (
                self.client_factory.create_for_knowledge_base(
                    db=db,
                    tenant_id=tenant_id,
                    knowledge_base_id=knowledge_base_id,
                )
            )
            resolution_source = "knowledge_base_or_tenant_default"
        else:
            _, configuration = (
                self.client_factory.create(
                    db=db,
                    tenant_id=tenant_id,
                )
            )
            resolution_source = "tenant_default"

        requested_model = str(judge_model or "").strip()
        effective_model = (
            requested_model
            if requested_model
            else configuration.model_name
        )

        judge = OpenAIModel(
            model=effective_model,
            api_key=configuration.api_key,
            base_url=configuration.base_url,
            temperature=0.0,
        )

        metadata = {
            "llm_configuration_id": str(configuration.id),
            "llm_configuration_name": configuration.name,
            "provider": configuration.provider.value,
            "configured_model": configuration.model_name,
            "judge_model": effective_model,
            "resolution_source": resolution_source,
        }

        return judge, metadata

    @staticmethod
    def _actual_tool_calls(
        result: AgentEvalResult,
    ) -> list[ToolCall]:
        calls = []

        for item in result.tools_called or []:
            name = str(
                item.get("name") or ""
            ).strip()

            if name:
                calls.append(
                    ToolCall(
                        name=name,
                        input=item.get("input") or {},
                        output=item.get("output"),
                    )
                )

        return calls

    @staticmethod
    def _expected_tool_calls(
        case: AgentEvalCase,
    ) -> list[ToolCall]:
        calls = []

        for item in case.expected_tools or []:
            if not isinstance(item, dict):
                continue

            name = str(
                item.get("name") or ""
            ).strip()

            if not name:
                continue

            if (
                "input" in item
                and item.get("input") is not None
            ):
                calls.append(
                    ToolCall(
                        name=name,
                        input=item.get("input"),
                    )
                )
            else:
                calls.append(
                    ToolCall(
                        name=name,
                    )
                )

        return calls

    @staticmethod
    def _expected_arguments_specified(
        case: AgentEvalCase,
    ) -> bool:
        """
        Return True only when every valid expected tool includes explicit
        expected input.

        Tool-name-only expectations are sufficient for Tool Correctness, but
        they do not provide a gold standard for Argument Correctness. In that
        case argument scoring must be N/A rather than a failing zero.
        """
        expected_items = []

        for item in case.expected_tools or []:
            if not isinstance(item, dict):
                continue

            name = str(
                item.get("name") or ""
            ).strip()

            if name:
                expected_items.append(item)

        if not expected_items:
            return False

        return all(
            (
                "input" in item
                and item.get("input") is not None
            )
            for item in expected_items
        )

    @staticmethod
    async def _measure(
        metric,
        test_case: LLMTestCase,
    ) -> dict:
        await metric.a_measure(test_case)

        return {
            "score": metric.score,
            "reason": getattr(
                metric,
                "reason",
                None,
            ),
            "passed": metric.is_successful(),
        }

    async def score(
        self,
        *,
        db: Session,
        tenant_id: UUID,
        case: AgentEvalCase,
        result: AgentEvalResult,
        judge_model: str | None,
        outcome_threshold: float,
        tool_threshold: float,
        argument_threshold: float,
        knowledge_base_id: UUID | None = None,
    ) -> dict:
        judge, judge_metadata = (
            self._resolve_judge(
                db=db,
                tenant_id=tenant_id,
                judge_model=judge_model,
                knowledge_base_id=knowledge_base_id,
            )
        )

        actual_tools = (
            self._actual_tool_calls(
                result
            )
        )

        expected_tools = (
            self._expected_tool_calls(
                case
            )
        )

        expected_arguments_specified = (
            self._expected_arguments_specified(
                case
            )
        )

        test_case = LLMTestCase(
            input=case.input,
            actual_output=(
                result.actual_answer
                or ""
            ),
            expected_output=(
                case.expected_outcome
            ),
            tools_called=actual_tools,
            expected_tools=expected_tools,
        )

        outcome_metric = GEval(
            name="Agent Outcome Correctness",
            criteria=(
                "Determine whether the agent's actual output satisfies the "
                "expected outcome for the user's request. Penalize false "
                "claims of successful actions, incorrect action results, "
                "and failure to clearly report an action that did not "
                "complete."
            ),
            evaluation_params=[
                SingleTurnParams.INPUT,
                SingleTurnParams.ACTUAL_OUTPUT,
                SingleTurnParams.EXPECTED_OUTPUT,
            ],
            threshold=outcome_threshold,
            model=judge,
            verbose_mode=False,
        )

        tool_metric = ToolCorrectnessMetric(
            threshold=tool_threshold,
            should_exact_match=True,
            model=judge,
        )

        argument_metric = (
            ArgumentCorrectnessMetric(
                threshold=argument_threshold,
                model=judge,
                include_reason=True,
                strict_mode=False,
                verbose_mode=False,
            )
        )

        outcome = await self._measure(
            outcome_metric,
            test_case,
        )

        if (
            not expected_tools
            and not actual_tools
        ):
            tool = {
                "score": 1.0,
                "reason": (
                    "No tool was expected and "
                    "no tool was called."
                ),
                "passed": True,
            }
        else:
            tool = await self._measure(
                tool_metric,
                test_case,
            )

        if (
            actual_tools
            and expected_arguments_specified
        ):
            arguments = await self._measure(
                argument_metric,
                test_case,
            )
        elif not actual_tools:
            arguments = {
                "score": None,
                "reason": (
                    "No tool call was made."
                ),
                "passed": None,
            }
        else:
            arguments = {
                "score": None,
                "reason": (
                    "No expected tool arguments were specified."
                ),
                "passed": None,
            }

        forbidden_ok = not bool(
            result.forbidden_tool_violations
        )

        checks = [
            bool(outcome["passed"]),
            bool(tool["passed"]),
            forbidden_ok,
        ]

        if (
            arguments["passed"]
            is not None
        ):
            checks.append(
                bool(
                    arguments["passed"]
                )
            )

        return {
            "outcome_correctness": outcome,
            "tool_correctness": tool,
            "argument_correctness": arguments,
            "forbidden_tool_check": {
                "passed": forbidden_ok,
                "violations": (
                    result.forbidden_tool_violations
                    or []
                ),
            },
            "judge_metadata": judge_metadata,
            "passed": all(checks),
        }

    @staticmethod
    def aggregate(
        results: list[AgentEvalResult],
    ) -> dict:
        if not results:
            return {
                "case_count": 0,
                "passed_count": 0,
                "pass_rate": 0.0,
                "outcome_correctness": None,
                "tool_correctness": None,
                "argument_correctness": None,
            }

        passed_count = sum(
            1
            for item in results
            if item.passed is True
        )

        outcome = [
            result.outcome_correctness
            for result in results
            if (
                result.outcome_correctness
                is not None
            )
        ]

        tool = [
            result.tool_correctness
            for result in results
            if (
                result.tool_correctness
                is not None
            )
        ]

        arguments = [
            result.argument_correctness
            for result in results
            if (
                result.argument_correctness
                is not None
            )
        ]

        return {
            "case_count": len(results),
            "passed_count": passed_count,
            "pass_rate": (
                passed_count
                / len(results)
            ),
            "outcome_correctness": (
                mean(outcome)
                if outcome
                else None
            ),
            "tool_correctness": (
                mean(tool)
                if tool
                else None
            ),
            "argument_correctness": (
                mean(arguments)
                if arguments
                else None
            ),
        }
