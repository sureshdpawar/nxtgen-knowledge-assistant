from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AgentRunStatus, AgentRunStepType
from app.models.agent import Agent
from app.models.agent_eval_case import AgentEvalCase
from app.models.agent_eval_experiment import AgentEvalExperiment
from app.models.agent_eval_result import AgentEvalResult
from app.models.agent_run_step import AgentRunStep
from app.models.user import User
from app.repositories.agent_eval_experiment_repository import AgentEvalExperimentRepository
from app.repositories.agent_eval_result_repository import AgentEvalResultRepository
from app.schemas.agent_eval import AgentEvalExperimentCreate
from app.services.agent_eval_dataset_service import AgentEvalDatasetService
from app.services.agent_eval_scoring_service import AgentEvalScoringService
from app.services.agent_execution_service import AgentExecutionService


class AgentEvalExperimentService:
    def __init__(self):
        self.repository = AgentEvalExperimentRepository()
        self.result_repository = AgentEvalResultRepository()
        self.dataset_service = AgentEvalDatasetService()
        self.execution_service = AgentExecutionService()
        self.scoring_service = AgentEvalScoringService()

    @staticmethod
    def _tenant_id(current_user: User) -> UUID:
        if current_user.tenant_id is None:
            raise ValueError("Agent Evaluation requires a tenant-scoped admin.")
        return current_user.tenant_id

    def create(self, db: Session, current_user: User, payload: AgentEvalExperimentCreate):
        tenant_id = self._tenant_id(current_user)
        dataset = self.dataset_service.get(db=db, current_user=current_user, dataset_id=payload.dataset_id)
        if dataset is None:
            raise ValueError("Agent Evaluation dataset not found.")
        agent = db.get(Agent, dataset.agent_id)
        if agent is None or agent.tenant_id != tenant_id:
            raise ValueError("Agent not found.")
        experiment = AgentEvalExperiment(
            tenant_id=tenant_id,
            dataset_id=dataset.id,
            agent_id=agent.id,
            name=payload.name.strip(),
            status="pending",
            judge_model=payload.judge_model.strip(),
            pass_rate_threshold=payload.pass_rate_threshold,
            case_count=0,
            passed_count=0,
            metrics={
                "thresholds": {
                    "outcome_correctness": payload.outcome_threshold,
                    "tool_correctness": payload.tool_threshold,
                    "argument_correctness": payload.argument_threshold,
                    "pass_rate": payload.pass_rate_threshold,
                },
                "quality_gate": "pending",
            },
        )
        experiment = self.repository.create(db=db, entity=experiment)
        db.commit(); db.refresh(experiment)
        return experiment

    def get(self, db: Session, current_user: User, experiment_id: UUID):
        tenant_id = self._tenant_id(current_user)
        experiment = self.repository.get(db=db, entity_id=experiment_id)
        if experiment is None or experiment.tenant_id != tenant_id:
            return None
        return experiment

    def list(self, db: Session, current_user: User, dataset_id: UUID | None = None):
        tenant_id = self._tenant_id(current_user)
        if dataset_id is not None and self.dataset_service.get(
            db=db, current_user=current_user, dataset_id=dataset_id
        ) is None:
            raise ValueError("Agent Evaluation dataset not found.")
        return self.repository.list_by_tenant_id(db=db, tenant_id=tenant_id, dataset_id=dataset_id)

    def list_results(self, db: Session, current_user: User, experiment_id: UUID):
        experiment = self.get(db, current_user, experiment_id)
        if experiment is None:
            raise ValueError("Agent Evaluation experiment not found.")
        return self.result_repository.list_by_experiment_id(db=db, experiment_id=experiment.id)

    @staticmethod
    def _extract_tools_called(db: Session, run_id: UUID) -> list[dict]:
        stmt = (select(AgentRunStep)
                .where(AgentRunStep.run_id == run_id, AgentRunStep.step_type == AgentRunStepType.TOOL)
                .order_by(AgentRunStep.step_number.asc()))
        return [{"name": step.name, "input": step.input_data or {}, "output": step.output_data or {},
                 "status": step.status.value} for step in db.scalars(stmt).all()]

    @staticmethod
    def _thresholds(experiment: AgentEvalExperiment) -> dict:
        t = (experiment.metrics or {}).get("thresholds") or {}
        return {
            "outcome_correctness": float(t.get("outcome_correctness", 0.80)),
            "tool_correctness": float(t.get("tool_correctness", 1.00)),
            "argument_correctness": float(t.get("argument_correctness", 0.80)),
        }

    async def run(self, db: Session, current_user: User, experiment_id: UUID):
        experiment = self.get(db, current_user, experiment_id)
        if experiment is None:
            raise ValueError("Agent Evaluation experiment not found.")
        if experiment.status == "running":
            raise ValueError("Agent Evaluation experiment is already running.")
        if experiment.results:
            raise ValueError("Agent Evaluation experiment has already been executed. Create a new experiment for another regression run.")

        cases = list(db.scalars(select(AgentEvalCase).where(
            AgentEvalCase.dataset_id == experiment.dataset_id,
            AgentEvalCase.enabled.is_(True),
        ).order_by(AgentEvalCase.created_at.asc())).all())
        if not cases:
            raise ValueError("Agent Evaluation dataset has no enabled cases.")

        thresholds = self._thresholds(experiment)
        experiment.status = "running"
        experiment.case_count = len(cases)
        experiment.passed_count = 0
        experiment.pass_rate = None
        experiment.metrics = {**(experiment.metrics or {}), "phase": "runtime_and_scoring", "quality_gate": "running"}
        db.commit()

        completed_results = 0
        try:
            for case in cases:
                run_result = await self.execution_service.run(
                    db=db, current_user=current_user, agent_id=experiment.agent_id,
                    query=case.input, thread_id=uuid4(),
                )
                run_id = run_result["run_id"]
                run_status = run_result["status"]
                tools_called = self._extract_tools_called(db, run_id)
                forbidden = {str(n).strip() for n in (case.forbidden_tools or []) if str(n).strip()}
                called = {str(i.get("name") or "").strip() for i in tools_called if str(i.get("name") or "").strip()}
                violations = sorted(forbidden.intersection(called))
                runtime_completed = run_status == AgentRunStatus.COMPLETED

                result = AgentEvalResult(
                    experiment_id=experiment.id,
                    eval_case_id=case.id,
                    agent_run_id=run_id,
                    actual_answer=run_result.get("answer"),
                    tools_called=tools_called,
                    forbidden_tool_violations=violations,
                    passed=False,
                    metrics={
                        "runtime_status": run_status.value,
                        "runtime_completed": runtime_completed,
                        "forbidden_tool_check": "PASS" if not violations else "FAIL",
                    },
                    judge_metadata={"judge_model": experiment.judge_model},
                )
                db.add(result); db.flush()

                if runtime_completed:
                    scores = self.scoring_service.score(
                        case=case, result=result, judge_model=experiment.judge_model or "gpt-5.4",
                        outcome_threshold=thresholds["outcome_correctness"],
                        tool_threshold=thresholds["tool_correctness"],
                        argument_threshold=thresholds["argument_correctness"],
                    )
                    result.outcome_correctness = scores["outcome_correctness"]["score"]
                    result.tool_correctness = scores["tool_correctness"]["score"]
                    result.argument_correctness = scores["argument_correctness"]["score"]
                    result.passed = scores["passed"]
                    result.metrics = {
                        **result.metrics,
                        "deepeval_scoring": "completed",
                        "outcome_correctness": scores["outcome_correctness"],
                        "tool_correctness": scores["tool_correctness"],
                        "argument_correctness": scores["argument_correctness"],
                        "forbidden_tool_check": scores["forbidden_tool_check"],
                    }
                else:
                    result.metrics = {**result.metrics, "deepeval_scoring": "skipped_runtime_not_completed"}

                db.commit(); completed_results += 1

            results = self.result_repository.list_by_experiment_id(db=db, experiment_id=experiment.id)
            agg = self.scoring_service.aggregate(results)
            experiment.case_count = agg["case_count"]
            experiment.passed_count = agg["passed_count"]
            experiment.pass_rate = agg["pass_rate"]
            experiment.outcome_correctness = agg["outcome_correctness"]
            experiment.tool_correctness = agg["tool_correctness"]
            experiment.argument_correctness = agg["argument_correctness"]
            gate = experiment.pass_rate >= experiment.pass_rate_threshold
            experiment.status = "passed" if gate else "failed"
            experiment.metrics = {
                **(experiment.metrics or {}),
                "phase": "completed",
                "completed_results": completed_results,
                "quality_gate": "PASS" if gate else "FAIL",
            }
            db.commit(); db.refresh(experiment)
            return experiment

        except HTTPException as exc:
            db.rollback()
            experiment = db.get(AgentEvalExperiment, experiment_id)
            if experiment is not None:
                experiment.status = "failed"
                experiment.metrics = {**(experiment.metrics or {}), "phase": "runtime_or_scoring_failure",
                                      "quality_gate": "FAIL", "failure": str(exc.detail),
                                      "completed_results": completed_results}
                db.commit()
            raise
        except Exception as exc:
            db.rollback()
            experiment = db.get(AgentEvalExperiment, experiment_id)
            if experiment is not None:
                experiment.status = "failed"
                experiment.metrics = {**(experiment.metrics or {}), "phase": "runtime_or_scoring_failure",
                                      "quality_gate": "FAIL", "failure": str(exc),
                                      "completed_results": completed_results}
                db.commit()
            raise
