from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.core.database import Base


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)

    # Metrics
    maintainability_score = Column(Float)
    reliability_score = Column(Float)
    scalability_score = Column(Float)
    security_score = Column(Float)
    overall_score = Column(Float)

    # Detailed results
    code_metrics = Column(JSON)  # Lines of code, complexity, etc.
    architecture_patterns = Column(JSON)  # Detected patterns
    dependencies = Column(JSON)  # Dependency analysis
    issues = Column(JSON)  # Code issues and smells
    suggestions = Column(Text)  # AI-generated suggestions
    detailed_report = Column(JSON)  # Full analysis report

    # Metadata
    analysis_duration = Column(Float)  # Duration in seconds
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    repository = relationship("Repository", back_populates="analyses")
