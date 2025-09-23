from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('chat-sessions/', views.ChatSessionList.as_view(), name = 'ChatList'),
    path('chat-sessions/<int:pk>/', views.ChatSessionDetailView.as_view(), name='ChatDetail'),
    path('chat-message/', views.ChatMessageAPIView.as_view(), name='ChatMessage'),
]
