from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.repository import Repository
from app.models.analysis import Analysis, AnalysisStatus
from app.schemas.analysis import AnalysisCreate, AnalysisResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analyses", tags=["Analyses"])


async def run_analysis_background(analysis_id: int, db: Session):
    """Background task to run analysis"""
    analysis_service = AnalysisService(db)
    await analysis_service.run_analysis(analysis_id)


@router.post("/", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    analysis_data: AnalysisCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new code analysis"""
    # Verify repository exists and belongs to user
    repository = db.query(Repository).filter(
        Repository.id == analysis_data.repository_id,
        Repository.user_id == current_user.id
    ).first()

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )

    # Create analysis record
    analysis = Analysis(
        repository_id=repository.id,
        status=AnalysisStatus.PENDING
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Run analysis in background
    background_tasks.add_task(run_analysis_background, analysis.id, db)

    return analysis


@router.get("/", response_model=List[AnalysisResponse])
def list_analyses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repository_id: int = None
):
    """List all analyses for the current user"""
    query = db.query(Analysis).join(Repository).filter(
        Repository.user_id == current_user.id
    )

    if repository_id:
        query = query.filter(Analysis.repository_id == repository_id)

    analyses = query.order_by(Analysis.created_at.desc()).all()

    return analyses


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific analysis"""
    analysis = db.query(Analysis).join(Repository).filter(
        Analysis.id == analysis_id,
        Repository.user_id == current_user.id
    ).first()

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
    db: Session = Depends(get_db)
):
    """Delete an analysis"""
    analysis = db.query(Analysis).join(Repository).filter(
        Analysis.id == analysis_id,
        Repository.user_id == current_user.id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    db.delete(analysis)
    db.commit()

    return None
