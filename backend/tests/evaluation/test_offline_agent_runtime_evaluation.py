import json
import os
from pathlib import Path
from statistics import mean
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
    target=config["target"]; id_env=target["agent_id_env"]; name_env=target["agent_name_env"]
    raw_id=os.getenv(id_env,"").strip(); raw_name=os.getenv(name_env,"").strip()
    stmt=select(Agent)
    if raw_id:
        try: agent_id=UUID(raw_id)
        except ValueError as exc: raise RuntimeError(f"{id_env} must be a valid UUID.") from exc
        stmt=stmt.where(Agent.id==agent_id)
    elif raw_name:
        stmt=stmt.where(Agent.name==raw_name)
    else:
        pytest.skip(f"Set {id_env} or {name_env} to select the real agent. The evaluation gate deliberately does not guess an agent.")
    agents=list(db.scalars(stmt).all())
    if not agents: raise RuntimeError("Configured evaluation agent was not found.")
    if len(agents)>1: raise RuntimeError(f"Agent name is not unique. Set {id_env} to the exact UUID.")
    return agents[0]

def resolve_user(db, agent):
    raw_id=os.getenv("KNOWGENTIQ_EVAL_USER_ID","").strip()
    if raw_id:
        try: user_id=UUID(raw_id)
        except ValueError as exc: raise RuntimeError("KNOWGENTIQ_EVAL_USER_ID must be a valid UUID.") from exc
        user=db.get(User,user_id)
        if user is None or user.tenant_id!=agent.tenant_id or not user.is_active:
            raise RuntimeError("Evaluation user must be active and belong to the agent tenant.")
        return user
    user=db.scalar(select(User).where(User.tenant_id==agent.tenant_id,User.is_active.is_(True)).order_by(User.created_at.asc()))
    if user is None: raise RuntimeError("Agent tenant has no active evaluation user.")
    return user

def load_run(db, run_id):
    return db.scalar(select(AgentRun).options(selectinload(AgentRun.steps)).where(AgentRun.id==run_id))

def enum_value(value):
    return str(getattr(value,"value",value)).upper()

def actual_tool_calls(run):
    calls=[]
    for step in sorted(run.steps,key=lambda item:item.step_number):
        if enum_value(step.step_type)!="TOOL" or step.name in {"human_rejected_tools","policy_blocked_tools"}: continue
        data=step.input_data if isinstance(step.input_data,dict) else {}
        for call in data.get("tool_calls",[]) or []:
            if not isinstance(call,dict): continue
            name=str(call.get("name","") or "").strip()
            if not name: continue
            args=call.get("args",{}) or {}
            if not isinstance(args,dict): args={"value":args}
            calls.append(ToolCall(name=name,input_parameters=args))
    return calls

def expected_tool_calls(case):
    return [ToolCall(name=item["name"],input_parameters=item.get("input_parameters",{}) or {}) for item in case.get("expected_tools",[]) or []]

def make_metrics(config):
    m=config["metrics"]; judge=config["judge"]
    outcome=GEval(name="Outcome Correctness",criteria="Determine whether the actual response accurately reflects the expected outcome for the user's request. Penalize incorrect action results, incorrect details, and false claims that an action succeeded when it did not.",evaluation_params=[SingleTurnParams.INPUT,SingleTurnParams.ACTUAL_OUTPUT,SingleTurnParams.EXPECTED_OUTPUT],threshold=m["outcome_correctness"]["threshold"],model=judge["model"],verbose_mode=bool(judge.get("verbose",False)))
    tool=ToolCorrectnessMetric(threshold=m["tool_correctness"]["threshold"],should_exact_match=True)
    arguments=ArgumentCorrectnessMetric(threshold=m["argument_correctness"]["threshold"],model=judge["model"],include_reason=True,strict_mode=False)
    return outcome,tool,arguments

def assert_range(score):
    assert -EPSILON<=float(score)<=1.0+EPSILON

def forbidden_tool_violations(case,tools_called):
    forbidden=set(case.get("forbidden_tools",[]) or [])
    return sorted(forbidden.intersection(tool.name for tool in tools_called))

def score_passes(score,threshold):
    return score is None or float(score)+EPSILON>=float(threshold)

def average(scores):
    values=[float(s) for s in scores if s is not None]
    return mean(values) if values else None

def fmt(score):
    return "N/A" if score is None else f"{float(score):.3f}"

def print_summary(results,config):
    required=float(config["suite"]["pass_rate_threshold"])
    passed=sum(1 for r in results if r["passed"])
    rate=passed/len(results) if results else 0.0
    print("\nAGENT EVALUATION QUALITY GATE")
    print("-"*86)
    print(f"{'Case':42} {'Outcome':>9} {'Tool':>9} {'Args':>9} {'Result':>10}")
    print("-"*86)
    for r in results:
        print(f"{r['id'][:42]:42} {fmt(r['outcome_score']):>9} {fmt(r['tool_score']):>9} {fmt(r['argument_score']):>9} {('PASS' if r['passed'] else 'FAIL'):>10}")
    print("-"*86)
    m=config["metrics"]
    print(f"Thresholds: outcome>={m['outcome_correctness']['threshold']:.2f}, tool>={m['tool_correctness']['threshold']:.2f}, arguments>={m['argument_correctness']['threshold']:.2f}")
    print(f"Outcome average:  {fmt(average([r['outcome_score'] for r in results]))}")
    print(f"Tool average:     {fmt(average([r['tool_score'] for r in results]))}")
    print(f"Argument average: {fmt(average([r['argument_score'] for r in results]))}")
    print(f"Cases passed:     {passed}/{len(results)}")
    print(f"Suite pass rate:  {rate:.1%}")
    print(f"Required rate:    {required:.1%}")
    print("QUALITY GATE:", "PASS" if rate+EPSILON>=required else "FAIL")
    return rate,required

@pytest.mark.asyncio
async def test_real_knowgentiq_agent_quality_gate():
    """Slice 2: thresholded offline quality gate against the real Knowgentiq runtime."""
    configure_judge(); config=load_yaml(CONFIG_PATH); cases=load_json(DATASET_PATH)
    service=AgentExecutionService(); results=[]; thresholds=config["metrics"]
    with SessionLocal() as db:
        agent=resolve_agent(db,config); user=resolve_user(db,agent)
        print(f"\nSuite: {config['suite']['name']}"); print(f"Agent: {agent.name} ({agent.id})")
        for case in cases:
            print(f"\nCASE: {case['id']}")
            result=await service.run(db=db,current_user=user,agent_id=agent.id,query=case["input"])
            run=load_run(db,result["run_id"])
            if run is None: pytest.fail("AgentRun was not persisted.")
            status=enum_value(run.status)
            if status=="WAITING_FOR_APPROVAL": pytest.fail("Case reached HUMAN_APPROVAL. Slice 2 never auto-approves governed actions.")
            if status!="COMPLETED": pytest.fail(f"Agent run status={status}; error={run.error_message}")
            tools=actual_tool_calls(run); expected=expected_tool_calls(case)
            tc=LLMTestCase(input=case["input"],actual_output=run.answer or "",expected_output=case["expected_outcome"],tools_called=tools,expected_tools=expected)
            outcome,tool,args_metric=make_metrics(config); outcome.measure(tc); oscore=float(outcome.score)
            tscore=None; treason="N/A: case does not declare expected_tools."
            if "expected_tools" in case:
                tool.measure(tc); tscore=float(tool.score); treason=tool.reason
            ascore=None; areason="N/A: no expected tool call to evaluate."
            if expected and tools:
                args_metric.measure(tc); ascore=float(args_metric.score); areason=args_metric.reason
            violations=forbidden_tool_violations(case,tools)
            assert_range(oscore)
            if tscore is not None: assert_range(tscore)
            if ascore is not None: assert_range(ascore)
            passed=all([score_passes(oscore,thresholds["outcome_correctness"]["threshold"]),score_passes(tscore,thresholds["tool_correctness"]["threshold"]),score_passes(ascore,thresholds["argument_correctness"]["threshold"]),not violations])
            results.append({"id":case["id"],"outcome_score":oscore,"tool_score":tscore,"argument_score":ascore,"passed":passed})
            print("Actual tools:",[{"name":c.name,"input_parameters":c.input_parameters} for c in tools])
            print("Actual output:",run.answer)
            print("Outcome Correctness:",oscore); print("  Reason:",outcome.reason)
            print("Tool Correctness:",tscore); print("  Reason:",treason)
            print("Argument Correctness:",ascore); print("  Reason:",areason)
            print("Forbidden Tool Check:","FAIL" if violations else "PASS")
            if violations: print("  Violations:",violations)
            print("CASE RESULT:","PASS" if passed else "FAIL")
    rate,required=print_summary(results,config)
    failed=[r["id"] for r in results if not r["passed"]]
    assert rate+EPSILON>=required, f"Agent evaluation quality gate failed. pass_rate={rate:.1%}, required={required:.1%}, failed_cases={failed}"
