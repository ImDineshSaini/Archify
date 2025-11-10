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
                Analyze the provided code metrics and provide actionable suggestions to improve:
                1. Code maintainability
                2. System reliability
                3. Scalability
                4. Security
                5. Overall architecture quality

                Be specific and prioritize the most impactful improvements."""),
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

        prompt += "\n\nBased on this analysis, provide specific, actionable recommendations to improve the codebase."

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
Analyze the directory structure and provide:

1. **Additional Architecture Patterns** (not detected by heuristics)
2. **Anti-Patterns** you notice
3. **SOLID Principles Compliance** (detailed assessment)
4. **Testability Assessment** (how easy to test this structure?)
5. **Coupling & Cohesion** (are modules properly separated?)
6. **Suggested Refactoring** (specific structural improvements)

Be specific and reference actual folders/files you see in the tree.
Format as JSON with keys: additional_patterns, anti_patterns, solid_assessment, testability_score (0-100), coupling_analysis, refactoring_suggestions
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
Based on the ACTUAL directory structure, provide refined scores (0-100) for these NFRs:

1. **Scalability** - Can this architecture handle growth?
2. **Testability** - How easy is it to test? (check for test folders)
3. **Maintainability** - Is the structure clean and organized?
4. **Deployability** - Deployment complexity? (check for Docker, CI/CD files)
5. **Observability** - Logging/monitoring setup?

For each NFR, provide:
- refined_score (0-100)
- confidence (low/medium/high)
- reasoning (why this score based on structure)

Format as JSON: {{"scalability": {{"refined_score": 85, "confidence": "high", "reasoning": "..."}}, ...}}
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
Create a prioritized improvement roadmap to enhance this codebase.

Current Scores:
- Maintainability: {current_scores.get('maintainability', 0):.1f}/100
- Reliability: {current_scores.get('reliability', 0):.1f}/100
- Scalability: {current_scores.get('scalability', 0):.1f}/100
- Security: {current_scores.get('security', 0):.1f}/100

Target: All scores above 80/100

Provide a phased approach (3 phases) with specific tasks for each phase.
"""

            messages = [
                SystemMessage(content="You are a technical project manager creating improvement roadmaps."),
                HumanMessage(content=prompt)
            ]

            response = self.client.invoke(messages)
            return response.content

        except Exception as e:
            return f"Error generating roadmap: {str(e)}"
