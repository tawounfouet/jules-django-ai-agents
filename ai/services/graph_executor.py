import json
import uuid
import logging
from django.utils import timezone
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from ai.models import Graph, Execution, ExecutionStep, AgentMessage, Agent
from ai.graph import build_graph

logger = logging.getLogger(__name__)


class GraphExecutor:
    def __init__(self, graph_key="main_workflow"):
        self.graph_key = graph_key
        try:
            self.graph_model = Graph.objects.get(key=graph_key)
        except Graph.DoesNotExist:
            # Fallback for development if seed wasn't run
            self.graph_model = None

    def execute(
        self,
        user_input: str,
        thread_id: str = None,
        triggered_by="api",
        user_id: int = None,
    ):
        """
        Executes the graph with the given input/thread, logging everything to DB.

        Args:
            user_input: The user's message/query
            thread_id: Optional thread ID for conversation continuity
            triggered_by: Source of the execution (api, webhook, etc.)
            user_id: Optional user ID for permission checks and context

        Returns:
            dict: Contains response, thread_id, and execution_id
        """
        if not thread_id:
            thread_id = str(uuid.uuid4())

        # 1. Create Execution Record
        execution = Execution.objects.create(
            graph=self.graph_model,
            triggered_by=triggered_by,
            status="running",
            thread_id=thread_id,
            context={"initial_input": user_input, "user_id": user_id},
        )

        app = build_graph()

        # Build config with user context for tools
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id,  # Pass user context to tools via RunnableConfig
            }
        }

        inputs = {"messages": [HumanMessage(content=user_input)]}

        # Log Human Message (LangChain terminology)
        AgentMessage.objects.create(
            execution=execution, role="human", content=user_input
        )

        final_response = "No response"

        try:
            # Stream the graph execution
            for event in app.stream(inputs, config=config):
                for node_name, node_value in event.items():
                    try:
                        # Create Step Record
                        step = ExecutionStep.objects.create(
                            execution=execution,
                            node_name=node_name,
                            status="success",  # Tentative, assumed success if we reached here
                            output_payload=json.loads(
                                json.dumps(node_value, default=str)
                            ),  # Simple serialization
                        )

                        # Log Messages generated in this step
                        if "messages" in node_value:
                            messages = node_value["messages"]
                            for msg in messages:
                                # Map LangChain message types to role strings
                                role = "ai"  # Default for AIMessage
                                if isinstance(msg, ToolMessage):
                                    role = "tool"
                                elif isinstance(msg, HumanMessage):
                                    role = "human"
                                elif isinstance(msg, SystemMessage):
                                    role = "system"

                                # Determine agent if possible (based on node_name mapping)
                                agent = self._get_agent_for_node(node_name)

                                AgentMessage.objects.create(
                                    execution=execution,
                                    agent=agent,
                                    role=role,
                                    content=msg.content,
                                )
                                step.agent = agent
                                step.save()

                                if msg.content:
                                    final_response = msg.content

                    except Exception as step_error:
                        logger.error(f"Error in node {node_name}: {step_error}")
                        ExecutionStep.objects.create(
                            execution=execution,
                            node_name=node_name,
                            status="failed",
                            output_payload={"error": str(step_error)},
                        )

            execution.status = "success"
            execution.finished_at = timezone.now()
            execution.save()

        except Exception as e:
            logger.exception(f"Execution {execution.id} failed")
            execution.status = "failed"
            execution.context["error"] = str(e)
            execution.finished_at = timezone.now()
            execution.save()
            raise e

        return {
            "response": final_response,
            "thread_id": thread_id,
            "execution_id": execution.id,
        }

    def _get_agent_for_node(self, node_name):
        """
        Helper to map node names to Agent DB objects.

        The supervisor generates nodes with various names:
        - 'supervisor' -> maps to 'supervisor'
        - 'data_agent' -> maps to 'data_agent'
        - 'support_agent' -> maps to 'support_agent'
        - 'document_agent' -> maps to 'document_agent'
        - 'movie_agent' -> maps to 'movie_agent'
        - Other nodes (routing, intermediate) -> None
        """
        # Direct mapping for agent nodes
        agent_mappings = {
            "supervisor": "supervisor",  # Supervisor node
            "data_agent": "data_agent",
            "support_agent": "support_agent",
            "document_agent": "document_agent",
            "movie_agent": "movie_agent",
        }

        # Check if node_name has a direct mapping
        agent_key = agent_mappings.get(node_name)

        if agent_key:
            try:
                return Agent.objects.get(key=agent_key)
            except Agent.DoesNotExist:
                logger.warning(f"Agent with key '{agent_key}' not found in database")
                return None

        # Try direct lookup for backward compatibility
        try:
            return Agent.objects.get(key=node_name)
        except Agent.DoesNotExist:
            # This is normal for intermediate routing nodes
            logger.debug(f"Node '{node_name}' does not map to any agent")
            return None
