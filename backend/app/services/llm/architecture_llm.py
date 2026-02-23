"""AI-powered architecture analysis functions."""

import json
import logging
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from app.core.constants import NFR_TREE_TRUNCATION_LIMIT
from app.services.llm.base_analyzer import extract_json
from app.services.llm.schemas import ArchitectureAnalysisOutput, NFRRefinementOutput

logger = logging.getLogger(__name__)


def analyze_architecture_patterns(client, file_structure: Dict[str, Any]) -> str:
    """Use AI to identify architecture patterns and anti-patterns."""
    try:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an expert software architect specializing in identifying architecture patterns."),
            ("human",
             "Analyze the following project structure and identify:\n"
             "1. Architecture patterns used\n"
             "2. Potential anti-patterns\n"
             "3. Structural improvements\n\n"
             "Project Structure:\n"
             "- Total Files: {total_files}\n"
             "- Total Directories: {total_directories}\n\n"
             "Provide a brief analysis focusing on architecture quality."),
        ])

        chain = prompt_template | client
        result = chain.invoke({
            "total_files": str(file_structure.get("total_files", 0)),
            "total_directories": str(file_structure.get("total_directories", 0)),
        })
        return result.content

    except Exception as e:
        return f"Error analyzing architecture: {str(e)}"


def analyze_architecture_from_tree(
    client, directory_tree: str, basic_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """AI-Enhanced Architecture Analysis using directory tree."""
    try:
        return _structured_architecture_analysis(client, directory_tree, basic_analysis)
    except Exception as e:
        logger.warning("Structured architecture analysis failed, using fallback: %s", e)
        return _fallback_architecture_analysis(client, directory_tree, basic_analysis)


def _structured_architecture_analysis(
    client, directory_tree: str, basic_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """Primary path: structured output."""
    architecture = basic_analysis.get("architecture", {})
    scores = basic_analysis.get("scores", {})

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert software architect specializing in architecture analysis."),
        ("human",
         "You are an expert software architect. Analyze this codebase directory structure "
         "and provide deep architecture insights.\n\n"
         "# Directory Structure:\n```\n{directory_tree}\n```\n\n"
         "# Basic Analysis:\n"
         "- Language: {language}\n"
         "- Frameworks: {frameworks}\n"
         "- Detected Patterns: {detected_patterns}\n"
         "- Design Patterns: {design_patterns}\n\n"
         "# Current Scores:\n"
         "- Maintainability: {maintainability}/100\n"
         "- Scalability: {scalability}/100\n\n"
         "Provide:\n"
         "1. Additional architecture patterns not detected by heuristics\n"
         "2. Anti-patterns with specific folder/file references\n"
         "3. SOLID principles compliance with specific violations and file paths\n"
         "4. Testability assessment\n"
         "5. Coupling & cohesion analysis\n"
         "6. Actionable refactoring suggestions with specific tools"),
    ])

    structured_llm = client.with_structured_output(ArchitectureAnalysisOutput)
    chain = prompt | structured_llm
    result = chain.invoke({
        "directory_tree": directory_tree,
        "language": architecture.get("language", "unknown"),
        "frameworks": ", ".join(architecture.get("frameworks", [])),
        "detected_patterns": ", ".join(architecture.get("detected_patterns", [])),
        "design_patterns": ", ".join(architecture.get("design_patterns", [])),
        "maintainability": f"{scores.get('maintainability', 0):.1f}",
        "scalability": f"{scores.get('scalability', 0):.1f}",
    })
    return result.model_dump()


def _fallback_architecture_analysis(
    client, directory_tree: str, basic_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """Legacy fallback path."""
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

Provide analysis as JSON with keys: additional_patterns, anti_patterns, solid_assessment, testability_score, coupling_analysis, refactoring_suggestions
"""

    messages = [
        SystemMessage(content="You are an expert software architect specializing in architecture analysis."),
        HumanMessage(content=prompt),
    ]

    response = client.invoke(messages)

    result = extract_json(response.content)
    if result is not None:
        return result
    return {"raw_analysis": response.content}


def refine_nfr_scores(
    client, directory_tree: str, basic_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """AI-Enhanced NFR scoring based on directory structure."""
    try:
        return _structured_nfr_refinement(client, directory_tree, basic_analysis)
    except Exception as e:
        logger.warning("Structured NFR refinement failed, using fallback: %s", e)
        return _fallback_nfr_refinement(client, directory_tree, basic_analysis)


def _structured_nfr_refinement(
    client, directory_tree: str, basic_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """Primary path: structured output."""
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

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert at evaluating software architecture quality."),
        ("human",
         "Analyze this codebase structure and refine the NFR scores:\n\n"
         "# Directory Structure:\n```\n{directory_tree}\n```\n\n"
         "# Architecture:\n- Language: {language}\n- Frameworks: {frameworks}\n"
         "- Patterns: {patterns}\n\n"
         "# Current NFR Scores (heuristic-based):\n{nfr_scores}\n\n"
         "For each NFR (scalability, testability, maintainability, deployability, "
         "observability), provide: refined_score (0-100), confidence (low/medium/high), "
         "reasoning (with concrete evidence from directory structure), and "
         "recommendations (specific tools/patterns)."),
    ])

    structured_llm = client.with_structured_output(NFRRefinementOutput)
    chain = prompt | structured_llm
    result = chain.invoke({
        "directory_tree": directory_tree[:NFR_TREE_TRUNCATION_LIMIT],
        "language": architecture.get("language", "unknown"),
        "frameworks": ", ".join(architecture.get("frameworks", [])),
        "patterns": ", ".join(architecture.get("detected_patterns", [])),
        "nfr_scores": json.dumps(key_nfrs, indent=2),
    })
    return result.model_dump()


def _fallback_nfr_refinement(
    client, directory_tree: str, basic_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """Legacy fallback path."""
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

Provide refined scores as JSON: {{"scalability": {{"refined_score": 85, "confidence": "high", "reasoning": "...", "recommendations": [...]}}, ...}}
"""

    messages = [
        SystemMessage(content="You are an expert at evaluating software architecture quality."),
        HumanMessage(content=prompt),
    ]

    response = client.invoke(messages)

    result = extract_json(response.content)
    if result is not None:
        return result
    return {"raw_refinement": response.content}


def generate_improvement_roadmap(
    client, current_scores: Dict[str, float], target_scores: Dict[str, float]
) -> str:
    """Generate a prioritized improvement roadmap."""
    try:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a technical project manager creating improvement roadmaps."),
            ("human",
             "Create a prioritized improvement roadmap with CONCRETE, ACTIONABLE steps.\n\n"
             "Current Scores:\n"
             "- Maintainability: {maintainability}/100\n"
             "- Reliability: {reliability}/100\n"
             "- Scalability: {scalability}/100\n"
             "- Security: {security}/100\n\n"
             "Target: All scores above 80/100\n\n"
             "Provide a phased approach (3 phases) with SPECIFIC tools, patterns, "
             "and implementation steps. For each task include: estimated effort, "
             "required expertise level, and expected score impact."),
        ])

        chain = prompt_template | client
        result = chain.invoke({
            "maintainability": f"{current_scores.get('maintainability', 0):.1f}",
            "reliability": f"{current_scores.get('reliability', 0):.1f}",
            "scalability": f"{current_scores.get('scalability', 0):.1f}",
            "security": f"{current_scores.get('security', 0):.1f}",
        })
        return result.content

    except Exception as e:
        return f"Error generating roadmap: {str(e)}"
