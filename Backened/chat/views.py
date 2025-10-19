# Backened/chat/views.py

from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

import asyncio
import httpx

from .models import ChatSession, Message  # noqa: F401 (Message kept for future use)
from .serializers import ChatSessionSerializer
from llm.services.chat_service import chat_service
from llm.utils.translation import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    detect_language,
    normalise_language,
    translate_text,
)


class ChatSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, retrieving, updating, and deleting chat sessions.
    """
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer


class ChatMessageAPIView(APIView):
    """
    Receives a user message and returns an LLM response.

    - If payload["type"] == "service_form": submit through in-process chat_service (kept intact).
    - Otherwise:
        * If FASTAPI proxy is enabled (see below), forwards the request to your FastAPI endpoint.
        * Else, uses in-process chat_service (kept intact).

    Enable FastAPI proxy by either:
      - Setting Django setting FASTAPI_CHAT_URL (e.g. in settings.py), or
      - Passing "use_fastapi": true in the request payload (optionally with "fastapi_url").
    """

    def post(self, request, *args, **kwargs):
        payload = request.data
        user_message = payload.get("message")
        session_id = payload.get("session_id")

        # --- (1) Service form: keep original behavior exactly ---
        if payload.get("type") == "service_form":
            try:
                llm_response = asyncio.run(
                    chat_service.process_message(
                        payload,  # special token & full payload for form
                        session_id=session_id,
                    )
                )
                return Response(
                    {
                        "response": llm_response.get("message"),
                        "session_id": llm_response.get("session_id"),
                        "action": llm_response.get("action"),
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Basic validation (keep both originals' intent)
        if not user_message:
            return Response({"error": "Missing message"}, status=status.HTTP_400_BAD_REQUEST)

        # --- Language detection & translation setup ---
        preferred_language = payload.get("language")
        language = (
            normalise_language(preferred_language)
            if preferred_language
            else detect_language(user_message, allow=SUPPORTED_LANGUAGES.keys())
        )

        message_for_backend = user_message
        if language != DEFAULT_LANGUAGE:
            translated = translate_text(user_message, DEFAULT_LANGUAGE, source_language=language)
            if translated and translated.strip():
                message_for_backend = translated

        # --- (2) Decide route: FastAPI proxy or local chat_service ---
        fastapi_from_settings = getattr(settings, "FASTAPI_CHAT_URL", None)
        backend_pref = getattr(settings, "CHAT_BACKEND", "")
        via = (request.query_params.get("via") or "").lower()
        use_fastapi = (
            bool(payload.get("use_fastapi"))
            or bool(fastapi_from_settings)
            or backend_pref.lower() == "fastapi"
            or via == "fastapi"
        )

        if use_fastapi:
            # Preserve explicit override path while keeping hardcoded fallback
            fastapi_url = (
                payload.get("fastapi_url")
                or fastapi_from_settings
                or "https://your-aws-fastapi-url.com/api/v1/chat/chat"
            )
            fastapi_payload = dict(payload) if isinstance(payload, dict) else {}
            fastapi_payload.update(
                {
                    "message": message_for_backend,
                    "session_id": session_id,
                    "language": language,
                }
            )
            if language != DEFAULT_LANGUAGE:
                fastapi_payload.setdefault("original_message", user_message)
            try:
                with httpx.Client() as client:
                    response = client.post(
                        fastapi_url,
                        json=fastapi_payload,
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    llm_response = response.json()

                llm_reply = llm_response.get("message")
                if language != DEFAULT_LANGUAGE and llm_reply:
                    llm_reply = translate_text(llm_reply, language, source_language=DEFAULT_LANGUAGE)

                return Response(
                    {
                        "response": llm_reply,
                        "session_id": llm_response.get("session_id"),
                        "action": llm_response.get("action"),
                        "language": language,
                    },
                    status=status.HTTP_200_OK,
                )
            except httpx.HTTPError as e:
                return Response(
                    {"error": f"FastAPI proxy error: {e}"},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # --- (3) Default: local chat_service (keep original behavior) ---
        try:
            llm_response = asyncio.run(
                chat_service.process_message(message_for_backend, session_id=session_id)
            )
            llm_reply = llm_response.get("message", "No reply from LLM.")
            if language != DEFAULT_LANGUAGE and llm_reply:
                llm_reply = translate_text(llm_reply, language, source_language=DEFAULT_LANGUAGE)
            return Response(
                {
                    "response": llm_reply,
                    "session_id": llm_response.get("session_id"),
                    "action": llm_response.get("action"),
                    "language": language,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
