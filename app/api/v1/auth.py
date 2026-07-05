import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.hash import bcrypt
from jose import jwt

from app.api.deps import get_current_user, get_bq_manager
from app.database.bigquery import BigQueryManager
from app.core.config import settings
from app.schemas.auth import (
    AssignRoleRequest,
    UserProfile,
    UserRegister,
    UserLogin,
    TokenResponse,
)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserRegister,
    bq_manager: BigQueryManager = Depends(get_bq_manager),
) -> TokenResponse:
    """Registers a new user inside the local SQLite database and generates a JWT token."""
    email_clean = payload.email.lower().strip()
    
    # Check if user already exists
    cursor = bq_manager.conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email_clean,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    # Hash the password
    hashed_password = bcrypt.hash(payload.password)
    uid = str(uuid.uuid4())
    roles = ["admin"]  # Default workspace administrator role
    created_at = datetime.now(timezone.utc).isoformat()

    try:
        cursor.execute(
            "INSERT INTO users (id, email, password_hash, name, roles, is_active, created_at) VALUES (?, ?, ?, ?, ?, 1, ?)",
            (uid, email_clean, hashed_password, payload.name, ",".join(roles), created_at),
        )
        bq_manager.conn.commit()
    except Exception as e:
        bq_manager.conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database signup transaction failed: {str(e)}",
        )

    # Sign JWT token
    token_data = {
        "uid": uid,
        "email": email_clean,
        "name": payload.name or email_clean.split("@")[0],
        "roles": roles,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: UserLogin,
    bq_manager: BigQueryManager = Depends(get_bq_manager),
) -> TokenResponse:
    """Verifies credentials against local users database and returns a signed JWT token."""
    email_clean = payload.email.lower().strip()

    cursor = bq_manager.conn.cursor()
    cursor.execute("SELECT id, password_hash, name, roles FROM users WHERE email = ?", (email_clean,))
    row = cursor.fetchone()

    if not row or not bcrypt.verify(payload.password, row[1]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials.",
        )

    uid, _, name, roles_str = row
    roles = roles_str.split(",") if roles_str else []

    # Sign JWT token
    token_data = {
        "uid": uid,
        "email": email_clean,
        "name": name or email_clean.split("@")[0],
        "roles": roles,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserProfile)
def get_me(current_user: dict[str, Any] = Depends(get_current_user)) -> UserProfile:
    """Returns the profile metadata of the current authenticated user."""
    return UserProfile(
        uid=current_user.get("uid", ""),
        email=current_user.get("email", ""),
        name=current_user.get("name"),
        roles=current_user.get("roles", []),
        is_active=current_user.get("email_verified", True) or current_user.get("is_active", True),
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
        is_active=current_user.get("email_verified", True) or current_user.get("is_active", True),
    )

