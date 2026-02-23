"""Reliability & Resilience NFR analysis."""

from typing import Dict


def analyze_reliability(code_analysis: Dict, architecture: Dict) -> Dict:
    scores = {}
    code_metrics = code_analysis.get("code_metrics", {})
    patterns = architecture.get("detected_patterns", [])
    design_patterns = architecture.get("design_patterns", [])

    total_lines = code_metrics.get("total_lines", 1)
    comment_ratio = code_metrics.get("comment_lines", 0) / max(total_lines, 1) * 100

    reliability = 50 + (comment_ratio * 2)
    if design_patterns:
        reliability += min(10, len(design_patterns) * 2)
    scores["reliability"] = min(100, reliability)

    availability = 60
    if "Microservices Architecture" in patterns:
        availability += 20
    if "Event-driven Pattern" in design_patterns:
        availability += 10
    scores["availability"] = min(100, availability)

    resilience = 55
    if "Microservices Architecture" in patterns:
        resilience += 25
    if "Event-driven Pattern" in design_patterns:
        resilience += 15
    scores["resilience"] = min(100, resilience)

    fault_tolerance = 50
    if "Microservices Architecture" in patterns:
        fault_tolerance += 20
    if "Event-driven Pattern" in design_patterns:
        fault_tolerance += 15
    scores["fault_tolerance"] = min(100, fault_tolerance)

    recoverability = 60
    if "Microservices Architecture" in patterns:
        recoverability += 15
    scores["recoverability"] = min(100, recoverability)

    durability = 65
    if "Repository Pattern" in design_patterns:
        durability += 15
    scores["durability"] = min(100, durability)

    consistency = 70
    if "CQRS Pattern" in design_patterns:
        consistency += 10
    scores["consistency"] = min(100, consistency)

    return scores
