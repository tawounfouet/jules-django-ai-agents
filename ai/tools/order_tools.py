"""
Order-related tools for AI agents.
"""

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from business.models import Order
from ai.permissions import check_user_can_access_order


@tool
def check_order_status(order_id: int, config: RunnableConfig = None) -> str:
    """
    Check the status of an order by its ID.

    Args:
        order_id: The ID of the order to check
        config: Runtime configuration containing user context

    Returns:
        str: Order status message or error message
    """
    # Extract user context if available for permission checks
    user_id = None
    if config:
        configurable = config.get("configurable", {})
        user_id = configurable.get("user_id")

    # Check permissions
    if user_id and not check_user_can_access_order(user_id, order_id):
        return f"You do not have permission to access order {order_id}."

    try:
        order = Order.objects.get(id=order_id)
        return f"Order {order_id} is currently {order.status}."
    except Order.DoesNotExist:
        return f"Order {order_id} not found."


# Export all order tools
order_tools = [check_order_status]
