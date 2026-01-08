from django.core.management.base import BaseCommand
from ai.models import AgentConfig, AIProvider

class Command(BaseCommand):
    help = 'Seeds default agent configurations'

    def handle(self, *args, **options):
        agents = [
            {
                "name": "decision_agent",
                "provider": AIProvider.OPENAI,
                "model_name": "gpt-4o",
                "temperature": 0.0,
                "system_prompt": "You are a precise routing agent."
            },
            {
                "name": "data_agent",
                "provider": AIProvider.OPENAI,
                "model_name": "gpt-4o",
                "temperature": 0.0,
                "system_prompt": "You are a data retrieval agent."
            },
            {
                "name": "support_agent",
                "provider": AIProvider.OPENAI,
                "model_name": "gpt-4o",
                "temperature": 0.7,
                "system_prompt": "You are a helpful support agent."
            }
        ]

        for agent_data in agents:
            obj, created = AgentConfig.objects.get_or_create(
                name=agent_data["name"],
                defaults=agent_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created config for {obj.name}"))
            else:
                self.stdout.write(f"Config for {obj.name} already exists")
