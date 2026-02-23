"""File and directory structure analysis."""

import os
from typing import Any, Dict
from app.core.constants import IGNORED_DIRECTORIES


def analyze_file_structure(repo_path: str) -> Dict[str, Any]:
    """Analyze file and directory structure."""
    structure = {
        "total_files": 0,
        "total_directories": 0,
        "largest_files": [],
    }

    skip_dirs = {'node_modules', 'venv', '__pycache__', '.git'}
    file_sizes = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        structure["total_directories"] += len(dirs)

        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                file_sizes.append({
                    "path": file_path.replace(repo_path, ""),
                    "size": size,
                })
                structure["total_files"] += 1
            except Exception:
                continue

    file_sizes.sort(key=lambda x: x["size"], reverse=True)
    structure["largest_files"] = file_sizes[:10]

    return structure
