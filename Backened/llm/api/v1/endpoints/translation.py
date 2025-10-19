"""
Translation API endpoints exposing language detection and translation helpers.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from llm.utils.translation import (  # type: ignore[attr-defined]
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    detect_language,
    normalise_language,
    translate_text,
)

router = APIRouter(prefix="/api/v1/translation", tags=["translation"])


class DetectRequest(BaseModel):
    text: str = Field("", description="Text to inspect for language detection.")
    preferred_language: Optional[str] = Field(
        default=None,
        description="Explicit language preference from the caller.",
    )


class DetectResponse(BaseModel):
    language: str
    detected: bool
    default_language: str = DEFAULT_LANGUAGE


@router.post("/detect", response_model=DetectResponse)
async def detect_language_endpoint(payload: DetectRequest) -> DetectResponse:
    """
    Normalise the preferred language when supplied, otherwise auto-detect.
    """

    if payload.preferred_language:
        language = normalise_language(payload.preferred_language)
        return DetectResponse(language=language, detected=False)

    language = detect_language(payload.text, allow=SUPPORTED_LANGUAGES.keys())
    return DetectResponse(language=language, detected=True)


class TranslateRequest(BaseModel):
    text: str = Field(..., description="Text to translate.")
    target_language: str = Field(..., description="Destination language code.")
    source_language: Optional[str] = Field(
        default=None,
        description="Optional source language code.",
    )
    max_tokens: int = Field(
        default=300,
        ge=1,
        le=2000,
        description="Cap for generated tokens to protect against runaway completions.",
    )


class TranslateResponse(BaseModel):
    text: str
    target_language: str
    source_language: Optional[str]
    translated: bool
    default_language: str = DEFAULT_LANGUAGE


@router.post("/translate", response_model=TranslateResponse)
async def translate_text_endpoint(payload: TranslateRequest) -> TranslateResponse:
    """
    Translate payload.text to the requested target language, returning the
    original text when no translation is required or translation fails.
    """

    target = normalise_language(payload.target_language)
    source = normalise_language(payload.source_language) if payload.source_language else None
    translated = translate_text(
        payload.text,
        target,
        source_language=source,
        max_tokens=payload.max_tokens,
    )
    return TranslateResponse(
        text=translated,
        target_language=target,
        source_language=source,
        translated=translated != payload.text,
    )
