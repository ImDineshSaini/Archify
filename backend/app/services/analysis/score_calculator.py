"""Quality score calculation based on analysis results."""

from typing import Any, Dict


def calculate_scores(results: Dict[str, Any]) -> Dict[str, float]:
    """Calculate quality scores based on analysis results."""
    scores = {
        "maintainability": 0.0,
        "reliability": 0.0,
        "scalability": 0.0,
        "security": 0.0,
        "overall": 0.0,
    }

    # Maintainability score (based on complexity and code metrics)
    complexity = results.get("complexity", {})
    avg_complexity = complexity.get("average_complexity", 0)
    maintainability = max(0, 100 - (avg_complexity * 3))

    architecture = results.get("architecture", {})
    if architecture.get("solid_compliance"):
        maintainability += 5
    if "Clean Architecture" in architecture.get("detected_patterns", []) or "Hexagonal/Clean Architecture" in architecture.get("detected_patterns", []):
        maintainability += 10

    scores["maintainability"] = min(100, maintainability)

    # Reliability score
    code_metrics = results.get("code_metrics", {})
    total_lines = code_metrics.get("total_lines", 1)
    comment_ratio = code_metrics.get("comment_lines", 0) / max(total_lines, 1) * 100
    reliability = 50 + (comment_ratio * 2)

    if architecture.get("design_patterns"):
        reliability += min(10, len(architecture["design_patterns"]) * 2)

    scores["reliability"] = min(100, reliability)

    # Scalability score
    scalability = 60.0
    if "Microservices Architecture" in architecture.get("detected_patterns", []):
        scalability += 20
    if "Component-based Architecture" in architecture.get("detected_patterns", []):
        scalability += 10
    if "Event-driven Pattern" in architecture.get("design_patterns", []):
        scalability += 10
    if "CQRS Pattern" in architecture.get("design_patterns", []):
        scalability += 5
    scores["scalability"] = min(100, scalability)

    # Security score
    security = 60.0
    frameworks = architecture.get("frameworks", [])
    if any(fw in frameworks for fw in ["FastAPI", "NestJS", "Spring Boot", "Django"]):
        security += 10
    if "Dependency Injection" in architecture.get("design_patterns", []):
        security += 5
    scores["security"] = min(100, security)

    # Overall score
    scores["overall"] = sum(scores.values()) / len(scores)

    return scores
