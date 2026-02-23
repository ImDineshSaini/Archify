"""Architecture pattern detection and SOLID principles analysis."""

import json
from pathlib import Path
from typing import Any, Dict


def detect_architecture_patterns(repo_path: str) -> Dict[str, Any]:
    """Detect common architecture patterns with deep analysis."""
    patterns = {
        "detected_patterns": [],
        "project_type": "unknown",
        "language": "unknown",
        "frameworks": [],
        "design_patterns": [],
        "solid_compliance": {},
        "architectural_insights": [],
    }

    path_obj = Path(repo_path)

    _detect_language_and_frameworks(path_obj, patterns)
    _detect_architecture_patterns(path_obj, patterns)
    _analyze_solid_principles(path_obj, patterns)

    return patterns


def _detect_language_and_frameworks(path_obj: Path, patterns: Dict[str, Any]) -> None:
    """Detect programming language and frameworks."""
    # Node.js / JavaScript / TypeScript
    if (path_obj / "package.json").exists():
        patterns["project_type"] = "javascript/nodejs"
        patterns["language"] = "JavaScript/TypeScript"
        with open(path_obj / "package.json", 'r') as f:
            try:
                pkg = json.load(f)
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

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

                if "redux" in deps or "@reduxjs/toolkit" in deps:
                    patterns["design_patterns"].append("Redux (Flux Pattern)")
                if "mobx" in deps:
                    patterns["design_patterns"].append("MobX (Observer Pattern)")
            except Exception:
                pass

    # Python
    if (path_obj / "requirements.txt").exists() or (path_obj / "setup.py").exists() or (path_obj / "pyproject.toml").exists():
        patterns["project_type"] = "python"
        patterns["language"] = "Python"

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
                except Exception:
                    pass

    # Java
    if (path_obj / "pom.xml").exists() or (path_obj / "build.gradle").exists():
        patterns["project_type"] = "java"
        patterns["language"] = "Java"

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
            except Exception:
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
        except Exception:
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
        except Exception:
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
        except Exception:
            pass


def _detect_architecture_patterns(path_obj: Path, patterns: Dict[str, Any]) -> None:
    """Detect architecture patterns from directory structure."""
    # Component-based architecture
    if (path_obj / "src" / "components").exists() or (path_obj / "components").exists():
        patterns["detected_patterns"].append("Component-based Architecture")

    # MVC pattern
    has_controllers = (path_obj / "src" / "controllers").exists() or (path_obj / "controllers").exists() or (path_obj / "app" / "controllers").exists()
    has_models = (path_obj / "src" / "models").exists() or (path_obj / "models").exists() or (path_obj / "app" / "models").exists()

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
    if (path_obj / "src" / "commands").exists() and (path_obj / "src" / "queries").exists():
        patterns["design_patterns"].append("CQRS Pattern")

    # Monorepo
    if (path_obj / "packages").exists() or (path_obj / "apps").exists():
        patterns["detected_patterns"].append("Monorepo Structure")

    # Docker support
    if (path_obj / "Dockerfile").exists():
        patterns["detected_patterns"].append("Containerized (Docker)")


def _analyze_solid_principles(path_obj: Path, patterns: Dict[str, Any]) -> None:
    """Analyze SOLID principles compliance."""
    if patterns.get("design_patterns") and "Service Layer Pattern" in patterns["design_patterns"]:
        patterns["solid_compliance"]["single_responsibility"] = "Likely - Service layer pattern detected"

    if (path_obj / "src" / "interfaces").exists() or (path_obj / "interfaces").exists():
        patterns["solid_compliance"]["open_closed"] = "Likely - Interface-based design detected"

    if patterns.get("language") in ["Java", "TypeScript", "Go"]:
        patterns["solid_compliance"]["interface_segregation"] = "Check interfaces folder for specific contracts"

    if "Repository Pattern" in patterns.get("design_patterns", []):
        patterns["solid_compliance"]["dependency_inversion"] = "Strong - Repository pattern provides abstraction"
    elif "Dependency Injection" in patterns.get("design_patterns", []):
        patterns["solid_compliance"]["dependency_inversion"] = "Strong - DI framework detected"
