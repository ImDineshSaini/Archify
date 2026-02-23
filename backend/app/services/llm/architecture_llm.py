"""AI-powered architecture analysis functions."""

import json
from typing import Any, Dict
from langchain.schema import HumanMessage, SystemMessage
from app.core.constants import NFR_TREE_TRUNCATION_LIMIT


def analyze_architecture_patterns(client, file_structure: Dict[str, Any]) -> str:
    """Use AI to identify architecture patterns and anti-patterns."""
    try:
        prompt = f"""
Analyze the following project structure and identify:
1. Architecture patterns used
2. Potential anti-patterns
3. Structural improvements

Project Structure:
- Total Files: {file_structure.get('total_files', 0)}
- Total Directories: {file_structure.get('total_directories', 0)}

Provide a brief analysis focusing on architecture quality.
"""
        messages = [
            SystemMessage(content="You are an expert software architect specializing in identifying architecture patterns."),
            HumanMessage(content=prompt),
        ]

        response = client.invoke(messages)
        return response.content

    except Exception as e:
        return f"Error analyzing architecture: {str(e)}"


def analyze_architecture_from_tree(
    client, directory_tree: str, basic_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """AI-Enhanced Architecture Analysis using directory tree."""
    try:
        architecture = basic_analysis.get("architecture", {})
        scores = basic_analysis.get("scores", {})

        prompt = f"""
You are an expert software architect. Analyze this codebase directory structure and provide deep architecture insights.

# Directory Structure:
```
{directory_tree}
```

# Basic Analysis:
- Language: {architecture.get('language', 'unknown')}
- Frameworks: {', '.join(architecture.get('frameworks', []))}
- Detected Patterns: {', '.join(architecture.get('detected_patterns', []))}
- Design Patterns: {', '.join(architecture.get('design_patterns', []))}

# Current Scores:
- Maintainability: {scores.get('maintainability', 0):.1f}/100
- Scalability: {scores.get('scalability', 0):.1f}/100

## Your Task:
Analyze the directory structure and provide CONCRETE, ACTIONABLE insights:

1. **Additional Architecture Patterns** (not detected by heuristics) - Be specific: "Uses Facade Pattern in /api/facades", not just "Good separation"
2. **Anti-Patterns** - Reference actual folders: "God Object in /services/user_service.py", "No separation between business logic and data access in /controllers"
3. **SOLID Principles Compliance** - Specific violations with file paths: "SRP violated in /services/payment.py - handles both payment processing AND email notifications"
4. **Testability Assessment** - Concrete issues: "No test coverage for /services/auth.py", "Hard-coded dependencies in /api/routes.py prevent mocking"
5. **Coupling & Cohesion** - Specific examples: "/modules/orders depends on 5 other modules", "Tight coupling between /ui and /database layers"
6. **Refactoring Suggestions** - Actionable steps with tools:
   - "Extract email logic from PaymentService into dedicated EmailService"
   - "Implement Dependency Injection using dependency-injector library"
   - "Add integration tests using pytest-mock for /services layer"
   - "Refactor /controllers to use Repository Pattern with SQLAlchemy repositories"

Format as JSON with keys: additional_patterns (array), anti_patterns (array), solid_assessment (object with specific violations), testability_score (0-100), coupling_analysis (object), refactoring_suggestions (array of concrete steps)
"""

        messages = [
            SystemMessage(content="You are an expert software architect specializing in architecture analysis."),
            HumanMessage(content=prompt),
        ]

        response = client.invoke(messages)

        try:
            return json.loads(response.content)
        except (json.JSONDecodeError, TypeError):
            return {"raw_analysis": response.content}

    except Exception as e:
        return {"error": f"AI architecture analysis failed: {str(e)}"}


def refine_nfr_scores(
    client, directory_tree: str, basic_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """AI-Enhanced NFR scoring based on directory structure."""
    try:
        nfr_analysis = basic_analysis.get("nfr_analysis", {})
        nfr_scores = nfr_analysis.get("nfr_scores", {})
        architecture = basic_analysis.get("architecture", {})

        key_nfrs = {
            "scalability": nfr_scores.get("scalability", 0),
            "testability": nfr_scores.get("testability", 0),
            "maintainability": nfr_scores.get("maintainability", 0),
            "deployability": nfr_scores.get("deployability", 0),
            "observability": nfr_scores.get("observability", 0),
        }

        prompt = f"""
Analyze this codebase structure and refine the NFR scores:

# Directory Structure:
```
{directory_tree[:NFR_TREE_TRUNCATION_LIMIT]}... (truncated)
```

# Architecture:
- Language: {architecture.get('language')}
- Frameworks: {', '.join(architecture.get('frameworks', []))}
- Patterns: {', '.join(architecture.get('detected_patterns', []))}

# Current NFR Scores (heuristic-based):
{json.dumps(key_nfrs, indent=2)}

## Your Task:
Based on the ACTUAL directory structure, provide refined scores (0-100) with CONCRETE observations:

1. **Scalability** - Check for: caching (Redis/Memcached), message queues (RabbitMQ/Kafka), load balancing configs, database connection pooling
2. **Testability** - Check for: /tests or /test folders, test fixtures, mocking setup, CI test configs (.github/workflows), test coverage tools
3. **Maintainability** - Check for: clear module separation, consistent naming, documentation (/docs), linting configs (.eslintrc, .pylintrc)
4. **Deployability** - Check for: Dockerfile, docker-compose.yml, Kubernetes manifests (/k8s), CI/CD files (.github/workflows, .gitlab-ci.yml)
5. **Observability** - Check for: logging configs, monitoring setup (Prometheus, Grafana), APM tools (New Relic, DataDog), health check endpoints

For each NFR, provide:
- refined_score (0-100)
- confidence (low/medium/high)
- reasoning (CONCRETE evidence from directory structure - reference actual files/folders you see)
- recommendations (specific tools/patterns to improve, e.g., "Add Dockerfile for containerization", "Implement pytest fixtures in /tests")

Format as JSON: {{"scalability": {{"refined_score": 85, "confidence": "high", "reasoning": "Found Redis config in /config/redis.py and message queue in /workers", "recommendations": ["Add horizontal scaling with Kubernetes HPA", "Implement database read replicas"]}}, ...}}
"""

        messages = [
            SystemMessage(content="You are an expert at evaluating software architecture quality."),
            HumanMessage(content=prompt),
        ]

        response = client.invoke(messages)

        try:
            return json.loads(response.content)
        except (json.JSONDecodeError, TypeError):
            return {"raw_refinement": response.content}

    except Exception as e:
        return {"error": f"NFR refinement failed: {str(e)}"}


def generate_improvement_roadmap(
    client, current_scores: Dict[str, float], target_scores: Dict[str, float]
) -> str:
    """Generate a prioritized improvement roadmap."""
    try:
        prompt = f"""
Create a prioritized improvement roadmap with CONCRETE, ACTIONABLE steps.

Current Scores:
- Maintainability: {current_scores.get('maintainability', 0):.1f}/100
- Reliability: {current_scores.get('reliability', 0):.1f}/100
- Scalability: {current_scores.get('scalability', 0):.1f}/100
- Security: {current_scores.get('security', 0):.1f}/100

Target: All scores above 80/100

Provide a phased approach (3 phases) with SPECIFIC tools, patterns, and implementation steps:

**Phase 1 (Weeks 1-2): Quick Wins**
- Example: "Set up ESLint/Prettier for code consistency"
- Example: "Add Dockerfile and docker-compose.yml for local development"
- Example: "Implement basic logging with Winston/Bunyan"

**Phase 2 (Weeks 3-6): Structural Improvements**
- Example: "Refactor to Repository Pattern - extract all DB queries from controllers"
- Example: "Add Redis caching layer for frequently accessed data"
- Example: "Implement JWT authentication with refresh tokens"

**Phase 3 (Weeks 7-12): Advanced Enhancements**
- Example: "Set up Kubernetes cluster with HPA for auto-scaling"
- Example: "Implement distributed tracing with OpenTelemetry + Jaeger"
- Example: "Add comprehensive E2E tests with Cypress/Playwright"

For each task, include: estimated effort (hours), required expertise (Junior/Mid/Senior), and expected score impact (+5 points).
"""

        messages = [
            SystemMessage(content="You are a technical project manager creating improvement roadmaps."),
            HumanMessage(content=prompt),
        ]

        response = client.invoke(messages)
        return response.content

    except Exception as e:
        return f"Error generating roadmap: {str(e)}"
