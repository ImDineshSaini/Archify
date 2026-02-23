"""Code embedding service for RAG-powered analysis.

Walks a repository, reads source files, splits them by language-aware
boundaries, and embeds into an ephemeral FAISS vector store.
"""

import logging
import os
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

from app.core.constants import ANALYZABLE_EXTENSIONS, IGNORED_DIRECTORIES

logger = logging.getLogger(__name__)

# Map file extensions to LangChain Language enum for smart splitting
_EXT_TO_LANGUAGE = {
    ".py": Language.PYTHON,
    ".js": Language.JS,
    ".jsx": Language.JS,
    ".ts": Language.TS,
    ".tsx": Language.TS,
    ".java": Language.JAVA,
    ".go": Language.GO,
    ".rs": Language.RUST,
    ".rb": Language.RUBY,
    ".php": Language.PHP,
    ".scala": Language.SCALA,
    ".swift": Language.SWIFT,
    ".kt": Language.KOTLIN,
    ".cs": Language.CSHARP,
    ".cpp": Language.CPP,
    ".c": Language.CPP,
    ".h": Language.CPP,
}

# Limits to keep embedding fast and memory-bounded
MAX_FILE_SIZE_BYTES = 100_000  # Skip files > 100KB
MAX_FILES = 500
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200


def embed_repository(repo_path: str) -> Optional[FAISS]:
    """Embed source files from a repository into an in-memory FAISS store.

    Returns None if no embeddable files are found or embedding fails.
    The vector store is ephemeral — discarded after analysis.
    """
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings

        documents = _collect_documents(repo_path)
        if not documents:
            logger.info("No source files found for embedding in %s", repo_path)
            return None

        chunks = _split_documents(documents)
        if not chunks:
            logger.info("No chunks produced after splitting")
            return None

        logger.info(
            "Embedding %d chunks from %d files in %s",
            len(chunks), len(documents), repo_path,
        )

        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )
        vector_store = FAISS.from_documents(chunks, embeddings)
        return vector_store

    except ImportError as e:
        logger.warning(
            "RAG dependencies not available (sentence-transformers / faiss-cpu): %s", e,
        )
        return None
    except Exception as e:
        logger.error("Failed to embed repository: %s", e)
        return None


def _collect_documents(repo_path: str) -> list[Document]:
    """Walk the repository and collect source file contents as Documents."""
    documents = []
    file_count = 0

    for root, dirs, files in os.walk(repo_path):
        # Prune ignored directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]

        for filename in files:
            if file_count >= MAX_FILES:
                break

            ext = os.path.splitext(filename)[1].lower()
            if ext not in ANALYZABLE_EXTENSIONS:
                continue

            filepath = os.path.join(root, filename)

            try:
                file_size = os.path.getsize(filepath)
                if file_size > MAX_FILE_SIZE_BYTES or file_size == 0:
                    continue

                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                rel_path = os.path.relpath(filepath, repo_path)
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "source": rel_path,
                        "extension": ext,
                        "size": file_size,
                    },
                ))
                file_count += 1

            except (OSError, UnicodeDecodeError):
                continue

    return documents


def _split_documents(documents: list[Document]) -> list[Document]:
    """Split documents using language-aware text splitters."""
    all_chunks = []

    # Group documents by language for language-aware splitting
    by_language: dict[Optional[Language], list[Document]] = {}
    for doc in documents:
        ext = doc.metadata.get("extension", "")
        lang = _EXT_TO_LANGUAGE.get(ext)
        by_language.setdefault(lang, []).append(doc)

    for lang, docs in by_language.items():
        if lang is not None:
            splitter = RecursiveCharacterTextSplitter.from_language(
                language=lang,
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
            )
        else:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
            )

        chunks = splitter.split_documents(docs)
        all_chunks.extend(chunks)

    return all_chunks
