from django.db import models
from core.models import TimeStampedModel

class AIProvider(models.TextChoices):
    OPENAI = 'openai', 'OpenAI'
    ANTHROPIC = 'anthropic', 'Anthropic'
    GOOGLE = 'google', 'Google'
    MISTRAL = 'mistral', 'Mistral'

class AgentConfig(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, help_text="Unique name for the agent (e.g., 'decision_agent')")
    provider = models.CharField(max_length=50, choices=AIProvider.choices, default=AIProvider.OPENAI)
    model_name = models.CharField(max_length=100, help_text="Model identifier (e.g., 'gpt-4o', 'claude-3-5-sonnet')")
    temperature = models.FloatField(default=0.7)
    system_prompt = models.TextField(blank=True, help_text="Initial system instruction for the agent")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.model_name})"
