"""NFR Analyzer orchestrator -- delegates to app.services.nfr submodules."""

from typing import Any, Dict, List
from app.services.nfr.performance import analyze_performance_scale
from app.services.nfr.reliability import analyze_reliability
from app.services.nfr.security import analyze_security
from app.services.nfr.maintainability import analyze_maintainability
from app.services.nfr.ux import analyze_ux
from app.services.nfr.integration import analyze_integration
from app.services.nfr.efficiency import analyze_efficiency
from app.services.nfr.business_continuity import analyze_business_continuity
from app.services.nfr.recommendations import generate_recommendations

NFR_CATEGORIES = {
    "Performance & Scale": [
        "scalability", "performance", "throughput", "latency",
        "elasticity", "capacity", "concurrency",
    ],
    "Reliability & Resilience": [
        "reliability", "availability", "resilience", "fault_tolerance",
        "recoverability", "durability", "consistency",
    ],
    "Security & Compliance": [
        "security", "confidentiality", "integrity", "authenticity",
        "compliance", "auditability", "governance",
    ],
    "Maintainability & Operations": [
        "maintainability", "operability", "debuggability", "supportability",
        "testability", "deployability", "observability", "monitoring",
    ],
    "User Experience": ["usability", "accessibility", "responsiveness"],
    "Integration & Portability": [
        "interoperability", "portability", "extensibility",
        "reconfigurability", "modularity",
    ],
    "Efficiency": ["cost_efficiency", "resource_efficiency", "energy_efficiency"],
    "Business Continuity": ["disaster_recovery", "business_continuity", "backup_recovery"],
}


class NFRAnalyzer:
    """Comprehensive Non-Functional Requirements analyzer."""

    def __init__(self):
        self.nfr_categories = NFR_CATEGORIES

    def analyze_nfr(
        self, code_analysis: Dict[str, Any], architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        nfr_scores = {}

        nfr_scores.update(analyze_performance_scale(code_analysis, architecture))
        nfr_scores.update(analyze_reliability(code_analysis, architecture))
        nfr_scores.update(analyze_security(code_analysis, architecture))
        nfr_scores.update(analyze_maintainability(code_analysis, architecture))
        nfr_scores.update(analyze_ux(code_analysis, architecture))
        nfr_scores.update(analyze_integration(code_analysis, architecture))
        nfr_scores.update(analyze_efficiency(code_analysis, architecture))
        nfr_scores.update(analyze_business_continuity(code_analysis, architecture))

        return {
            "nfr_scores": nfr_scores,
            "nfr_categories": self.nfr_categories,
            "category_averages": self._calculate_category_averages(nfr_scores),
            "recommendations": generate_recommendations(nfr_scores, architecture),
        }

    def _calculate_category_averages(self, nfr_scores: Dict) -> Dict:
        averages = {}
        for category, attributes in self.nfr_categories.items():
            category_scores = [nfr_scores.get(attr, 0) for attr in attributes if attr in nfr_scores]
            averages[category] = sum(category_scores) / len(category_scores) if category_scores else 0
        return averages
