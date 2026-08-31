import json
from pathlib import Path
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class EvaluationSourceDefinition(
    BaseModel
):
    """
    Portable expected-source definition.

    Examples:

        type=url
        value=https://...

        type=external_id
        value=employee-handbook
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    type: str = Field(
        min_length=1,
    )

    value: str = Field(
        min_length=1,
    )


class EvaluationCaseDefinition(
    BaseModel
):
    """
    Portable golden evaluation case.

    It intentionally contains no database
    IDs so the same dataset can be used by
    CI and imported into Knowgentiq.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    id: str = Field(
        min_length=1,
    )

    question: str = Field(
        min_length=1,
    )

    expected_answer: str | None = None

    expected_text: str | None = None

    expected_sources: list[
        EvaluationSourceDefinition
    ] = Field(
        default_factory=list,
    )

    answerable: bool = True

    metadata: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict,
    )

    @model_validator(
        mode="after"
    )
    def validate_ground_truth(
        self,
    ) -> "EvaluationCaseDefinition":
        """
        Keep CI golden-data semantics aligned
        with the existing production dataset
        import rules.

        Answerable cases require an approved
        expected answer.
        """

        if (
            self.answerable
            and not self.expected_answer
        ):
            raise ValueError(
                f"Answerable evaluation case "
                f"'{self.id}' must contain an "
                "expected_answer."
            )

        return self


class EvaluationDatasetDefinition(
    BaseModel
):
    """
    Portable evaluation dataset.

    The target Knowledge Base is deliberately
    not stored here. Target selection belongs
    to the evaluation run configuration.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    name: str = Field(
        min_length=1,
    )

    version: str = Field(
        default="v1",
        min_length=1,
    )

    description: str | None = None

    cases: list[
        EvaluationCaseDefinition
    ] = Field(
        min_length=1,
    )

    @model_validator(
        mode="after"
    )
    def validate_unique_case_ids(
        self,
    ) -> "EvaluationDatasetDefinition":
        case_ids = [
            case.id
            for case
            in self.cases
        ]

        if (
            len(case_ids)
            != len(set(case_ids))
        ):
            raise ValueError(
                "Evaluation dataset contains "
                "duplicate case IDs."
            )

        return self


def load_evaluation_dataset(
    path: str | Path,
) -> EvaluationDatasetDefinition:
    """
    Load and validate a portable JSON
    evaluation dataset.

    CI reads datasets through this function.

    Production dataset upload can later
    validate uploaded JSON against the same
    EvaluationDatasetDefinition before
    mapping it into EvalDataset / EvalCase.
    """

    dataset_path = Path(
        path
    )

    if not dataset_path.exists():
        raise FileNotFoundError(
            "Evaluation dataset file "
            f"not found: {dataset_path}"
        )

    if not dataset_path.is_file():
        raise ValueError(
            "Evaluation dataset path "
            f"is not a file: {dataset_path}"
        )

    with dataset_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        raw_dataset: Any = (
            json.load(
                file
            )
        )

    if not isinstance(
        raw_dataset,
        dict,
    ):
        raise ValueError(
            "Evaluation dataset root "
            "must be a JSON object."
        )

    return (
        EvaluationDatasetDefinition
        .model_validate(
            raw_dataset
        )
    )