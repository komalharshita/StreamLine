import logging
from typing import Any

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

from app.core.config import settings

logger = logging.getLogger("app.security")

# HTTP Bearer scheme setup
security_scheme = HTTPBearer(auto_error=True)

# Initialize Firebase Admin SDK if not already initialized
if not settings.FIREBASE_MOCK_AUTH:
    try:
        # Check if already initialized to avoid throwing exception
        firebase_admin.get_app()
    except ValueError:
        # Use default credentials (e.g. from Google Application Credentials or metadata server)
        firebase_admin.initialize_app()
        logger.info("Firebase Admin SDK successfully initialized.")


class SecurityManager:
    """Handles token validation against Firebase Authentication services."""

    def __init__(self, mock_auth: bool = settings.FIREBASE_MOCK_AUTH):
        self.mock_auth = mock_auth

    def verify_token(self, token: str) -> dict[str, Any]:
        """Verifies a Firebase ID token.

        In production, verifies token signature and expiration.
        In mock mode, returns a simulated authenticated user identity.
        """
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
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict[str, Any]:
    """FastAPI dependency to secure endpoints.

    Retrieves and validates the authentication token, returning the user identity.
    """
    token = credentials.credentials
    return security_manager.verify_token(token)
