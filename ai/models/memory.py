from django.db import models
from core.models import TimeStampedModel
from .agent import Agent
from .execution import Execution

class AgentMessage(TimeStampedModel):
    execution = models.ForeignKey(Execution, on_delete=models.CASCADE, null=True, blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)

    role = models.CharField(
        max_length=20,
        choices=[
            ("system", "System"),
            ("user", "User"),
            ("assistant", "Assistant"),
            ("tool", "Tool"),
        ],
    )

    content = models.TextField()


class AgentMemory(TimeStampedModel):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    embedding = models.BinaryField(null=True, blank=True)
    content = models.TextField()

    source = models.CharField(max_length=100, blank=True)
