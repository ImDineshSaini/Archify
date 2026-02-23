"""Repository for Analysis entity."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.analysis import Analysis
from app.models.repository import Repository


class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, analysis_id: int) -> Optional[Analysis]:
        return self.db.query(Analysis).filter(Analysis.id == analysis_id).first()

    def find_by_id_and_user(self, analysis_id: int, user_id: int) -> Optional[Analysis]:
        return (
            self.db.query(Analysis)
            .join(Repository)
            .filter(Analysis.id == analysis_id, Repository.user_id == user_id)
            .first()
        )

    def find_all_by_user(
        self, user_id: int, repository_id: int = None
    ) -> List[Analysis]:
        query = (
            self.db.query(Analysis)
            .join(Repository)
            .filter(Repository.user_id == user_id)
        )
        if repository_id:
            query = query.filter(Analysis.repository_id == repository_id)
        return query.order_by(Analysis.created_at.desc()).all()

    def create(self, analysis: Analysis) -> Analysis:
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def delete(self, analysis: Analysis) -> None:
        self.db.delete(analysis)
        self.db.commit()
