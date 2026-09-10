from uuid import UUID

from sqlalchemy.orm import Session

from app.models.agent_eval_case import AgentEvalCase
from app.models.agent_eval_experiment import AgentEvalExperiment
from app.models.agent_eval_result import AgentEvalResult
from app.models.user import User
from app.repositories.agent_eval_experiment_repository import AgentEvalExperimentRepository
from app.repositories.agent_eval_result_repository import AgentEvalResultRepository


class AgentEvalComparisonService:
    """Compare two fully evaluated experiments over the same dataset."""

    def __init__(self):
        self.experiment_repository = AgentEvalExperimentRepository()
        self.result_repository = AgentEvalResultRepository()

    @staticmethod
    def _tenant_id(current_user: User) -> UUID:
        if current_user.tenant_id is None:
            raise ValueError("Agent Evaluation requires a tenant-scoped admin.")
        return current_user.tenant_id

    def _get_experiment(self, db: Session, tenant_id: UUID, experiment_id: UUID) -> AgentEvalExperiment:
        experiment = self.experiment_repository.get(db=db, entity_id=experiment_id)
        if experiment is None or experiment.tenant_id != tenant_id:
            raise ValueError("Agent Evaluation experiment not found.")
        return experiment

    @staticmethod
    def _delta(baseline: float | None, candidate: float | None) -> dict:
        return {
            "baseline": baseline,
            "candidate": candidate,
            "delta": None if baseline is None or candidate is None else candidate - baseline,
        }

    @staticmethod
    def _classification(baseline: AgentEvalResult | None, candidate: AgentEvalResult | None) -> str:
        if baseline is None or candidate is None:
            return "missing_result"
        if baseline.passed is True and candidate.passed is False:
            return "regression"
        if baseline.passed is False and candidate.passed is True:
            return "improvement"
        return "unchanged"

    def compare(
        self,
        db: Session,
        current_user: User,
        baseline_experiment_id: UUID,
        candidate_experiment_id: UUID,
    ) -> dict:
        tenant_id = self._tenant_id(current_user)
        if baseline_experiment_id == candidate_experiment_id:
            raise ValueError("Baseline and candidate experiments must be different.")

        baseline = self._get_experiment(db, tenant_id, baseline_experiment_id)
        candidate = self._get_experiment(db, tenant_id, candidate_experiment_id)

        if baseline.dataset_id != candidate.dataset_id:
            raise ValueError("Experiments must use the same Agent Evaluation dataset.")
        if baseline.agent_id != candidate.agent_id:
            raise ValueError("Experiments must target the same agent.")

        comparable = {"passed", "failed"}
        if baseline.status not in comparable:
            raise ValueError("Baseline experiment must be fully evaluated before comparison.")
        if candidate.status not in comparable:
            raise ValueError("Candidate experiment must be fully evaluated before comparison.")

        baseline_results = {
            r.eval_case_id: r
            for r in self.result_repository.list_by_experiment_id(db=db, experiment_id=baseline.id)
        }
        candidate_results = {
            r.eval_case_id: r
            for r in self.result_repository.list_by_experiment_id(db=db, experiment_id=candidate.id)
        }

        counts = {"regression": 0, "improvement": 0, "unchanged": 0, "missing_result": 0}
        cases = []

        for case_id in sorted(set(baseline_results) | set(candidate_results), key=str):
            b = baseline_results.get(case_id)
            c = candidate_results.get(case_id)
            eval_case = db.get(AgentEvalCase, case_id)
            classification = self._classification(b, c)
            counts[classification] += 1

            cases.append({
                "eval_case_id": case_id,
                "case_name": eval_case.name if eval_case is not None else str(case_id),
                "baseline_result_id": b.id if b is not None else None,
                "candidate_result_id": c.id if c is not None else None,
                "baseline_passed": b.passed if b is not None else None,
                "candidate_passed": c.passed if c is not None else None,
                "classification": classification,
                "outcome_correctness": self._delta(
                    b.outcome_correctness if b is not None else None,
                    c.outcome_correctness if c is not None else None,
                ),
                "tool_correctness": self._delta(
                    b.tool_correctness if b is not None else None,
                    c.tool_correctness if c is not None else None,
                ),
                "argument_correctness": self._delta(
                    b.argument_correctness if b is not None else None,
                    c.argument_correctness if c is not None else None,
                ),
                "baseline_forbidden_tool_violations": (b.forbidden_tool_violations or []) if b else [],
                "candidate_forbidden_tool_violations": (c.forbidden_tool_violations or []) if c else [],
            })

        return {
            "baseline_experiment": baseline,
            "candidate_experiment": candidate,
            "pass_rate": self._delta(baseline.pass_rate, candidate.pass_rate),
            "outcome_correctness": self._delta(baseline.outcome_correctness, candidate.outcome_correctness),
            "tool_correctness": self._delta(baseline.tool_correctness, candidate.tool_correctness),
            "argument_correctness": self._delta(baseline.argument_correctness, candidate.argument_correctness),
            "regressions": counts["regression"],
            "improvements": counts["improvement"],
            "unchanged": counts["unchanged"],
            "missing_results": counts["missing_result"],
            "cases": cases,
        }
