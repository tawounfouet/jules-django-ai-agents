"""
Permission checks for AI agents.
This module provides functions to verify user permissions for various operations.
"""

from business.models import Order, Ticket


def check_user_can_access_order(user_id: int, order_id: int) -> bool:
    """
    Check if a user has permission to access an order.
    Returns True if user owns the order (via customer) or is staff.

    Args:
        user_id: The ID of the user requesting access
        order_id: The ID of the order to check

    Returns:
        bool: True if user has access, False otherwise
    """
    try:
        order = Order.objects.get(id=order_id)
        # For now, we check if customer.id matches user_id
        # In production, you'd link Customer to User model
        if order.customer_id == user_id:
            return True
        # Check if user is staff
        return is_staff_user(user_id)
    except Order.DoesNotExist:
        return False


def check_user_can_access_ticket(user_id: int, ticket_id: int) -> bool:
    """
    Check if a user has permission to access a support ticket.
    Returns True if user owns the ticket or is staff.

    Args:
        user_id: The ID of the user requesting access
        ticket_id: The ID of the ticket to check

    Returns:
        bool: True if user has access, False otherwise
    """
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        # Check if user is ticket creator or staff
        if ticket.customer_id == user_id:
            return True
        return is_staff_user(user_id)
    except Ticket.DoesNotExist:
        return False


def is_staff_user(user_id: int) -> bool:
    """
    Check if a user is a staff member.

    Args:
        user_id: The ID of the user to check

    Returns:
        bool: True if user is staff, False otherwise
    """
    from users.models import User

    try:
        user = User.objects.get(id=user_id)
        return user.is_staff
    except User.DoesNotExist:
        return False


def check_permission(user_id: int, action: str, resource: str) -> bool:
    """
    Generic permission check function.
    This is a placeholder for future integration with a permission system
    like django-guardian, django-rules, or permit.io

    Args:
        user_id: The ID of the user requesting permission
        action: The action to perform (e.g., 'read', 'write', 'delete', 'create', 'update')
        resource: The resource type (e.g., 'order', 'ticket', 'document')

    Returns:
        bool: True if user has permission, False otherwise
    """
    # TODO: Integrate with a proper permission system (e.g., permit.io)
    # For now, allow all authenticated users
    if user_id is None:
        return False

    # Staff users have all permissions
    if is_staff_user(user_id):
        return True

    # Regular users have specific permissions based on resource
    if resource == "document":
        # Documents: Full CRUD for authenticated users (they own their docs)
        if action in ["read", "list", "create", "update", "delete"]:
            return True

    # Orders and Tickets: read-only for regular users
    if resource in ["order", "ticket"]:
        if action in ["read", "list"]:
            return True

    return False
