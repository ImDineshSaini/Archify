"""Basic code metrics analysis using radon."""

import os
from pathlib import Path
from typing import Any, Dict
from radon.raw import analyze
from app.core.constants import IGNORED_DIRECTORIES, ANALYZABLE_EXTENSIONS


def analyze_code_metrics(repo_path: str) -> Dict[str, Any]:
    """Analyze basic code metrics using radon."""
    metrics = {
        "total_lines": 0,
        "code_lines": 0,
        "comment_lines": 0,
        "blank_lines": 0,
        "files_analyzed": 0,
        "languages": {},
    }

    skip_dirs = IGNORED_DIRECTORIES & {'.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build'}

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if file.endswith(ANALYZABLE_EXTENSIONS):
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

                        ext = Path(file).suffix
                        metrics["languages"][ext] = metrics["languages"].get(ext, 0) + 1
                except Exception:
                    continue

    return metrics
