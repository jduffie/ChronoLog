"""
Dependency injection setup for chronograph API.

This module provides proper dependency injection for production use,
including Supabase client configuration, authentication, and service
layer instantiation.
"""

import os
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from supabase import Client, create_client

from .service import ChronographService

# Security setup
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


class AuthenticationError(Exception):
    """Exception raised for authentication errors"""


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get Supabase client instance.

    Returns:
        Client: Configured Supabase client

    Raises:
        ValueError: If required environment variables are not set
    """
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL environment variable is required")

    if not SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable is required")

    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def get_chronograph_service(
    supabase_client: Client = Depends(get_supabase_client)
) -> ChronographService:
    """
    Get ChronographService instance with dependency injection.

    Args:
        supabase_client: Injected Supabase client

    Returns:
        ChronographService: Service instance
    """
    return ChronographService(supabase_client)


def verify_token(token: str) -> dict:
    """
    Verify JWT token and extract user information.

    Args:
        token: JWT token string

    Returns:
        dict: User payload from token

    Raises:
        AuthenticationError: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Token missing user ID")
        return payload
    except JWTError as e:
        raise AuthenticationError(f"Token validation failed: {str(e)}")


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract and validate user ID from JWT token.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        str: User ID

    Raises:
        HTTPException: If authentication fails
    """
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Extract full user payload from JWT token.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        dict: Full user payload

    Raises:
        HTTPException: If authentication fails
    """
    try:
        payload = verify_token(credentials.credentials)
        return payload
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# Optional: Admin user dependency
async def get_admin_user(
    user_payload: dict = Depends(get_current_user_payload)
) -> dict:
    """
    Verify user has admin privileges.

    Args:
        user_payload: User payload from JWT token

    Returns:
        dict: Admin user payload

    Raises:
        HTTPException: If user is not admin
    """
    is_admin = user_payload.get("is_admin", False)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user_payload


class DatabaseConfig:
    """Database configuration class"""

    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.service_role_key = SUPABASE_SERVICE_ROLE_KEY

    def validate(self) -> bool:
        """Validate database configuration"""
        return bool(self.supabase_url and self.service_role_key)


class APIConfig:
    """API configuration class"""

    def __init__(self):
        self.jwt_secret = SECRET_KEY
        self.jwt_algorithm = ALGORITHM
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.debug


@lru_cache()
def get_api_config() -> APIConfig:
    """Get API configuration instance"""
    return APIConfig()


@lru_cache()
def get_database_config() -> DatabaseConfig:
    """Get database configuration instance"""
    config = DatabaseConfig()
    if not config.validate():
        raise ValueError("Database configuration is invalid")
    return config


# Health check dependencies
async def check_database_health(
    supabase_client: Client = Depends(get_supabase_client)
) -> bool:
    """
    Check database health.

    Args:
        supabase_client: Supabase client instance

    Returns:
        bool: True if database is healthy
    """
    try:
        # Simple query to check database connectivity
        response = supabase_client.table("chrono_sessions").select("count", count="exact").limit(1).execute()
        return response is not None
    except Exception:
        return False


# Rate limiting (placeholder for future implementation)
class RateLimiter:
    """Rate limiter for API endpoints"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute

    async def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: User identifier

        Returns:
            bool: True if within rate limit
        """
        # Placeholder implementation
        # In production, this would use Redis or similar for tracking
        return True


def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance"""
    return RateLimiter()


# Validation helpers
def validate_environment() -> None:
    """
    Validate that all required environment variables are set.

    Raises:
        ValueError: If required variables are missing
    """
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


# Optional: Metrics dependencies
class MetricsCollector:
    """Metrics collection for monitoring"""

    def __init__(self):
        self.requests_count = 0
        self.error_count = 0

    def increment_requests(self):
        """Increment request counter"""
        self.requests_count += 1

    def increment_errors(self):
        """Increment error counter"""
        self.error_count += 1

    def get_metrics(self) -> dict:
        """Get current metrics"""
        return {
            "requests_count": self.requests_count,
            "error_count": self.error_count,
        }


@lru_cache()
def get_metrics_collector() -> MetricsCollector:
    """Get metrics collector instance"""
    return MetricsCollector()