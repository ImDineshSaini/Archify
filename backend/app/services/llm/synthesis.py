"""Synthesis of all deep analysis layers into a prioritized report."""

import json
from typing import Any, Dict
from langchain.schema import HumanMessage, SystemMessage
from app.core.constants import SYNTHESIS_SECTION_LIMIT


def synthesize_deep_analysis(
    client,
    security_analysis: Dict[str, Any],
    performance_analysis: Dict[str, Any],
    testing_analysis: Dict[str, Any],
    devops_analysis: Dict[str, Any],
    code_quality_analysis: Dict[str, Any],
    basic_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """Synthesize all layer analyses into a prioritized final report."""
    try:
        prompt = f"""
You are a technical architect creating a comprehensive analysis report. Synthesize findings from multiple layer analyses into a PRIORITIZED action plan.

# Layer Analysis Results:

## Security Findings:
{json.dumps(security_analysis, indent=2)[:SYNTHESIS_SECTION_LIMIT]}

## Performance Findings:
{json.dumps(performance_analysis, indent=2)[:SYNTHESIS_SECTION_LIMIT]}

## Testing Findings:
{json.dumps(testing_analysis, indent=2)[:SYNTHESIS_SECTION_LIMIT]}

## DevOps Findings:
{json.dumps(devops_analysis, indent=2)[:SYNTHESIS_SECTION_LIMIT]}

## Code Quality Findings:
{json.dumps(code_quality_analysis, indent=2)[:SYNTHESIS_SECTION_LIMIT]}

## Your Task:
Create a PRIORITIZED synthesis report with:

1. **Critical Issues** (Fix immediately - security, data loss risks)
2. **High Priority** (Fix within 1-2 sprints - performance bottlenecks, missing tests for critical paths)
3. **Medium Priority** (Fix within 1-2 months - code quality, DevOps improvements)
4. **Low Priority** (Nice to have - documentation, minor refactorings)

For each priority level, provide:
- Top 5 most impactful issues with specific locations
- Expected business impact (uptime, performance, security, speed to market)
- Effort estimate (hours/days)
- Dependencies between issues

Return JSON with:
{{
  "executive_summary": "2-3 sentence overview of overall architecture health",
  "critical_issues": [
    {{
      "issue": "Specific issue",
      "location": "Exact file/path",
      "category": "Security/Performance/Testing/DevOps/Quality",
      "fix": "Concrete solution with tool",
      "effort_hours": 8,
      "business_impact": "e.g., Prevents data breaches",
      "dependencies": []
    }}
  ],
  "high_priority": [...],
  "medium_priority": [...],
  "low_priority": [...],
  "quick_wins": [
    "Easy fixes with high impact - can be done in < 4 hours"
  ],
  "estimated_total_effort_days": 30
}}
"""

        messages = [
            SystemMessage(content="You are a technical architect creating comprehensive analysis reports."),
            HumanMessage(content=prompt),
        ]

        response = client.invoke(messages)

        try:
            return json.loads(response.content)
        except (json.JSONDecodeError, TypeError):
            return {
                "executive_summary": response.content[:500],
                "critical_issues": [],
                "high_priority": [],
                "medium_priority": [],
                "low_priority": [],
                "quick_wins": [],
            }

    except Exception as e:
        return {"error": f"Synthesis failed: {str(e)}"}
