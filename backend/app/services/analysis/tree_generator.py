"""Directory tree generation for AI analysis."""

from pathlib import Path
from app.core.constants import IGNORED_DIRECTORIES, IGNORED_FILES, TREE_MAX_DEPTH, TREE_MAX_FILES


def generate_directory_tree(repo_path: str, max_depth: int = TREE_MAX_DEPTH, max_files: int = TREE_MAX_FILES) -> str:
    """Generate a directory tree structure for AI analysis."""
    tree_lines = []
    file_count = 0

    def should_skip(name: str) -> bool:
        return name in IGNORED_DIRECTORIES or name in IGNORED_FILES

    def build_tree(path: Path, prefix: str = "", depth: int = 0):
        nonlocal file_count

        if depth > max_depth or file_count > max_files:
            return

        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

            for i, entry in enumerate(entries):
                if should_skip(entry.name):
                    continue

                is_last = i == len(entries) - 1
                current_prefix = "└── " if is_last else "├── "
                tree_lines.append(f"{prefix}{current_prefix}{entry.name}")

                if entry.is_dir():
                    extension = "    " if is_last else "│   "
                    build_tree(entry, prefix + extension, depth + 1)
                else:
                    file_count += 1
                    if file_count > max_files:
                        tree_lines.append(f"{prefix}    ... (truncated, too many files)")
                        return
        except PermissionError:
            pass

    repo_name = Path(repo_path).name
    tree_lines.append(f"{repo_name}/")
    build_tree(Path(repo_path))

    return "\n".join(tree_lines)
