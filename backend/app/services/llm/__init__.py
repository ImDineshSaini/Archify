"""LLM service package - modular LLM integration."""

from app.services.llm.client_factory import create_llm_client
from app.services.llm.suggestions import generate_analysis_suggestions
from app.services.llm.architecture_llm import (
    analyze_architecture_patterns,
    analyze_architecture_from_tree,
    refine_nfr_scores,
    generate_improvement_roadmap,
)
from app.services.llm.security_analyzer import SecurityAnalyzer
from app.services.llm.performance_analyzer import PerformanceAnalyzer
from app.services.llm.testing_analyzer import TestingAnalyzer
from app.services.llm.devops_analyzer import DevOpsAnalyzer
from app.services.llm.code_quality_analyzer import CodeQualityAnalyzer
from app.services.llm.synthesis import synthesize_deep_analysis

__all__ = [
    "create_llm_client",
    "generate_analysis_suggestions",
    "analyze_architecture_patterns",
    "analyze_architecture_from_tree",
    "refine_nfr_scores",
    "generate_improvement_roadmap",
    "SecurityAnalyzer",
    "PerformanceAnalyzer",
    "TestingAnalyzer",
    "DevOpsAnalyzer",
    "CodeQualityAnalyzer",
    "synthesize_deep_analysis",
]
