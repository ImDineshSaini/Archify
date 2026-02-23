"""AI-powered analysis suggestions and prompt building."""

from typing import Any, Dict
from langchain.schema import HumanMessage, SystemMessage


def generate_analysis_suggestions(client, analysis_results: Dict[str, Any]) -> str:
    """Generate AI-powered suggestions based on code analysis results."""
    prompt = _create_analysis_prompt(analysis_results)

    try:
        messages = [
            SystemMessage(content="""You are an expert software architect and code reviewer.
                Analyze the provided code metrics and provide CONCRETE, ACTIONABLE suggestions.

                IMPORTANT: Be specific with tools, patterns, and implementation steps. Examples:
                - BAD: "Improve auditability through architecture refactoring"
                - GOOD: "Implement structured logging using ELK Stack (Elasticsearch, Logstack, Kibana) for centralized audit trails"

                - BAD: "Enhance scalability"
                - GOOD: "Implement Redis caching for frequently accessed data and add horizontal pod autoscaling (HPA) in Kubernetes"

                - BAD: "Improve code structure"
                - GOOD: "Refactor data access to Repository Pattern - move all database queries from controllers to dedicated repository classes"

                For each recommendation, specify:
                1. Exact tool/library/pattern to use (with version if relevant)
                2. Where in the codebase to implement it
                3. Expected impact (performance gain, reduced complexity, etc.)
                4. Priority level (Critical/High/Medium/Low)

                Focus on: Architecture patterns, Design patterns, DevOps tools, Monitoring tools, Testing frameworks, Security tools, Performance optimization techniques.

                Prioritize the most impactful improvements."""),
            HumanMessage(content=prompt),
        ]

        response = client.invoke(messages)
        return response.content

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
- **Expected Impact:** [Quantify if possible: "Reduce complexity by 30%", "Improve response time by 50%", etc.]
- **Resources:** [Link to docs or mention specific tutorials if relevant]

Examples of good recommendations:
- Implement Repository Pattern using TypeORM decorators in data access layer
- Add OpenTelemetry instrumentation for distributed tracing
- Set up SonarQube quality gates in CI/CD pipeline
- Refactor to CQRS pattern using MediatR library
- Implement circuit breaker pattern using Polly (C#) or resilience4j (Java)
- Add Redis caching layer with cache-aside pattern
- Implement API rate limiting using express-rate-limit or rate-limiter-flexible
- Set up Prometheus + Grafana for application monitoring"""

    return prompt
