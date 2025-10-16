"""
OpenAI client helpers for the mental health LLM backend.

This module centralises creation of both the low-level OpenAI SDK client and the
LangChain compatible `ChatOpenAI` wrapper so that downstream services share a
consistent configuration (model, temperature, retry policy, etc.).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import openai
import structlog
from langchain_openai import ChatOpenAI

from ...app.config import get_settings

logger = structlog.get_logger(__name__)


class OpenAIClient:
    """Thin wrapper around the official OpenAI client with lazy initialisation."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Optional[openai.OpenAI] = None

    @property
    def client(self) -> openai.OpenAI:
        """
        Return a shared OpenAI client. Instantiated on first access so that API
        keys or other configuration can be loaded from the environment at runtime.
        """

        if self._client is None:
            if not self.settings.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY is not configured.")
            self._client = openai.OpenAI(api_key=self.settings.openai_api_key)
        return self._client

    async def test_connection(self) -> Dict[str, Any]:
        """
        Perform a minimal chat completion to verify connectivity. Any exception
        is logged and surfaced as a structured error response so that health
        checks can act on it without crashing.
        """

        try:
            self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=4,
            )
            return {
                "status": "connected",
                "model": self.settings.openai_model,
                "api_configured": True,
            }
        except Exception as exc:  # pragma: no cover - exercised via health check
            logger.error("OpenAI connection test failed", error=str(exc))
            return {
                "status": "error",
                "error": str(exc),
                "api_configured": bool(self.settings.openai_api_key),
            }


openai_client = OpenAIClient()


def get_openai_client() -> OpenAIClient:
    """Return the shared OpenAI client wrapper."""

    return openai_client


_cached_chat_llm: Optional[ChatOpenAI] = None


def get_chat_llm(
    *,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **overrides: Any,
) -> ChatOpenAI:
    """
    Provide a LangChain `ChatOpenAI` instance configured from application
    settings. Results are cached at the module level so repeated callers reuse
    the same underlying HTTP session which improves performance.
    """

    global _cached_chat_llm

    settings = get_settings()

    if _cached_chat_llm is None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        _cached_chat_llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=model or settings.openai_model,
            temperature=temperature if temperature is not None else settings.openai_temperature,
            max_tokens=max_tokens if max_tokens is not None else settings.max_response_tokens,
            max_retries=overrides.get("max_retries", 3),
            timeout=overrides.get("timeout"),
        )
    else:
        # Apply any on-the-fly overrides without rebuilding the client.
        if model and _cached_chat_llm.model_name != model:
            _cached_chat_llm.model_name = model
        if temperature is not None:
            _cached_chat_llm.temperature = temperature
        if max_tokens is not None:
            _cached_chat_llm.max_tokens = max_tokens

    return _cached_chat_llm
