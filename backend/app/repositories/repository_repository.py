"""Repository for Repository entity."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.repository import Repository


class RepositoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_user(self, user_id: int) -> List[Repository]:
        return (
            self.db.query(Repository)
            .filter(Repository.user_id == user_id)
            .order_by(Repository.created_at.desc())
            .all()
        )

    def find_by_id_and_user(
        self, repository_id: int, user_id: int
    ) -> Optional[Repository]:
        return (
            self.db.query(Repository)
            .filter(Repository.id == repository_id, Repository.user_id == user_id)
            .first()
        )

    def exists_for_user(self, user_id: int, url: str) -> bool:
        return (
            self.db.query(Repository)
            .filter(Repository.user_id == user_id, Repository.url == url)
            .first()
        ) is not None

    def find_by_id(self, repository_id: int) -> Optional[Repository]:
        return self.db.query(Repository).filter(Repository.id == repository_id).first()

    def create(self, repository: Repository) -> Repository:
        self.db.add(repository)
        self.db.commit()
        self.db.refresh(repository)
        return repository

    def delete(self, repository: Repository) -> None:
        self.db.delete(repository)
        self.db.commit()
