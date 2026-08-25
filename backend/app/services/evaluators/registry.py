from app.services.evaluators.base import (
    BaseEvaluator,
)
from app.services.evaluators.retrieval import (
    HitAtKEvaluator,
    ReciprocalRankEvaluator,
)


class EvaluatorRegistry:
    """
    Registry of evaluators supported by Knowgentiq.

    Application code asks for an evaluator by
    metric name rather than depending directly
    on DeepEval, RAGAS, or custom implementations.
    """

    def __init__(self):
        self._evaluators: dict[
            str,
            BaseEvaluator,
        ] = {}

        self.register(
            HitAtKEvaluator()
        )

        self.register(
            ReciprocalRankEvaluator()
        )

    def register(
        self,
        evaluator: BaseEvaluator,
    ) -> None:
        metric_name = (
            evaluator
            .metric_name
            .strip()
            .lower()
        )

        if not metric_name:
            raise ValueError(
                "Evaluator metric_name "
                "cannot be empty."
            )

        self._evaluators[
            metric_name
        ] = evaluator

    def get(
        self,
        metric_name: str,
    ) -> BaseEvaluator:
        normalized_name = (
            metric_name
            .strip()
            .lower()
        )

        evaluator = (
            self._evaluators.get(
                normalized_name
            )
        )

        if evaluator is None:
            raise ValueError(
                "Unknown evaluation metric: "
                f"{metric_name}"
            )

        return evaluator

    def list_metric_names(
        self,
    ) -> list[str]:
        return sorted(
            self._evaluators.keys()
        )