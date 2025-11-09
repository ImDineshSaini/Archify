from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.core.database import Base


class RepoSource(str, Enum):
    GITHUB = "github"
    GITLAB = "gitlab"


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    source = Column(SQLEnum(RepoSource), nullable=False)
    description = Column(Text)
    language = Column(String)
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="repositories")
    analyses = relationship("Analysis", back_populates="repository", cascade="all, delete-orphan")
