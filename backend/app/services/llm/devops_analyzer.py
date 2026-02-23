"""Deep DevOps analysis layer."""

from typing import Any, Dict, Type

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.core.constants import TREE_TRUNCATION_LIMIT
from app.services.llm.base_analyzer import BaseLLMAnalyzer
from app.services.llm.schemas import DevOpsAnalysisOutput


class DevOpsAnalyzer(BaseLLMAnalyzer):
    def _get_layer_name(self) -> str:
        return "DevOps"

    def _get_output_schema(self) -> Type[BaseModel]:
        return DevOpsAnalysisOutput

    def _get_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", "You are a DevOps expert specializing in deployment automation."),
            ("human",
             "You are a DevOps expert analyzing deployment and infrastructure. "
             "Find SPECIFIC DevOps gaps.\n\n"
             "# Directory Structure:\n```\n{directory_tree}\n```\n\n"
             "# Architecture:\n- Language: {language}\n- Frameworks: {frameworks}\n\n"
             "{relevant_code_context}"
             "## Your Task:\n"
             "Find SPECIFIC DevOps gaps with EXACT file references:\n\n"
             "BAD: \"Improve deployment process\"\n"
             "GOOD: \"No Dockerfile found - containerization missing for deployment\"\n\n"
             "Check for:\n"
             "1. **Containerization** - Missing Dockerfile, no docker-compose, "
             "missing .dockerignore\n"
             "2. **CI/CD** - No pipeline config, missing deployment scripts\n"
             "3. **Infrastructure as Code** - No K8s manifests, missing Terraform\n"
             "4. **Monitoring & Observability** - No health checks, missing metrics, "
             "no centralized logging\n\n"
             "Provide missing_devops (each with gap, location, impact, fix, priority) "
             "and recommendations."),
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
            "Dockerfile docker-compose container",
            "CI CD pipeline workflow github actions",
            "kubernetes helm deployment",
            "health check monitoring prometheus",
        ]

    # ── Legacy fallback methods ─────────────────────────────────────────

    def _get_system_prompt(self) -> str:
        return "You are a DevOps expert specializing in deployment automation."

    def _get_fallback_response(self, raw_content: str) -> Dict[str, Any]:
        return {"raw_analysis": raw_content, "missing_devops": [], "recommendations": []}

    def _build_prompt(self, directory_tree: str, basic_analysis: Dict[str, Any]) -> str:
        architecture = basic_analysis.get("architecture", {})
        return f"""
You are a DevOps expert analyzing deployment and infrastructure. Find SPECIFIC DevOps gaps.

# Directory Structure:
```
{directory_tree[:TREE_TRUNCATION_LIMIT]}
```

# Architecture:
- Language: {architecture.get('language')}
- Frameworks: {', '.join(architecture.get('frameworks', []))}

## Your Task:
Find SPECIFIC DevOps gaps with EXACT file references.

Return JSON with:
{{
  "missing_devops": [
    {{
      "gap": "Specific missing component",
      "location": "Where it should be",
      "impact": "Risk/consequence",
      "fix": "Specific tool/setup to implement",
      "priority": "Critical/High/Medium/Low"
    }}
  ],
  "recommendations": ["..."]
}}
"""
