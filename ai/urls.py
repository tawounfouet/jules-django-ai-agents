from django.urls import path
from .views import trigger_agent

urlpatterns = [
    path('chat/', trigger_agent, name='trigger_agent'),
]
