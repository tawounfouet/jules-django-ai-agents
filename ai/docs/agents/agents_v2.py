"""
Agent Factory using LangGraph's official create_react_agent.

This version uses the official LangGraph prebuilt functions instead of manual implementation.
Benefits:
- Less code to maintain
- Official support and updates
- Battle-tested implementations
- Better error handling
"""

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from .utils import get_llm, load_tools_for_agent


def create_data_agent(checkpointer=None):
    """
    Creates a data retrieval agent using create_react_agent.

    Returns:
        CompiledStateGraph: A compiled agent ready to use
    """
    llm = get_llm("data_agent")
    tools = load_tools_for_agent("data_agent")

    if checkpointer is None:
        checkpointer = MemorySaver()

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt="You are a data retrieval agent. Help users check order status and ticket information.",
        checkpointer=checkpointer,
        name="data_agent",
    )

    return agent


def create_support_agent(checkpointer=None):
    """
    Creates a customer support agent using create_react_agent.

    Returns:
        CompiledStateGraph: A compiled agent ready to use
    """
    llm = get_llm("support_agent")

    if checkpointer is None:
        checkpointer = MemorySaver()

    agent = create_react_agent(
        model=llm,
        tools=[],  # Support agent doesn't need tools
        prompt="You are a helpful customer support agent. Answer questions clearly and professionally.",
        checkpointer=checkpointer,
        name="support_agent",
    )

    return agent


def create_document_agent(checkpointer=None):
    """
    Creates a document management agent using create_react_agent.

    Returns:
        CompiledStateGraph: A compiled agent ready to use
    """
    llm = get_llm("document_agent")
    tools = load_tools_for_agent("document_agent")

    if checkpointer is None:
        checkpointer = MemorySaver()

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt="You are a document management agent. Help users create, search, update, and delete their documents.",
        checkpointer=checkpointer,
        name="document_agent",
    )

    return agent


# Factory function to get all agents
def get_all_agents(checkpointer=None):
    """
    Get all available agents.

    Returns:
        list: List of compiled agents
    """
    return [
        create_data_agent(checkpointer),
        create_support_agent(checkpointer),
        create_document_agent(checkpointer),
    ]
