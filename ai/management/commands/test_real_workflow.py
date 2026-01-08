import uuid
from django.core.management.base import BaseCommand
from langchain_core.messages import HumanMessage
from ai.graph import build_graph
from business.models import Customer, Order

class Command(BaseCommand):
    help = 'Runs the AI Agent Workflow with REAL database data'

    def handle(self, *args, **options):
        # 1. Setup Data
        self.stdout.write("Setting up test data...")
        customer, _ = Customer.objects.get_or_create(
            email="test@example.com", 
            defaults={"name": "Test User"}
        )
        # Create a new order to ensure we have a known ID
        order = Order.objects.create(
            customer=customer,
            status='SHIPPED',
            total_amount=199.99
        )
        self.stdout.write(self.style.SUCCESS(f"Created Order {order.id} with status SHIPPED"))

        # 2. Run Workflow
        prompt = f"Check status for order {order.id}"
        thread_id = str(uuid.uuid4())
        
        self.stdout.write(f"\nStarting workflow with prompt: '{prompt}'")

        app = build_graph()
        config = {"configurable": {"thread_id": thread_id}}
        inputs = {"messages": [HumanMessage(content=prompt)]}

        try:
            for event in app.stream(inputs, config=config):
                for key, value in event.items():
                    self.stdout.write(self.style.SUCCESS(f"\n--- Node: {key} ---"))
                    if "messages" in value:
                        last_msg = value["messages"][-1]
                        self.stdout.write(f"Output: {last_msg.content}")
                        
            self.stdout.write("\n" + "-"*30)
            self.stdout.write("Test Complete. Please verify the final output matches 'SHIPPED'.")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
        
        # Optional: Cleanup? Keeping it might be useful for manual inspection.
