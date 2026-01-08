import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from .models import AIProvider, AgentConfig

def get_llm(agent_name: str):
    """
    Retrieves the AgentConfig from the database and returns the corresponding LangChain ChatModel.
    If configuration doesn't exist, it falls back to a default OpenAI model or raises an error.
    """
    try:
        config = AgentConfig.objects.get(name=agent_name)
    except AgentConfig.DoesNotExist:
        # Fallback or Error. For now, let's raise a helpful error or return a default.
        # Returning None to let the caller handle it or raising generic error.
        raise ValueError(f"AgentConfig with name '{agent_name}' not found. Please create it in Admin.")

    if not config.is_active:
        raise ValueError(f"Agent '{agent_name}' is disabled.")

    temperature = config.temperature
    model_name = config.model_name
    
    if config.provider == AIProvider.OPENAI:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
             raise ValueError("OPENAI_API_KEY not found in environment")
        return ChatOpenAI(model=model_name, temperature=temperature, api_key=api_key)

    elif config.provider == AIProvider.ANTHROPIC:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
             raise ValueError("ANTHROPIC_API_KEY not found in environment")
        return ChatAnthropic(model=model_name, temperature=temperature, api_key=api_key)

    elif config.provider == AIProvider.GOOGLE:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
             raise ValueError("GOOGLE_API_KEY not found in environment")
        return ChatGoogleGenerativeAI(model=model_name, temperature=temperature, google_api_key=api_key)

    elif config.provider == AIProvider.MISTRAL:
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
             raise ValueError("MISTRAL_API_KEY not found in environment")
        return ChatMistralAI(model=model_name, temperature=temperature, api_key=api_key)

    else:
        raise ValueError(f"Unsupported provider: {config.provider}")
