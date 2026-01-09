from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .agents import AgentState, data_agent_node, support_agent_node, document_agent_node
from .supervisor import create_supervisor_node


def build_graph():
    """
    Constructs the LangGraph for the multi-agent system with Supervisor pattern.

    The supervisor intelligently routes requests to specialized agents:
    - data_agent: Handles data retrieval (orders, tickets)
    - support_agent: Handles general support queries
    - document_agent: Handles document management (CRUD operations)
    """
    workflow = StateGraph(AgentState)

    # Create supervisor node with available agents
    available_agents = ["data_agent", "support_agent", "document_agent"]
    supervisor = create_supervisor_node(available_agents)

    # Add Nodes
    workflow.add_node("supervisor", supervisor)  # Supervisor replaces decision_agent
    workflow.add_node("data_agent", data_agent_node)
    workflow.add_node("support_agent", support_agent_node)
    workflow.add_node("document_agent", document_agent_node)  # NEW: Document agent

    # Add Edges
    workflow.add_edge(START, "supervisor")  # Start with supervisor

    # Conditional Edges from Supervisor
    def route_from_supervisor(state: AgentState):
        """Route based on supervisor's decision."""
        return state["next_step"]

    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "data_agent": "data_agent",
            "support_agent": "support_agent",
            "document_agent": "document_agent",  # NEW: Document routing
            "end": END,  # Allow supervisor to end directly if needed
        },
    )

    # Edges to End
    workflow.add_edge("data_agent", END)
    workflow.add_edge("support_agent", END)
    workflow.add_edge("document_agent", END)  # NEW: Document to end

    # Persistence
    memory = MemorySaver()

    # Compile
    app = workflow.compile(checkpointer=memory)
    return app
