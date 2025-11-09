import os
import json
from pathlib import Path
from typing import Dict, Any, List
import radon.complexity as radon_cc
import radon.metrics as radon_metrics
from radon.raw import analyze
import lizard
from git import Repo
import tempfile
import shutil


class CodeAnalyzer:
    """Analyzes code quality, complexity, and architecture"""

    def __init__(self):
        self.temp_dir = None

    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """
        Main method to analyze a repository
        Returns comprehensive metrics and insights
        """
        try:
            results = {
                "code_metrics": self._analyze_code_metrics(repo_path),
                "complexity": self._analyze_complexity(repo_path),
                "architecture": self._detect_architecture_patterns(repo_path),
                "dependencies": self._analyze_dependencies(repo_path),
                "file_structure": self._analyze_file_structure(repo_path),
            }

            # Calculate scores
            scores = self._calculate_scores(results)
            results["scores"] = scores

            return results
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")

    def _analyze_code_metrics(self, repo_path: str) -> Dict[str, Any]:
        """Analyze basic code metrics using radon"""
        metrics = {
            "total_lines": 0,
            "code_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "files_analyzed": 0,
            "languages": {},
        }

        for root, dirs, files in os.walk(repo_path):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build']]

            for file in files:
                if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            raw_metrics = analyze(content)

                            metrics["total_lines"] += raw_metrics.loc
                            metrics["code_lines"] += raw_metrics.lloc
                            metrics["comment_lines"] += raw_metrics.comments
                            metrics["blank_lines"] += raw_metrics.blank
                            metrics["files_analyzed"] += 1

                            # Track language
                            ext = Path(file).suffix
                            metrics["languages"][ext] = metrics["languages"].get(ext, 0) + 1
                    except:
                        continue

        return metrics

    def _analyze_complexity(self, repo_path: str) -> Dict[str, Any]:
        """Analyze code complexity using lizard"""
        complexity_data = {
            "average_complexity": 0,
            "max_complexity": 0,
            "high_complexity_functions": [],
        }

        try:
            analysis = lizard.analyze_files([repo_path])

            complexities = []
            for func in analysis.function_list:
                complexities.append(func.cyclomatic_complexity)

                if func.cyclomatic_complexity > 15:  # High complexity threshold
                    complexity_data["high_complexity_functions"].append({
                        "name": func.name,
                        "complexity": func.cyclomatic_complexity,
                        "lines": func.nloc,
                        "file": func.filename
                    })

            if complexities:
                complexity_data["average_complexity"] = sum(complexities) / len(complexities)
                complexity_data["max_complexity"] = max(complexities)

        except Exception as e:
            print(f"Complexity analysis error: {e}")

        return complexity_data

    def _detect_architecture_patterns(self, repo_path: str) -> Dict[str, Any]:
        """Detect common architecture patterns"""
        patterns = {
            "detected_patterns": [],
            "project_type": "unknown",
            "frameworks": [],
        }

        # Check for common files and directories
        path_obj = Path(repo_path)

        # Check for web frameworks
        if (path_obj / "package.json").exists():
            patterns["project_type"] = "javascript"
            with open(path_obj / "package.json", 'r') as f:
                try:
                    pkg = json.load(f)
                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

                    if "react" in deps:
                        patterns["frameworks"].append("React")
                    if "vue" in deps:
                        patterns["frameworks"].append("Vue")
                    if "angular" in deps or "@angular/core" in deps:
                        patterns["frameworks"].append("Angular")
                    if "next" in deps:
                        patterns["frameworks"].append("Next.js")
                    if "express" in deps:
                        patterns["frameworks"].append("Express")
                except:
                    pass

        if (path_obj / "requirements.txt").exists() or (path_obj / "setup.py").exists():
            patterns["project_type"] = "python"

        if (path_obj / "pom.xml").exists() or (path_obj / "build.gradle").exists():
            patterns["project_type"] = "java"

        if (path_obj / "go.mod").exists():
            patterns["project_type"] = "go"

        if (path_obj / "Cargo.toml").exists():
            patterns["project_type"] = "rust"

        # Detect architecture patterns
        if (path_obj / "src" / "components").exists():
            patterns["detected_patterns"].append("Component-based architecture")

        if (path_obj / "src" / "controllers").exists() and (path_obj / "src" / "models").exists():
            patterns["detected_patterns"].append("MVC pattern")

        if (path_obj / "microservices").exists() or len(list(path_obj.glob("**/docker-compose.yml"))) > 0:
            patterns["detected_patterns"].append("Microservices architecture")

        return patterns

    def _analyze_dependencies(self, repo_path: str) -> Dict[str, Any]:
        """Analyze project dependencies"""
        deps = {
            "total_dependencies": 0,
            "dependencies_list": [],
            "outdated_warning": False
        }

        path_obj = Path(repo_path)

        # JavaScript/Node.js
        if (path_obj / "package.json").exists():
            with open(path_obj / "package.json", 'r') as f:
                try:
                    pkg = json.load(f)
                    all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                    deps["total_dependencies"] = len(all_deps)
                    deps["dependencies_list"] = list(all_deps.keys())
                except:
                    pass

        # Python
        elif (path_obj / "requirements.txt").exists():
            with open(path_obj / "requirements.txt", 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                deps["total_dependencies"] = len(lines)
                deps["dependencies_list"] = [line.split('==')[0].split('>=')[0] for line in lines]

        return deps

    def _analyze_file_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze file and directory structure"""
        structure = {
            "total_files": 0,
            "total_directories": 0,
            "largest_files": [],
        }

        file_sizes = []

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__']]
            structure["total_directories"] += len(dirs)

            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    file_sizes.append({
                        "path": file_path.replace(repo_path, ""),
                        "size": size
                    })
                    structure["total_files"] += 1
                except:
                    continue

        # Get top 10 largest files
        file_sizes.sort(key=lambda x: x["size"], reverse=True)
        structure["largest_files"] = file_sizes[:10]

        return structure

    def _calculate_scores(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality scores based on analysis results"""
        scores = {
            "maintainability": 0.0,
            "reliability": 0.0,
            "scalability": 0.0,
            "security": 0.0,
            "overall": 0.0,
        }

        # Maintainability score (based on complexity and code metrics)
        complexity = results.get("complexity", {})
        avg_complexity = complexity.get("average_complexity", 0)
        maintainability = max(0, 100 - (avg_complexity * 3))  # Lower complexity = better
        scores["maintainability"] = min(100, maintainability)

        # Reliability score (based on code quality indicators)
        code_metrics = results.get("code_metrics", {})
        total_lines = code_metrics.get("total_lines", 1)
        comment_ratio = code_metrics.get("comment_lines", 0) / max(total_lines, 1) * 100
        reliability = 50 + (comment_ratio * 2)  # More comments = better documentation
        scores["reliability"] = min(100, reliability)

        # Scalability score (based on architecture)
        architecture = results.get("architecture", {})
        scalability = 60  # Base score
        if "Microservices architecture" in architecture.get("detected_patterns", []):
            scalability += 20
        if "Component-based architecture" in architecture.get("detected_patterns", []):
            scalability += 10
        scores["scalability"] = min(100, scalability)

        # Security score (placeholder - would need actual security scanning)
        scores["security"] = 70.0  # Default score

        # Overall score
        scores["overall"] = sum(scores.values()) / len(scores)

        return scores
