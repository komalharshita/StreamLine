from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class TokenPayload(BaseModel):
    """Pydantic model representing decoded JWT claims."""

    sub: str = Field(..., alias="uid", description="Subject UID")
    email: EmailStr = Field(...)
    name: Optional[str] = None
    roles: list[str] = Field(default_factory=list)


class UserProfile(BaseModel):
    """Pydantic schema representing the authenticated user profile."""

    uid: str
    email: EmailStr
    name: Optional[str] = None
    roles: list[str]
    is_active: bool


class AssignRoleRequest(BaseModel):
    """Request payload to assign a workspace role to a user."""

    role: str = Field(..., description="Role name to grant, e.g. admin, analyst")


class UserRegister(BaseModel):
    """Payload to register a new local user."""

    email: str = Field(...)
    password: str = Field(..., min_length=6)
    name: Optional[str] = None


class UserLogin(BaseModel):
    """Payload to login an existing local user."""

    email: str = Field(...)
    password: str = Field(...)


class TokenResponse(BaseModel):
    """Successful authentication token payload."""

    access_token: str
    token_type: str = "bearer"

