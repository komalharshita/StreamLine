import logging
from typing import Any, Optional

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

from app.core.config import settings

from jose import jwt
from jose.exceptions import JWTError

from app.core.config import settings

logger = logging.getLogger("app.security")

# HTTP Bearer scheme setup
security_scheme = HTTPBearer(auto_error=False)

# Initialize Firebase Admin SDK if not already initialized
firebase_initialized = False
try:
    firebase_admin.get_app()
    firebase_initialized = True
except ValueError:
    try:
        # Use default credentials (e.g. from Google Application Credentials or metadata server)
        firebase_admin.initialize_app()
        firebase_initialized = True
        logger.info("Firebase Admin SDK successfully initialized.")
    except Exception as e:
        logger.warning(
            f"Firebase Admin SDK could not be initialized (offline/unconfigured): {str(e)}"
        )


class SecurityManager:
    """Handles token validation against local JWT credentials or Firebase Authentication services."""

    def __init__(self, mock_auth: bool = settings.FIREBASE_MOCK_AUTH):
        self.mock_auth = mock_auth

    def verify_token(self, token: str) -> dict[str, Any]:
        """Verifies a custom local JWT token or Firebase ID token.

        Returns authenticated user identity details.
        """
        # 1. Attempt to decode as local/custom JWT
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            logger.debug("Successfully validated credentials via local JWT signature.")
            return payload
        except JWTError:
            # If not a valid custom JWT, fallback to Firebase validation if initialized
            pass

        if self.mock_auth:
            logger.debug("Bypassing authentication check (Mock Auth active).")
            # Return a valid mock payload for testing
            return {
                "uid": "mock-user-12345",
                "email": "user@streamline.ai",
                "name": "Mock User",
                "email_verified": True,
                "roles": ["admin", "analyst"],
            }

        if not firebase_initialized:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication provider is unavailable.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # Verify the ID token against Firebase Authentication servers
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            logger.warning(f"Firebase token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )



# Dependency instance
security_manager = SecurityManager()


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> dict[str, Any]:
    """FastAPI dependency to secure endpoints.

    Retrieves and validates the authentication token, returning the user identity.
    """
    if settings.FIREBASE_MOCK_AUTH:
        # Bypass authentication in mock mode
        return security_manager.verify_token("")

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated",
        )

    token = credentials.credentials
    return security_manager.verify_token(token)
