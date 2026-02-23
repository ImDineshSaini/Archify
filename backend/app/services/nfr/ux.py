"""User Experience NFR analysis."""

from typing import Dict


def analyze_ux(code_analysis: Dict, architecture: Dict) -> Dict:
    scores = {}
    frameworks = architecture.get("frameworks", [])

    usability = 70
    if any(fw in frameworks for fw in ["React", "Vue.js", "Angular"]):
        usability += 15
    scores["usability"] = min(100, usability)

    accessibility = 65
    if any(fw in frameworks for fw in ["React", "Vue.js", "Angular"]):
        accessibility += 10
    scores["accessibility"] = min(100, accessibility)

    responsiveness = 70
    if "Server-Side Rendering" in architecture.get("detected_patterns", []):
        responsiveness += 15
    scores["responsiveness"] = min(100, responsiveness)

    return scores
