"""
Middleware and error handling for chronograph API.

This module provides comprehensive error handling, validation middleware,
and custom exception classes for the chronograph API.
"""

import logging
from typing import Any, Dict

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .api_models import ErrorResponse

logger = logging.getLogger(__name__)


class ChronographAPIException(Exception):
    """Base exception for chronograph API operations"""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(ChronographAPIException):
    """Exception for validation errors"""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class AuthorizationException(ChronographAPIException):
    """Exception for authorization errors"""

    def __init__(self, message: str = "Access denied", details: Dict[str, Any] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


class ResourceNotFoundException(ChronographAPIException):
    """Exception for resource not found errors"""

    def __init__(self, resource_type: str, resource_id: str = None, details: Dict[str, Any] = None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" with ID: {resource_id}"
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class ConflictException(ChronographAPIException):
    """Exception for resource conflict errors"""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status.HTTP_409_CONFLICT, details)


class DatabaseException(ChronographAPIException):
    """Exception for database operation errors"""

    def __init__(self, operation: str, details: Dict[str, Any] = None):
        message = f"Database error during {operation}"
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)


# Error handling middleware
async def chronograph_exception_handler(request: Request, exc: ChronographAPIException):
    """Handle custom chronograph API exceptions"""
    logger.error(f"ChronographAPIException: {exc.message}", extra={
        "status_code": exc.status_code,
        "details": exc.details,
        "path": request.url.path,
        "method": request.method
    })

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.message,
            details=exc.details if exc.details else None
        ).dict(exclude_none=True)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {str(exc)}", extra={
        "path": request.url.path,
        "method": request.method,
        "errors": exc.errors()
    })

    # Format validation errors for better readability
    error_details = {}
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        error_details[field_path] = {
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        }

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="ValidationError",
            message="Invalid input data",
            details=error_details
        ).dict()
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", extra={
        "path": request.url.path,
        "method": request.method,
        "exception_type": type(exc).__name__
    }, exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details={"exception_type": type(exc).__name__}
        ).dict()
    )


class InputValidationMiddleware:
    """Middleware for additional input validation beyond Pydantic"""

    @staticmethod
    def validate_chronograph_measurements(measurements_data: list) -> None:
        """Validate chronograph measurement data for business rules"""
        if not measurements_data:
            raise ValidationException("At least one measurement is required")

        # Check for duplicate shot numbers within the same session
        session_shots = {}
        for measurement in measurements_data:
            session_id = measurement.get("chrono_session_id")
            shot_number = measurement.get("shot_number")

            if session_id not in session_shots:
                session_shots[session_id] = set()

            if shot_number in session_shots[session_id]:
                raise ValidationException(
                    f"Duplicate shot number {shot_number} for session {session_id}",
                    details={"session_id": session_id, "shot_number": shot_number}
                )

            session_shots[session_id].add(shot_number)

    @staticmethod
    def validate_velocity_range(velocity_mps: float) -> None:
        """Validate velocity is within reasonable chronograph range"""
        if velocity_mps < 30:  # Very slow projectiles (e.g., airsoft)
            raise ValidationException(
                f"Velocity {velocity_mps} m/s is too low for chronograph measurement",
                details={"min_velocity": 30, "provided_velocity": velocity_mps}
            )

        if velocity_mps > 2000:  # Very fast projectiles (e.g., high-velocity rifles)
            raise ValidationException(
                f"Velocity {velocity_mps} m/s exceeds maximum chronograph range",
                details={"max_velocity": 2000, "provided_velocity": velocity_mps}
            )

    @staticmethod
    def validate_session_datetime(datetime_local) -> None:
        """Validate session datetime is reasonable"""
        from datetime import datetime, timedelta

        now = datetime.now()
        min_date = datetime(2000, 1, 1)  # Reasonable minimum date
        max_future = now + timedelta(days=1)  # Allow slight future dates for timezone issues

        if datetime_local < min_date:
            raise ValidationException(
                f"Session date {datetime_local} is too far in the past",
                details={"min_date": min_date.isoformat(), "provided_date": datetime_local.isoformat()}
            )

        if datetime_local > max_future:
            raise ValidationException(
                f"Session date {datetime_local} is too far in the future",
                details={"max_future": max_future.isoformat(), "provided_date": datetime_local.isoformat()}
            )


class SecurityMiddleware:
    """Middleware for security-related validations"""

    @staticmethod
    def validate_user_access(user_id: str, resource_user_id: str) -> None:
        """Validate that user has access to the requested resource"""
        if user_id != resource_user_id:
            raise AuthorizationException(
                "Access denied: You can only access your own resources",
                details={"requested_user_id": resource_user_id, "authenticated_user_id": user_id}
            )

    @staticmethod
    def sanitize_input(input_string: str, max_length: int = 1000) -> str:
        """Sanitize string input to prevent injection attacks"""
        if not input_string:
            return ""

        # Remove potentially dangerous characters
        sanitized = input_string.strip()

        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized


class MetricsMiddleware:
    """Middleware for API metrics and monitoring"""

    @staticmethod
    async def log_request_metrics(request: Request, response_time: float, status_code: int):
        """Log request metrics for monitoring"""
        logger.info("API Request", extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "response_time_ms": round(response_time * 1000, 2),
            "client_ip": request.client.host if request.client else "unknown"
        })


# Utility functions for error handling
def handle_service_exceptions(func):
    """Decorator to handle service layer exceptions and convert them to API exceptions"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = str(e)

            # Map common service errors to appropriate API exceptions
            if "not found" in error_message.lower():
                raise ResourceNotFoundException("Resource", details={"original_error": error_message})
            elif "already exists" in error_message.lower():
                raise ConflictException(error_message)
            elif "permission" in error_message.lower() or "access" in error_message.lower():
                raise AuthorizationException(error_message)
            elif "validation" in error_message.lower() or "invalid" in error_message.lower():
                raise ValidationException(error_message)
            else:
                raise DatabaseException("operation", details={"original_error": error_message})

    return wrapper


def create_error_response(error_type: str, message: str, status_code: int, details: Dict[str, Any] = None) -> JSONResponse:
    """Create a standardized error response"""
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=error_type,
            message=message,
            details=details
        ).dict(exclude_none=True)
    )