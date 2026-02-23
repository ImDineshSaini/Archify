from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.repository import Repository
from app.schemas.repository import RepositoryCreate, RepositoryResponse
from app.services.repo_service import RepoService
from app.repositories.repository_repository import RepositoryRepository

router = APIRouter(prefix="/repositories", tags=["Repositories"])


def _get_repository_repo(db: Session = Depends(get_db)) -> RepositoryRepository:
    return RepositoryRepository(db)


@router.post("/", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def create_repository(
    repo_data: RepositoryCreate,
    current_user: User = Depends(get_current_user),
    repo_repo: RepositoryRepository = Depends(_get_repository_repo),
):
    """Add a new repository for analysis"""
    try:
        repo_service = RepoService(
            source=repo_data.source,
            token=repo_data.access_token
        )

        repo_info = await repo_service.get_repo_info(repo_data.url)

        if repo_repo.exists_for_user(current_user.id, repo_data.url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Repository already exists"
            )

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

        return repo_repo.create(repository)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add repository: {str(e)}"
        )


@router.get("/", response_model=List[RepositoryResponse])
def list_repositories(
    current_user: User = Depends(get_current_user),
    repo_repo: RepositoryRepository = Depends(_get_repository_repo),
):
    """List all repositories for the current user"""
    return repo_repo.find_by_user(current_user.id)


@router.get("/{repository_id}", response_model=RepositoryResponse)
def get_repository(
    repository_id: int,
    current_user: User = Depends(get_current_user),
    repo_repo: RepositoryRepository = Depends(_get_repository_repo),
):
    """Get a specific repository"""
    repository = repo_repo.find_by_id_and_user(repository_id, current_user.id)

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
    repo_repo: RepositoryRepository = Depends(_get_repository_repo),
):
    """Delete a repository"""
    repository = repo_repo.find_by_id_and_user(repository_id, current_user.id)

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )

    repo_repo.delete(repository)

    return None
