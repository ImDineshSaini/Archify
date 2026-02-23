"""Deep testing analysis layer."""

from typing import Any, Dict, Type

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.core.constants import TREE_TRUNCATION_LIMIT
from app.services.llm.base_analyzer import BaseLLMAnalyzer
from app.services.llm.schemas import TestingAnalysisOutput


class TestingAnalyzer(BaseLLMAnalyzer):
    def _get_layer_name(self) -> str:
        return "Testing"

    def _get_output_schema(self) -> Type[BaseModel]:
        return TestingAnalysisOutput

    def _get_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", "You are a QA expert specializing in test strategy."),
            ("human",
             "You are a QA expert analyzing test coverage and quality. "
             "Find SPECIFIC testing gaps.\n\n"
             "# Directory Structure:\n```\n{directory_tree}\n```\n\n"
             "# Architecture:\n- Language: {language}\n- Frameworks: {frameworks}\n\n"
             "{relevant_code_context}"
             "## Your Task:\n"
             "Find SPECIFIC testing gaps with EXACT locations:\n\n"
             "BAD: \"Add more tests\"\n"
             "GOOD: \"No test coverage for /services/payment.py - "
             "critical business logic untested\"\n\n"
             "Check for:\n"
             "1. **Test Coverage Gaps** - Missing test directories, critical paths "
             "without tests, no integration/E2E tests\n"
             "2. **Test Quality Issues** - No fixtures, hard-coded test data, "
             "no CI automation\n"
             "3. **Testing Infrastructure** - No framework configured, missing "
             "test DB setup\n\n"
             "Provide coverage_gaps (each with missing_tests_for, test_type, "
             "risk_level, fix) and recommendations."),
        ])

    def _get_prompt_variables(
        self, directory_tree: str, basic_analysis: Dict[str, Any]
    ) -> dict:
        architecture = basic_analysis.get("architecture", {})
        return {
            "directory_tree": directory_tree[:TREE_TRUNCATION_LIMIT],
            "language": architecture.get("language", "unknown"),
            "frameworks": ", ".join(architecture.get("frameworks", [])),
            "relevant_code_context": "",
        }

    def _get_retrieval_queries(self) -> list:
        return [
            "test unittest pytest jest mock",
            "fixture conftest setup teardown",
            "coverage report assertion",
        ]

    # ── Legacy fallback methods ─────────────────────────────────────────

    def _get_system_prompt(self) -> str:
        return "You are a QA expert specializing in test strategy."

    def _get_fallback_response(self, raw_content: str) -> Dict[str, Any]:
        return {"raw_analysis": raw_content, "coverage_gaps": [], "recommendations": []}

    def _build_prompt(self, directory_tree: str, basic_analysis: Dict[str, Any]) -> str:
        architecture = basic_analysis.get("architecture", {})
        return f"""
You are a QA expert analyzing test coverage and quality. Find SPECIFIC testing gaps.

# Directory Structure:
```
{directory_tree[:TREE_TRUNCATION_LIMIT]}
```

# Architecture:
- Language: {architecture.get('language')}
- Frameworks: {', '.join(architecture.get('frameworks', []))}

## Your Task:
Find SPECIFIC testing gaps with EXACT locations.

Return JSON with:
{{
  "coverage_gaps": [
    {{
      "missing_tests_for": "File/module path",
      "test_type": "unit/integration/e2e",
      "risk_level": "Critical/High/Medium/Low",
      "fix": "Specific testing framework/approach"
    }}
  ],
  "recommendations": ["..."]
}}
"""
