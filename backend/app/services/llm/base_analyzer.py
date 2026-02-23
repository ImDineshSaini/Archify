"""Base class for LLM-powered deep analysis layers."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict
from langchain.schema import HumanMessage, SystemMessage
from app.core.constants import TREE_TRUNCATION_LIMIT


class BaseLLMAnalyzer(ABC):
    """Template method pattern for deep analysis layers.

    Subclasses implement ``_get_system_prompt``, ``_build_prompt``,
    ``_get_fallback_response``, and ``_get_layer_name``.
    """

    def analyze(self, client, directory_tree: str, basic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Run analysis: build prompt -> call LLM -> parse JSON -> handle error."""
        try:
            prompt = self._build_prompt(directory_tree, basic_analysis)
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ]
            response = client.invoke(messages)

            try:
                return json.loads(response.content)
            except (json.JSONDecodeError, TypeError):
                return self._get_fallback_response(response.content)

        except Exception as e:
            return {"error": f"{self._get_layer_name()} analysis failed: {str(e)}"}

    @abstractmethod
    def _get_system_prompt(self) -> str: ...

    @abstractmethod
    def _build_prompt(self, directory_tree: str, basic_analysis: Dict[str, Any]) -> str: ...

    @abstractmethod
    def _get_fallback_response(self, raw_content: str) -> Dict[str, Any]: ...

    @abstractmethod
    def _get_layer_name(self) -> str: ...
