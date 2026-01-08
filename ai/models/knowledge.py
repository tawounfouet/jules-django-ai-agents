from django.db import models
from core.models import TimeStampedModel

class KnowledgeSource(TimeStampedModel):
    key = models.SlugField(unique=True)
    name = models.CharField(max_length=150)

    type = models.CharField(
        max_length=50,
        choices=[
            ("file", "File"),
            ("db", "Database"),
            ("api", "External API"),
            ("web", "Web"),
        ],
    )

    config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
