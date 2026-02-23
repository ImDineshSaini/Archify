"""Shared NFR recommendation logic."""

from typing import Dict, List

IMPACT_MAP = {
    "scalability": "Limits growth potential and user capacity",
    "performance": "Affects user satisfaction and conversion rates",
    "reliability": "Increases risk of outages and data loss",
    "security": "High risk of breaches and compliance violations",
    "maintainability": "Increases development costs and time-to-market",
    "availability": "Impacts revenue and customer trust",
    "testability": "Slower releases and more production bugs",
    "deployability": "Longer deployment times and higher risk",
    "observability": "Difficult to debug production issues",
    "cost_efficiency": "Higher operational costs",
}

RECOMMENDATION_MAP = {
    "scalability": "Consider microservices architecture and horizontal scaling",
    "performance": "Optimize algorithms, add caching, reduce complexity",
    "reliability": "Implement comprehensive error handling and testing",
    "security": "Add authentication/authorization, security scanning, HTTPS",
    "maintainability": "Refactor complex code, improve documentation, follow SOLID principles",
    "testability": "Implement dependency injection and repository patterns",
    "observability": "Add structured logging, metrics, and distributed tracing",
}


def get_business_impact(attribute: str) -> str:
    return IMPACT_MAP.get(attribute, "Impacts overall system quality")


def get_recommendation(attribute: str, architecture: Dict) -> str:
    return RECOMMENDATION_MAP.get(
        attribute, f"Improve {attribute.replace('_', ' ')} through architecture refactoring"
    )


def generate_recommendations(nfr_scores: Dict, architecture: Dict) -> List[Dict]:
    """Generate prioritized recommendations based on NFR scores."""
    recommendations = []

    sorted_scores = sorted(nfr_scores.items(), key=lambda x: x[1])

    for attr, score in sorted_scores[:10]:
        if score < 70:
            priority = "HIGH" if score < 50 else "MEDIUM" if score < 60 else "LOW"
            recommendations.append({
                "attribute": attr.replace("_", " ").title(),
                "current_score": round(score, 1),
                "priority": priority,
                "impact": get_business_impact(attr),
                "recommendation": get_recommendation(attr, architecture),
            })

    return recommendations
