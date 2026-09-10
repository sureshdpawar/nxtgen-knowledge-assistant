import os
from statistics import mean

from deepeval.metrics import ArgumentCorrectnessMetric, GEval, ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, SingleTurnParams, ToolCall

from app.core.config import settings
from app.models.agent_eval_case import AgentEvalCase
from app.models.agent_eval_result import AgentEvalResult


class AgentEvalScoringService:
    @staticmethod
    def configure_judge() -> None:
        if not settings.LLM_API_KEY:
            raise RuntimeError("LLM_API_KEY is not configured.")
        os.environ.setdefault("OPENAI_API_KEY", settings.LLM_API_KEY)

    @staticmethod
    def _actual_tool_calls(result: AgentEvalResult) -> list[ToolCall]:
        calls = []
        for item in result.tools_called or []:
            name = str(item.get("name") or "").strip()
            if name:
                calls.append(ToolCall(name=name, input=item.get("input") or {}, output=item.get("output")))
        return calls

    @staticmethod
    def _expected_tool_calls(case: AgentEvalCase) -> list[ToolCall]:
        calls = []
        for item in case.expected_tools or []:
            name = str(item.get("name") or "").strip()
            if name:
                calls.append(ToolCall(name=name))
        return calls

    @staticmethod
    def _measure(metric, test_case: LLMTestCase) -> dict:
        metric.measure(test_case)
        return {
            "score": metric.score,
            "reason": getattr(metric, "reason", None),
            "passed": metric.is_successful(),
        }

    def score(self, *, case: AgentEvalCase, result: AgentEvalResult, judge_model: str,
              outcome_threshold: float, tool_threshold: float, argument_threshold: float) -> dict:
        self.configure_judge()
        actual_tools = self._actual_tool_calls(result)
        expected_tools = self._expected_tool_calls(case)
        test_case = LLMTestCase(
            input=case.input,
            actual_output=result.actual_answer or "",
            expected_output=case.expected_outcome,
            tools_called=actual_tools,
            expected_tools=expected_tools,
        )
        outcome_metric = GEval(
            name="Agent Outcome Correctness",
            criteria=("Determine whether the agent's actual output satisfies the expected outcome for the user's "
                      "request. Penalize false claims of successful actions, incorrect action results, and failure "
                      "to clearly report an action that did not complete."),
            evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
            threshold=outcome_threshold,
            model=judge_model,
            verbose_mode=False,
        )
        tool_metric = ToolCorrectnessMetric(threshold=tool_threshold, should_exact_match=True)
        argument_metric = ArgumentCorrectnessMetric(
            threshold=argument_threshold, model=judge_model, include_reason=True, strict_mode=False, verbose_mode=False
        )
        outcome = self._measure(outcome_metric, test_case)
        tool = ({"score": 1.0, "reason": "No tool was expected and no tool was called.", "passed": True}
                if not expected_tools and not actual_tools else self._measure(tool_metric, test_case))
        arguments = (self._measure(argument_metric, test_case) if actual_tools else
                     {"score": None, "reason": "No tool call was made.", "passed": None})
        forbidden_ok = not bool(result.forbidden_tool_violations)
        checks = [bool(outcome["passed"]), bool(tool["passed"]), forbidden_ok]
        if arguments["passed"] is not None:
            checks.append(bool(arguments["passed"]))
        return {
            "outcome_correctness": outcome,
            "tool_correctness": tool,
            "argument_correctness": arguments,
            "forbidden_tool_check": {"passed": forbidden_ok, "violations": result.forbidden_tool_violations or []},
            "passed": all(checks),
        }

    @staticmethod
    def aggregate(results: list[AgentEvalResult]) -> dict:
        if not results:
            return {"case_count": 0, "passed_count": 0, "pass_rate": 0.0,
                    "outcome_correctness": None, "tool_correctness": None, "argument_correctness": None}
        passed_count = sum(1 for item in results if item.passed is True)
        outcome = [r.outcome_correctness for r in results if r.outcome_correctness is not None]
        tool = [r.tool_correctness for r in results if r.tool_correctness is not None]
        args = [r.argument_correctness for r in results if r.argument_correctness is not None]
        return {
            "case_count": len(results),
            "passed_count": passed_count,
            "pass_rate": passed_count / len(results),
            "outcome_correctness": mean(outcome) if outcome else None,
            "tool_correctness": mean(tool) if tool else None,
            "argument_correctness": mean(args) if args else None,
        }
