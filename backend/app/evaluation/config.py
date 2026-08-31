from pathlib import Path
from typing import Any

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class EvaluationTargetConfig(
    BaseModel
):
    """
    Defines the system under evaluation.

    For the first RAG integration we support
    Knowledge Base targets.

    This belongs to the evaluation run, not
    the golden dataset.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    knowledge_base_id: str = Field(
        min_length=1,
    )


class EvaluationMetricConfig(
    BaseModel
):
    """
    Configuration for one evaluation metric.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    enabled: bool = True

    threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
    )


class EvaluationRetrievalConfig(
    BaseModel
):
    """
    Retrieval parameters used for a RAG run.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=100,
    )


class EvaluationExecutionConfig(
    BaseModel
):
    """
    Controls execution behavior.

    CI usually fails on metric thresholds.
    Product runs can instead persist results
    and evaluate release policy separately.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    fail_on_threshold: bool = True

    fail_fast: bool = False


class EvaluationSuiteConfig(
    BaseModel
):
    """
    Metadata describing an evaluation suite.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    name: str = Field(
        min_length=1,
    )

    description: str | None = None


class EvaluationRunConfig(
    BaseModel
):
    """
    Source-independent evaluation-run
    configuration.

    CI:
        constructed from YAML.

    Production:
        constructed from platform/database
        configuration.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    suite: EvaluationSuiteConfig

    target: EvaluationTargetConfig

    retrieval: EvaluationRetrievalConfig = (
        EvaluationRetrievalConfig()
    )

    metrics: dict[
        str,
        EvaluationMetricConfig,
    ]

    execution: EvaluationExecutionConfig = (
        EvaluationExecutionConfig()
    )

    @model_validator(
        mode="after"
    )
    def validate_metrics(
        self,
    ) -> "EvaluationRunConfig":
        if not self.metrics:
            raise ValueError(
                "Evaluation configuration must "
                "contain at least one metric."
            )

        if not any(
            metric.enabled
            for metric
            in self.metrics.values()
        ):
            raise ValueError(
                "Evaluation configuration must "
                "enable at least one metric."
            )

        return self

    def enabled_metrics(
        self,
    ) -> dict[
        str,
        EvaluationMetricConfig,
    ]:
        return {
            name: config
            for name, config
            in self.metrics.items()
            if config.enabled
        }


def load_evaluation_config(
    path: str | Path,
) -> EvaluationRunConfig:
    """
    Load and validate an evaluation
    configuration file.
    """

    config_path = Path(
        path
    )

    if not config_path.exists():
        raise FileNotFoundError(
            "Evaluation configuration file "
            f"not found: {config_path}"
        )

    if not config_path.is_file():
        raise ValueError(
            "Evaluation configuration path "
            f"is not a file: {config_path}"
        )

    with config_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        raw_config: Any = (
            yaml.safe_load(
                file
            )
        )

    if raw_config is None:
        raise ValueError(
            "Evaluation configuration file "
            "is empty."
        )

    if not isinstance(
        raw_config,
        dict,
    ):
        raise ValueError(
            "Evaluation configuration root "
            "must be a YAML object."
        )

    return (
        EvaluationRunConfig
        .model_validate(
            raw_config
        )
    )