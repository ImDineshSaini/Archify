"""Centralized constants for the Archify application."""

# LLM Defaults
DEFAULT_CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
DEFAULT_OPENAI_MODEL = "gpt-4-turbo-preview"
DEFAULT_LLM_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096
DEFAULT_AZURE_API_VERSION = "2024-02-01"

# Analysis
COMPLEXITY_THRESHOLD = 15
TREE_MAX_DEPTH = 4
TREE_MAX_FILES = 200
IGNORED_DIRECTORIES = frozenset({
    '.git', 'node_modules', 'venv', '__pycache__', 'dist',
    'build', '.next', '.venv', 'vendor', 'target', 'bin', 'obj',
})
IGNORED_FILES = frozenset({'.DS_Store', 'package-lock.json', 'yarn.lock', '.env'})
ANALYZABLE_EXTENSIONS = (
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs',
    '.rb', '.php', '.cs', '.cpp', '.c', '.h', '.swift', '.kt', '.scala',
)

# Git Providers
GITHUB_API_BASE_URL = "https://api.github.com"
GITLAB_API_BASE_URL = "https://gitlab.com/api/v4"

# LLM Prompt truncation limits
TREE_TRUNCATION_LIMIT = 3000
NFR_TREE_TRUNCATION_LIMIT = 2000
SYNTHESIS_SECTION_LIMIT = 1500
