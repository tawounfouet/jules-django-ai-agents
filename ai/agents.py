from typing import TypedDict, Annotated, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from .utils import get_llm, load_tools_for_agent

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
    Handles data retrieval tasks. Uses 'data_agent' configuration and dynamic tools.
    """
    messages = state["messages"]
    try:
        model = get_llm("data_agent")
        tools = load_tools_for_agent("data_agent")
        
        if tools:
            model_with_tools = model.bind_tools(tools)
        else:
            model_with_tools = model # No tools available
            
    except Exception as e:
         return {"messages": [AIMessage(content=f"Error loading data agent: {e}")], "next_step": "end"}

    response = model_with_tools.invoke(messages)

    # Simple tool execution loop (for 1 tool call depth)
    # In a real graph, we might want a prebuilt 'prebuilt_tool_node' or a loop.
    # Here we handle the tool call manually as before.
    if response.tool_calls:
        # We need a map of name -> func to invoke
        tool_map = {t.name: t for t in tools}
        
        executed_messages = [response]
        
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            if tool_name in tool_map:
                tool_func = tool_map[tool_name]
                # Invoke the tool
                # Note: tool_func is a LangChain Tool object, invoke it directly
                try:
                    result = tool_func.invoke(tool_call["args"])
                except Exception as tool_err:
                    result = f"Error executing {tool_name}: {tool_err}"

                tool_msg = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                    name=tool_name
                )
                executed_messages.append(tool_msg)
            else:
                executed_messages.append(
                    ToolMessage(
                         content=f"Tool {tool_name} not found or not allowed.",
                         tool_call_id=tool_call["id"],
                         name=tool_name
                    )
                )

        return {"messages": executed_messages, "next_step": "end"}

    return {"messages": [response], "next_step": "end"}


def support_agent_node(state: AgentState, config: RunnableConfig):
    """
    Handles general support queries. Uses 'support_agent' configuration.
    """
    messages = state["messages"]
    try:
         model = get_llm("support_agent")
    except Exception as e:
         return {"messages": [AIMessage(content="I am the Support Agent. I can help with general questions.")], "next_step": "end"}

    response = model.invoke(messages)
    return {"messages": [response], "next_step": "end"}
