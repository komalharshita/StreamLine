from typing import Any
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.auth import AssignRoleRequest, UserProfile

router = APIRouter()


@router.get("/me", response_model=UserProfile)
def get_me(current_user: dict[str, Any] = Depends(get_current_user)) -> UserProfile:
    """Returns the profile metadata of the current authenticated user."""
    return UserProfile(
        uid=current_user.get("uid", ""),
        email=current_user.get("email", ""),
        name=current_user.get("name"),
        roles=current_user.get("roles", []),
        is_active=current_user.get("email_verified", True),
    )


@router.post("/role", response_model=UserProfile)
def assign_role(
    request: AssignRoleRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> UserProfile:
    """Simulates assigning a new security role to the user profile."""
    # Return updated user profile
    roles = list(current_user.get("roles", []))
    if request.role not in roles:
        roles.append(request.role)

    return UserProfile(
        uid=current_user.get("uid", ""),
        email=current_user.get("email", ""),
        name=current_user.get("name"),
        roles=roles,
        is_active=current_user.get("email_verified", True),
    )
