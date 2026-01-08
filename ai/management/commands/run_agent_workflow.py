import uuid
from django.core.management.base import BaseCommand
from ai.services import GraphExecutor

class Command(BaseCommand):
    help = 'Runs the AI Agent Workflow with a given prompt (Logged)'

    def add_arguments(self, parser):
        parser.add_argument('prompt', type=str, help='The input prompt for the agent')
        parser.add_argument('--thread_id', type=str, default=None, help='Thread ID for memory')

    def handle(self, *args, **options):
        prompt = options['prompt']
        thread_id = options['thread_id']

        self.stdout.write(f"Starting workflow with prompt: \'{prompt}\' (Thread: {thread_id})...")

        try:
            executor = GraphExecutor()
            result = executor.execute(prompt, thread_id=thread_id, triggered_by="manual")
            
            self.stdout.write(self.style.SUCCESS(f"Execution complete. ID: {result['execution_id']}"))
            self.stdout.write(f"Response: {result['response']}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
