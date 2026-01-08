from typing import TypedDict, Annotated, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from .tools import check_order_status
from .utils import get_llm

# --- State Definition ---
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next_step: str

# --- Node Definitions ---

def decision_node(state: AgentState, config: RunnableConfig):
    """
    Decides whether to route to DataAgent or SupportAgent.
    Uses 'decision_agent' configuration.
    """
    messages = state["messages"]
    try:
        model = get_llm("decision_agent")
    except Exception as e:
        # Fallback if config is missing (for safety during development)
        return {"next_step": "support_agent", "messages": [AIMessage(content=f"Error loading decision agent: {e}")]}

    # System instruction for routing
    system_message = SystemMessage(content="""You are a routing agent. 
    If the user asks about order status, tracking, or ticket details, respond with 'ROUTING_TO_DATA'.
    Otherwise, respond with 'ROUTING_TO_SUPPORT'.""")
    
    response = model.invoke([system_message] + messages)

    if "ROUTING_TO_DATA" in response.content:
        return {"next_step": "data_agent", "messages": [AIMessage(content="Routing to Data Agent...")]}
    else:
        return {"next_step": "support_agent", "messages": [AIMessage(content="Routing to Support Agent...")]}


def data_agent_node(state: AgentState, config: RunnableConfig):
    """
    Handles data retrieval tasks. Uses 'data_agent' configuration.
    """
    messages = state["messages"]
    try:
        model = get_llm("data_agent")
        # Bind tools
        model_with_tools = model.bind_tools([check_order_status])
    except Exception as e:
         return {"messages": [AIMessage(content=f"Error loading data agent: {e}")], "next_step": "end"}

    response = model_with_tools.invoke(messages)

    # If the LLM decided to call a tool
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
    Handles general support queries. Uses 'support_agent' configuration.
    """
    messages = state["messages"]
    try:
         model = get_llm("support_agent")
    except Exception as e:
         # Fallback to a simple message if config fails
         return {"messages": [AIMessage(content="I am the Support Agent. I can help with general questions.")], "next_step": "end"}

    response = model.invoke(messages)
    return {"messages": [response], "next_step": "end"}
