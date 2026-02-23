"""Deep DevOps analysis layer."""

from typing import Any, Dict
from app.core.constants import TREE_TRUNCATION_LIMIT
from app.services.llm.base_analyzer import BaseLLMAnalyzer


class DevOpsAnalyzer(BaseLLMAnalyzer):
    def _get_layer_name(self) -> str:
        return "DevOps"

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
Find SPECIFIC DevOps gaps with EXACT file references:

BAD: "Improve deployment process"
GOOD: "No Dockerfile found - containerization missing for deployment"

Check for:
1. **Containerization**
   - Missing Dockerfile in root
   - No docker-compose.yml for local dev
   - Missing .dockerignore

2. **CI/CD**
   - No CI/CD configuration (.github/workflows, .gitlab-ci.yml, Jenkinsfile)
   - Missing automated deployment scripts
   - No build automation

3. **Infrastructure as Code**
   - No Kubernetes manifests (/k8s or /manifests)
   - Missing Terraform/CloudFormation in /infrastructure
   - No Helm charts

4. **Monitoring & Observability**
   - No health check endpoints in /api
   - Missing Prometheus metrics
   - No centralized logging configuration
   - Missing APM setup (New Relic, DataDog)

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
  "recommendations": [
    "Create Dockerfile with multi-stage build in project root",
    "Add GitHub Actions workflow in .github/workflows/ci.yml",
    "Implement health check endpoint at /api/health using Flask-HealthCheck"
  ]
}}
"""
