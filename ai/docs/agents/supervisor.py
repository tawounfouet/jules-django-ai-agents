"""
Supervisor Pattern for Multi-Agent Orchestration.

The supervisor is an LLM-based agent that decides which specialized agent
should handle a given task. This provides more intelligent and flexible
routing than hardcoded if/else logic.
"""

from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate

from .utils import get_llm
from .agents import AgentState


def create_supervisor_node(available_agents: list[str]):
    """
    Creates a supervisor node function that routes to available agents.

    Args:
        available_agents: List of agent keys (e.g., ['data_agent', 'support_agent'])

    Returns:
        A node function that can be used in a LangGraph StateGraph
    """

    def supervisor_node(state: AgentState, config: RunnableConfig):
        """
        Supervisor agent that decides which specialized agent should handle the task.
        Uses an LLM to make intelligent routing decisions.
        """
        messages = state["messages"]

        # Get the supervisor's LLM (using decision_agent config for now)
        try:
            model = get_llm("decision_agent")
        except Exception as e:
            # Fallback to first available agent
            return {
                "next_step": available_agents[0] if available_agents else "end",
                "messages": [AIMessage(content=f"Error loading supervisor: {e}")],
            }

        # Create routing prompt
        agents_list = "\n".join([f"- {agent}" for agent in available_agents])

        system_prompt = f"""You are a supervisor agent that routes user requests to specialized agents.

Available agents:
{agents_list}

Agent descriptions:
- data_agent: Handles order status checks, ticket lookups, and data retrieval tasks
- support_agent: Handles general questions, explanations, and support conversations
- document_agent: Handles document management (create, search, list, get, update, delete documents)

Based on the user's request, decide which agent should handle it.
Respond with ONLY the agent name (e.g., 'data_agent', 'support_agent', or 'document_agent').
Do not include any other text in your response."""

        system_message = SystemMessage(content=system_prompt)

        # Get LLM decision
        response = model.invoke([system_message] + messages)

        # Parse the decision
        decision = response.content.strip().lower()

        # Validate decision
        if decision not in available_agents:
            # Default to support agent if decision is unclear
            decision = "support_agent"

        routing_message = AIMessage(
            content=f"🔀 Routing to {decision.replace('_', ' ').title()}..."
        )

        return {"next_step": decision, "messages": [routing_message]}

    return supervisor_node


def create_supervisor_prompt_template(available_agents: list[dict]):
    """
    Creates a structured prompt template for the supervisor.

    Args:
        available_agents: List of agent configs with 'key', 'name', and 'description'

    Example:
        agents = [
            {
                "key": "data_agent",
                "name": "Data Agent",
                "description": "Retrieves order and ticket information"
            },
            {
                "key": "support_agent",
                "name": "Support Agent",
                "description": "Provides general support and answers questions"
            }
        ]

    Returns:
        ChatPromptTemplate for supervisor routing
    """
    agents_description = "\n".join(
        [
            f"- {agent['key']}: {agent['name']} - {agent['description']}"
            for agent in available_agents
        ]
    )

    agent_keys = [agent["key"] for agent in available_agents]

    system_template = f"""You are a supervisor managing a team of specialized agents.

Your team:
{agents_description}

Your task is to analyze the user's request and route it to the most appropriate agent.
Respond with ONLY the agent key: {', '.join(agent_keys)}

Guidelines:
- If the user asks about specific data (orders, tickets, status), route to data_agent
- If the user asks general questions or needs explanations, route to support_agent
- If unsure, default to support_agent

Response format: Just the agent key, nothing else."""

    return ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            ("placeholder", "{messages}"),
        ]
    )


# Example configuration for our current agents
CURRENT_AGENTS = [
    {
        "key": "data_agent",
        "name": "Data Retrieval Agent",
        "description": "Checks order status, retrieves ticket information, and accesses customer data",
    },
    {
        "key": "support_agent",
        "name": "Customer Support Agent",
        "description": "Provides general support, answers questions, and handles conversations",
    },
    {
        "key": "document_agent",
        "name": "Document Management Agent",
        "description": "Creates, searches, lists, retrieves, updates, and deletes user documents",
    },
]
