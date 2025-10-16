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

        # --- (2) Decide route: FastAPI proxy or local chat_service ---
        fastapi_from_settings = getattr(settings, "FASTAPI_CHAT_URL", None)
        use_fastapi = bool(payload.get("use_fastapi")) or bool(fastapi_from_settings)

        if use_fastapi:
            # preserve the original hardcoded path as a fallback
            fastapi_url = (
                payload.get("fastapi_url")
                or fastapi_from_settings
                or "https://your-aws-fastapi-url.com/api/v1/chat/chat"
            )
            try:
                with httpx.Client() as client:
                    response = client.post(
                        fastapi_url,
                        json={"message": user_message, "session_id": session_id},
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    llm_response = response.json()

                return Response(
                    {
                        "response": llm_response.get("message"),
                        "session_id": llm_response.get("session_id"),
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # --- (3) Default: local chat_service (keep original behavior) ---
        try:
            llm_response = asyncio.run(
                chat_service.process_message(user_message, session_id=session_id)
            )
            llm_reply = llm_response.get("message", "No reply from LLM.")
            return Response(
                {
                    "response": llm_reply,
                    "session_id": llm_response.get("session_id"),
                    "action": llm_response.get("action"),
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)