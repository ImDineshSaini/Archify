"""Maintainability & Operations NFR analysis."""

from typing import Dict


def analyze_maintainability(code_analysis: Dict, architecture: Dict) -> Dict:
    scores = {}
    complexity = code_analysis.get("complexity", {})
    avg_complexity = complexity.get("average_complexity", 0)
    design_patterns = architecture.get("design_patterns", [])
    patterns = architecture.get("detected_patterns", [])

    maintainability = max(0, 100 - (avg_complexity * 3))
    if architecture.get("solid_compliance"):
        maintainability += 5
    if "Hexagonal/Clean Architecture" in patterns:
        maintainability += 10
    scores["maintainability"] = min(100, maintainability)

    operability = 65
    if "Containerized (Docker)" in patterns:
        operability += 15
    scores["operability"] = min(100, operability)

    debuggability = 60
    if avg_complexity < 5:
        debuggability += 20
    scores["debuggability"] = min(100, debuggability)

    supportability = 65
    if "Service Layer Pattern" in design_patterns:
        supportability += 15
    scores["supportability"] = min(100, supportability)

    testability = 60
    if "Hexagonal/Clean Architecture" in patterns:
        testability += 20
    if "Repository Pattern" in design_patterns:
        testability += 10
    scores["testability"] = min(100, testability)

    deployability = 60
    if "Containerized (Docker)" in patterns:
        deployability += 20
    if "Microservices Architecture" in patterns:
        deployability += 15
    scores["deployability"] = min(100, deployability)

    observability = 55
    if "Microservices Architecture" in patterns:
        observability += 20
    if "Event-driven Pattern" in design_patterns:
        observability += 15
    scores["observability"] = min(100, observability)

    monitoring = 60
    if "Microservices Architecture" in patterns:
        monitoring += 15
    scores["monitoring"] = min(100, monitoring)

    return scores
