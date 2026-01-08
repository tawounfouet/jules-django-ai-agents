from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .agents import AgentState, decision_node, data_agent_node, support_agent_node

def build_graph():
    """
    Constructs the LangGraph for the multi-agent system.
    """
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("decision_agent", decision_node)
    workflow.add_node("data_agent", data_agent_node)
    workflow.add_node("support_agent", support_agent_node)

    # Add Edges
    workflow.add_edge(START, "decision_agent")

    # Conditional Edges from Decision Agent
    def route_decision(state: AgentState):
        return state["next_step"]

    workflow.add_conditional_edges(
        "decision_agent",
        route_decision,
        {
            "data_agent": "data_agent",
            "support_agent": "support_agent"
        }
    )

    # Edges to End (simplification for POC)
    workflow.add_edge("data_agent", END)
    workflow.add_edge("support_agent", END)

    # Persistence
    memory = MemorySaver()

    # Compile
    app = workflow.compile(checkpointer=memory)
    return app
