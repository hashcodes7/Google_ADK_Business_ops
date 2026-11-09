"""Google ADK Inbound Adapter: Exposes controlled user administration tools."""
from app.services.user_service import user_service
from app.core.security import create_security_context, Role
from app.core.exceptions import UnauthorizedException


def get_all_users(context=None) -> list | str:
    """
    Get all users from the system.
    Only users with Admin role are authorized to view the user list.
    If the caller is not an Admin, returns an explicit permission denial message.
    """
    if context is None:
        context = create_security_context(actor="agent")

    # Verify if caller has Admin role
    if context.role != Role.ADMIN:
        return "You do not have sufficient permissions to view all users. (Admin role required)"

    try:
        users = user_service.get_all_users(context=context)
        return users
    except UnauthorizedException:
        return "You do not have sufficient permissions to view all users. (Admin role required)"
