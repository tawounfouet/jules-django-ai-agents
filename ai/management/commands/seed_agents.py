from django.core.management.base import BaseCommand
from ai.models import Agent, Tool, AgentTool, Graph, GraphVersion

class Command(BaseCommand):
    help = 'Seeds default agent configurations (V3)'

    def handle(self, *args, **options):
        # 1. Agents
        agents = [
            {
                "key": "decision_agent",
                "name": "Decision Agent",
                "role": "Routing",
                "llm_provider": "openai",
                "llm_model": "gpt-4o",
                "temperature": 0.0,
                "system_prompt": "You are a precise routing agent."
            },
            {
                "key": "data_agent",
                "name": "Data Agent",
                "role": "Retrieval",
                "llm_provider": "openai",
                "llm_model": "gpt-4o",
                "temperature": 0.0,
                "system_prompt": "You are a data retrieval agent."
            },
            {
                "key": "support_agent",
                "name": "Support Agent",
                "role": "Support",
                "llm_provider": "openai",
                "llm_model": "gpt-4o",
                "temperature": 0.7,
                "system_prompt": "You are a helpful support agent."
            }
        ]

        created_agents = {}
        for agent_data in agents:
            obj, created = Agent.objects.update_or_create(
                key=agent_data["key"],
                defaults=agent_data
            )
            created_agents[obj.key] = obj
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Agent: {obj.name} ({obj.key})"))
            else:
                self.stdout.write(f"Updated Agent: {obj.name} ({obj.key})")

        # 2. Tools
        tools = [
            {
                "key": "check_order_status",
                "name": "Check Order Status",
                "description": "Checks order status by ID",
                "python_path": "ai.tools.check_order_status"
            },
            {
                "key": "get_ticket_info",
                "name": "Get Ticket Info",
                "description": "Gets details of a support ticket",
                "python_path": "ai.tools.get_ticket_info"
            }
        ]
        
        created_tools = {}
        for tool_data in tools:
            obj, created = Tool.objects.update_or_create(
                key=tool_data["key"],
                defaults=tool_data
            )
            created_tools[obj.key] = obj
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Tool: {obj.name}"))
            else:
                self.stdout.write(f"Updated Tool: {obj.name}")

        # 3. Agent Tools (Permissions)
        if "data_agent" in created_agents:
            data_agent = created_agents["data_agent"]
            for tool_key, tool_obj in created_tools.items():
                at, created = AgentTool.objects.get_or_create(
                    agent=data_agent,
                    tool=tool_obj,
                    defaults={"allowed": True}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Linked {tool_obj.name} to {data_agent.name}"))

        # 4. Graph & Version
        graph, created = Graph.objects.get_or_create(
            key="main_workflow",
            defaults={
                "name": "Main Customer Support Workflow",
                "description": "Routing between decision, data, and support agents.",
                "entry_agent": created_agents.get("decision_agent")
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Graph: {graph.name}"))
        
        # Create a default version
        GraphVersion.objects.get_or_create(
            graph=graph,
            version="1.0",
            defaults={
                "definition": {
                    "nodes": ["decision_agent", "data_agent", "support_agent"],
                    "edges": ["decision->data", "decision->support"]
                }
            }
        )
