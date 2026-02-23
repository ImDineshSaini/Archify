from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.analysis import Analysis, AnalysisStatus
from app.schemas.analysis import AnalysisCreate, AnalysisResponse
from app.services.analysis_service import AnalysisService
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.repository_repository import RepositoryRepository

router = APIRouter(prefix="/analyses", tags=["Analyses"])


def _get_analysis_repo(db: Session = Depends(get_db)) -> AnalysisRepository:
    return AnalysisRepository(db)


def _get_repository_repo(db: Session = Depends(get_db)) -> RepositoryRepository:
    return RepositoryRepository(db)


async def run_analysis_background(analysis_id: int, db: Session):
    """Background task to run analysis"""
    analysis_service = AnalysisService(db)
    await analysis_service.run_analysis(analysis_id)


@router.post("/", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    analysis_data: AnalysisCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo_repo: RepositoryRepository = Depends(_get_repository_repo),
    analysis_repo: AnalysisRepository = Depends(_get_analysis_repo),
):
    """Start a new code analysis"""
    repository = repo_repo.find_by_id_and_user(analysis_data.repository_id, current_user.id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )

    analysis = Analysis(
        repository_id=repository.id,
        status=AnalysisStatus.PENDING
    )
    analysis = analysis_repo.create(analysis)

    background_tasks.add_task(run_analysis_background, analysis.id, db)

    return analysis


@router.get("/", response_model=List[AnalysisResponse])
def list_analyses(
    current_user: User = Depends(get_current_user),
    analysis_repo: AnalysisRepository = Depends(_get_analysis_repo),
    repository_id: int = None,
):
    """List all analyses for the current user"""
    return analysis_repo.find_all_by_user(current_user.id, repository_id)


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    analysis_repo: AnalysisRepository = Depends(_get_analysis_repo),
):
    """Get a specific analysis"""
    analysis = analysis_repo.find_by_id_and_user(analysis_id, current_user.id)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    return analysis


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    analysis_repo: AnalysisRepository = Depends(_get_analysis_repo),
):
    """Delete an analysis"""
    analysis = analysis_repo.find_by_id_and_user(analysis_id, current_user.id)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    analysis_repo.delete(analysis)

    return None
