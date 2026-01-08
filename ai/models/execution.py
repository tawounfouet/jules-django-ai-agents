from django.db import models
from core.models import TimeStampedModel
from .graph import Graph, GraphVersion
from .agent import Agent

class Execution(TimeStampedModel):
    graph = models.ForeignKey(Graph, on_delete=models.CASCADE)
    graph_version = models.ForeignKey(GraphVersion, on_delete=models.SET_NULL, null=True, blank=True)

    triggered_by = models.CharField(
        max_length=50,
        choices=[
            ("api", "API"),
            ("signal", "Django Signal"),
            ("cron", "Cron"),
            ("agent", "Agent"),
            ("manual", "Manual"),
        ],
        default="api"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("running", "Running"),
            ("success", "Success"),
            ("failed", "Failed"),
        ],
        default="pending",
    )

    context = models.JSONField(default=dict, blank=True)
    thread_id = models.CharField(max_length=100, blank=True, help_text="LangGraph Thread ID")
    
    # TimeStampedModel provides created_at (started_at equivalent) and updated_at
    # We might want separate started_at/finished_at logic, but for now lets keep fields explicit if they have specific semantic meaning beyond 'record creation'.
    # Actually, created_at is fine for 'started_at' if it's created when started.
    # explicit started_at/finished_at is better for process duration tracking.
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.graph.key} - {self.status} ({self.id})"


class ExecutionStep(TimeStampedModel):
    execution = models.ForeignKey(Execution, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)
    node_name = models.CharField(max_length=100, blank=True, help_text="Name of the node in the graph")

    input_payload = models.JSONField(default=dict, blank=True)
    output_payload = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=20, default="pending")
    
    # Explicit timing
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
