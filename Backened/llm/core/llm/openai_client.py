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
        self._chat_llm: Optional[ChatOpenAI] = None

    @property
    def client(self) -> openai.OpenAI:
        """
        Return a shared OpenAI client. Instantiated on first access so that API
        keys or other configuration can be loaded from the environment at runtime.
        """

        if self._client is None:
            if not self.settings.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY is not configured.")
            openai.api_key = self.settings.openai_api_key
            self._client = openai.OpenAI(api_key=self.settings.openai_api_key)
        return self._client

    def get_chat_llm(
        self,
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **overrides: Any,
    ) -> ChatOpenAI:
        """
        Provide a LangChain `ChatOpenAI` instance configured from application
        settings. Results are cached so repeated callers reuse the same HTTP
        session. Optional overrides mirror the legacy helper API.
        """

        if self._chat_llm is None:
            if not self.settings.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY is not configured.")

            self._chat_llm = ChatOpenAI(
                api_key=self.settings.openai_api_key,
                model=model or self.settings.openai_model,
                temperature=self._resolve_temperature(temperature),
                max_tokens=self._resolve_max_tokens(max_tokens),
                max_retries=overrides.get("max_retries", 3),
                timeout=overrides.get("timeout"),
            )
        else:
            if model and getattr(self._chat_llm, "model_name", None) != model:
                self._chat_llm.model_name = model
            if temperature is not None:
                self._chat_llm.temperature = temperature
            if max_tokens is not None:
                self._chat_llm.max_tokens = max_tokens

        return self._chat_llm

    def create_chat_llm_with_params(
        self,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **overrides: Any,
    ) -> ChatOpenAI:
        """
        Create a new `ChatOpenAI` instance with custom parameters without touching
        the cached shared instance. Handy for background tasks that need different
        sampling strategies.
        """

        if not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        return ChatOpenAI(
            api_key=self.settings.openai_api_key,
            model=self.settings.openai_model,
            temperature=self._resolve_temperature(temperature),
            max_tokens=self._resolve_max_tokens(max_tokens),
            max_retries=overrides.get("max_retries", 3),
            timeout=overrides.get("timeout"),
        )

    def _resolve_temperature(self, override: Optional[float]) -> float:
        return override if override is not None else self.settings.openai_temperature

    def _resolve_max_tokens(self, override: Optional[int]) -> Optional[int]:
        return override if override is not None else self.settings.max_response_tokens

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


def get_chat_llm(
    *,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **overrides: Any,
) -> ChatOpenAI:
    """Provide access to the shared LangChain client with optional overrides."""

    return openai_client.get_chat_llm(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        **overrides,
    )
