import json
import uuid
from django.utils import timezone
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from ai.models import Graph, Execution, ExecutionStep, AgentMessage, Agent
from ai.graph import build_graph

class GraphExecutor:
    def __init__(self, graph_key="main_workflow"):
        self.graph_key = graph_key
        try:
            self.graph_model = Graph.objects.get(key=graph_key)
        except Graph.DoesNotExist:
            # Fallback for development if seed wasn't run
            self.graph_model = None

    def execute(self, user_input: str, thread_id: str = None, triggered_by="api"):
        """
        Executes the graph with the given input/thread, logging everything to DB.
        Returns the final response string.
        """
        if not thread_id:
            thread_id = str(uuid.uuid4())
            
        # 1. Create Execution Record
        execution = Execution.objects.create(
            graph=self.graph_model,
            triggered_by=triggered_by,
            status="running",
            thread_id=thread_id,
            context={"initial_input": user_input}
        )

        app = build_graph()
        config = {"configurable": {"thread_id": thread_id}}
        inputs = {"messages": [HumanMessage(content=user_input)]}

        # Log User Message
        AgentMessage.objects.create(
            execution=execution,
            role="user",
            content=user_input
        )

        final_response = "No response"
        
        try:
            # Stream the graph execution
            for event in app.stream(inputs, config=config):
                for node_name, node_value in event.items():
                    # Create Step Record
                    step = ExecutionStep.objects.create(
                        execution=execution,
                        node_name=node_name,
                        status="success", # Tentative, assumed success if we reached here
                        output_payload=json.loads(json.dumps(node_value, default=str)) # Simple serialization
                    )
                    
                    # Log Messages generated in this step
                    if "messages" in node_value:
                        messages = node_value["messages"]
                        for msg in messages:
                            role = "assistant"
                            if isinstance(msg, ToolMessage):
                                role = "tool"
                            
                            # Determine agent if possible (based on node_name mapping)
                            agent = self._get_agent_for_node(node_name)
                            
                            AgentMessage.objects.create(
                                execution=execution,
                                agent=agent,
                                role=role,
                                content=msg.content
                            )
                            step.agent = agent
                            step.save()

                            if msg.content:
                                final_response = msg.content
            
            execution.status = "success"
            execution.finished_at = timezone.now()
            execution.save()
            
        except Exception as e:
            execution.status = "failed"
            execution.context["error"] = str(e)
            execution.finished_at = timezone.now()
            execution.save()
            raise e

        return {
            "response": final_response,
            "thread_id": thread_id,
            "execution_id": execution.id
        }

    def _get_agent_for_node(self, node_name):
        """Helper to map node names to Agent DB objects."""
        # This mapping depends on how nodes are named in ai/graph.py
        # Current mapping: 'decision_agent' -> 'decision_agent' key
        # 'data_agent' -> 'data_agent' key
        # 'support_agent' -> 'support_agent' key
        try:
            return Agent.objects.get(key=node_name)
        except Agent.DoesNotExist:
            return None
