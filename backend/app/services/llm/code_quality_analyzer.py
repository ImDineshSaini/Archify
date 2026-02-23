"""Deep code quality analysis layer."""

from typing import Any, Dict, Type

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.core.constants import TREE_TRUNCATION_LIMIT
from app.services.llm.base_analyzer import BaseLLMAnalyzer
from app.services.llm.schemas import CodeQualityAnalysisOutput


class CodeQualityAnalyzer(BaseLLMAnalyzer):
    def _get_layer_name(self) -> str:
        return "Code quality"

    def _get_output_schema(self) -> Type[BaseModel]:
        return CodeQualityAnalysisOutput

    def _get_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", "You are a code quality expert specializing in maintainability."),
            ("human",
             "You are a code quality expert analyzing maintainability. "
             "Find SPECIFIC code quality issues.\n\n"
             "# Directory Structure:\n```\n{directory_tree}\n```\n\n"
             "# Complexity Metrics:\n- Avg Complexity: {avg_complexity}\n"
             "- Max Complexity: {max_complexity}\n"
             "- High Complexity Functions: {high_complexity_count}\n\n"
             "{relevant_code_context}"
             "## Your Task:\n"
             "Find SPECIFIC code quality issues with EXACT locations:\n\n"
             "BAD: \"Refactor complex code\"\n"
             "GOOD: \"calculatePrice() has complexity 45 - extract tax and discount "
             "logic into separate functions\"\n\n"
             "Check for:\n"
             "1. **Code Smells** - God Objects, duplicate code, long parameter lists, "
             "deep nesting\n"
             "2. **Architecture Violations** - Business logic in controllers, "
             "DB queries in views, tight coupling\n"
             "3. **Maintainability Issues** - No linting, missing formatting, "
             "no documentation, inconsistent naming\n"
             "4. **SOLID Principle Violations** - SRP violations, hard-coded "
             "dependencies, tight coupling\n\n"
             "Provide quality_issues (each with issue, location, evidence, "
             "refactoring, priority) and recommendations."),
        ])

    def _get_prompt_variables(
        self, directory_tree: str, basic_analysis: Dict[str, Any]
    ) -> dict:
        complexity = basic_analysis.get("complexity", {})
        high_complexity_funcs = complexity.get("high_complexity_functions", [])
        return {
            "directory_tree": directory_tree[:TREE_TRUNCATION_LIMIT],
            "avg_complexity": f"{complexity.get('average_complexity', 0):.2f}",
            "max_complexity": str(complexity.get("max_complexity", 0)),
            "high_complexity_count": str(len(high_complexity_funcs)),
            "relevant_code_context": "",
        }

    def _get_retrieval_queries(self) -> list:
        return [
            "class service controller handler",
            "error handling exception try catch",
            "import dependency module coupling",
        ]

    # ── Legacy fallback methods ─────────────────────────────────────────

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
Find SPECIFIC code quality issues with EXACT locations.

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
  "recommendations": ["..."]
}}
"""
