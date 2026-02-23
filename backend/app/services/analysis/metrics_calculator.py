"""Basic code metrics analysis using radon (Python) + generic line counting."""

import os
import re
from pathlib import Path
from typing import Any, Dict

from app.core.constants import IGNORED_DIRECTORIES, ANALYZABLE_EXTENSIONS

# Extensions beyond ANALYZABLE_EXTENSIONS that we still want to count lines for
EXTRA_COUNTABLE_EXTENSIONS = (
    '.html', '.htm', '.css', '.scss', '.sass', '.less',
    '.json', '.xml', '.yaml', '.yml', '.toml',
    '.md', '.txt', '.sql', '.sh', '.bash', '.zsh',
    '.vue', '.svelte',
)

ALL_COUNTABLE_EXTENSIONS = ANALYZABLE_EXTENSIONS + EXTRA_COUNTABLE_EXTENSIONS

# Single-line comment patterns per language family
_COMMENT_PATTERNS = {
    'hash':   re.compile(r'^\s*#'),      # Python, Ruby, Shell, YAML
    'slash':  re.compile(r'^\s*//'),      # JS, TS, Java, Go, C, C++, Rust, Swift, Kotlin, Scala, PHP, C#
    'html':   re.compile(r'^\s*<!--'),    # HTML, XML
    'css':    re.compile(r'^\s*/\*'),     # CSS (single-line block comment start)
}

_EXT_COMMENT_STYLE = {
    '.py': 'hash', '.rb': 'hash', '.sh': 'hash', '.bash': 'hash', '.zsh': 'hash',
    '.yaml': 'hash', '.yml': 'hash', '.toml': 'hash',
    '.js': 'slash', '.jsx': 'slash', '.ts': 'slash', '.tsx': 'slash',
    '.java': 'slash', '.go': 'slash', '.rs': 'slash', '.swift': 'slash',
    '.kt': 'slash', '.scala': 'slash', '.php': 'slash', '.cs': 'slash',
    '.cpp': 'slash', '.c': 'slash', '.h': 'slash',
    '.vue': 'slash', '.svelte': 'slash',
    '.html': 'html', '.htm': 'html', '.xml': 'html',
    '.css': 'css', '.scss': 'css', '.sass': 'hash', '.less': 'css',
}


def analyze_code_metrics(repo_path: str) -> Dict[str, Any]:
    """Analyze basic code metrics: lines, files, languages.

    Uses radon for Python files (accurate AST-based metrics).
    Falls back to generic line counting for all other languages.
    """
    metrics = {
        "total_lines": 0,
        "code_lines": 0,
        "comment_lines": 0,
        "blank_lines": 0,
        "files_analyzed": 0,
        "languages": {},
        "functions": 0,
        "classes": 0,
    }

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]

        for file in files:
            ext = Path(file).suffix.lower()
            if ext not in ALL_COUNTABLE_EXTENSIONS:
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                if not content.strip():
                    continue

                # Try radon for Python files
                if ext == '.py':
                    file_metrics = _analyze_python(content)
                else:
                    file_metrics = _analyze_generic(content, ext)

                metrics["total_lines"] += file_metrics["total"]
                metrics["code_lines"] += file_metrics["code"]
                metrics["comment_lines"] += file_metrics["comments"]
                metrics["blank_lines"] += file_metrics["blank"]
                metrics["functions"] += file_metrics.get("functions", 0)
                metrics["classes"] += file_metrics.get("classes", 0)
                metrics["files_analyzed"] += 1

                lang = _ext_to_language(ext)
                metrics["languages"][lang] = metrics["languages"].get(lang, 0) + 1

            except Exception:
                continue

    # Compute avg_complexity placeholder (actual complexity comes from complexity_analyzer)
    if metrics["total_lines"] > 0:
        metrics["avg_complexity"] = round(
            metrics["code_lines"] / max(metrics["files_analyzed"], 1) / 10, 1
        )
    else:
        metrics["avg_complexity"] = 0

    return metrics


def _analyze_python(content: str) -> Dict[str, int]:
    """Use radon for accurate Python metrics."""
    try:
        from radon.raw import analyze
        raw = analyze(content)
        functions = content.count('\ndef ') + content.count('\n    def ')
        classes = content.count('\nclass ')
        return {
            "total": raw.loc,
            "code": raw.lloc,
            "comments": raw.comments,
            "blank": raw.blank,
            "functions": functions,
            "classes": classes,
        }
    except Exception:
        return _analyze_generic(content, '.py')


def _analyze_generic(content: str, ext: str) -> Dict[str, int]:
    """Generic line counting for non-Python files."""
    lines = content.splitlines()
    total = len(lines)
    blank = sum(1 for line in lines if not line.strip())
    comments = 0

    comment_style = _EXT_COMMENT_STYLE.get(ext)
    if comment_style:
        pattern = _COMMENT_PATTERNS[comment_style]
        comments = sum(1 for line in lines if pattern.match(line))

    code = total - blank - comments

    # Rough function/class counting for JS/TS/Java-family
    functions = 0
    classes = 0
    if ext in ('.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte'):
        functions = (
            len(re.findall(r'\bfunction\s+\w+', content)) +
            len(re.findall(r'(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\(', content)) +
            len(re.findall(r'\w+\s*\([^)]*\)\s*\{', content))
        )
        classes = len(re.findall(r'\bclass\s+\w+', content))
    elif ext in ('.java', '.cs', '.kt', '.scala'):
        functions = len(re.findall(r'(?:public|private|protected|static)\s+\w+\s+\w+\s*\(', content))
        classes = len(re.findall(r'\bclass\s+\w+', content))
    elif ext in ('.go',):
        functions = len(re.findall(r'\bfunc\s+', content))
    elif ext in ('.rs',):
        functions = len(re.findall(r'\bfn\s+\w+', content))
        classes = len(re.findall(r'\bstruct\s+\w+', content))
    elif ext in ('.rb',):
        functions = len(re.findall(r'\bdef\s+\w+', content))
        classes = len(re.findall(r'\bclass\s+\w+', content))
    elif ext in ('.php',):
        functions = len(re.findall(r'\bfunction\s+\w+', content))
        classes = len(re.findall(r'\bclass\s+\w+', content))

    return {
        "total": total,
        "code": max(code, 0),
        "comments": comments,
        "blank": blank,
        "functions": functions,
        "classes": classes,
    }


def _ext_to_language(ext: str) -> str:
    """Map file extension to display language name."""
    mapping = {
        '.py': 'Python', '.js': 'JavaScript', '.jsx': 'JavaScript',
        '.ts': 'TypeScript', '.tsx': 'TypeScript', '.java': 'Java',
        '.go': 'Go', '.rs': 'Rust', '.rb': 'Ruby', '.php': 'PHP',
        '.cs': 'C#', '.cpp': 'C++', '.c': 'C', '.h': 'C/C++',
        '.swift': 'Swift', '.kt': 'Kotlin', '.scala': 'Scala',
        '.html': 'HTML', '.htm': 'HTML', '.css': 'CSS',
        '.scss': 'SCSS', '.sass': 'Sass', '.less': 'Less',
        '.json': 'JSON', '.xml': 'XML', '.yaml': 'YAML', '.yml': 'YAML',
        '.toml': 'TOML', '.md': 'Markdown', '.txt': 'Text',
        '.sql': 'SQL', '.sh': 'Shell', '.bash': 'Shell', '.zsh': 'Shell',
        '.vue': 'Vue', '.svelte': 'Svelte',
    }
    return mapping.get(ext, ext)
