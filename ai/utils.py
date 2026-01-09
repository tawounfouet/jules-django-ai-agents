import importlib
from .llms import get_llm_for_agent
from .models import Agent, AgentTool


def get_llm(agent_key: str):
    """
    Retrieves the Agent from the database (by unique key) and returns the LangChain ChatModel.

    Args:
        agent_key: Unique key identifying the agent

    Returns:
        LangChain ChatModel instance configured for the agent

    Raises:
        ValueError: If agent not found or is disabled
    """
    try:
        agent = Agent.objects.get(key=agent_key)
    except Agent.DoesNotExist:
        raise ValueError(
            f"Agent with key '{agent_key}' not found. Please create it in Admin."
        )

    if not agent.is_active:
        raise ValueError(f"Agent '{agent_key}' is disabled.")

    return get_llm_for_agent(agent)


def load_tools_for_agent(agent_key: str):
    """
    Loads allowable tools for a specific agent from the database.
    Returns a list of tool functions/objects.
    """
    try:
        agent = Agent.objects.get(key=agent_key)
    except Agent.DoesNotExist:
        return []

    # Get allowed tools through the M2M relationship
    agent_tools = AgentTool.objects.filter(agent=agent, allowed=True).select_related(
        "tool"
    )

    loaded_tools = []
    for at in agent_tools:
        path = at.tool.python_path
        try:
            module_name, func_name = path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            tool_func = getattr(module, func_name)
            loaded_tools.append(tool_func)
        except (ImportError, AttributeError, ValueError) as e:
            print(f"Error loading tool {path}: {e}")
            # In production, we might want to log this but not crash the whole agent?
            # Or crash during initialization. For now, skipping.
            continue

    return loaded_tools


def get_all_available_tools():
    """
    Get all available tools from the modular tools structure.
    This is useful for loading default tools when database is not yet seeded.

    Returns:
        list: List of all available tool functions
    """
    from ai.tools import (
        order_tools,
        ticket_tools,
        support_tools,
        document_tools,
        tmdb_tools,
    )

    return order_tools + ticket_tools + support_tools + document_tools + tmdb_tools
