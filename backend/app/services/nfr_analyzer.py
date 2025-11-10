"""
NFR (Non-Functional Requirements) Analyzer
Analyzes 40+ quality attributes ("-ity" qualities) for comprehensive architecture assessment
"""

from typing import Dict, Any, List
from pathlib import Path


class NFRAnalyzer:
    """
    Comprehensive Non-Functional Requirements analyzer
    Evaluates 40+ quality attributes for business-level architecture insights
    """

    def __init__(self):
        self.nfr_categories = {
            "Performance & Scale": [
                "scalability", "performance", "throughput", "latency",
                "elasticity", "capacity", "concurrency"
            ],
            "Reliability & Resilience": [
                "reliability", "availability", "resilience", "fault_tolerance",
                "recoverability", "durability", "consistency"
            ],
            "Security & Compliance": [
                "security", "confidentiality", "integrity", "authenticity",
                "compliance", "auditability", "governance"
            ],
            "Maintainability & Operations": [
                "maintainability", "operability", "debuggability", "supportability",
                "testability", "deployability", "observability", "monitoring"
            ],
            "User Experience": [
                "usability", "accessibility", "responsiveness"
            ],
            "Integration & Portability": [
                "interoperability", "portability", "extensibility",
                "reconfigurability", "modularity"
            ],
            "Efficiency": [
                "cost_efficiency", "resource_efficiency", "energy_efficiency"
            ],
            "Business Continuity": [
                "disaster_recovery", "business_continuity", "backup_recovery"
            ]
        }

    def analyze_nfr(self, code_analysis: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive NFR analysis based on code metrics and architecture patterns

        Returns:
            Dictionary with scores for all NFR attributes
        """
        nfr_scores = {}

        # Performance & Scale
        nfr_scores.update(self._analyze_performance_scale(code_analysis, architecture))

        # Reliability & Resilience
        nfr_scores.update(self._analyze_reliability(code_analysis, architecture))

        # Security & Compliance
        nfr_scores.update(self._analyze_security(code_analysis, architecture))

        # Maintainability & Operations
        nfr_scores.update(self._analyze_maintainability(code_analysis, architecture))

        # User Experience
        nfr_scores.update(self._analyze_ux(code_analysis, architecture))

        # Integration & Portability
        nfr_scores.update(self._analyze_integration(code_analysis, architecture))

        # Efficiency
        nfr_scores.update(self._analyze_efficiency(code_analysis, architecture))

        # Business Continuity
        nfr_scores.update(self._analyze_business_continuity(code_analysis, architecture))

        return {
            "nfr_scores": nfr_scores,
            "nfr_categories": self.nfr_categories,
            "category_averages": self._calculate_category_averages(nfr_scores),
            "recommendations": self._generate_recommendations(nfr_scores, architecture)
        }

    def _analyze_performance_scale(self, code_analysis: Dict, architecture: Dict) -> Dict:
        """Analyze performance and scalability attributes"""
        scores = {}
        complexity = code_analysis.get("complexity", {})
        patterns = architecture.get("detected_patterns", [])
        design_patterns = architecture.get("design_patterns", [])

        # Scalability
        scalability = 60
        if "Microservices Architecture" in patterns:
            scalability += 25
        if "Component-based Architecture" in patterns:
            scalability += 10
        if "Event-driven Pattern" in design_patterns:
            scalability += 10
        if "CQRS Pattern" in design_patterns:
            scalability += 5
        scores["scalability"] = min(100, scalability)

        # Performance
        avg_complexity = complexity.get("average_complexity", 0)
        performance = max(20, 100 - (avg_complexity * 4))
        if "Caching" in str(architecture):
            performance += 10
        scores["performance"] = min(100, performance)

        # Throughput
        throughput = 70
        if "Event-driven Pattern" in design_patterns:
            throughput += 15
        if "Microservices Architecture" in patterns:
            throughput += 10
        scores["throughput"] = min(100, throughput)

        # Latency
        latency = 75  # Lower complexity = better latency
        if avg_complexity < 5:
            latency += 15
        scores["latency"] = min(100, latency)

        # Elasticity
        elasticity = 50
        if "Microservices Architecture" in patterns:
            elasticity += 30
        if "Containerized (Docker)" in patterns:
            elasticity += 15
        scores["elasticity"] = min(100, elasticity)

        # Capacity
        capacity = 70
        if "Microservices Architecture" in patterns:
            capacity += 20
        scores["capacity"] = min(100, capacity)

        # Concurrency
        concurrency = 65
        if "Event-driven Pattern" in design_patterns:
            concurrency += 20
        if any(fw in architecture.get("frameworks", []) for fw in ["FastAPI", "Go", "Rust"]):
            concurrency += 10
        scores["concurrency"] = min(100, concurrency)

        return scores

    def _analyze_reliability(self, code_analysis: Dict, architecture: Dict) -> Dict:
        """Analyze reliability and resilience attributes"""
        scores = {}
        code_metrics = code_analysis.get("code_metrics", {})
        patterns = architecture.get("detected_patterns", [])
        design_patterns = architecture.get("design_patterns", [])

        total_lines = code_metrics.get("total_lines", 1)
        comment_ratio = code_metrics.get("comment_lines", 0) / max(total_lines, 1) * 100

        # Reliability
        reliability = 50 + (comment_ratio * 2)
        if design_patterns:
            reliability += min(10, len(design_patterns) * 2)
        scores["reliability"] = min(100, reliability)

        # Availability
        availability = 60
        if "Microservices Architecture" in patterns:
            availability += 20
        if "Event-driven Pattern" in design_patterns:
            availability += 10
        scores["availability"] = min(100, availability)

        # Resilience
        resilience = 55
        if "Microservices Architecture" in patterns:
            resilience += 25
        if "Event-driven Pattern" in design_patterns:
            resilience += 15
        scores["resilience"] = min(100, resilience)

        # Fault Tolerance
        fault_tolerance = 50
        if "Microservices Architecture" in patterns:
            fault_tolerance += 20
        if "Event-driven Pattern" in design_patterns:
            fault_tolerance += 15
        scores["fault_tolerance"] = min(100, fault_tolerance)

        # Recoverability
        recoverability = 60
        if "Microservices Architecture" in patterns:
            recoverability += 15
        scores["recoverability"] = min(100, recoverability)

        # Durability
        durability = 65
        if "Repository Pattern" in design_patterns:
            durability += 15
        scores["durability"] = min(100, durability)

        # Consistency
        consistency = 70
        if "CQRS Pattern" in design_patterns:
            consistency += 10
        scores["consistency"] = min(100, consistency)

        return scores

    def _analyze_security(self, code_analysis: Dict, architecture: Dict) -> Dict:
        """Analyze security and compliance attributes"""
        scores = {}
        frameworks = architecture.get("frameworks", [])
        design_patterns = architecture.get("design_patterns", [])

        # Security (base)
        security = 60
        if any(fw in frameworks for fw in ["FastAPI", "NestJS", "Spring Boot", "Django"]):
            security += 10
        if "Dependency Injection" in design_patterns:
            security += 5
        scores["security"] = min(100, security)

        # Confidentiality
        confidentiality = 65
        if "Dependency Injection" in design_patterns:
            confidentiality += 10
        scores["confidentiality"] = min(100, confidentiality)

        # Integrity
        integrity = 70
        if "Repository Pattern" in design_patterns:
            integrity += 10
        scores["integrity"] = min(100, integrity)

        # Authenticity
        authenticity = 65
        if any(fw in frameworks for fw in ["FastAPI", "NestJS", "Spring Security"]):
            authenticity += 15
        scores["authenticity"] = min(100, authenticity)

        # Compliance
        compliance = 60
        if "Hexagonal/Clean Architecture" in architecture.get("detected_patterns", []):
            compliance += 15
        scores["compliance"] = min(100, compliance)

        # Auditability
        auditability = 55
        if "Event-driven Pattern" in design_patterns:
            auditability += 20
        scores["auditability"] = min(100, auditability)

        # Governance
        governance = 65
        if "Hexagonal/Clean Architecture" in architecture.get("detected_patterns", []):
            governance += 15
        scores["governance"] = min(100, governance)

        return scores

    def _analyze_maintainability(self, code_analysis: Dict, architecture: Dict) -> Dict:
        """Analyze maintainability and operations attributes"""
        scores = {}
        complexity = code_analysis.get("complexity", {})
        avg_complexity = complexity.get("average_complexity", 0)
        design_patterns = architecture.get("design_patterns", [])
        patterns = architecture.get("detected_patterns", [])

        # Maintainability
        maintainability = max(0, 100 - (avg_complexity * 3))
        if architecture.get("solid_compliance"):
            maintainability += 5
        if "Hexagonal/Clean Architecture" in patterns:
            maintainability += 10
        scores["maintainability"] = min(100, maintainability)

        # Operability
        operability = 65
        if "Containerized (Docker)" in patterns:
            operability += 15
        scores["operability"] = min(100, operability)

        # Debuggability
        debuggability = 60
        if avg_complexity < 5:
            debuggability += 20
        scores["debuggability"] = min(100, debuggability)

        # Supportability
        supportability = 65
        if "Service Layer Pattern" in design_patterns:
            supportability += 15
        scores["supportability"] = min(100, supportability)

        # Testability
        testability = 60
        if "Hexagonal/Clean Architecture" in patterns:
            testability += 20
        if "Repository Pattern" in design_patterns:
            testability += 10
        scores["testability"] = min(100, testability)

        # Deployability
        deployability = 60
        if "Containerized (Docker)" in patterns:
            deployability += 20
        if "Microservices Architecture" in patterns:
            deployability += 15
        scores["deployability"] = min(100, deployability)

        # Observability
        observability = 55
        if "Microservices Architecture" in patterns:
            observability += 20
        if "Event-driven Pattern" in design_patterns:
            observability += 15
        scores["observability"] = min(100, observability)

        # Monitoring
        monitoring = 60
        if "Microservices Architecture" in patterns:
            monitoring += 15
        scores["monitoring"] = min(100, monitoring)

        return scores

    def _analyze_ux(self, code_analysis: Dict, architecture: Dict) -> Dict:
        """Analyze user experience attributes"""
        scores = {}
        frameworks = architecture.get("frameworks", [])

        # Usability
        usability = 70
        if any(fw in frameworks for fw in ["React", "Vue.js", "Angular"]):
            usability += 15
        scores["usability"] = min(100, usability)

        # Accessibility
        accessibility = 65
        if any(fw in frameworks for fw in ["React", "Vue.js", "Angular"]):
            accessibility += 10
        scores["accessibility"] = min(100, accessibility)

        # Responsiveness
        responsiveness = 70
        if "Server-Side Rendering" in architecture.get("detected_patterns", []):
            responsiveness += 15
        scores["responsiveness"] = min(100, responsiveness)

        return scores

    def _analyze_integration(self, code_analysis: Dict, architecture: Dict) -> Dict:
        """Analyze integration and portability attributes"""
        scores = {}
        patterns = architecture.get("detected_patterns", [])
        design_patterns = architecture.get("design_patterns", [])

        # Interoperability
        interoperability = 65
        if "API-first Architecture" in patterns:
            interoperability += 20
        scores["interoperability"] = min(100, interoperability)

        # Portability
        portability = 60
        if "Containerized (Docker)" in patterns:
            portability += 25
        scores["portability"] = min(100, portability)

        # Extensibility
        extensibility = 65
        if "Hexagonal/Clean Architecture" in patterns:
            extensibility += 20
        if "Repository Pattern" in design_patterns:
            extensibility += 10
        scores["extensibility"] = min(100, extensibility)

        # Reconfigurability
        reconfigurability = 60
        if "Microservices Architecture" in patterns:
            reconfigurability += 20
        scores["reconfigurability"] = min(100, reconfigurability)

        # Modularity
        modularity = 65
        if "Component-based Architecture" in patterns:
            modularity += 15
        if "Service Layer Pattern" in design_patterns:
            modularity += 10
        scores["modularity"] = min(100, modularity)

        return scores

    def _analyze_efficiency(self, code_analysis: Dict, architecture: Dict) -> Dict:
        """Analyze efficiency attributes"""
        scores = {}
        complexity = code_analysis.get("complexity", {})
        avg_complexity = complexity.get("average_complexity", 0)

        # Cost Efficiency
        cost_efficiency = 70
        if "Microservices Architecture" in architecture.get("detected_patterns", []):
            cost_efficiency += 10
        scores["cost_efficiency"] = min(100, cost_efficiency)

        # Resource Efficiency
        resource_efficiency = max(20, 90 - (avg_complexity * 2))
        scores["resource_efficiency"] = min(100, resource_efficiency)

        # Energy Efficiency
        energy_efficiency = max(30, 85 - (avg_complexity * 2))
        scores["energy_efficiency"] = min(100, energy_efficiency)

        return scores

    def _analyze_business_continuity(self, code_analysis: Dict, architecture: Dict) -> Dict:
        """Analyze business continuity attributes"""
        scores = {}
        patterns = architecture.get("detected_patterns", [])

        # Disaster Recovery
        disaster_recovery = 55
        if "Microservices Architecture" in patterns:
            disaster_recovery += 20
        scores["disaster_recovery"] = min(100, disaster_recovery)

        # Business Continuity
        business_continuity = 60
        if "Microservices Architecture" in patterns:
            business_continuity += 20
        scores["business_continuity"] = min(100, business_continuity)

        # Backup Recovery
        backup_recovery = 65
        if "Repository Pattern" in architecture.get("design_patterns", []):
            backup_recovery += 10
        scores["backup_recovery"] = min(100, backup_recovery)

        return scores

    def _calculate_category_averages(self, nfr_scores: Dict) -> Dict:
        """Calculate average scores for each NFR category"""
        averages = {}

        for category, attributes in self.nfr_categories.items():
            category_scores = [nfr_scores.get(attr, 0) for attr in attributes if attr in nfr_scores]
            if category_scores:
                averages[category] = sum(category_scores) / len(category_scores)
            else:
                averages[category] = 0

        return averages

    def _generate_recommendations(self, nfr_scores: Dict, architecture: Dict) -> List[Dict]:
        """Generate prioritized recommendations based on NFR scores"""
        recommendations = []

        # Find lowest scoring attributes
        sorted_scores = sorted(nfr_scores.items(), key=lambda x: x[1])

        for attr, score in sorted_scores[:10]:  # Top 10 lowest scores
            if score < 70:
                priority = "HIGH" if score < 50 else "MEDIUM" if score < 60 else "LOW"
                recommendations.append({
                    "attribute": attr.replace("_", " ").title(),
                    "current_score": round(score, 1),
                    "priority": priority,
                    "impact": self._get_business_impact(attr),
                    "recommendation": self._get_recommendation(attr, architecture)
                })

        return recommendations

    def _get_business_impact(self, attribute: str) -> str:
        """Get business impact description for an attribute"""
        impact_map = {
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
        return impact_map.get(attribute, "Impacts overall system quality")

    def _get_recommendation(self, attribute: str, architecture: Dict) -> str:
        """Get specific recommendation for improving an attribute"""
        recommendations_map = {
            "scalability": "Consider microservices architecture and horizontal scaling",
            "performance": "Optimize algorithms, add caching, reduce complexity",
            "reliability": "Implement comprehensive error handling and testing",
            "security": "Add authentication/authorization, security scanning, HTTPS",
            "maintainability": "Refactor complex code, improve documentation, follow SOLID principles",
            "testability": "Implement dependency injection and repository patterns",
            "observability": "Add structured logging, metrics, and distributed tracing",
        }
        return recommendations_map.get(attribute, f"Improve {attribute.replace('_', ' ')} through architecture refactoring")
