import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


def get_llm_for_agent(agent):
    """
    Factory function to create LLM instances from Agent model.
    Centralizes API key management and model instantiation.

    Args:
        agent: Agent model instance

    Returns:
        LangChain ChatModel instance

    Raises:
        ValueError: If provider is unsupported or API key is missing
    """
    temperature = agent.temperature
    model_name = agent.llm_model
    provider = agent.llm_provider

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        return ChatOpenAI(
            model=model_name, temperature=temperature, api_key=api_key, max_retries=2
        )

    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        return ChatAnthropic(
            model=model_name, temperature=temperature, api_key=api_key, max_retries=2
        )

    elif provider == "local":
        # Placeholder for local LLM (e.g. Ollama)
        from langchain_community.chat_models import ChatOllama

        return ChatOllama(model=model_name, temperature=temperature)

    else:
        raise ValueError(f"Unsupported provider: {provider}")
