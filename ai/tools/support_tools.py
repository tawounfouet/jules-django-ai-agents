"""
General support tools for AI agents.
"""

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig


@tool
def create_support_response(
    issue_type: str, details: str, config: RunnableConfig = None
) -> str:
    """
    Generate a standard support response based on issue type.

    Args:
        issue_type: Type of issue (e.g., 'order_status', 'technical')
        details: Additional details about the issue
        config: Runtime configuration containing user context

    Returns:
        str: Generated support response
    """
    # Extract user context if available
    user_id = None
    if config:
        configurable = config.get("configurable", {})
        user_id = configurable.get("user_id")

    if issue_type == "order_status":
        return f"Regarding your order status: {details} If you need more help, please contact us."
    elif issue_type == "technical":
        return "Please try restarting your device. If the issue persists, reply to this ticket."
    else:
        return "Thank you for contacting support. We will get back to you shortly."


# Export all support tools
support_tools = [create_support_response]
