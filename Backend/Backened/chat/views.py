from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import DetailView
from .utils import get_chatbot_response
from django.shortcuts import render
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from .models import ChatSession, Message
from .serializers import *
from rest_framework.views import APIView


class ChatSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, retrieving, updating, and deleting chat sessions.
    """
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    
class ChatMessageAPIView(APIView):
    """
    Receives a user message, sends it to the LLM, and returns the response.
    """
    def post(self, request, *args, **kwargs):
        # 1. Extract user message and session info from request
        user_message = request.data.get('message')
        session_id = request.data.get('session_id')
        
        if not user_message or not session_id:
            return Response({'error': 'Missing message or session_id'}, status=status.HTTP_400_BAD_REQUEST)

        # 2. (Optional) Save the user message to the database
        # Message.objects.create(session_id=session_id, content=user_message, sender='user')

        # 3. Send the message to the LLM (to be integrated)
        # For now, use a placeholder response
        llm_response = "This is a placeholder response from the LLM."

        # 4. (Optional) Save the LLM response to the database
        # Message.objects.create(session_id=session_id, content=llm_response, sender='bot')

        # 5. Return the LLM response
        return Response({'response': llm_response}, status=status.HTTP_200_OK)