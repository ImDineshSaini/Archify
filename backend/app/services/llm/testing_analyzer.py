"""Deep testing analysis layer."""

from typing import Any, Dict
from app.core.constants import TREE_TRUNCATION_LIMIT
from app.services.llm.base_analyzer import BaseLLMAnalyzer


class TestingAnalyzer(BaseLLMAnalyzer):
    def _get_layer_name(self) -> str:
        return "Testing"

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
Find SPECIFIC testing gaps with EXACT locations:

BAD: "Add more tests"
GOOD: "No test coverage for /services/payment.py - critical business logic untested"

Check for:
1. **Test Coverage Gaps**
   - Missing /tests or /test directory
   - Critical paths without tests (auth, payment, etc.)
   - No integration tests for /api endpoints
   - Missing E2E tests

2. **Test Quality Issues**
   - No test fixtures or mocking setup
   - Hard-coded test data
   - No CI test automation (.github/workflows)
   - Missing test coverage reporting

3. **Testing Infrastructure**
   - No testing framework configured (pytest, jest, etc.)
   - Missing test database setup
   - No test environment configuration

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
  "recommendations": [
    "Add pytest fixtures in /tests/conftest.py for database mocking",
    "Implement integration tests using pytest-mock for /services layer",
    "Set up GitHub Actions workflow for automated testing"
  ]
}}
"""
