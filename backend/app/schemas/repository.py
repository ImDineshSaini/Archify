from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from app.models.repository import RepoSource


class RepositoryCreate(BaseModel):
    url: str
    source: RepoSource
    access_token: Optional[str] = None


class RepositoryResponse(BaseModel):
    id: int
    user_id: int
    name: str
    url: str
    source: RepoSource
    description: Optional[str]
    language: Optional[str]
    stars: int
    forks: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
