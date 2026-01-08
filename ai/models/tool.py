from django.db import models
from core.models import TimeStampedModel
from .agent import Agent

class Tool(TimeStampedModel):
    key = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()

    python_path = models.CharField(
        max_length=255,
        help_text="ex: ai.tools.check_order_status",
    )

    is_sensitive = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class AgentTool(TimeStampedModel):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    allowed = models.BooleanField(default=True)

    class Meta:
        unique_together = ("agent", "tool")
