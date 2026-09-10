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
from app.services.agent_execution_service import AgentExecutionService


class AgentEvalExperimentService:
    """Slice 4A: persisted experiment lifecycle plus real AgentExecutionService execution."""

    def __init__(self):
        self.repository = AgentEvalExperimentRepository()
        self.result_repository = AgentEvalResultRepository()
        self.dataset_service = AgentEvalDatasetService()
        self.execution_service = AgentExecutionService()

    @staticmethod
    def _tenant_id(current_user: User) -> UUID:
        if current_user.tenant_id is None:
            raise ValueError("Agent Evaluation requires a tenant-scoped admin.")
        return current_user.tenant_id

    def create(self, db: Session, current_user: User, payload: AgentEvalExperimentCreate):
        tenant_id = self._tenant_id(current_user)
        dataset = self.dataset_service.get(
            db=db, current_user=current_user, dataset_id=payload.dataset_id
        )
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
            pass_rate_threshold=payload.pass_rate_threshold,
            case_count=0,
            passed_count=0,
            metrics={},
        )
        experiment = self.repository.create(db=db, entity=experiment)
        db.commit()
        db.refresh(experiment)
        return experiment

    def get(self, db: Session, current_user: User, experiment_id: UUID):
        tenant_id = self._tenant_id(current_user)
        experiment = self.repository.get(db=db, entity_id=experiment_id)
        if experiment is None or experiment.tenant_id != tenant_id:
            return None
        return experiment

    def list(self, db: Session, current_user: User, dataset_id: UUID | None = None):
        tenant_id = self._tenant_id(current_user)
        if dataset_id is not None:
            dataset = self.dataset_service.get(
                db=db, current_user=current_user, dataset_id=dataset_id
            )
            if dataset is None:
                raise ValueError("Agent Evaluation dataset not found.")
        return self.repository.list_by_tenant_id(
            db=db, tenant_id=tenant_id, dataset_id=dataset_id
        )

    def list_results(self, db: Session, current_user: User, experiment_id: UUID):
        experiment = self.get(db, current_user, experiment_id)
        if experiment is None:
            raise ValueError("Agent Evaluation experiment not found.")
        return self.result_repository.list_by_experiment_id(
            db=db, experiment_id=experiment.id
        )

    @staticmethod
    def _extract_tools_called(db: Session, run_id: UUID) -> list[dict]:
        stmt = (
            select(AgentRunStep)
            .where(
                AgentRunStep.run_id == run_id,
                AgentRunStep.step_type == AgentRunStepType.TOOL,
            )
            .order_by(AgentRunStep.step_number.asc())
        )
        result = []
        for step in db.scalars(stmt).all():
            result.append({
                "name": step.name,
                "input": step.input_data or {},
                "output": step.output_data or {},
                "status": step.status.value,
            })
        return result

    async def run(self, db: Session, current_user: User, experiment_id: UUID):
        experiment = self.get(db, current_user, experiment_id)
        if experiment is None:
            raise ValueError("Agent Evaluation experiment not found.")
        if experiment.status == "running":
            raise ValueError("Agent Evaluation experiment is already running.")
        if experiment.results:
            raise ValueError(
                "Agent Evaluation experiment has already been executed. "
                "Create a new experiment for another regression run."
            )

        cases = list(db.scalars(
            select(AgentEvalCase)
            .where(
                AgentEvalCase.dataset_id == experiment.dataset_id,
                AgentEvalCase.enabled.is_(True),
            )
            .order_by(AgentEvalCase.created_at.asc())
        ).all())
        if not cases:
            raise ValueError("Agent Evaluation dataset has no enabled cases.")

        experiment.status = "running"
        experiment.case_count = len(cases)
        experiment.metrics = {
            "phase": "runtime_execution",
            "scoring": "pending_deepeval_slice_4b",
        }
        db.commit()

        completed_results = 0
        try:
            for case in cases:
                run_result = await self.execution_service.run(
                    db=db,
                    current_user=current_user,
                    agent_id=experiment.agent_id,
                    query=case.input,
                    thread_id=uuid4(),
                )
                run_id = run_result["run_id"]
                run_status = run_result["status"]
                tools_called = self._extract_tools_called(db, run_id)

                forbidden = {
                    str(name).strip() for name in (case.forbidden_tools or [])
                    if str(name).strip()
                }
                called_names = {
                    str(item.get("name") or "").strip()
                    for item in tools_called
                    if str(item.get("name") or "").strip()
                }
                violations = sorted(forbidden.intersection(called_names))
                runtime_completed = run_status == AgentRunStatus.COMPLETED

                db.add(AgentEvalResult(
                    experiment_id=experiment.id,
                    eval_case_id=case.id,
                    agent_run_id=run_id,
                    actual_answer=run_result.get("answer"),
                    tools_called=tools_called,
                    forbidden_tool_violations=violations,
                    passed=False if (not runtime_completed or violations) else None,
                    metrics={
                        "runtime_status": run_status.value,
                        "runtime_completed": runtime_completed,
                        "forbidden_tool_check": "PASS" if not violations else "FAIL",
                        "deepeval_scoring": "pending",
                    },
                    judge_metadata={},
                ))
                db.commit()
                completed_results += 1

                if not runtime_completed:
                    experiment.status = "failed"
                    experiment.metrics = {
                        "phase": "runtime_execution",
                        "failure": f"Agent run did not complete. Status: {run_status.value}",
                        "completed_results": completed_results,
                    }
                    db.commit()
                    db.refresh(experiment)
                    return experiment

            experiment.status = "executed"
            experiment.metrics = {
                "phase": "runtime_execution",
                "completed_results": completed_results,
                "scoring": "pending_deepeval_slice_4b",
            }
            db.commit()
            db.refresh(experiment)
            return experiment

        except HTTPException as exc:
            db.rollback()
            experiment = db.get(AgentEvalExperiment, experiment_id)
            if experiment is not None:
                experiment.status = "failed"
                experiment.metrics = {
                    "phase": "runtime_execution",
                    "failure": str(exc.detail),
                    "completed_results": completed_results,
                }
                db.commit()
            raise
        except Exception as exc:
            db.rollback()
            experiment = db.get(AgentEvalExperiment, experiment_id)
            if experiment is not None:
                experiment.status = "failed"
                experiment.metrics = {
                    "phase": "runtime_execution",
                    "failure": str(exc),
                    "completed_results": completed_results,
                }
                db.commit()
            raise
