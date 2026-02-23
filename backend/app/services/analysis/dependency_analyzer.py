"""Project dependency analysis."""

import json
from pathlib import Path
from typing import Any, Dict


def analyze_dependencies(repo_path: str) -> Dict[str, Any]:
    """Analyze project dependencies."""
    deps = {
        "total_dependencies": 0,
        "dependencies_list": [],
        "outdated_warning": False,
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
            except Exception:
                pass

    # Python
    elif (path_obj / "requirements.txt").exists():
        with open(path_obj / "requirements.txt", 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            deps["total_dependencies"] = len(lines)
            deps["dependencies_list"] = [line.split('==')[0].split('>=')[0] for line in lines]

    return deps
