from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.repository import Repository
from app.schemas.repository import RepositoryCreate, RepositoryResponse
from app.services.repo_service import RepoService

router = APIRouter(prefix="/repositories", tags=["Repositories"])


@router.post("/", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def create_repository(
    repo_data: RepositoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new repository for analysis"""
    try:
        # Initialize repo service
        repo_service = RepoService(
            source=repo_data.source,
            token=repo_data.access_token
        )

        # Fetch repository information
        repo_info = await repo_service.get_repo_info(repo_data.url)

        # Check if repository already exists for this user
        existing_repo = db.query(Repository).filter(
            Repository.user_id == current_user.id,
            Repository.url == repo_data.url
        ).first()

        if existing_repo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Repository already exists"
            )

        # Create repository record
        repository = Repository(
            user_id=current_user.id,
            name=repo_info["name"],
            url=repo_data.url,
            source=repo_data.source,
            description=repo_info.get("description"),
            language=repo_info.get("language"),
            stars=repo_info.get("stars", 0),
            forks=repo_info.get("forks", 0),
        )

        db.add(repository)
        db.commit()
        db.refresh(repository)

        return repository

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add repository: {str(e)}"
        )


@router.get("/", response_model=List[RepositoryResponse])
def list_repositories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all repositories for the current user"""
    repositories = db.query(Repository).filter(
        Repository.user_id == current_user.id
    ).order_by(Repository.created_at.desc()).all()

    return repositories


@router.get("/{repository_id}", response_model=RepositoryResponse)
def get_repository(
    repository_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific repository"""
    repository = db.query(Repository).filter(
        Repository.id == repository_id,
        Repository.user_id == current_user.id
    ).first()

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )

    return repository


@router.delete("/{repository_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_repository(
    repository_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a repository"""
    repository = db.query(Repository).filter(
        Repository.id == repository_id,
        Repository.user_id == current_user.id
    ).first()

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )

    db.delete(repository)
    db.commit()

    return None
