"""Security & Compliance NFR analysis."""

from typing import Dict


def analyze_security(code_analysis: Dict, architecture: Dict) -> Dict:
    scores = {}
    frameworks = architecture.get("frameworks", [])
    design_patterns = architecture.get("design_patterns", [])

    security = 60
    if any(fw in frameworks for fw in ["FastAPI", "NestJS", "Spring Boot", "Django"]):
        security += 10
    if "Dependency Injection" in design_patterns:
        security += 5
    scores["security"] = min(100, security)

    confidentiality = 65
    if "Dependency Injection" in design_patterns:
        confidentiality += 10
    scores["confidentiality"] = min(100, confidentiality)

    integrity = 70
    if "Repository Pattern" in design_patterns:
        integrity += 10
    scores["integrity"] = min(100, integrity)

    authenticity = 65
    if any(fw in frameworks for fw in ["FastAPI", "NestJS", "Spring Security"]):
        authenticity += 15
    scores["authenticity"] = min(100, authenticity)

    compliance = 60
    if "Hexagonal/Clean Architecture" in architecture.get("detected_patterns", []):
        compliance += 15
    scores["compliance"] = min(100, compliance)

    auditability = 55
    if "Event-driven Pattern" in design_patterns:
        auditability += 20
    scores["auditability"] = min(100, auditability)

    governance = 65
    if "Hexagonal/Clean Architecture" in architecture.get("detected_patterns", []):
        governance += 15
    scores["governance"] = min(100, governance)

    return scores
