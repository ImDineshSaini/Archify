"""LLM Service facade -- delegates to app.services.llm submodules.

Public API is unchanged so callers (analysis_service.py, settings.py) need no modifications.
"""

from typing import Dict, Any, Optional
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
from app.services.llm.synthesis import synthesize_deep_analysis as _synthesize


class LLMService:
    """Service for interacting with different LLM providers."""

    def __init__(
        self,
        provider: str,
        api_key: str,
        model: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment_name: Optional[str] = None,
    ):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.client = create_llm_client(
            provider=self.provider,
            api_key=self.api_key,
            model=self.model,
            endpoint=self.endpoint,
            deployment_name=self.deployment_name,
        )

    # --- suggestion / architecture helpers ---

    def generate_analysis_suggestions(self, analysis_results: Dict[str, Any]) -> str:
        return generate_analysis_suggestions(self.client, analysis_results)

    def analyze_architecture_patterns(self, file_structure: Dict[str, Any]) -> str:
        return analyze_architecture_patterns(self.client, file_structure)

    def analyze_architecture_from_tree(
        self, directory_tree: str, basic_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        return analyze_architecture_from_tree(self.client, directory_tree, basic_analysis)

    def refine_nfr_scores(
        self, directory_tree: str, basic_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        return refine_nfr_scores(self.client, directory_tree, basic_analysis)

    def generate_improvement_roadmap(
        self, current_scores: Dict[str, float], target_scores: Dict[str, float]
    ) -> str:
        return generate_improvement_roadmap(self.client, current_scores, target_scores)

    # --- deep analysis layers (with optional RAG vector_store) ---

    def analyze_security_layer(
        self, directory_tree: str, basic_analysis: Dict[str, Any],
        vector_store=None,
    ) -> Dict[str, Any]:
        return SecurityAnalyzer().analyze(self.client, directory_tree, basic_analysis, vector_store)

    def analyze_performance_layer(
        self, directory_tree: str, basic_analysis: Dict[str, Any],
        vector_store=None,
    ) -> Dict[str, Any]:
        return PerformanceAnalyzer().analyze(self.client, directory_tree, basic_analysis, vector_store)

    def analyze_testing_layer(
        self, directory_tree: str, basic_analysis: Dict[str, Any],
        vector_store=None,
    ) -> Dict[str, Any]:
        return TestingAnalyzer().analyze(self.client, directory_tree, basic_analysis, vector_store)

    def analyze_devops_layer(
        self, directory_tree: str, basic_analysis: Dict[str, Any],
        vector_store=None,
    ) -> Dict[str, Any]:
        return DevOpsAnalyzer().analyze(self.client, directory_tree, basic_analysis, vector_store)

    def analyze_code_quality_layer(
        self, directory_tree: str, basic_analysis: Dict[str, Any],
        vector_store=None,
    ) -> Dict[str, Any]:
        return CodeQualityAnalyzer().analyze(self.client, directory_tree, basic_analysis, vector_store)

    def synthesize_deep_analysis(
        self,
        security_analysis: Dict[str, Any],
        performance_analysis: Dict[str, Any],
        testing_analysis: Dict[str, Any],
        devops_analysis: Dict[str, Any],
        code_quality_analysis: Dict[str, Any],
        basic_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        return _synthesize(
            client=self.client,
            security_analysis=security_analysis,
            performance_analysis=performance_analysis,
            testing_analysis=testing_analysis,
            devops_analysis=devops_analysis,
            code_quality_analysis=code_quality_analysis,
            basic_analysis=basic_analysis,
        )
