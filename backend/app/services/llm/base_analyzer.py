"""Base class for LLM-powered deep analysis layers."""

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

logger = logging.getLogger(__name__)


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Extract a JSON object from LLM response text (fallback parser).

    Handles: direct JSON, markdown code fences, and JSON embedded in prose.
    Returns None if no valid JSON object can be extracted.
    """
    if not text or not isinstance(text, str):
        return None

    # 1. Try direct parse
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, TypeError):
        pass

    # 2. Strip markdown code fences
    fence_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?\s*```', text)
    if fence_match:
        try:
            result = json.loads(fence_match.group(1))
            if isinstance(result, dict):
                return result
        except (json.JSONDecodeError, TypeError):
            pass

    # 3. Find outermost { ... } block
    start = text.find('{')
    if start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    try:
                        result = json.loads(text[start:i + 1])
                        if isinstance(result, dict):
                            return result
                    except (json.JSONDecodeError, TypeError):
                        pass
                    break

    return None


class BaseLLMAnalyzer(ABC):
    """Template method pattern for deep analysis layers.

    Primary path: ChatPromptTemplate | client.with_structured_output(Schema)
    Fallback path: raw invoke → extract_json() → _get_fallback_response()
    """

    def analyze(
        self,
        client,
        directory_tree: str,
        basic_analysis: Dict[str, Any],
        vector_store=None,
    ) -> Dict[str, Any]:
        """Run analysis using structured output with unstructured fallback."""
        try:
            return self._structured_analyze(client, directory_tree, basic_analysis, vector_store)
        except Exception as e:
            logger.warning(
                "%s structured output failed, trying fallback: %s",
                self._get_layer_name(), e,
            )
            return self._fallback_unstructured(client, directory_tree, basic_analysis, vector_store)

    # ── Primary path: structured output ─────────────────────────────────

    def _structured_analyze(
        self,
        client,
        directory_tree: str,
        basic_analysis: Dict[str, Any],
        vector_store=None,
    ) -> Dict[str, Any]:
        """Use ChatPromptTemplate + with_structured_output for guaranteed schema."""
        schema = self._get_output_schema()
        prompt_template = self._get_prompt_template()
        variables = self._get_prompt_variables(directory_tree, basic_analysis)

        # Add relevant code context from RAG if available
        if vector_store is not None:
            variables["relevant_code_context"] = self._retrieve_relevant_code(vector_store)
        else:
            variables["relevant_code_context"] = ""

        structured_llm = client.with_structured_output(schema)
        chain = prompt_template | structured_llm
        result = chain.invoke(variables)
        return result.model_dump()

    # ── Fallback path: unstructured ─────────────────────────────────────

    def _fallback_unstructured(
        self,
        client,
        directory_tree: str,
        basic_analysis: Dict[str, Any],
        vector_store=None,
    ) -> Dict[str, Any]:
        """Legacy path: build prompt → invoke → extract_json."""
        try:
            prompt = self._build_prompt(directory_tree, basic_analysis)

            # Append RAG context if available
            if vector_store is not None:
                code_context = self._retrieve_relevant_code(vector_store)
                if code_context:
                    prompt += f"\n\n# Relevant Source Code:\n{code_context}"

            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ]
            response = client.invoke(messages)

            result = extract_json(response.content)
            if result is not None:
                return result
            return self._get_fallback_response(response.content)

        except Exception as e:
            return {"error": f"{self._get_layer_name()} analysis failed: {str(e)}"}

    # ── RAG retrieval ───────────────────────────────────────────────────

    def _retrieve_relevant_code(self, vector_store) -> str:
        """Retrieve relevant code snippets from vector store."""
        queries = self._get_retrieval_queries()
        if not queries:
            return ""

        seen = set()
        snippets = []
        max_chars = 8000

        for query in queries:
            try:
                docs = vector_store.similarity_search(query, k=3)
                for doc in docs:
                    content = doc.page_content.strip()
                    content_hash = hash(content)
                    if content_hash not in seen:
                        seen.add(content_hash)
                        source = doc.metadata.get("source", "unknown")
                        snippets.append(f"## {source}\n```\n{content}\n```")
            except Exception:
                continue

        result = "\n\n".join(snippets)
        if len(result) > max_chars:
            result = result[:max_chars] + "\n... (truncated)"
        return result

    def _get_retrieval_queries(self) -> list:
        """Override in subclasses to provide domain-specific RAG queries."""
        return []

    # ── Abstract methods for new structured path ────────────────────────

    @abstractmethod
    def _get_output_schema(self) -> Type[BaseModel]:
        """Return the Pydantic model for this layer's structured output."""
        ...

    @abstractmethod
    def _get_prompt_template(self) -> ChatPromptTemplate:
        """Return the ChatPromptTemplate with {variable} placeholders."""
        ...

    @abstractmethod
    def _get_prompt_variables(
        self, directory_tree: str, basic_analysis: Dict[str, Any]
    ) -> dict:
        """Return the dict of variables to fill the prompt template."""
        ...

    # ── Abstract methods for legacy fallback path ───────────────────────

    @abstractmethod
    def _get_system_prompt(self) -> str: ...

    @abstractmethod
    def _build_prompt(self, directory_tree: str, basic_analysis: Dict[str, Any]) -> str: ...

    @abstractmethod
    def _get_fallback_response(self, raw_content: str) -> Dict[str, Any]: ...

    @abstractmethod
    def _get_layer_name(self) -> str: ...
