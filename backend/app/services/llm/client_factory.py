"""Factory for creating LLM clients."""

from typing import Optional
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from app.core.constants import (
    DEFAULT_CLAUDE_MODEL,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_LLM_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_AZURE_API_VERSION,
)


def create_llm_client(
    provider: str,
    api_key: str,
    model: Optional[str] = None,
    endpoint: Optional[str] = None,
    deployment_name: Optional[str] = None,
):
    """Initialize the appropriate LLM client based on provider."""
    if provider == "claude":
        return ChatAnthropic(
            anthropic_api_key=api_key,
            model=model or DEFAULT_CLAUDE_MODEL,
            temperature=DEFAULT_LLM_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
        )
    elif provider == "openai":
        return ChatOpenAI(
            openai_api_key=api_key,
            model=model or DEFAULT_OPENAI_MODEL,
            temperature=DEFAULT_LLM_TEMPERATURE,
        )
    elif provider == "azure":
        if not endpoint or not deployment_name:
            raise ValueError("Azure OpenAI requires endpoint and deployment_name")
        return AzureChatOpenAI(
            azure_endpoint=endpoint,
            openai_api_key=api_key,
            deployment_name=deployment_name,
            openai_api_version=DEFAULT_AZURE_API_VERSION,
            temperature=DEFAULT_LLM_TEMPERATURE,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
