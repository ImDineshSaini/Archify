"""AI-powered analysis suggestions and prompt building."""

from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate


SYSTEM_PROMPT = """You are an expert software architect and code reviewer.
Analyze the provided code metrics and provide CONCRETE, ACTIONABLE suggestions.

IMPORTANT: Be specific with tools, patterns, and implementation steps. Examples:
- BAD: "Improve auditability through architecture refactoring"
- GOOD: "Implement structured logging using ELK Stack (Elasticsearch, Logstack, Kibana) for centralized audit trails"

- BAD: "Enhance scalability"
- GOOD: "Implement Redis caching for frequently accessed data and add horizontal pod autoscaling (HPA) in Kubernetes"

For each recommendation, specify:
1. Exact tool/library/pattern to use (with version if relevant)
2. Where in the codebase to implement it
3. Expected impact (performance gain, reduced complexity, etc.)
4. Priority level (Critical/High/Medium/Low)

Focus on: Architecture patterns, Design patterns, DevOps tools, Monitoring tools, Testing frameworks, Security tools, Performance optimization techniques.

Prioritize the most impactful improvements."""


def generate_analysis_suggestions(client, analysis_results: Dict[str, Any]) -> str:
    """Generate AI-powered suggestions based on code analysis results."""
    try:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{analysis_prompt}"),
        ])

        chain = prompt_template | client
        result = chain.invoke({
            "analysis_prompt": _create_analysis_prompt(analysis_results),
        })
        return result.content

    except Exception as e:
        return f"Error generating suggestions: {str(e)}"


def _create_analysis_prompt(results: Dict[str, Any]) -> str:
    """Create a detailed prompt from analysis results."""
    code_metrics = results.get("code_metrics", {})
    complexity = results.get("complexity", {})
    architecture = results.get("architecture", {})
    scores = results.get("scores", {})

    prompt = f"""
# Code Analysis Report

## Overview Metrics
- Total Lines of Code: {code_metrics.get('total_lines', 0)}
- Files Analyzed: {code_metrics.get('files_analyzed', 0)}
- Languages: {', '.join(code_metrics.get('languages', {}).keys())}

## Complexity Analysis
- Average Complexity: {complexity.get('average_complexity', 0):.2f}
- Maximum Complexity: {complexity.get('max_complexity', 0)}
- High Complexity Functions: {len(complexity.get('high_complexity_functions', []))}

## Architecture
- Project Type: {architecture.get('project_type', 'unknown')}
- Frameworks: {', '.join(architecture.get('frameworks', []))}
- Detected Patterns: {', '.join(architecture.get('detected_patterns', []))}

## Quality Scores
- Maintainability: {scores.get('maintainability', 0):.1f}/100
- Reliability: {scores.get('reliability', 0):.1f}/100
- Scalability: {scores.get('scalability', 0):.1f}/100
- Security: {scores.get('security', 0):.1f}/100
- Overall: {scores.get('overall', 0):.1f}/100

## High Complexity Functions
"""
    for func in complexity.get("high_complexity_functions", [])[:5]:
        prompt += f"\n- {func['name']}: Complexity {func['complexity']} ({func['lines']} lines)"

    prompt += """

Based on this analysis, provide 5-8 CONCRETE recommendations. For each recommendation, use this format:

**[Priority] Recommendation Title**
- **Tool/Pattern:** [Specific tool, library, pattern, or framework]
- **Implementation:** [Where and how to implement - be specific about files/modules]
- **Expected Impact:** [Quantify if possible]
- **Resources:** [Link to docs or mention specific tutorials if relevant]
"""

    return prompt
