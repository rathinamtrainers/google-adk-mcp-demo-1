"""
Permission checking and enforcement
"""
from typing import Optional
from fastapi import HTTPException, status, Depends
from auth.models import User
from auth.dependencies import require_authentication


def check_permission(user: User, tool_name: str, action: str) -> bool:
    """
    Check if user has permission for a specific tool and action

    Args:
        user: User object
        tool_name: Name of the tool (e.g., "add", "multiply")
        action: Action type ("list", "execute")

    Returns:
        True if user has permission, False otherwise
    """
    # Superusers have all permissions
    if user.is_superuser:
        return True

    # Check user's roles and permissions
    for role in user.roles:
        for permission in role.permissions:
            # Check exact match
            if permission.tool_name == tool_name and permission.action == action:
                return True

            # Check wildcard permissions
            if permission.tool_name == "*" and permission.action == action:
                return True

            if permission.tool_name == tool_name and permission.action == "*":
                return True

            if permission.tool_name == "*" and permission.action == "*":
                return True

    return False


async def require_permission(
    tool_name: str,
    action: str,
    current_user: User = Depends(require_authentication)
) -> User:
    """
    FastAPI dependency to require a specific permission

    Args:
        tool_name: Name of the tool
        action: Action type
        current_user: Current authenticated user

    Returns:
        User object if authorized

    Raises:
        HTTPException: 403 if not authorized
    """
    if not check_permission(current_user, tool_name, action):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {tool_name}:{action}"
        )

    return current_user


def create_permission_dependency(tool_name: str, action: str):
    """
    Factory function to create a permission dependency for a specific tool

    Usage:
        @app.post("/tools/add", dependencies=[Depends(create_permission_dependency("add", "execute"))])
        async def call_add_tool():
            ...

    Args:
        tool_name: Name of the tool
        action: Action type

    Returns:
        FastAPI dependency function
    """
    async def permission_checker(
        current_user: User = Depends(require_authentication)
    ) -> User:
        return await require_permission(tool_name, action, current_user)

    return permission_checker
