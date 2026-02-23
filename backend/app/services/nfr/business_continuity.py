"""Business Continuity NFR analysis."""

from typing import Dict


def analyze_business_continuity(code_analysis: Dict, architecture: Dict) -> Dict:
    scores = {}
    patterns = architecture.get("detected_patterns", [])

    disaster_recovery = 55
    if "Microservices Architecture" in patterns:
        disaster_recovery += 20
    scores["disaster_recovery"] = min(100, disaster_recovery)

    business_continuity = 60
    if "Microservices Architecture" in patterns:
        business_continuity += 20
    scores["business_continuity"] = min(100, business_continuity)

    backup_recovery = 65
    if "Repository Pattern" in architecture.get("design_patterns", []):
        backup_recovery += 10
    scores["backup_recovery"] = min(100, backup_recovery)

    return scores
