"""Synthesis of all deep analysis layers into a prioritized report."""

import json
import logging
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from app.core.constants import SYNTHESIS_SECTION_LIMIT
from app.services.llm.base_analyzer import extract_json
from app.services.llm.schemas import SynthesisOutput

logger = logging.getLogger(__name__)


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
        return _structured_synthesis(
            client,
            security_analysis,
            performance_analysis,
            testing_analysis,
            devops_analysis,
            code_quality_analysis,
        )
    except Exception as e:
        logger.warning("Structured synthesis failed, trying fallback: %s", e)
        return _fallback_synthesis(
            client,
            security_analysis,
            performance_analysis,
            testing_analysis,
            devops_analysis,
            code_quality_analysis,
        )


def _structured_synthesis(
    client,
    security_analysis: Dict[str, Any],
    performance_analysis: Dict[str, Any],
    testing_analysis: Dict[str, Any],
    devops_analysis: Dict[str, Any],
    code_quality_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """Primary path: ChatPromptTemplate + with_structured_output."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a technical architect creating comprehensive analysis reports."),
        ("human",
         "You are a technical architect creating a comprehensive analysis report. "
         "Synthesize findings from multiple layer analyses into a PRIORITIZED action plan.\n\n"
         "# Layer Analysis Results:\n\n"
         "## Security Findings:\n{security}\n\n"
         "## Performance Findings:\n{performance}\n\n"
         "## Testing Findings:\n{testing}\n\n"
         "## DevOps Findings:\n{devops}\n\n"
         "## Code Quality Findings:\n{code_quality}\n\n"
         "## Your Task:\n"
         "Create a PRIORITIZED synthesis report with:\n\n"
         "1. **Critical Issues** (Fix immediately - security, data loss risks)\n"
         "2. **High Priority** (Fix within 1-2 sprints)\n"
         "3. **Medium Priority** (Fix within 1-2 months)\n"
         "4. **Low Priority** (Nice to have)\n\n"
         "For each priority level, provide top 5 most impactful issues with specific "
         "locations, expected business impact, effort estimate, and dependencies.\n\n"
         "Also provide an executive_summary (2-3 sentences), quick_wins (easy fixes "
         "with high impact, < 4 hours each), and estimated_total_effort_days."),
    ])

    structured_llm = client.with_structured_output(SynthesisOutput)
    chain = prompt | structured_llm

    result = chain.invoke({
        "security": json.dumps(security_analysis, indent=2)[:SYNTHESIS_SECTION_LIMIT],
        "performance": json.dumps(performance_analysis, indent=2)[:SYNTHESIS_SECTION_LIMIT],
        "testing": json.dumps(testing_analysis, indent=2)[:SYNTHESIS_SECTION_LIMIT],
        "devops": json.dumps(devops_analysis, indent=2)[:SYNTHESIS_SECTION_LIMIT],
        "code_quality": json.dumps(code_quality_analysis, indent=2)[:SYNTHESIS_SECTION_LIMIT],
    })
    return result.model_dump()


def _fallback_synthesis(
    client,
    security_analysis: Dict[str, Any],
    performance_analysis: Dict[str, Any],
    testing_analysis: Dict[str, Any],
    devops_analysis: Dict[str, Any],
    code_quality_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """Legacy fallback path with manual JSON extraction."""
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
Create a PRIORITIZED synthesis report. Return JSON with:
{{
  "executive_summary": "2-3 sentence overview",
  "critical_issues": [
    {{"issue": "...", "location": "...", "category": "...", "fix": "...", "effort_hours": 8, "business_impact": "...", "dependencies": []}}
  ],
  "high_priority": [...],
  "medium_priority": [...],
  "low_priority": [...],
  "quick_wins": ["Easy fixes with high impact"],
  "estimated_total_effort_days": 30
}}
"""

        messages = [
            SystemMessage(content="You are a technical architect creating comprehensive analysis reports."),
            HumanMessage(content=prompt),
        ]

        response = client.invoke(messages)

        result = extract_json(response.content)
        if result is not None:
            return result

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
