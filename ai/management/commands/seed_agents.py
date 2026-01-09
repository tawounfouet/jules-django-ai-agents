from django.core.management.base import BaseCommand
from ai.models import Agent, Tool, AgentTool, Graph, GraphVersion


class Command(BaseCommand):
    help = "Seeds default agent configurations (V3)"

    def handle(self, *args, **options):
        # 1. Agents
        agents = [
            {
                "key": "supervisor",
                "name": "Supervisor",
                "role": "Routing",
                "llm_provider": "openai",
                "llm_model": "gpt-4o",
                "temperature": 0.0,
                "system_prompt": "You are a supervisor agent that routes requests to specialized agents.",
            },
            {
                "key": "data_agent",
                "name": "Data Agent",
                "role": "Retrieval",
                "llm_provider": "openai",
                "llm_model": "gpt-4o",
                "temperature": 0.0,
                "system_prompt": "You are a data retrieval agent.",
            },
            {
                "key": "support_agent",
                "name": "Customer Support Agent",
                "role": "Customer Support",
                "llm_provider": "openai",
                "llm_model": "gpt-4o",
                "temperature": 0.7,
                "system_prompt": "You are a helpful customer support agent. Answer questions clearly and professionally.",
            },
            {
                "key": "document_agent",
                "name": "Document Agent",
                "role": "Document Management",
                "llm_provider": "openai",
                "llm_model": "gpt-4o",
                "temperature": 0.2,
                "system_prompt": "You are a document management agent. You help users create, search, update, and delete their documents.",
            },
            {
                "key": "movie_agent",
                "name": "Movie Agent",
                "role": "Movie Discovery",
                "llm_provider": "openai",
                "llm_model": "gpt-4o",
                "temperature": 0.3,
                "system_prompt": "You are a movie discovery agent. You help users search for movies and get detailed information from The Movie Database (TMDB).",
            },
        ]

        created_agents = {}
        for agent_data in agents:
            obj, created = Agent.objects.update_or_create(
                key=agent_data["key"], defaults=agent_data
            )
            created_agents[obj.key] = obj
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created Agent: {obj.name} ({obj.key})")
                )
            else:
                self.stdout.write(f"Updated Agent: {obj.name} ({obj.key})")

        # 2. Tools (NEW MODULAR STRUCTURE)
        tools = [
            {
                "key": "check_order_status",
                "name": "Check Order Status",
                "description": "Checks order status by ID",
                "python_path": "ai.tools.order_tools.check_order_status",
            },
            {
                "key": "get_ticket_info",
                "name": "Get Ticket Info",
                "description": "Gets details of a support ticket",
                "python_path": "ai.tools.ticket_tools.get_ticket_info",
            },
            {
                "key": "create_support_response",
                "name": "Create Support Response",
                "description": "Generate a standard support response based on issue type",
                "python_path": "ai.tools.support_tools.create_support_response",
            },
            # Document Tools
            {
                "key": "search_query_documents",
                "name": "Search Documents",
                "description": "Search documents by query string",
                "python_path": "ai.tools.document_tools.search_query_documents",
            },
            {
                "key": "list_documents",
                "name": "List Documents",
                "description": "List all documents for the user",
                "python_path": "ai.tools.document_tools.list_documents",
            },
            {
                "key": "get_document",
                "name": "Get Document",
                "description": "Get details of a specific document by ID",
                "python_path": "ai.tools.document_tools.get_document",
            },
            {
                "key": "create_document",
                "name": "Create Document",
                "description": "Create a new document",
                "python_path": "ai.tools.document_tools.create_document",
            },
            {
                "key": "update_document",
                "name": "Update Document",
                "description": "Update an existing document",
                "python_path": "ai.tools.document_tools.update_document",
            },
            {
                "key": "delete_document",
                "name": "Delete Document",
                "description": "Delete a document",
                "python_path": "ai.tools.document_tools.delete_document",
            },
            # TMDB Tools
            {
                "key": "search_movies",
                "name": "Search Movies",
                "description": "Search for movies in The Movie Database (TMDB)",
                "python_path": "ai.tools.tmdb_tools.search_movies",
            },
            {
                "key": "movie_detail",
                "name": "Get Movie Details",
                "description": "Get detailed information about a specific movie from TMDB",
                "python_path": "ai.tools.tmdb_tools.movie_detail",
            },
        ]

        created_tools = {}
        for tool_data in tools:
            obj, created = Tool.objects.update_or_create(
                key=tool_data["key"], defaults=tool_data
            )
            created_tools[obj.key] = obj
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Tool: {obj.name}"))
            else:
                self.stdout.write(f"Updated Tool: {obj.name}")

        # 3. Agent Tools (Permissions)
        # Link data tools to data_agent
        if "data_agent" in created_agents:
            data_agent = created_agents["data_agent"]
            data_tools = ["check_order_status", "get_ticket_info"]
            for tool_key in data_tools:
                if tool_key in created_tools:
                    _, created = AgentTool.objects.get_or_create(
                        agent=data_agent,
                        tool=created_tools[tool_key],
                        defaults={"allowed": True},
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Linked {created_tools[tool_key].name} to {data_agent.name}"
                            )
                        )

        # Link document tools to document_agent
        if "document_agent" in created_agents:
            document_agent = created_agents["document_agent"]
            document_tool_keys = [
                "search_query_documents",
                "list_documents",
                "get_document",
                "create_document",
                "update_document",
                "delete_document",
            ]
            for tool_key in document_tool_keys:
                if tool_key in created_tools:
                    _, created = AgentTool.objects.get_or_create(
                        agent=document_agent,
                        tool=created_tools[tool_key],
                        defaults={"allowed": True},
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Linked {created_tools[tool_key].name} to {document_agent.name}"
                            )
                        )

        # Link TMDB tools to movie_agent
        if "movie_agent" in created_agents:
            movie_agent = created_agents["movie_agent"]
            movie_tool_keys = [
                "search_movies",
                "movie_detail",
            ]
            for tool_key in movie_tool_keys:
                if tool_key in created_tools:
                    _, created = AgentTool.objects.get_or_create(
                        agent=movie_agent,
                        tool=created_tools[tool_key],
                        defaults={"allowed": True},
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Linked {created_tools[tool_key].name} to {movie_agent.name}"
                            )
                        )

        # 4. Graph & Version
        graph, created = Graph.objects.get_or_create(
            key="main_workflow",
            defaults={
                "name": "Main Customer Support Workflow",
                "description": "Multi-agent system with supervisor routing to specialized agents.",
                "entry_agent": created_agents.get("supervisor"),
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created Graph: {graph.name}"))

        # Create a default version
        GraphVersion.objects.get_or_create(
            graph=graph,
            version="1.0",
            defaults={
                "definition": {
                    "nodes": [
                        "supervisor",
                        "data_agent",
                        "support_agent",
                        "document_agent",
                        "movie_agent",
                    ],
                    "edges": ["supervisor->*"],
                }
            },
        )
