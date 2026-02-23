"""Deep code quality analysis layer."""

from typing import Any, Dict
from app.core.constants import TREE_TRUNCATION_LIMIT
from app.services.llm.base_analyzer import BaseLLMAnalyzer


class CodeQualityAnalyzer(BaseLLMAnalyzer):
    def _get_layer_name(self) -> str:
        return "Code quality"

    def _get_system_prompt(self) -> str:
        return "You are a code quality expert specializing in maintainability."

    def _get_fallback_response(self, raw_content: str) -> Dict[str, Any]:
        return {"raw_analysis": raw_content, "quality_issues": [], "recommendations": []}

    def _build_prompt(self, directory_tree: str, basic_analysis: Dict[str, Any]) -> str:
        complexity = basic_analysis.get("complexity", {})
        high_complexity_funcs = complexity.get("high_complexity_functions", [])
        return f"""
You are a code quality expert analyzing maintainability. Find SPECIFIC code quality issues.

# Directory Structure:
```
{directory_tree[:TREE_TRUNCATION_LIMIT]}
```

# Complexity Metrics:
- Avg Complexity: {complexity.get('average_complexity', 0):.2f}
- Max Complexity: {complexity.get('max_complexity', 0)}
- High Complexity Functions: {len(high_complexity_funcs)}

## Your Task:
Find SPECIFIC code quality issues with EXACT locations:

BAD: "Refactor complex code"
GOOD: "calculatePrice() has complexity 45 - extract tax and discount logic into separate functions"

Check for:
1. **Code Smells**
   - God Objects (files > 500 lines)
   - Duplicate code patterns
   - Long parameter lists
   - Deep nesting in complex functions

2. **Architecture Violations**
   - Business logic in controllers (should be in /services)
   - Database queries in views/controllers
   - Tight coupling between modules
   - Missing abstraction layers

3. **Maintainability Issues**
   - No linting configuration (.eslintrc, .pylintrc, etc.)
   - Missing code formatting (Prettier, Black)
   - No documentation (/docs folder)
   - Inconsistent naming conventions

4. **SOLID Principle Violations**
   - SRP violations (classes doing too much)
   - Hard-coded dependencies (no DI)
   - Tight coupling between layers

Return JSON with:
{{
  "quality_issues": [
    {{
      "issue": "Specific code smell/violation",
      "location": "File/function path",
      "evidence": "What indicates this issue",
      "refactoring": "Specific refactoring technique",
      "priority": "Critical/High/Medium/Low"
    }}
  ],
  "recommendations": [
    "Extract business logic from /controllers to /services using Service Layer pattern",
    "Add ESLint with Airbnb config for code consistency",
    "Implement Dependency Injection using dependency-injector library"
  ]
}}
"""
