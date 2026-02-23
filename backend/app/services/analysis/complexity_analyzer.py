"""Code complexity analysis using lizard."""

from typing import Any, Dict
import lizard
from app.core.constants import COMPLEXITY_THRESHOLD


def analyze_complexity(repo_path: str) -> Dict[str, Any]:
    """Analyze code complexity using lizard."""
    complexity_data = {
        "average_complexity": 0,
        "max_complexity": 0,
        "high_complexity_functions": [],
        "total_functions": 0,
    }

    try:
        analysis_results = list(lizard.analyze_files([repo_path]))

        complexities = []
        for file_analysis in analysis_results:
            for func in file_analysis.function_list:
                complexity_data["total_functions"] += 1
                complexities.append(func.cyclomatic_complexity)

                if func.cyclomatic_complexity > COMPLEXITY_THRESHOLD:
                    complexity_data["high_complexity_functions"].append({
                        "name": func.name,
                        "complexity": func.cyclomatic_complexity,
                        "lines": func.nloc,
                        "file": func.filename,
                    })

        if complexities:
            complexity_data["average_complexity"] = sum(complexities) / len(complexities)
            complexity_data["max_complexity"] = max(complexities)

    except Exception as e:
        print(f"Complexity analysis error: {e}")
        import traceback
        traceback.print_exc()

    return complexity_data
