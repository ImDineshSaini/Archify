"""Deep security analysis layer."""

from typing import Any, Dict, Type

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.core.constants import TREE_TRUNCATION_LIMIT
from app.services.llm.base_analyzer import BaseLLMAnalyzer
from app.services.llm.schemas import SecurityAnalysisOutput


class SecurityAnalyzer(BaseLLMAnalyzer):
    def _get_layer_name(self) -> str:
        return "Security"

    def _get_output_schema(self) -> Type[BaseModel]:
        return SecurityAnalysisOutput

    def _get_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", "You are a security expert specializing in vulnerability detection."),
            ("human",
             "You are a security expert conducting a code security audit. "
             "Analyze this codebase structure for SPECIFIC security vulnerabilities.\n\n"
             "# Directory Structure:\n```\n{directory_tree}\n```\n\n"
             "# Architecture:\n- Language: {language}\n- Frameworks: {frameworks}\n\n"
             "{relevant_code_context}"
             "## Your Task:\n"
             "Find SPECIFIC security issues with EXACT file/folder references. Be concrete:\n\n"
             "BAD: \"Improve authentication security\"\n"
             "GOOD: \"No password hashing detected - check if passwords stored in plaintext "
             "in /models/user.py or /services/auth.py\"\n\n"
             "Check for:\n"
             "1. **Authentication/Authorization Issues** - Missing JWT validation, "
             "no rate limiting, weak password requirements\n"
             "2. **Data Protection Issues** - Hardcoded secrets, missing input sanitization, "
             "no HTTPS enforcement\n"
             "3. **Dependency Vulnerabilities** - Outdated packages, missing security headers\n"
             "4. **API Security** - No CORS configuration, missing rate limiting, "
             "no request validation\n\n"
             "Provide critical_issues (each with issue, location, evidence, fix, priority) "
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
            "authentication login password hashing",
            "authorization permission middleware",
            "secret key configuration environment variable",
            "input validation sanitization",
            "CORS security headers",
        ]

    # ── Legacy fallback methods ─────────────────────────────────────────

    def _get_system_prompt(self) -> str:
        return "You are a security expert specializing in vulnerability detection."

    def _get_fallback_response(self, raw_content: str) -> Dict[str, Any]:
        return {"raw_analysis": raw_content, "critical_issues": [], "recommendations": []}

    def _build_prompt(self, directory_tree: str, basic_analysis: Dict[str, Any]) -> str:
        architecture = basic_analysis.get("architecture", {})
        return f"""
You are a security expert conducting a code security audit. Analyze this codebase structure for SPECIFIC security vulnerabilities.

# Directory Structure:
```
{directory_tree[:TREE_TRUNCATION_LIMIT]}
```

# Architecture:
- Language: {architecture.get('language')}
- Frameworks: {', '.join(architecture.get('frameworks', []))}

## Your Task:
Find SPECIFIC security issues with EXACT file/folder references. Be concrete:

BAD: "Improve authentication security"
GOOD: "No password hashing detected - check if passwords stored in plaintext in /models/user.py or /services/auth.py"

Check for:
1. **Authentication/Authorization Issues**
2. **Data Protection Issues**
3. **Dependency Vulnerabilities**
4. **API Security**

Return JSON with:
{{
  "critical_issues": [
    {{
      "issue": "Specific issue description",
      "location": "Exact file/folder path",
      "evidence": "What you see in directory tree",
      "fix": "Specific tool/library to use",
      "priority": "Critical/High/Medium/Low"
    }}
  ],
  "recommendations": ["..."]
}}
"""
