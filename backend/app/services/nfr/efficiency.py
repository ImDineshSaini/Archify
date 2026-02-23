"""Efficiency NFR analysis."""

from typing import Dict


def analyze_efficiency(code_analysis: Dict, architecture: Dict) -> Dict:
    scores = {}
    complexity = code_analysis.get("complexity", {})
    avg_complexity = complexity.get("average_complexity", 0)

    cost_efficiency = 70
    if "Microservices Architecture" in architecture.get("detected_patterns", []):
        cost_efficiency += 10
    scores["cost_efficiency"] = min(100, cost_efficiency)

    resource_efficiency = max(20, 90 - (avg_complexity * 2))
    scores["resource_efficiency"] = min(100, resource_efficiency)

    energy_efficiency = max(30, 85 - (avg_complexity * 2))
    scores["energy_efficiency"] = min(100, energy_efficiency)

    return scores
