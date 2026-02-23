"""Cache utilities for LLM response caching and content-based invalidation."""

import hashlib
import logging
import os

from app.core.constants import ANALYZABLE_EXTENSIONS, IGNORED_DIRECTORIES

logger = logging.getLogger(__name__)


def compute_repo_hash(repo_path: str) -> str:
    """Compute a SHA-256 hash of all source files in a repository.

    Used for content-based cache invalidation: if the hash matches
    a previous analysis, LLM calls can be skipped.
    """
    hasher = hashlib.sha256()

    for root, dirs, files in sorted(os.walk(repo_path)):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRECTORIES)

        for filename in sorted(files):
            ext = os.path.splitext(filename)[1].lower()
            if ext not in ANALYZABLE_EXTENSIONS:
                continue

            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, repo_path)

            try:
                with open(filepath, "rb") as f:
                    content = f.read()
                hasher.update(rel_path.encode("utf-8"))
                hasher.update(content)
            except (OSError, IOError):
                continue

    return hasher.hexdigest()


def setup_llm_cache(cache_dir: str = "/tmp/archify_llm_cache") -> None:
    """Initialize SQLite-based LLM response cache.

    Caches by exact prompt+model. Same repo re-analyzed without code
    changes will hit cache for all LLM calls.
    """
    try:
        from langchain_community.cache import SQLiteCache
        from langchain_core.globals import set_llm_cache

        os.makedirs(cache_dir, exist_ok=True)
        db_path = os.path.join(cache_dir, "llm_cache.db")
        set_llm_cache(SQLiteCache(database_path=db_path))
        logger.info("LLM cache initialized at %s", db_path)
    except ImportError as e:
        logger.warning("LLM caching unavailable (missing dependency): %s", e)
    except Exception as e:
        logger.warning("Failed to initialize LLM cache: %s", e)
