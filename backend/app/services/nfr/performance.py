"""Performance & Scale NFR analysis."""

from typing import Dict


def analyze_performance_scale(code_analysis: Dict, architecture: Dict) -> Dict:
    scores = {}
    complexity = code_analysis.get("complexity", {})
    patterns = architecture.get("detected_patterns", [])
    design_patterns = architecture.get("design_patterns", [])

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

    avg_complexity = complexity.get("average_complexity", 0)
    performance = max(20, 100 - (avg_complexity * 4))
    if "Caching" in str(architecture):
        performance += 10
    scores["performance"] = min(100, performance)

    throughput = 70
    if "Event-driven Pattern" in design_patterns:
        throughput += 15
    if "Microservices Architecture" in patterns:
        throughput += 10
    scores["throughput"] = min(100, throughput)

    latency = 75
    if avg_complexity < 5:
        latency += 15
    scores["latency"] = min(100, latency)

    elasticity = 50
    if "Microservices Architecture" in patterns:
        elasticity += 30
    if "Containerized (Docker)" in patterns:
        elasticity += 15
    scores["elasticity"] = min(100, elasticity)

    capacity = 70
    if "Microservices Architecture" in patterns:
        capacity += 20
    scores["capacity"] = min(100, capacity)

    concurrency = 65
    if "Event-driven Pattern" in design_patterns:
        concurrency += 20
    if any(fw in architecture.get("frameworks", []) for fw in ["FastAPI", "Go", "Rust"]):
        concurrency += 10
    scores["concurrency"] = min(100, concurrency)

    return scores
