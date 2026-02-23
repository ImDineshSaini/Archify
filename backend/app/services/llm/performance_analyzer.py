"""Deep performance analysis layer."""

from typing import Any, Dict, Type

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.core.constants import TREE_TRUNCATION_LIMIT
from app.services.llm.base_analyzer import BaseLLMAnalyzer
from app.services.llm.schemas import PerformanceAnalysisOutput


class PerformanceAnalyzer(BaseLLMAnalyzer):
    def _get_layer_name(self) -> str:
        return "Performance"

    def _get_output_schema(self) -> Type[BaseModel]:
        return PerformanceAnalysisOutput

    def _get_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", "You are a performance optimization expert."),
            ("human",
             "You are a performance optimization expert. Find SPECIFIC performance "
             "issues in this codebase.\n\n"
             "# Directory Structure:\n```\n{directory_tree}\n```\n\n"
             "# Metrics:\n- Avg Complexity: {avg_complexity}\n"
             "- Max Complexity: {max_complexity}\n- Language: {language}\n\n"
             "{relevant_code_context}"
             "## Your Task:\n"
             "Find SPECIFIC performance bottlenecks with EXACT locations:\n\n"
             "BAD: \"Optimize database queries\"\n"
             "GOOD: \"Likely N+1 query problem in /controllers/orders.py - "
             "no eager loading detected\"\n\n"
             "Check for:\n"
             "1. **Database Issues** - No caching, missing indexes, N+1 queries, "
             "no connection pooling\n"
             "2. **API Performance** - Missing pagination, no compression, "
             "sync ops that should be async\n"
             "3. **Frontend Performance** - No lazy loading, missing code splitting\n"
             "4. **Infrastructure** - No load balancing, missing CDN, no caching headers\n\n"
             "Provide bottlenecks (each with issue, location, evidence, fix, "
             "expected_improvement, priority) and recommendations."),
        ])

    def _get_prompt_variables(
        self, directory_tree: str, basic_analysis: Dict[str, Any]
    ) -> dict:
        complexity = basic_analysis.get("complexity", {})
        architecture = basic_analysis.get("architecture", {})
        return {
            "directory_tree": directory_tree[:TREE_TRUNCATION_LIMIT],
            "avg_complexity": f"{complexity.get('average_complexity', 0):.2f}",
            "max_complexity": str(complexity.get("max_complexity", 0)),
            "language": architecture.get("language", "unknown"),
            "relevant_code_context": "",
        }

    def _get_retrieval_queries(self) -> list:
        return [
            "database query ORM select join",
            "cache Redis memcached",
            "async await concurrent threading",
            "pagination limit offset",
        ]

    # ── Legacy fallback methods ─────────────────────────────────────────

    def _get_system_prompt(self) -> str:
        return "You are a performance optimization expert."

    def _get_fallback_response(self, raw_content: str) -> Dict[str, Any]:
        return {"raw_analysis": raw_content, "bottlenecks": [], "recommendations": []}

    def _build_prompt(self, directory_tree: str, basic_analysis: Dict[str, Any]) -> str:
        complexity = basic_analysis.get("complexity", {})
        architecture = basic_analysis.get("architecture", {})
        return f"""
You are a performance optimization expert. Find SPECIFIC performance issues in this codebase.

# Directory Structure:
```
{directory_tree[:TREE_TRUNCATION_LIMIT]}
```

# Metrics:
- Avg Complexity: {complexity.get('average_complexity', 0):.2f}
- Max Complexity: {complexity.get('max_complexity', 0)}
- Language: {architecture.get('language')}

## Your Task:
Find SPECIFIC performance bottlenecks with EXACT locations.

Check for:
1. **Database Issues**
2. **API Performance**
3. **Frontend Performance**
4. **Infrastructure**

Return JSON with:
{{
  "bottlenecks": [
    {{
      "issue": "Specific bottleneck",
      "location": "File/folder path",
      "evidence": "What indicates this issue",
      "fix": "Specific optimization technique/tool",
      "expected_improvement": "e.g., 50% faster response time",
      "priority": "Critical/High/Medium/Low"
    }}
  ],
  "recommendations": ["..."]
}}
"""
