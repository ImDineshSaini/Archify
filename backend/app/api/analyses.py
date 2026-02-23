from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import Response
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


@router.get("/{analysis_id}/pdf")
def download_analysis_pdf(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    analysis_repo: AnalysisRepository = Depends(_get_analysis_repo),
    repo_repo: RepositoryRepository = Depends(_get_repository_repo),
):
    """Download analysis report as PDF"""
    analysis = analysis_repo.find_by_id_and_user(analysis_id, current_user.id)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    repo = repo_repo.find_by_id(analysis.repository_id)
    repo_name = repo.name if repo else "Unknown Repository"
    repo_url = repo.url if repo else ""

    from app.services.pdf_report import generate_analysis_pdf

    analysis_data = {
        "overall_score": analysis.overall_score,
        "maintainability_score": analysis.maintainability_score,
        "reliability_score": analysis.reliability_score,
        "scalability_score": analysis.scalability_score,
        "security_score": analysis.security_score,
        "detailed_report": analysis.detailed_report,
        "code_metrics": analysis.code_metrics,
        "suggestions": analysis.suggestions,
        "issues": analysis.issues,
        "analysis_duration": analysis.analysis_duration,
    }

    pdf_bytes = generate_analysis_pdf(analysis_data, repo_name, repo_url=repo_url)

    filename = f"archify-report-{repo_name.replace(' ', '_')}-{analysis_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


from pydantic import BaseModel as _BaseModel


class IssueStatusUpdate(_BaseModel):
    layer: str
    issue_index: int
    status: str  # "open", "false_positive", "accepted", "resolved"


@router.patch("/{analysis_id}/issue-status")
def update_issue_status(
    analysis_id: int,
    update: IssueStatusUpdate,
    current_user: User = Depends(get_current_user),
    analysis_repo: AnalysisRepository = Depends(_get_analysis_repo),
    db: Session = Depends(get_db),
):
    """Update the triage status of a specific issue (e.g. mark as false positive)"""
    analysis = analysis_repo.find_by_id_and_user(analysis_id, current_user.id)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    valid_statuses = {"open", "false_positive", "accepted", "resolved"}
    new_status = update.status
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    # Store issue statuses in detailed_report.issue_statuses
    detailed_report = analysis.detailed_report or {}
    issue_statuses = detailed_report.get("issue_statuses", {})

    status_key = f"{update.layer}:{update.issue_index}"
    issue_statuses[status_key] = new_status

    detailed_report["issue_statuses"] = issue_statuses
    analysis.detailed_report = detailed_report

    # Force SQLAlchemy to detect JSON mutation
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(analysis, "detailed_report")
    db.commit()

    return {"message": "Issue status updated", "key": status_key, "status": new_status}
