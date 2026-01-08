from django.core.management.base import BaseCommand
from ai.models import Execution, ExecutionStep, AgentMessage

class Command(BaseCommand):
    help = 'Inspects execution records'

    def handle(self, *args, **options):
        last_exec = Execution.objects.last()
        if not last_exec:
            self.stdout.write("No executions found.")
            return
            
        self.stdout.write(f"Execution ID: {last_exec.id}, Status: {last_exec.status}")
        
        steps = ExecutionStep.objects.filter(execution=last_exec).order_by('created_at')
        self.stdout.write(f"Steps ({steps.count()}):")
        for step in steps:
            self.stdout.write(f" - {step.node_name} (Status: {step.status})")
            
        messages = AgentMessage.objects.filter(execution=last_exec).order_by('created_at')
        self.stdout.write(f"Messages ({messages.count()}):")
        for msg in messages:
            self.stdout.write(f" - [{msg.role}] ({msg.agent}): {msg.content}")
