import os
import importlib
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_mistralai import ChatMistralAI
from .models import Agent, AgentTool

def get_llm(agent_key: str):
    """
    Retrieves the Agent from the database (by unique key) and returns the LangChain ChatModel.
    """
    try:
        agent = Agent.objects.get(key=agent_key)
    except Agent.DoesNotExist:
        raise ValueError(f"Agent with key '{agent_key}' not found. Please create it in Admin.")

    if not agent.is_active:
        raise ValueError(f"Agent '{agent_key}' is disabled.")

    temperature = agent.temperature
    model_name = agent.llm_model
    provider = agent.llm_provider
    
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
             raise ValueError("OPENAI_API_KEY not found in environment")
        return ChatOpenAI(model=model_name, temperature=temperature, api_key=api_key)

    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
             raise ValueError("ANTHROPIC_API_KEY not found in environment")
        return ChatAnthropic(model=model_name, temperature=temperature, api_key=api_key)

    elif provider == "local":
        # Placeholder for local LLM (e.g. Ollama)
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(model=model_name, temperature=temperature)

    else:
        raise ValueError(f"Unsupported provider: {provider}")


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
    agent_tools = AgentTool.objects.filter(agent=agent, allowed=True).select_related('tool')
    
    loaded_tools = []
    for at in agent_tools:
        path = at.tool.python_path
        try:
            module_name, func_name = path.rsplit('.', 1)
            module = importlib.import_module(module_name)
            tool_func = getattr(module, func_name)
            loaded_tools.append(tool_func)
        except (ImportError, AttributeError, ValueError) as e:
            print(f"Error loading tool {path}: {e}")
            # In production, we might want to log this but not crash the whole agent?
            # Or crash during initialization. For now, skipping.
            continue
            
    return loaded_tools
