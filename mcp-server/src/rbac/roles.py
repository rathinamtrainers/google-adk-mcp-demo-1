"""
Default roles and permissions initialization
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from auth.models import Role, Permission, User
from auth.jwt_handler import get_password_hash


# Default role configurations
DEFAULT_ROLES = {
    "admin": {
        "description": "Full system access including admin functions",
        "rate_limit": 1000,
        "permissions": [
            {"tool_name": "*", "action": "*", "description": "All tools, all actions"},
        ]
    },
    "developer": {
        "description": "Can execute all calculator tools",
        "rate_limit": 100,
        "permissions": [
            {"tool_name": "*", "action": "list", "description": "List all tools"},
            {"tool_name": "add", "action": "execute", "description": "Execute add tool"},
            {"tool_name": "subtract", "action": "execute", "description": "Execute subtract tool"},
            {"tool_name": "multiply", "action": "execute", "description": "Execute multiply tool"},
            {"tool_name": "divide", "action": "execute", "description": "Execute divide tool"},
            {"tool_name": "percentage", "action": "execute", "description": "Execute percentage tool"},
            {"tool_name": "sqrt", "action": "execute", "description": "Execute sqrt tool"},
            {"tool_name": "power", "action": "execute", "description": "Execute power tool"},
        ]
    },
    "viewer": {
        "description": "Read-only access to list tools",
        "rate_limit": 10,
        "permissions": [
            {"tool_name": "*", "action": "list", "description": "List all tools"},
        ]
    }
}


async def init_default_roles(db: AsyncSession) -> None:
    """
    Initialize default roles and permissions in the database

    Args:
        db: Database session
    """
    print("Initializing default roles and permissions...")

    for role_name, role_config in DEFAULT_ROLES.items():
        # Check if role already exists
        result = await db.execute(
            select(Role).where(Role.name == role_name)
        )
        role = result.scalar_one_or_none()

        if not role:
            # Create role
            role = Role(
                name=role_name,
                description=role_config["description"],
                rate_limit=role_config["rate_limit"],
                is_system_role=True
            )
            db.add(role)
            await db.flush()  # Flush to get role.id
            print(f"  Created role: {role_name}")
        else:
            print(f"  Role already exists: {role_name}")

        # Add permissions to role
        for perm_config in role_config["permissions"]:
            # Check if permission exists
            result = await db.execute(
                select(Permission).where(
                    Permission.tool_name == perm_config["tool_name"],
                    Permission.action == perm_config["action"]
                )
            )
            permission = result.scalar_one_or_none()

            if not permission:
                # Create permission
                permission = Permission(
                    tool_name=perm_config["tool_name"],
                    action=perm_config["action"],
                    description=perm_config["description"]
                )
                db.add(permission)
                await db.flush()
                print(f"    Created permission: {perm_config['tool_name']}:{perm_config['action']}")

            # Link permission to role if not already linked
            if permission not in role.permissions:
                role.permissions.append(permission)
                print(f"    Linked permission to {role_name}: {perm_config['tool_name']}:{perm_config['action']}")

    await db.commit()
    print("Default roles and permissions initialized successfully!")


async def create_default_admin_user(db: AsyncSession, username: str = "admin", password: str = "admin123") -> User:
    """
    Create a default admin user

    Args:
        db: Database session
        username: Admin username
        password: Admin password

    Returns:
        Created User object
    """
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.username == username)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        print(f"Admin user '{username}' already exists")
        return existing_user

    # Get admin role
    result = await db.execute(
        select(Role).where(Role.name == "admin")
    )
    admin_role = result.scalar_one_or_none()

    if not admin_role:
        raise ValueError("Admin role not found. Run init_default_roles() first.")

    # Create user
    admin_user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=get_password_hash(password),
        is_active=True,
        is_superuser=True,
        full_name="System Administrator"
    )

    # Generate API key
    admin_user.generate_api_key()

    # Assign admin role
    admin_user.roles.append(admin_role)

    db.add(admin_user)
    await db.commit()
    await db.refresh(admin_user)

    print(f"Created admin user: {username}")
    print(f"  Password: {password}")
    print(f"  API Key: {admin_user.api_key}")

    return admin_user


async def create_demo_users(db: AsyncSession) -> list[User]:
    """
    Create demo users for testing

    Args:
        db: Database session

    Returns:
        List of created User objects
    """
    demo_users_config = [
        {
            "username": "developer1",
            "email": "developer1@example.com",
            "password": "dev123",
            "role": "developer",
            "full_name": "Demo Developer"
        },
        {
            "username": "viewer1",
            "email": "viewer1@example.com",
            "password": "view123",
            "role": "viewer",
            "full_name": "Demo Viewer"
        }
    ]

    created_users = []

    for user_config in demo_users_config:
        # Check if user exists
        result = await db.execute(
            select(User).where(User.username == user_config["username"])
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"User '{user_config['username']}' already exists")
            created_users.append(existing_user)
            continue

        # Get role
        result = await db.execute(
            select(Role).where(Role.name == user_config["role"])
        )
        role = result.scalar_one_or_none()

        if not role:
            print(f"Role '{user_config['role']}' not found, skipping user creation")
            continue

        # Create user
        user = User(
            username=user_config["username"],
            email=user_config["email"],
            hashed_password=get_password_hash(user_config["password"]),
            is_active=True,
            full_name=user_config["full_name"]
        )

        # Generate API key
        user.generate_api_key()

        # Assign role
        user.roles.append(role)

        db.add(user)
        created_users.append(user)

        print(f"Created user: {user_config['username']} with role: {user_config['role']}")
        print(f"  Password: {user_config['password']}")

    await db.commit()

    # Refresh all users to get API keys
    for user in created_users:
        await db.refresh(user)
        print(f"  API Key for {user.username}: {user.api_key}")

    return created_users
