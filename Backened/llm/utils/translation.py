"""
Utility helpers for language detection and translation.

These functions keep the chat pipeline lightweight by relying on OpenAI (which
is already configured for the project) for translation, and on `langdetect`
for best-effort language detection. All helpers fail gracefully and return the
original text if translation is unavailable so existing behaviour is preserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional

import structlog
from langdetect import DetectorFactory, LangDetectException, detect

from ..core.llm.openai_client import get_openai_client

logger = structlog.get_logger(__name__)


# Ensure deterministic results from `langdetect`.
DetectorFactory.seed = 0


@dataclass(frozen=True)
class LanguageMeta:
    code: str
    label: str
    locale: str


SUPPORTED_LANGUAGES: Dict[str, LanguageMeta] = {
    "en": LanguageMeta(code="en", label="English", locale="en-AU"),
    "es": LanguageMeta(code="es", label="Español", locale="es-ES"),
    "hi": LanguageMeta(code="hi", label="हिन्दी", locale="hi-IN"),
}

DEFAULT_LANGUAGE = "en"


def normalise_language(code: Optional[str]) -> str:
    """
    Normalise a language code to one of the supported values; fall back to the
    default language when the input is missing or unsupported.
    """

    if not code:
        return DEFAULT_LANGUAGE
    canonical = code.lower().split("-")[0]
    return canonical if canonical in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def detect_language(text: str, *, allow: Optional[Iterable[str]] = None) -> str:
    """
    Guess the language of `text` and return a supported language code.

    - If detection fails, returns the default language.
    - If `allow` is provided, the detected language must appear in that list.
    """

    if not text or not text.strip():
        return DEFAULT_LANGUAGE

    try:
        code = detect(text)
    except LangDetectException:
        return DEFAULT_LANGUAGE
    except Exception as exc:  # pragma: no cover: defensive logging path
        logger.warning("Language detection failed", error=str(exc))
        return DEFAULT_LANGUAGE

    code = code.lower().split("-")[0]
    if allow and code not in allow:
        return DEFAULT_LANGUAGE

    return normalise_language(code)


def translate_text(
    text: str,
    target_language: str,
    *,
    source_language: Optional[str] = None,
    max_tokens: int = 300,
) -> str:
    """
    Translate `text` to `target_language` using the configured OpenAI client.

    Falls back to returning the original text when:
      * the languages already match
      * translation fails (missing API key, request error, etc.)
    """

    if not text or not text.strip():
        return text

    target = normalise_language(target_language)
    source = normalise_language(source_language) if source_language else None

    if source and source == target:
        return text

    try:
        openai_client = get_openai_client()
        target_label = SUPPORTED_LANGUAGES[target].label
        source_label = SUPPORTED_LANGUAGES[source].label if source else "auto-detect"
        prompt_system = (
            "You are a translation engine. Translate the user supplied text "
            f"into {target_label}. Return only the translated text without additional commentary."
        )
        prompt_user = (
            f"Source language: {source_label}\n"
            f"Target language: {target_label}\n"
            "Text:\n"
            f"{text}"
        )

        response = openai_client.client.chat.completions.create(
            model=openai_client.settings.openai_model,
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user},
            ],
            temperature=0.2,
            max_tokens=max_tokens,
        )
        translated = response.choices[0].message.content.strip()
        return translated or text
    except Exception as exc:
        logger.warning("Translation failed", error=str(exc))
        return text


def get_language_meta(code: str) -> LanguageMeta:
    """Return metadata for `code`, defaulting to English."""

    return SUPPORTED_LANGUAGES.get(normalise_language(code), SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE])
