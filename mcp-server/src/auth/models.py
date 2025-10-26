"""
Database models for authentication and authorization
"""
from datetime import datetime
from typing import List
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text, JSON
)
from sqlalchemy.orm import relationship
from database import Base
import secrets


# Association tables for many-to-many relationships
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    api_key = Column(String(64), unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Metadata
    full_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

    def generate_api_key(self):
        """Generate a secure API key"""
        self.api_key = secrets.token_urlsafe(48)
        return self.api_key

    def has_permission(self, tool_name: str, action: str) -> bool:
        """Check if user has specific permission"""
        for role in self.roles:
            for permission in role.permissions:
                if permission.tool_name == tool_name and permission.action == action:
                    return True
                # Check for wildcard permissions
                if permission.tool_name == "*" and permission.action == action:
                    return True
                if permission.tool_name == tool_name and permission.action == "*":
                    return True
                if permission.tool_name == "*" and permission.action == "*":
                    return True
        return self.is_superuser


class Role(Base):
    """Role model for RBAC"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_system_role = Column(Boolean, default=False)  # System roles can't be deleted
    created_at = Column(DateTime, default=datetime.utcnow)

    # Rate limiting config per role (requests per minute)
    rate_limit = Column(Integer, default=100)

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base):
    """Permission model for fine-grained access control"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    tool_name = Column(String(50), index=True, nullable=False)  # e.g., "add", "multiply", "*" for all
    action = Column(String(20), nullable=False)  # "list", "execute", "*" for all
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    def __repr__(self):
        return f"<Permission {self.tool_name}:{self.action}>"


class AuditLog(Base):
    """Audit log for tracking all API calls"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    username = Column(String(50), nullable=True)  # Denormalized for performance
    tool_name = Column(String(50), nullable=True)
    action = Column(String(20), nullable=False)  # "list_tools", "execute_tool", "login", etc.
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, etc.
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    request_payload = Column(JSON, nullable=True)
    response_status = Column(Integer, nullable=True)
    response_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.username}:{self.action} at {self.created_at}>"


class IPWhitelist(Base):
    """IP whitelist/blacklist for network-level access control"""
    __tablename__ = "ip_whitelist"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), unique=True, index=True, nullable=False)  # IPv4 or IPv6
    ip_type = Column(String(10), default="whitelist")  # "whitelist" or "blacklist"
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(50), nullable=True)  # Username who added this

    def __repr__(self):
        return f"<IPWhitelist {self.ip_address} ({self.ip_type})>"


class RefreshToken(Base):
    """Refresh token for JWT authentication"""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)

    # Metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken user_id={self.user_id}, expires={self.expires_at}>"
