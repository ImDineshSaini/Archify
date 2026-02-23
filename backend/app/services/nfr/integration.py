"""Integration & Portability NFR analysis."""

from typing import Dict


def analyze_integration(code_analysis: Dict, architecture: Dict) -> Dict:
    scores = {}
    patterns = architecture.get("detected_patterns", [])
    design_patterns = architecture.get("design_patterns", [])

    interoperability = 65
    if "API-first Architecture" in patterns:
        interoperability += 20
    scores["interoperability"] = min(100, interoperability)

    portability = 60
    if "Containerized (Docker)" in patterns:
        portability += 25
    scores["portability"] = min(100, portability)

    extensibility = 65
    if "Hexagonal/Clean Architecture" in patterns:
        extensibility += 20
    if "Repository Pattern" in design_patterns:
        extensibility += 10
    scores["extensibility"] = min(100, extensibility)

    reconfigurability = 60
    if "Microservices Architecture" in patterns:
        reconfigurability += 20
    scores["reconfigurability"] = min(100, reconfigurability)

    modularity = 65
    if "Component-based Architecture" in patterns:
        modularity += 15
    if "Service Layer Pattern" in design_patterns:
        modularity += 10
    scores["modularity"] = min(100, modularity)

    return scores
