from django.urls import path
from .views import trigger_agent, chat_ui

urlpatterns = [
    path('chat/', trigger_agent, name='trigger_agent'),
    path('ui/', chat_ui, name='chat_ui'),
]
