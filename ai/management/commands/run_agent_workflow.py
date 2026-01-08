from django.core.management.base import BaseCommand
from ai.graph import build_graph
from langchain_core.messages import HumanMessage
import uuid

class Command(BaseCommand):
    help = 'Runs the AI Agent Workflow with a given prompt'

    def add_arguments(self, parser):
        parser.add_argument('prompt', type=str, help='The input prompt for the agent')
        parser.add_argument('--thread_id', type=str, default=str(uuid.uuid4()), help='Thread ID for memory')

    def handle(self, *args, **options):
        prompt = options['prompt']
        thread_id = options['thread_id']

        self.stdout.write(f"Starting workflow with prompt: '{prompt}' (Thread: {thread_id})")

        app = build_graph()

        config = {"configurable": {"thread_id": thread_id}}
        inputs = {"messages": [HumanMessage(content=prompt)]}

        try:
            for event in app.stream(inputs, config=config):
                for key, value in event.items():
                    self.stdout.write(self.style.SUCCESS(f"\n--- Node: {key} ---"))
                    if "messages" in value:
                        # Print the last message from the node
                        last_msg = value["messages"][-1]
                        self.stdout.write(f"Output: {last_msg.content}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
