"""Code analyzer orchestrator -- delegates to app.services.analysis submodules."""

from typing import Any, Dict
from app.services.analysis.metrics_calculator import analyze_code_metrics
from app.services.analysis.complexity_analyzer import analyze_complexity
from app.services.analysis.architecture_detector import detect_architecture_patterns
from app.services.analysis.dependency_analyzer import analyze_dependencies
from app.services.analysis.file_structure import analyze_file_structure
from app.services.analysis.score_calculator import calculate_scores
from app.services.analysis.tree_generator import generate_directory_tree
from app.services.nfr_analyzer import NFRAnalyzer


class CodeAnalyzer:
    """Analyzes code quality, complexity, and architecture."""

    def __init__(self):
        self.nfr_analyzer = NFRAnalyzer()

    def analyze_repository(
        self, repo_path: str, use_ai_enhancement: bool = False, llm_service=None
    ) -> Dict[str, Any]:
        """Main method to analyze a repository."""
        try:
            results = {
                "code_metrics": analyze_code_metrics(repo_path),
                "complexity": analyze_complexity(repo_path),
                "architecture": detect_architecture_patterns(repo_path),
                "dependencies": analyze_dependencies(repo_path),
                "file_structure": analyze_file_structure(repo_path),
            }

            results["scores"] = calculate_scores(results)

            if use_ai_enhancement and llm_service:
                try:
                    directory_tree = generate_directory_tree(repo_path)
                    results["directory_tree"] = directory_tree

                    results["ai_architecture_analysis"] = llm_service.analyze_architecture_from_tree(
                        directory_tree=directory_tree,
                        basic_analysis=results,
                    )

                    results["ai_nfr_refinement"] = llm_service.refine_nfr_scores(
                        directory_tree=directory_tree,
                        basic_analysis=results,
                    )
                except Exception as e:
                    print(f"AI enhancement failed: {e}, continuing with basic analysis")
                    results["ai_enhancement_error"] = str(e)

            nfr_analysis = self.nfr_analyzer.analyze_nfr(results, results["architecture"])
            results["nfr_analysis"] = nfr_analysis

            return results
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")
