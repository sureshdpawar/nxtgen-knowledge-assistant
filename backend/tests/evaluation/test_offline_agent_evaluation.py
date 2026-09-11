import json
import os

from pathlib import Path
from statistics import mean

import yaml

from deepeval.metrics import (
    ArgumentCorrectnessMetric,
    GEval,
    ToolCorrectnessMetric,
)
from deepeval.test_case import (
    LLMTestCase,
    SingleTurnParams,
    ToolCall,
)

from app.core.config import settings


EVALUATION_DIR = Path(__file__).resolve().parent

CONFIG_PATH = (
    EVALUATION_DIR
    / "config"
    / "offline_agent.yaml"
)

DATASET_PATH = (
    EVALUATION_DIR
    / "datasets"
    / "offline_agent_goldens.json"
)


def configure_judge():
    if not settings.LLM_API_KEY:
        raise RuntimeError(
            "LLM_API_KEY is not configured."
        )

    os.environ.setdefault(
        "OPENAI_API_KEY",
        settings.LLM_API_KEY,
    )


def load_config():
    with CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return yaml.safe_load(file)


def load_dataset():
    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def build_tool_call(item):
    return ToolCall(
        name=item["name"],
        input=item.get("input", {}),
        output=item.get("output"),
    )


def build_expected_tool(item):
    return ToolCall(
        name=item["name"],
    )


def build_test_case(case):
    return LLMTestCase(
        input=case["input"],
        actual_output=case["actual_output"],
        expected_output=case["expected_output"],
        tools_called=[
            build_tool_call(item)
            for item in case.get(
                "tools_called",
                [],
            )
        ],
        expected_tools=[
            build_expected_tool(item)
            for item in case.get(
                "expected_tools",
                [],
            )
        ],
    )


def build_metrics(config):
    metric_config = config["metrics"]
    model = config["judge"]["model"]
    verbose = config["judge"].get(
        "verbose",
        False,
    )

    return {
        "outcome_correctness": GEval(
            name="Agent Outcome Correctness",
            criteria=(
                "Determine whether the agent's "
                "actual output satisfies the "
                "expected outcome for the user's "
                "request. Penalize false claims "
                "of successful actions, incorrect "
                "action results, and failure to "
                "clearly report an action that "
                "did not complete."
            ),
            evaluation_params=[
                SingleTurnParams.INPUT,
                SingleTurnParams.ACTUAL_OUTPUT,
                SingleTurnParams.EXPECTED_OUTPUT,
            ],
            threshold=metric_config[
                "outcome_correctness"
            ]["threshold"],
            model=model,
            verbose_mode=verbose,
        ),
        "tool_correctness":
            ToolCorrectnessMetric(
                threshold=metric_config[
                    "tool_correctness"
                ]["threshold"],
                should_exact_match=True,
            ),
        "argument_correctness":
            ArgumentCorrectnessMetric(
                threshold=metric_config[
                    "argument_correctness"
                ]["threshold"],
                model=model,
                include_reason=True,
                strict_mode=False,
                verbose_mode=verbose,
            ),
    }


def measure_metric(metric, test_case):
    metric.measure(test_case)

    return {
        "score": metric.score,
        "reason": getattr(
            metric,
            "reason",
            None,
        ),
        "passed": metric.is_successful(),
    }


def score_case(case, config):
    test_case = build_test_case(case)
    metrics = build_metrics(config)
    results = {}

    results["outcome_correctness"] = (
        measure_metric(
            metrics["outcome_correctness"],
            test_case,
        )
    )

    expected_tools = case.get(
        "expected_tools",
        [],
    )
    tools_called = case.get(
        "tools_called",
        [],
    )

    # Empty-vs-empty means the agent correctly
    # avoided tool use. Treat that as a perfect
    # deterministic result instead of asking a
    # ratio-based metric to score an empty set.
    if (
        not expected_tools
        and not tools_called
    ):
        results["tool_correctness"] = {
            "score": 1.0,
            "reason": (
                "No tool was expected and "
                "no tool was called."
            ),
            "passed": True,
        }
    else:
        results["tool_correctness"] = (
            measure_metric(
                metrics["tool_correctness"],
                test_case,
            )
        )

    # Argument correctness only applies when
    # the agent generated tool arguments.
    if tools_called:
        results["argument_correctness"] = (
            measure_metric(
                metrics[
                    "argument_correctness"
                ],
                test_case,
            )
        )
    else:
        results["argument_correctness"] = {
            "score": None,
            "reason": "No tool call was made.",
            "passed": None,
        }

    return results


def format_score(value):
    if value is None:
        return "N/A"

    return f"{value:.3f}"


def format_verdict(result):
    if result["passed"] is None:
        return "N/A"

    return (
        "PASS"
        if result["passed"]
        else "FAIL"
    )


def print_case_report(case_id, results):
    print()
    print("=" * 72)
    print(f"CASE: {case_id}")
    print("=" * 72)

    labels = {
        "outcome_correctness":
            "Outcome Correctness",
        "tool_correctness":
            "Tool Correctness",
        "argument_correctness":
            "Argument Correctness",
    }

    for key, label in labels.items():
        result = results[key]

        print(
            f"{label:24}",
            format_score(result["score"]),
            format_verdict(result),
        )

        if result["reason"]:
            print(
                "  Reason:",
                result["reason"],
            )


def average_metric(
    all_results,
    metric_name,
):
    scores = [
        result[metric_name]["score"]
        for result in all_results
        if (
            result[metric_name]["score"]
            is not None
        )
    ]

    if not scores:
        return None

    return mean(scores)


def print_suite_report(
    dataset,
    all_results,
):
    print()
    print()
    print("#" * 72)
    print("OFFLINE AGENT EVALUATION SUMMARY")
    print("#" * 72)
    print()
    print(
        f"{'Cases':24}",
        len(dataset["cases"]),
    )

    for metric_name, label in [
        (
            "outcome_correctness",
            "Outcome Correctness",
        ),
        (
            "tool_correctness",
            "Tool Correctness",
        ),
        (
            "argument_correctness",
            "Argument Correctness",
        ),
    ]:
        print(
            f"{label:24}",
            format_score(
                average_metric(
                    all_results,
                    metric_name,
                )
            ),
        )


def test_generic_offline_agent_evaluation():
    """
    Slice 1: offline agent-evaluation learning lab.

    This is intentionally NOT a CI quality
    gate. It uses precomputed outcomes and
    tool calls so we can understand metric
    behavior before touching the production
    LangGraph execution path.

    The next slice replaces precomputed
    actual_output/tools_called with real
    AgentRun and AgentRunStep trace data.
    """

    configure_judge()

    config = load_config()
    dataset = load_dataset()
    all_results = []

    for case in dataset["cases"]:
        results = score_case(
            case=case,
            config=config,
        )

        all_results.append(results)

        print_case_report(
            case_id=case["id"],
            results=results,
        )

        # Deliberately bad cases may fail their
        # thresholds. Slice 1 only verifies that
        # every applicable metric executed and
        # produced a valid score.
        for metric_name in [
            "outcome_correctness",
            "tool_correctness",
        ]:
            score = results[
                metric_name
            ]["score"]

            assert score is not None
            # LLM/evaluation libraries can return a value
            # infinitesimally above 1.0 because of normal
            # floating-point arithmetic (for example,
            # 1.0000000000000002). Treat that as 1.0 for
            # range validation rather than failing the lab.
            epsilon = 1e-9
            assert -epsilon <= score <= 1.0 + epsilon

        argument_score = results[
            "argument_correctness"
        ]["score"]

        if argument_score is not None:
            epsilon = 1e-9
            assert (
                -epsilon
                <= argument_score
                <= 1.0 + epsilon
            )

    print_suite_report(
        dataset=dataset,
        all_results=all_results,
    )
