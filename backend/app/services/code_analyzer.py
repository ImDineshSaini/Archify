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
        """Detect common architecture patterns with deep analysis"""
        patterns = {
            "detected_patterns": [],
            "project_type": "unknown",
            "language": "unknown",
            "frameworks": [],
            "design_patterns": [],
            "solid_compliance": {},
            "architectural_insights": []
        }

        # Check for common files and directories
        path_obj = Path(repo_path)

        # === LANGUAGE & FRAMEWORK DETECTION ===

        # Node.js / JavaScript / TypeScript
        if (path_obj / "package.json").exists():
            patterns["project_type"] = "javascript/nodejs"
            patterns["language"] = "JavaScript/TypeScript"
            with open(path_obj / "package.json", 'r') as f:
                try:
                    pkg = json.load(f)
                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

                    # Frontend frameworks
                    if "react" in deps:
                        patterns["frameworks"].append("React")
                        patterns["design_patterns"].append("Component Pattern")
                    if "vue" in deps:
                        patterns["frameworks"].append("Vue.js")
                        patterns["design_patterns"].append("MVVM Pattern")
                    if "angular" in deps or "@angular/core" in deps:
                        patterns["frameworks"].append("Angular")
                        patterns["design_patterns"].append("MVC Pattern")
                    if "next" in deps:
                        patterns["frameworks"].append("Next.js")
                        patterns["detected_patterns"].append("Server-Side Rendering")
                    if "svelte" in deps:
                        patterns["frameworks"].append("Svelte")

                    # Backend frameworks
                    if "express" in deps:
                        patterns["frameworks"].append("Express.js")
                    if "nestjs" in deps or "@nestjs/core" in deps:
                        patterns["frameworks"].append("NestJS")
                        patterns["design_patterns"].append("Dependency Injection")
                        patterns["architectural_insights"].append("NestJS follows Angular-style architecture with modules, controllers, and services")
                    if "fastify" in deps:
                        patterns["frameworks"].append("Fastify")
                    if "koa" in deps:
                        patterns["frameworks"].append("Koa")

                    # State management
                    if "redux" in deps or "@reduxjs/toolkit" in deps:
                        patterns["design_patterns"].append("Redux (Flux Pattern)")
                    if "mobx" in deps:
                        patterns["design_patterns"].append("MobX (Observer Pattern)")
                except:
                    pass

        # Python
        if (path_obj / "requirements.txt").exists() or (path_obj / "setup.py").exists() or (path_obj / "pyproject.toml").exists():
            patterns["project_type"] = "python"
            patterns["language"] = "Python"

            # Check for Python frameworks
            requirements_files = [path_obj / "requirements.txt", path_obj / "setup.py"]
            for req_file in requirements_files:
                if req_file.exists():
                    try:
                        content = req_file.read_text().lower()
                        if "django" in content:
                            patterns["frameworks"].append("Django")
                            patterns["design_patterns"].append("MTV (Model-Template-View)")
                            patterns["architectural_insights"].append("Django follows MTV architecture with ORM, middleware, and app-based structure")
                        if "flask" in content:
                            patterns["frameworks"].append("Flask")
                            patterns["design_patterns"].append("Microframework Pattern")
                        if "fastapi" in content:
                            patterns["frameworks"].append("FastAPI")
                            patterns["design_patterns"].append("Dependency Injection")
                            patterns["architectural_insights"].append("FastAPI uses async/await with Pydantic validation")
                        if "pyramid" in content:
                            patterns["frameworks"].append("Pyramid")
                    except:
                        pass

        # Java
        if (path_obj / "pom.xml").exists() or (path_obj / "build.gradle").exists():
            patterns["project_type"] = "java"
            patterns["language"] = "Java"

            # Check for Spring Framework
            if (path_obj / "pom.xml").exists():
                try:
                    content = (path_obj / "pom.xml").read_text()
                    if "spring" in content.lower():
                        patterns["frameworks"].append("Spring Framework")
                        patterns["design_patterns"].append("Dependency Injection")
                        patterns["design_patterns"].append("MVC Pattern")
                        patterns["architectural_insights"].append("Spring uses IoC container with dependency injection")
                    if "springboot" in content.lower() or "spring-boot" in content.lower():
                        patterns["frameworks"].append("Spring Boot")
                except:
                    pass

        # Ruby / Rails
        if (path_obj / "Gemfile").exists():
            patterns["project_type"] = "ruby"
            patterns["language"] = "Ruby"
            try:
                gemfile_content = (path_obj / "Gemfile").read_text().lower()
                if "rails" in gemfile_content:
                    patterns["frameworks"].append("Ruby on Rails")
                    patterns["design_patterns"].append("MVC Pattern")
                    patterns["design_patterns"].append("Active Record Pattern")
                    patterns["design_patterns"].append("Convention over Configuration")
                    patterns["architectural_insights"].append("Rails follows MVC with Active Record ORM and RESTful routing")
                if "sinatra" in gemfile_content:
                    patterns["frameworks"].append("Sinatra")
            except:
                pass

        # Go
        if (path_obj / "go.mod").exists():
            patterns["project_type"] = "go"
            patterns["language"] = "Go"
            try:
                go_mod_content = (path_obj / "go.mod").read_text().lower()
                if "gin" in go_mod_content:
                    patterns["frameworks"].append("Gin")
                if "echo" in go_mod_content:
                    patterns["frameworks"].append("Echo")
                if "fiber" in go_mod_content:
                    patterns["frameworks"].append("Fiber")
            except:
                pass

        # Rust
        if (path_obj / "Cargo.toml").exists():
            patterns["project_type"] = "rust"
            patterns["language"] = "Rust"
            try:
                cargo_content = (path_obj / "Cargo.toml").read_text().lower()
                if "actix" in cargo_content:
                    patterns["frameworks"].append("Actix-web")
                if "rocket" in cargo_content:
                    patterns["frameworks"].append("Rocket")
            except:
                pass

        # === ARCHITECTURE PATTERN DETECTION ===

        # Component-based architecture
        if (path_obj / "src" / "components").exists() or (path_obj / "components").exists():
            patterns["detected_patterns"].append("Component-based Architecture")

        # MVC pattern
        has_controllers = (path_obj / "src" / "controllers").exists() or (path_obj / "controllers").exists() or (path_obj / "app" / "controllers").exists()
        has_models = (path_obj / "src" / "models").exists() or (path_obj / "models").exists() or (path_obj / "app" / "models").exists()
        has_views = (path_obj / "src" / "views").exists() or (path_obj / "views").exists() or (path_obj / "app" / "views").exists()

        if has_controllers and has_models:
            patterns["detected_patterns"].append("MVC Pattern")

        # Repository Pattern
        if (path_obj / "src" / "repositories").exists() or (path_obj / "repositories").exists():
            patterns["design_patterns"].append("Repository Pattern")
            patterns["solid_compliance"]["dependency_inversion"] = "Detected - Repository abstraction"

        # Service Layer
        if (path_obj / "src" / "services").exists() or (path_obj / "services").exists():
            patterns["design_patterns"].append("Service Layer Pattern")
            patterns["solid_compliance"]["single_responsibility"] = "Likely - Services separate business logic"

        # Microservices architecture
        if (path_obj / "microservices").exists() or len(list(path_obj.glob("**/docker-compose.yml"))) > 0:
            patterns["detected_patterns"].append("Microservices Architecture")
            patterns["architectural_insights"].append("Microservices detected - ensures scalability and independent deployment")

        # Hexagonal/Clean Architecture
        has_domain = (path_obj / "src" / "domain").exists() or (path_obj / "domain").exists()
        has_infrastructure = (path_obj / "src" / "infrastructure").exists() or (path_obj / "infrastructure").exists()
        has_application = (path_obj / "src" / "application").exists() or (path_obj / "application").exists()

        if has_domain and (has_infrastructure or has_application):
            patterns["detected_patterns"].append("Hexagonal/Clean Architecture")
            patterns["solid_compliance"]["dependency_inversion"] = "Strong - Domain independent of infrastructure"
            patterns["architectural_insights"].append("Clean Architecture promotes testability and maintainability through separation of concerns")

        # API patterns
        if (path_obj / "src" / "api").exists() or (path_obj / "api").exists():
            patterns["detected_patterns"].append("API-first Architecture")

        # Event-driven
        if (path_obj / "src" / "events").exists() or (path_obj / "events").exists():
            patterns["design_patterns"].append("Event-driven Pattern")
            patterns["architectural_insights"].append("Event-driven architecture enables loose coupling and asynchronous processing")

        # CQRS
        if ((path_obj / "src" / "commands").exists() and (path_obj / "src" / "queries").exists()):
            patterns["design_patterns"].append("CQRS Pattern")

        # Monorepo
        if (path_obj / "packages").exists() or (path_obj / "apps").exists():
            patterns["detected_patterns"].append("Monorepo Structure")

        # Docker support
        if (path_obj / "Dockerfile").exists():
            patterns["detected_patterns"].append("Containerized (Docker)")

        # === SOLID PRINCIPLES DETECTION ===
        self._analyze_solid_principles(path_obj, patterns)

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

    def _analyze_solid_principles(self, path_obj: Path, patterns: Dict[str, Any]) -> None:
        """Analyze SOLID principles compliance"""
        # This is a heuristic-based analysis

        # Single Responsibility Principle
        if patterns.get("design_patterns") and "Service Layer Pattern" in patterns["design_patterns"]:
            patterns["solid_compliance"]["single_responsibility"] = "Likely - Service layer pattern detected"

        # Open/Closed Principle
        if (path_obj / "src" / "interfaces").exists() or (path_obj / "interfaces").exists():
            patterns["solid_compliance"]["open_closed"] = "Likely - Interface-based design detected"

        # Liskov Substitution Principle
        # Would require deeper code analysis

        # Interface Segregation Principle
        if patterns.get("language") in ["Java", "TypeScript", "Go"]:
            patterns["solid_compliance"]["interface_segregation"] = "Check interfaces folder for specific contracts"

        # Dependency Inversion Principle
        if "Repository Pattern" in patterns.get("design_patterns", []):
            patterns["solid_compliance"]["dependency_inversion"] = "Strong - Repository pattern provides abstraction"
        elif "Dependency Injection" in patterns.get("design_patterns", []):
            patterns["solid_compliance"]["dependency_inversion"] = "Strong - DI framework detected"

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

        # Bonus for good architecture
        architecture = results.get("architecture", {})
        if architecture.get("solid_compliance"):
            maintainability += 5  # Bonus for SOLID compliance
        if "Clean Architecture" in architecture.get("detected_patterns", []) or "Hexagonal/Clean Architecture" in architecture.get("detected_patterns", []):
            maintainability += 10

        scores["maintainability"] = min(100, maintainability)

        # Reliability score (based on code quality indicators)
        code_metrics = results.get("code_metrics", {})
        total_lines = code_metrics.get("total_lines", 1)
        comment_ratio = code_metrics.get("comment_lines", 0) / max(total_lines, 1) * 100
        reliability = 50 + (comment_ratio * 2)  # More comments = better documentation

        # Bonus for design patterns
        if architecture.get("design_patterns"):
            reliability += min(10, len(architecture["design_patterns"]) * 2)

        scores["reliability"] = min(100, reliability)

        # Scalability score (based on architecture)
        scalability = 60  # Base score
        if "Microservices Architecture" in architecture.get("detected_patterns", []):
            scalability += 20
        if "Component-based Architecture" in architecture.get("detected_patterns", []):
            scalability += 10
        if "Event-driven Pattern" in architecture.get("design_patterns", []):
            scalability += 10
        if "CQRS Pattern" in architecture.get("design_patterns", []):
            scalability += 5
        scores["scalability"] = min(100, scalability)

        # Security score (based on framework and patterns)
        security = 60.0  # Base score

        # Modern frameworks often have better security
        frameworks = architecture.get("frameworks", [])
        if any(fw in frameworks for fw in ["FastAPI", "NestJS", "Spring Boot", "Django"]):
            security += 10

        # Bonus for dependency injection (reduces hardcoded credentials)
        if "Dependency Injection" in architecture.get("design_patterns", []):
            security += 5

        scores["security"] = min(100, security)

        # Overall score
        scores["overall"] = sum(scores.values()) / len(scores)

        return scores
