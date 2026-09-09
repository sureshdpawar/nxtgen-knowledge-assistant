import json
import os
from pathlib import Path
from uuid import UUID

import pytest
import yaml
from deepeval.metrics import ArgumentCorrectnessMetric, GEval, ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, SingleTurnParams, ToolCall
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.agent import Agent
from app.models.agent_run import AgentRun
from app.models.user import User
from app.services.agent_execution_service import AgentExecutionService

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config" / "offline_agent_runtime.yaml"
DATASET_PATH = HERE / "datasets" / "offline_agent_runtime_goldens.json"
EPSILON = 1e-9


def load_yaml(path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def configure_judge():
    if not settings.LLM_API_KEY:
        raise RuntimeError("LLM_API_KEY is not configured.")
    os.environ.setdefault("OPENAI_API_KEY", settings.LLM_API_KEY)


def resolve_agent(db, config):
    target = config["target"]
    id_env = target["agent_id_env"]
    name_env = target["agent_name_env"]
    raw_id = os.getenv(id_env, "").strip()
    raw_name = os.getenv(name_env, "").strip()

    stmt = select(Agent)
    if raw_id:
        try:
            agent_id = UUID(raw_id)
        except ValueError as exc:
            raise RuntimeError(f"{id_env} must be a valid UUID.") from exc
        stmt = stmt.where(Agent.id == agent_id)
    elif raw_name:
        stmt = stmt.where(Agent.name == raw_name)
    else:
        pytest.skip(
            f"Set {id_env} or {name_env} to select the real agent. "
            "The evaluation test deliberately does not guess an agent."
        )

    agents = list(db.scalars(stmt).all())
    if not agents:
        raise RuntimeError("Configured evaluation agent was not found.")
    if len(agents) > 1:
        raise RuntimeError(
            f"Agent name is not unique. Set {id_env} to the exact UUID."
        )
    return agents[0]


def resolve_user(db, agent):
    raw_id = os.getenv("KNOWGENTIQ_EVAL_USER_ID", "").strip()
    if raw_id:
        try:
            user_id = UUID(raw_id)
        except ValueError as exc:
            raise RuntimeError(
                "KNOWGENTIQ_EVAL_USER_ID must be a valid UUID."
            ) from exc
        user = db.get(User, user_id)
        if user is None or user.tenant_id != agent.tenant_id or not user.is_active:
            raise RuntimeError(
                "Evaluation user must be active and belong to the agent tenant."
            )
        return user

    user = db.scalar(
        select(User)
        .where(
            User.tenant_id == agent.tenant_id,
            User.is_active.is_(True),
        )
        .order_by(User.created_at.asc())
    )
    if user is None:
        raise RuntimeError("Agent tenant has no active evaluation user.")
    return user


def load_run(db, run_id):
    return db.scalar(
        select(AgentRun)
        .options(selectinload(AgentRun.steps))
        .where(AgentRun.id == run_id)
    )


def enum_value(value):
    return str(getattr(value, "value", value)).upper()


def actual_tool_calls(run):
    calls = []
    for step in sorted(run.steps, key=lambda item: item.step_number):
        if enum_value(step.step_type) != "TOOL":
            continue
        if step.name in {"human_rejected_tools", "policy_blocked_tools"}:
            continue
        data = step.input_data if isinstance(step.input_data, dict) else {}
        for call in data.get("tool_calls", []) or []:
            if not isinstance(call, dict):
                continue
            name = str(call.get("name", "") or "").strip()
            if not name:
                continue
            args = call.get("args", {}) or {}
            if not isinstance(args, dict):
                args = {"value": args}
            calls.append(ToolCall(name=name, input_parameters=args))
    return calls


def expected_tool_calls(case):
    return [
        ToolCall(
            name=item["name"],
            input_parameters=item.get("input_parameters", {}) or {},
        )
        for item in case.get("expected_tools", []) or []
    ]


def make_metrics(config):
    m = config["metrics"]
    judge = config["judge"]
    outcome = GEval(
        name="Outcome Correctness",
        criteria=(
            "Determine whether the actual response accurately reflects the "
            "expected outcome for the user's request. Penalize incorrect "
            "action results, incorrect details, and false claims that an "
            "action succeeded when it did not."
        ),
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
        ],
        threshold=m["outcome_correctness"]["threshold"],
        model=judge["model"],
        verbose_mode=bool(judge.get("verbose", False)),
    )
    tool = ToolCorrectnessMetric(
        threshold=m["tool_correctness"]["threshold"],
        should_exact_match=True,
    )
    arguments = ArgumentCorrectnessMetric(
        threshold=m["argument_correctness"]["threshold"],
        model=judge["model"],
        include_reason=True,
        strict_mode=False,
    )
    return outcome, tool, arguments


def assert_range(score):
    assert -EPSILON <= float(score) <= 1.0 + EPSILON


def assert_no_forbidden_tools(case, tools_called):
    forbidden = set(case.get("forbidden_tools", []) or [])
    called = [tool.name for tool in tools_called]
    violations = sorted(forbidden.intersection(called))
    assert not violations, (
        f"Case {case['id']} executed forbidden tool(s): {violations}. "
        f"Actual tools: {called}"
    )


@pytest.mark.asyncio
async def test_real_knowgentiq_agent_evaluation():
    """
    Slice 1C: small real-runtime evaluation suite.

    Semantic behavior uses DeepEval. Unsupported-action safety uses a
    deterministic forbidden-tool assertion. This is still a learning lab,
    not the CI threshold gate.
    """
    configure_judge()
    config = load_yaml(CONFIG_PATH)
    cases = load_json(DATASET_PATH)
    service = AgentExecutionService()

    with SessionLocal() as db:
        agent = resolve_agent(db, config)
        user = resolve_user(db, agent)

        print(f"\nSuite: {config['suite']['name']}")
        print(f"Agent: {agent.name} ({agent.id})")

        for case in cases:
            print(f"\nCASE: {case['id']}")
            result = await service.run(
                db=db,
                current_user=user,
                agent_id=agent.id,
                query=case["input"],
            )
            run = load_run(db, result["run_id"])
            if run is None:
                pytest.fail("AgentRun was not persisted.")

            status = enum_value(run.status)
            if status == "WAITING_FOR_APPROVAL":
                pytest.fail(
                    "Case reached HUMAN_APPROVAL. Slice 1C never auto-approves "
                    "governed actions."
                )
            if status != "COMPLETED":
                pytest.fail(
                    f"Agent run status={status}; error={run.error_message}"
                )

            tools_called = actual_tool_calls(run)
            expected_tools = expected_tool_calls(case)
            test_case = LLMTestCase(
                input=case["input"],
                actual_output=run.answer or "",
                expected_output=case["expected_outcome"],
                tools_called=tools_called,
                expected_tools=expected_tools,
            )
            outcome, tool, arguments = make_metrics(config)
            outcome.measure(test_case)

            tool_score = None
            tool_reason = "N/A: case does not declare expected_tools."
            if "expected_tools" in case:
                tool.measure(test_case)
                tool_score = float(tool.score)
                tool_reason = tool.reason

            argument_score = None
            argument_reason = "N/A: no expected tool call to evaluate."
            if expected_tools and tools_called:
                arguments.measure(test_case)
                argument_score = float(arguments.score)
                argument_reason = arguments.reason

            assert_no_forbidden_tools(case, tools_called)

            print(f"Run ID: {run.id}")
            print(
                "Actual tools:",
                [
                    {"name": c.name, "input_parameters": c.input_parameters}
                    for c in tools_called
                ],
            )
            print("Actual output:", run.answer)
            print("Outcome Correctness:", float(outcome.score))
            print("  Reason:", outcome.reason)
            print("Tool Correctness:", tool_score)
            print("  Reason:", tool_reason)
            print("Argument Correctness:", argument_score)
            print("  Reason:", argument_reason)
            if case.get("forbidden_tools"):
                print("Forbidden Tool Check: PASS")
                print("  Forbidden:", case["forbidden_tools"])

            assert_range(outcome.score)
            if tool_score is not None:
                assert_range(tool_score)
            if argument_score is not None:
                assert_range(argument_score)
