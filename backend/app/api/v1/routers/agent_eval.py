import json
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.auth.permissions import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent_eval import (
    AgentEvalCaseCreate, AgentEvalCaseRead, AgentEvalDatasetCreate,
    AgentEvalDatasetImportPayload, AgentEvalDatasetImportRead, AgentEvalDatasetRead,
    AgentEvalExperimentCompareRead, AgentEvalExperimentCompareRequest,
    AgentEvalExperimentCreate, AgentEvalExperimentRead, AgentEvalResultRead,
)
from app.services.agent_eval_case_service import AgentEvalCaseService
from app.services.agent_eval_comparison_service import AgentEvalComparisonService
from app.services.agent_eval_dataset_import_service import AgentEvalDatasetImportService
from app.services.agent_eval_dataset_service import AgentEvalDatasetService
from app.services.agent_eval_experiment_service import AgentEvalExperimentService

router = APIRouter(prefix="/agent-eval", tags=["Agent Evaluation"])
dataset_service = AgentEvalDatasetService()
dataset_import_service = AgentEvalDatasetImportService()
case_service = AgentEvalCaseService()
experiment_service = AgentEvalExperimentService()
comparison_service = AgentEvalComparisonService()

def bad_request(exc: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.post("/datasets", response_model=AgentEvalDatasetRead, status_code=status.HTTP_201_CREATED)
def create_dataset(payload: AgentEvalDatasetCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try: return dataset_service.create(db=db, current_user=current_user, payload=payload)
    except ValueError as exc: raise bad_request(exc) from exc

@router.post("/datasets/import", response_model=AgentEvalDatasetImportRead, status_code=status.HTTP_201_CREATED)
async def import_dataset(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    filename = file.filename or ""
    if not filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Agent Evaluation dataset must be a JSON file.")
    try:
        raw_content = await file.read()
        if not raw_content: raise ValueError("Uploaded JSON file is empty.")
        try: data = json.loads(raw_content.decode("utf-8"))
        except UnicodeDecodeError as exc: raise ValueError("Agent Evaluation dataset must be UTF-8 encoded.") from exc
        except json.JSONDecodeError as exc: raise ValueError(f"Invalid JSON: {exc.msg}.") from exc
        if not isinstance(data, dict): raise ValueError("Agent Evaluation dataset JSON must contain one object.")
        try: payload = AgentEvalDatasetImportPayload.model_validate(data)
        except ValidationError as exc: raise ValueError(f"Invalid Agent Evaluation dataset: {exc}") from exc
        dataset, case_count = dataset_import_service.import_dataset(db=db, current_user=current_user, payload=payload)
        return AgentEvalDatasetImportRead(dataset=AgentEvalDatasetRead.model_validate(dataset), case_count=case_count)
    except ValueError as exc: raise bad_request(exc) from exc

@router.get("/datasets", response_model=list[AgentEvalDatasetRead])
def list_datasets(agent_id: UUID | None = None, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try: return dataset_service.list(db=db, current_user=current_user, agent_id=agent_id)
    except ValueError as exc: raise bad_request(exc) from exc

@router.get("/datasets/{dataset_id}", response_model=AgentEvalDatasetRead)
def get_dataset(dataset_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try: dataset = dataset_service.get(db=db, current_user=current_user, dataset_id=dataset_id)
    except ValueError as exc: raise bad_request(exc) from exc
    if dataset is None: raise HTTPException(status_code=404, detail="Agent Evaluation dataset not found.")
    return dataset

@router.post("/datasets/{dataset_id}/cases", response_model=AgentEvalCaseRead, status_code=status.HTTP_201_CREATED)
def create_case(dataset_id: UUID, payload: AgentEvalCaseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try: return case_service.create(db=db, current_user=current_user, dataset_id=dataset_id, payload=payload)
    except ValueError as exc: raise bad_request(exc) from exc

@router.get("/datasets/{dataset_id}/cases", response_model=list[AgentEvalCaseRead])
def list_cases(dataset_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try: return case_service.list(db=db, current_user=current_user, dataset_id=dataset_id)
    except ValueError as exc: raise bad_request(exc) from exc

@router.delete("/datasets/{dataset_id}/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(dataset_id: UUID, case_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try: case_service.delete(db=db, current_user=current_user, dataset_id=dataset_id, case_id=case_id)
    except ValueError as exc: raise bad_request(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/experiments", response_model=AgentEvalExperimentRead, status_code=status.HTTP_201_CREATED)
def create_experiment(payload: AgentEvalExperimentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try: return experiment_service.create(db=db, current_user=current_user, payload=payload)
    except ValueError as exc: raise bad_request(exc) from exc

@router.get("/experiments", response_model=list[AgentEvalExperimentRead])
def list_experiments(dataset_id: UUID | None = None, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try: return experiment_service.list(db=db, current_user=current_user, dataset_id=dataset_id)
    except ValueError as exc: raise bad_request(exc) from exc

@router.post("/experiments/compare", response_model=AgentEvalExperimentCompareRead)
def compare_experiments(payload: AgentEvalExperimentCompareRequest, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try:
        return comparison_service.compare(
            db=db, current_user=current_user,
            baseline_experiment_id=payload.baseline_experiment_id,
            candidate_experiment_id=payload.candidate_experiment_id,
        )
    except ValueError as exc: raise bad_request(exc) from exc

@router.get("/experiments/{experiment_id}", response_model=AgentEvalExperimentRead)
def get_experiment(experiment_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try: experiment = experiment_service.get(db=db, current_user=current_user, experiment_id=experiment_id)
    except ValueError as exc: raise bad_request(exc) from exc
    if experiment is None: raise HTTPException(status_code=404, detail="Agent Evaluation experiment not found.")
    return experiment

@router.post("/experiments/{experiment_id}/run", response_model=AgentEvalExperimentRead)
async def run_experiment(experiment_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try: return await experiment_service.run(db=db, current_user=current_user, experiment_id=experiment_id)
    except ValueError as exc: raise bad_request(exc) from exc

@router.get("/experiments/{experiment_id}/results", response_model=list[AgentEvalResultRead])
def list_experiment_results(experiment_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try: return experiment_service.list_results(db=db, current_user=current_user, experiment_id=experiment_id)
    except ValueError as exc: raise bad_request(exc) from exc
