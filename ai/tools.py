from langchain_core.tools import tool
from business.models import Order, Ticket

@tool
def check_order_status(order_id: int) -> str:
    """Check the status of an order by its ID."""
    try:
        order = Order.objects.get(id=order_id)
        return f"Order {order_id} is currently {order.status}."
    except Order.DoesNotExist:
        return f"Order {order_id} not found."

@tool
def get_ticket_info(ticket_id: int) -> str:
    """Get details of a support ticket."""
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        return f"Ticket {ticket.id}: {ticket.subject} - {ticket.status}"
    except Ticket.DoesNotExist:
        return f"Ticket {ticket_id} not found."

@tool
def create_support_response(issue_type: str, details: str) -> str:
    """Generate a standard support response based on issue type."""
    if issue_type == "order_status":
        return f"Regarding your order status: {details} If you need more help, please contact us."
    elif issue_type == "technical":
        return "Please try restarting your device. If the issue persists, reply to this ticket."
    else:
        return "Thank you for contacting support. We will get back to you shortly."
