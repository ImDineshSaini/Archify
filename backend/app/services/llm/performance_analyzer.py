"""Deep performance analysis layer."""

from typing import Any, Dict
from app.core.constants import TREE_TRUNCATION_LIMIT
from app.services.llm.base_analyzer import BaseLLMAnalyzer


class PerformanceAnalyzer(BaseLLMAnalyzer):
    def _get_layer_name(self) -> str:
        return "Performance"

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
Find SPECIFIC performance bottlenecks with EXACT locations:

BAD: "Optimize database queries"
GOOD: "Likely N+1 query problem in /controllers/orders.py - no eager loading detected"

Check for:
1. **Database Issues**
   - No caching layer (Redis/Memcached)
   - Missing database indexes (check migration files)
   - N+1 query patterns in /controllers or /services
   - No connection pooling in /config/database

2. **API Performance**
   - Missing pagination in /api/routes
   - No response compression in server config
   - Synchronous operations that should be async

3. **Frontend Performance** (if applicable)
   - No lazy loading in /components
   - Missing code splitting in webpack/vite config
   - No image optimization

4. **Infrastructure**
   - No load balancing configuration
   - Missing CDN setup for static assets
   - No caching headers in /middleware

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
  "recommendations": [
    "Add Redis caching using redis-py in /services/cache.py",
    "Implement database connection pooling with SQLAlchemy pool_size=10"
  ]
}}
"""
