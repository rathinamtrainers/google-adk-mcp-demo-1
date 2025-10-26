"""
RBAC (Role-Based Access Control) module
"""
from .permissions import check_permission, require_permission
from .roles import init_default_roles

__all__ = [
    "check_permission",
    "require_permission",
    "init_default_roles",
]
