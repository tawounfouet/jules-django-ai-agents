from django.db import models
from core.models import TimeStampedModel

class Agent(TimeStampedModel):
    key = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    role = models.TextField()
    description = models.TextField(blank=True)

    llm_provider = models.CharField(
        max_length=50,
        choices=[
            ("openai", "OpenAI"),
            ("anthropic", "Anthropic"),
            ("google", "Google"),
            ("mistral", "Mistral"),
            ("azure", "Azure OpenAI"),
            ("local", "Local LLM"),
        ],
        default="openai"
    )
    llm_model = models.CharField(max_length=100, help_text="e.g. gpt-4o, claude-3-5-sonnet")
    temperature = models.FloatField(default=0.0)
    
    system_prompt = models.TextField(blank=True, help_text="Default system prompt for this agent")

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
