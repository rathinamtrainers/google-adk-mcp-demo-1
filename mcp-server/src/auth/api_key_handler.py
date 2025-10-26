"""
API Key authentication handler
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from auth.models import User
import secrets


async def verify_api_key(api_key: str, db: AsyncSession) -> Optional[User]:
    """
    Verify an API key and return the associated user

    Args:
        api_key: API key to verify
        db: Database session

    Returns:
        User object if valid, None otherwise
    """
    if not api_key:
        return None

    # Query for user with this API key
    result = await db.execute(
        select(User).where(
            User.api_key == api_key,
            User.is_active == True
        )
    )
    user = result.scalar_one_or_none()

    return user


def generate_api_key() -> str:
    """
    Generate a secure random API key

    Returns:
        Secure random API key string
    """
    return secrets.token_urlsafe(48)


async def create_api_key_for_user(user_id: int, db: AsyncSession) -> Optional[str]:
    """
    Create or regenerate an API key for a user

    Args:
        user_id: User ID
        db: Database session

    Returns:
        New API key or None if user not found
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return None

    # Generate new API key
    api_key = generate_api_key()
    user.api_key = api_key

    await db.commit()
    await db.refresh(user)

    return api_key


async def revoke_api_key(user_id: int, db: AsyncSession) -> bool:
    """
    Revoke (delete) a user's API key

    Args:
        user_id: User ID
        db: Database session

    Returns:
        True if revoked, False if user not found
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return False

    user.api_key = None
    await db.commit()

    return True
