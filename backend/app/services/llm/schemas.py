"""Pydantic output schemas for structured LLM responses.

These models match the exact shapes consumed by the frontend:
- IssueCard.jsx reads: issue, location, evidence, fix, refactoring, priority,
  effort_hours, expected_improvement, business_impact, dependencies, category
- LayerAnalysisTab.jsx pickIssues() looks for: critical_issues, bottlenecks,
  coverage_gaps, missing_devops, quality_issues
- SynthesisSection.jsx reads: executive_summary, critical_issues, high_priority,
  medium_priority, low_priority, quick_wins, estimated_total_effort_days
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ── Security Layer ──────────────────────────────────────────────────────────

class SecurityIssue(BaseModel):
    issue: str
    location: str
    evidence: str
    fix: str
    priority: str = Field(description="Critical, High, Medium, or Low")


class SecurityAnalysisOutput(BaseModel):
    critical_issues: List[SecurityIssue] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


# ── Performance Layer ───────────────────────────────────────────────────────

class PerformanceBottleneck(BaseModel):
    issue: str
    location: str
    evidence: str
    fix: str
    expected_improvement: str = ""
    priority: str = Field(description="Critical, High, Medium, or Low")


class PerformanceAnalysisOutput(BaseModel):
    bottlenecks: List[PerformanceBottleneck] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


# ── Testing Layer ───────────────────────────────────────────────────────────

class CoverageGap(BaseModel):
    missing_tests_for: str = Field(alias="missing_tests_for", default="")
    test_type: str = ""
    risk_level: str = ""
    fix: str = ""

    model_config = {"populate_by_name": True}


class TestingAnalysisOutput(BaseModel):
    coverage_gaps: List[CoverageGap] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


# ── DevOps Layer ────────────────────────────────────────────────────────────

class DevOpsGap(BaseModel):
    gap: str = ""
    location: str = ""
    impact: str = ""
    fix: str = ""
    priority: str = Field(default="Medium", description="Critical, High, Medium, or Low")


class DevOpsAnalysisOutput(BaseModel):
    missing_devops: List[DevOpsGap] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


# ── Code Quality Layer ──────────────────────────────────────────────────────

class QualityIssue(BaseModel):
    issue: str
    location: str
    evidence: str
    refactoring: str = ""
    priority: str = Field(description="Critical, High, Medium, or Low")


class CodeQualityAnalysisOutput(BaseModel):
    quality_issues: List[QualityIssue] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


# ── Synthesis ───────────────────────────────────────────────────────────────

class SynthesisIssue(BaseModel):
    issue: str = ""
    location: str = ""
    category: str = ""
    fix: str = ""
    effort_hours: Optional[int] = None
    business_impact: str = ""
    dependencies: List[str] = Field(default_factory=list)


class SynthesisOutput(BaseModel):
    executive_summary: str = ""
    critical_issues: List[SynthesisIssue] = Field(default_factory=list)
    high_priority: List[SynthesisIssue] = Field(default_factory=list)
    medium_priority: List[SynthesisIssue] = Field(default_factory=list)
    low_priority: List[SynthesisIssue] = Field(default_factory=list)
    quick_wins: List[str] = Field(default_factory=list)
    estimated_total_effort_days: Optional[int] = None


# ── Architecture ────────────────────────────────────────────────────────────

class SolidAssessment(BaseModel):
    violations: List[str] = Field(default_factory=list)
    score: Optional[int] = None


class CouplingAnalysis(BaseModel):
    high_coupling_modules: List[str] = Field(default_factory=list)
    notes: str = ""


class ArchitectureAnalysisOutput(BaseModel):
    additional_patterns: List[str] = Field(default_factory=list)
    anti_patterns: List[str] = Field(default_factory=list)
    solid_assessment: Optional[SolidAssessment] = None
    testability_score: Optional[int] = None
    coupling_analysis: Optional[CouplingAnalysis] = None
    refactoring_suggestions: List[str] = Field(default_factory=list)


class NFRScore(BaseModel):
    refined_score: int = 0
    confidence: str = "low"
    reasoning: str = ""
    recommendations: List[str] = Field(default_factory=list)


class NFRRefinementOutput(BaseModel):
    scalability: Optional[NFRScore] = None
    testability: Optional[NFRScore] = None
    maintainability: Optional[NFRScore] = None
    deployability: Optional[NFRScore] = None
    observability: Optional[NFRScore] = None
