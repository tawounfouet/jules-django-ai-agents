"""
Support ticket-related tools for AI agents.
"""

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from business.models import Ticket
from ai.permissions import check_user_can_access_ticket


@tool
def get_ticket_info(ticket_id: int, config: RunnableConfig = None) -> str:
    """
    Get details of a support ticket.

    Args:
        ticket_id: The ID of the ticket to retrieve
        config: Runtime configuration containing user context

    Returns:
        str: Ticket information or error message
    """
    # Extract user context if available for permission checks
    user_id = None
    if config:
        configurable = config.get("configurable", {})
        user_id = configurable.get("user_id")

    # Check permissions
    if user_id and not check_user_can_access_ticket(user_id, ticket_id):
        return f"You do not have permission to access ticket {ticket_id}."

    try:
        ticket = Ticket.objects.get(id=ticket_id)
        return f"Ticket {ticket.id}: {ticket.subject} - {ticket.status}"
    except Ticket.DoesNotExist:
        return f"Ticket {ticket_id} not found."


# Export all ticket tools
ticket_tools = [get_ticket_info]
