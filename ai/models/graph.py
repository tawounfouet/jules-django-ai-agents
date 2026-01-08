from django.db import models
from core.models import TimeStampedModel
from .agent import Agent

class Graph(TimeStampedModel):
    key = models.SlugField(unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    entry_agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        related_name="entry_graphs",
        blank=True
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class GraphVersion(TimeStampedModel):
    graph = models.ForeignKey(Graph, on_delete=models.CASCADE)
    version = models.CharField(max_length=20)

    definition = models.JSONField(
        help_text="Structure of the graph (nodes, edges, conditions)"
    )

    class Meta:
        unique_together = ("graph", "version")
    
    def __str__(self):
        return f"{self.graph.name} v{self.version}"
