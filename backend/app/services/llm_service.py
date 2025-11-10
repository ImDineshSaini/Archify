from typing import Dict, Any, Optional
from anthropic import Anthropic
from openai import OpenAI, AzureOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class LLMService:
    """Service for interacting with different LLM providers"""

    def __init__(
        self,
        provider: str,
        api_key: str,
        model: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment_name: Optional[str] = None
    ):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.client = self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate LLM client"""
        if self.provider == "claude":
            model_name = self.model or "claude-3-5-sonnet-20241022"
            return ChatAnthropic(
                anthropic_api_key=self.api_key,
                model=model_name,
                temperature=0.7,
                max_tokens=4096
            )
        elif self.provider == "openai":
            model_name = self.model or "gpt-4-turbo-preview"
            return ChatOpenAI(
                openai_api_key=self.api_key,
                model=model_name,
                temperature=0.7
            )
        elif self.provider == "azure":
            if not self.endpoint or not self.deployment_name:
                raise ValueError("Azure OpenAI requires endpoint and deployment_name")
            return AzureChatOpenAI(
                azure_endpoint=self.endpoint,
                openai_api_key=self.api_key,
                deployment_name=self.deployment_name,
                openai_api_version="2024-02-01",
                temperature=0.7
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate_analysis_suggestions(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate AI-powered suggestions based on code analysis results
        """
        # Create a comprehensive prompt
        prompt = self._create_analysis_prompt(analysis_results)

        try:
            messages = [
                SystemMessage(content="""You are an expert software architect and code reviewer.
                Analyze the provided code metrics and provide CONCRETE, ACTIONABLE suggestions.

                IMPORTANT: Be specific with tools, patterns, and implementation steps. Examples:
                - ❌ BAD: "Improve auditability through architecture refactoring"
                - ✅ GOOD: "Implement structured logging using ELK Stack (Elasticsearch, Logstack, Kibana) for centralized audit trails"

                - ❌ BAD: "Enhance scalability"
                - ✅ GOOD: "Implement Redis caching for frequently accessed data and add horizontal pod autoscaling (HPA) in Kubernetes"

                - ❌ BAD: "Improve code structure"
                - ✅ GOOD: "Refactor data access to Repository Pattern - move all database queries from controllers to dedicated repository classes"

                For each recommendation, specify:
                1. Exact tool/library/pattern to use (with version if relevant)
                2. Where in the codebase to implement it
                3. Expected impact (performance gain, reduced complexity, etc.)
                4. Priority level (Critical/High/Medium/Low)

                Focus on: Architecture patterns, Design patterns, DevOps tools, Monitoring tools, Testing frameworks, Security tools, Performance optimization techniques.

                Prioritize the most impactful improvements."""),
                HumanMessage(content=prompt)
            ]

            response = self.client.invoke(messages)
            return response.content

        except Exception as e:
            return f"Error generating suggestions: {str(e)}"

    def _create_analysis_prompt(self, results: Dict[str, Any]) -> str:
        """Create a detailed prompt from analysis results"""
        code_metrics = results.get("code_metrics", {})
        complexity = results.get("complexity", {})
        architecture = results.get("architecture", {})
        scores = results.get("scores", {})

        prompt = f"""
# Code Analysis Report

## Overview Metrics
- Total Lines of Code: {code_metrics.get('total_lines', 0)}
- Files Analyzed: {code_metrics.get('files_analyzed', 0)}
- Languages: {', '.join(code_metrics.get('languages', {}).keys())}

## Complexity Analysis
- Average Complexity: {complexity.get('average_complexity', 0):.2f}
- Maximum Complexity: {complexity.get('max_complexity', 0)}
- High Complexity Functions: {len(complexity.get('high_complexity_functions', []))}

## Architecture
- Project Type: {architecture.get('project_type', 'unknown')}
- Frameworks: {', '.join(architecture.get('frameworks', []))}
- Detected Patterns: {', '.join(architecture.get('detected_patterns', []))}

## Quality Scores
- Maintainability: {scores.get('maintainability', 0):.1f}/100
- Reliability: {scores.get('reliability', 0):.1f}/100
- Scalability: {scores.get('scalability', 0):.1f}/100
- Security: {scores.get('security', 0):.1f}/100
- Overall: {scores.get('overall', 0):.1f}/100

## High Complexity Functions
"""
        for func in complexity.get('high_complexity_functions', [])[:5]:
            prompt += f"\n- {func['name']}: Complexity {func['complexity']} ({func['lines']} lines)"

        prompt += """

Based on this analysis, provide 5-8 CONCRETE recommendations. For each recommendation, use this format:

**[Priority] Recommendation Title**
- **Tool/Pattern:** [Specific tool, library, pattern, or framework]
- **Implementation:** [Where and how to implement - be specific about files/modules]
- **Expected Impact:** [Quantify if possible: "Reduce complexity by 30%", "Improve response time by 50%", etc.]
- **Resources:** [Link to docs or mention specific tutorials if relevant]

Examples of good recommendations:
- Implement Repository Pattern using TypeORM decorators in data access layer
- Add OpenTelemetry instrumentation for distributed tracing
- Set up SonarQube quality gates in CI/CD pipeline
- Refactor to CQRS pattern using MediatR library
- Implement circuit breaker pattern using Polly (C#) or resilience4j (Java)
- Add Redis caching layer with cache-aside pattern
- Implement API rate limiting using express-rate-limit or rate-limiter-flexible
- Set up Prometheus + Grafana for application monitoring"""

        return prompt

    def analyze_architecture_patterns(self, file_structure: Dict[str, Any]) -> str:
        """
        Use AI to identify architecture patterns and anti-patterns
        """
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
                HumanMessage(content=prompt)
            ]

            response = self.client.invoke(messages)
            return response.content

        except Exception as e:
            return f"Error analyzing architecture: {str(e)}"

    def analyze_architecture_from_tree(self, directory_tree: str, basic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI-Enhanced Architecture Analysis using directory tree
        Premium feature that provides deeper insights
        """
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
                HumanMessage(content=prompt)
            ]

            response = self.client.invoke(messages)

            # Try to parse as JSON, fallback to text
            try:
                import json
                result = json.loads(response.content)
            except:
                result = {"raw_analysis": response.content}

            return result

        except Exception as e:
            return {"error": f"AI architecture analysis failed: {str(e)}"}

    def refine_nfr_scores(self, directory_tree: str, basic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI-Enhanced NFR scoring based on directory structure
        Refines the heuristic-based scores with AI insights
        """
        try:
            nfr_analysis = basic_analysis.get("nfr_analysis", {})
            nfr_scores = nfr_analysis.get("nfr_scores", {})
            architecture = basic_analysis.get("architecture", {})

            # Select key NFRs for AI refinement
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
{directory_tree[:2000]}... (truncated)
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
                HumanMessage(content=prompt)
            ]

            response = self.client.invoke(messages)

            # Try to parse as JSON
            try:
                import json
                result = json.loads(response.content)
            except:
                result = {"raw_refinement": response.content}

            return result

        except Exception as e:
            return {"error": f"NFR refinement failed: {str(e)}"}

    def generate_improvement_roadmap(
        self,
        current_scores: Dict[str, float],
        target_scores: Dict[str, float]
    ) -> str:
        """
        Generate a prioritized improvement roadmap
        """
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
                HumanMessage(content=prompt)
            ]

            response = self.client.invoke(messages)
            return response.content

        except Exception as e:
            return f"Error generating roadmap: {str(e)}"
