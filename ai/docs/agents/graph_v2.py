"""
Multi-Agent System using Official LangGraph Supervisor.

This version uses langgraph_supervisor.create_supervisor instead of manual implementation.
Benefits:
- Official support
- Automatic routing logic
- Built-in handoff mechanisms
- Less code to maintain
"""

from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import MemorySaver

from .agents_v2 import get_all_agents
from .utils import get_llm


def build_graph_v2(checkpointer=None):
    """
    Constructs the LangGraph using the official create_supervisor function.

    The supervisor automatically manages routing between specialized agents:
    - data_agent: Handles data retrieval (orders, tickets)
    - support_agent: Handles general support queries
    - document_agent: Handles document management (CRUD operations)

    Returns:
        StateGraph: Compiled workflow ready to execute
    """
    if checkpointer is None:
        checkpointer = MemorySaver()

    # Get the supervisor's LLM (decision_agent config)
    supervisor_model = get_llm("decision_agent")

    # Get all specialized agents
    agents = get_all_agents(checkpointer)

    # Create supervisor with custom prompt
    supervisor_prompt = """You are a supervisor managing a team of specialized agents.

Your team:
- data_agent: Handles order status checks, ticket lookups, and data retrieval tasks
- support_agent: Handles general questions, explanations, and support conversations  
- document_agent: Handles document management (create, search, list, get, update, delete documents)

Your task: Analyze the user's request and route it to the most appropriate agent.

Guidelines:
- If the user asks about orders or tickets → route to data_agent
- If the user asks about documents (create, search, list, etc.) → route to document_agent
- If the user asks general questions or needs explanations → route to support_agent
- If unsure → default to support_agent

After an agent completes its task, you can either:
1. Route to another agent if more work is needed
2. End the conversation if the task is complete
"""

    # Create the supervisor workflow
    workflow = create_supervisor(
        agents=agents,
        model=supervisor_model,
        prompt=supervisor_prompt,
        supervisor_name="supervisor",
    )

    # Compile the workflow
    app = workflow.compile(checkpointer=checkpointer)

    return app
