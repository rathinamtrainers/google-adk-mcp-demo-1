"""
FastAPI dependencies for authentication and authorization
"""
import os
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, Header, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from auth.models import User
from auth.jwt_handler import verify_access_token
from auth.api_key_handler import verify_api_key

# Security schemes
security = HTTPBearer(auto_error=False)

# Configuration
RBAC_ENFORCEMENT_MODE = os.getenv("RBAC_ENFORCEMENT_MODE", "strict")  # "strict" or "permissive"


async def get_current_user_from_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from JWT token

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        User object or None
    """
    if not credentials:
        return None

    token = credentials.credentials

    # Verify JWT token
    payload = verify_access_token(token)
    if not payload:
        return None

    # Get user from database
    user_id = int(payload.get("sub"))
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if user:
        # Update last login (optional, can be expensive)
        # user.last_login = datetime.utcnow()
        # await db.commit()
        pass

    return user


async def get_current_user_from_api_key(
    x_api_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from API key

    Args:
        x_api_key: API key from header
        db: Database session

    Returns:
        User object or None
    """
    if not x_api_key:
        return None

    user = await verify_api_key(x_api_key, db)
    return user


async def get_current_user(
    jwt_user: Optional[User] = Depends(get_current_user_from_jwt),
    api_key_user: Optional[User] = Depends(get_current_user_from_api_key),
    request: Request = None
) -> Optional[User]:
    """
    Get current user from either JWT or API key

    Priority: JWT first, then API key

    Args:
        jwt_user: User from JWT token
        api_key_user: User from API key
        request: FastAPI request object

    Returns:
        User object or None
    """
    # Try JWT first
    if jwt_user:
        return jwt_user

    # Try API key
    if api_key_user:
        return api_key_user

    # Backward compatibility: Check if request is from Vertex AI service account
    if RBAC_ENFORCEMENT_MODE == "permissive":
        # In permissive mode, allow unauthenticated access
        # This is for backward compatibility during migration
        return None

    return None


async def require_authentication(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Require authentication - raises 401 if not authenticated

    Args:
        current_user: Current user from authentication

    Returns:
        User object

    Raises:
        HTTPException: 401 if not authenticated
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return current_user


async def require_admin(
    current_user: User = Depends(require_authentication)
) -> User:
    """
    Require admin/superuser privileges

    Args:
        current_user: Current authenticated user

    Returns:
        User object

    Raises:
        HTTPException: 403 if not admin
    """
    if not current_user.is_superuser:
        # Check if user has admin role
        admin_role = any(role.name == "admin" for role in current_user.roles)
        if not admin_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )

    return current_user


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request

    Args:
        request: FastAPI request

    Returns:
        Client IP address
    """
    # Check X-Forwarded-For header (for proxies/load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the list
        return forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to direct client
    return request.client.host if request.client else "unknown"
