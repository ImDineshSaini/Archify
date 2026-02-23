"""Deep security analysis layer."""

from typing import Any, Dict
from app.core.constants import TREE_TRUNCATION_LIMIT
from app.services.llm.base_analyzer import BaseLLMAnalyzer


class SecurityAnalyzer(BaseLLMAnalyzer):
    def _get_layer_name(self) -> str:
        return "Security"

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
   - Missing JWT validation in /middleware
   - No rate limiting on /api/auth/login endpoint
   - Weak password requirements in /validators

2. **Data Protection Issues**
   - No .env file but hardcoded secrets in /config
   - Missing input sanitization in /controllers
   - No HTTPS enforcement in server config

3. **Dependency Vulnerabilities**
   - Outdated packages in package.json/requirements.txt
   - Missing security headers in /middleware

4. **API Security**
   - No CORS configuration in /api
   - Missing API rate limiting
   - No request validation middleware

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
  "recommendations": [
    "Install helmet.js for security headers",
    "Add express-rate-limit middleware to /api/routes.js",
    "Implement bcrypt for password hashing in /services/auth.py"
  ]
}}
"""
