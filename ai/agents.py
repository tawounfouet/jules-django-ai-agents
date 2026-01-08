from typing import TypedDict, Annotated, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from .tools import check_order_status, get_ticket_info, create_support_response

# --- State Definition ---
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next_step: str

# --- Mocks for LLM (since we don't have an API key) ---

class MockLLM:
    """A simple mock LLM that acts based on input text keywords."""

    def __init__(self, role="router"):
        self.role = role

    def invoke(self, messages):
        # We need to look at the *conversation history* to find the user's intent or the order ID.
        # But for 'data' agent, the immediate previous message might be "Routing to Data Agent..." (AIMessage).
        # We should find the last HumanMessage to get the actual request.

        last_human_message = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                last_human_message = msg
                break

        content = last_human_message.content.lower() if last_human_message else ""

        if self.role == "decision":
            # Routing logic based on keywords
            if "order" in content or "status" in content:
                return AIMessage(content="ROUTING_TO_DATA")
            else:
                return AIMessage(content="ROUTING_TO_SUPPORT")

        elif self.role == "data":
            # Extract ID simply for the mock
            import re
            match = re.search(r'\d+', content)
            order_id = match.group(0) if match else "1"

            # Simulate tool call
            return AIMessage(
                content="",
                tool_calls=[{
                    "name": "check_order_status",
                    "args": {"order_id": int(order_id)},
                    "id": "call_123"
                }]
            )

        elif self.role == "support":
             return AIMessage(content="Hello, how can I help you today?")

        return AIMessage(content="I don't know what to do.")


# --- Node Definitions ---

def decision_node(state: AgentState, config: RunnableConfig):
    """
    Decides whether to route to DataAgent or SupportAgent.
    In a real app, this would use an LLM to classify intent.
    """
    messages = state["messages"]
    # For POC: simple keyword match or use the MockLLM
    # We'll use the MockLLM to simulate an agent thinking
    llm = MockLLM(role="decision")
    response = llm.invoke(messages)

    if "ROUTING_TO_DATA" in response.content:
        return {"next_step": "data_agent", "messages": [AIMessage(content="Routing to Data Agent...")]}
    else:
        return {"next_step": "support_agent", "messages": [AIMessage(content="Routing to Support Agent...")]}


def data_agent_node(state: AgentState, config: RunnableConfig):
    """
    Handles data retrieval tasks.
    """
    messages = state["messages"]
    llm = MockLLM(role="data")
    response = llm.invoke(messages)

    # If the LLM decided to call a tool (simulated)
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        if tool_call["name"] == "check_order_status":
            # Execute the tool
            result = check_order_status.invoke(tool_call["args"])

            tool_msg = ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
                name=tool_call["name"]
            )
            # Return the AI message (tool call) AND the Tool message (result)
            return {"messages": [response, tool_msg], "next_step": "end"}

    return {"messages": [response], "next_step": "end"}


def support_agent_node(state: AgentState, config: RunnableConfig):
    """
    Handles general support queries.
    """
    # Simply respond with a canned message or use a tool
    return {"messages": [AIMessage(content="This is the Support Agent. I see you have a query not related to order data. How can I assist regarding our policies?")], "next_step": "end"}
