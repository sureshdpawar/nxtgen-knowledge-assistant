from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvaluationInput:
    question: str

    actual_answer: str | None = None

    expected_answer: str | None = None

    retrieved_context: list[str] = field(
        default_factory=list,
    )

    expected_context: list[str] = field(
        default_factory=list,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


@dataclass
class EvaluationMetricResult:
    metric_name: str

    score: float | None

    passed: bool | None = None

    threshold: float | None = None

    reason: str | None = None

    evaluator_type: str = (
        "deterministic"
    )

    evaluator_engine: str = (
        "knowgentiq"
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


class BaseEvaluator(ABC):
    metric_name: str = ""

    evaluator_type: str = (
        "deterministic"
    )

    evaluator_engine: str = (
        "knowgentiq"
    )

    @abstractmethod
    def evaluate(
        self,
        evaluation_input: EvaluationInput,
    ) -> EvaluationMetricResult:
        raise NotImplementedError