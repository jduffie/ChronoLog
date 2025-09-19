"""
API models and DTOs for chronograph module.

This module provides Pydantic models for API request/response serialization,
following the project's metric-only data requirements.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class ChronographSessionRequest(BaseModel):
    """Request model for creating/updating chronograph sessions"""
    tab_name: str = Field(..., description="Name of the tab/file from chronograph")
    session_name: str = Field(..., description="User-friendly session name")
    datetime_local: datetime = Field(..., description="Local datetime of the session")
    file_path: Optional[str] = Field(None, description="Path to uploaded file")
    chronograph_source_id: Optional[str] = Field(None, description="ID of chronograph source device")

    class Config:
        schema_extra = {
            "example": {
                "tab_name": "Session_01",
                "session_name": "308 Winchester Load Development",
                "datetime_local": "2025-01-15T14:30:00",
                "file_path": "uploads/session_01.xlsx",
                "chronograph_source_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class ChronographSessionResponse(BaseModel):
    """Response model for chronograph sessions"""
    id: str
    user_id: str
    tab_name: str
    session_name: str
    datetime_local: datetime
    uploaded_at: datetime
    file_path: Optional[str]
    chronograph_source_id: Optional[str]
    shot_count: int
    avg_speed_mps: Optional[float] = Field(None, description="Average velocity in meters per second")
    std_dev_mps: Optional[float] = Field(None, description="Standard deviation in meters per second")
    min_speed_mps: Optional[float] = Field(None, description="Minimum velocity in meters per second")
    max_speed_mps: Optional[float] = Field(None, description="Maximum velocity in meters per second")
    created_at: Optional[datetime]

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_123",
                "tab_name": "Session_01",
                "session_name": "308 Winchester Load Development",
                "datetime_local": "2025-01-15T14:30:00Z",
                "uploaded_at": "2025-01-15T15:00:00Z",
                "file_path": "uploads/session_01.xlsx",
                "chronograph_source_id": "550e8400-e29b-41d4-a716-446655440001",
                "shot_count": 10,
                "avg_speed_mps": 762.5,
                "std_dev_mps": 8.2,
                "min_speed_mps": 751.3,
                "max_speed_mps": 775.1,
                "created_at": "2025-01-15T15:00:00Z"
            }
        }


class ChronographMeasurementRequest(BaseModel):
    """Request model for creating/updating chronograph measurements"""
    chrono_session_id: str = Field(..., description="ID of the associated chronograph session")
    shot_number: int = Field(..., ge=1, description="Shot number (must be >= 1)")
    speed_mps: float = Field(..., gt=0, description="Velocity in meters per second")
    datetime_local: datetime = Field(..., description="Local datetime of the measurement")
    delta_avg_mps: Optional[float] = Field(None, description="Delta from average velocity in m/s")
    ke_j: Optional[float] = Field(None, description="Kinetic energy in joules")
    power_factor_kgms: Optional[float] = Field(None, description="Power factor in kg⋅m/s")
    clean_bore: Optional[bool] = Field(None, description="Whether this was a clean bore shot")
    cold_bore: Optional[bool] = Field(None, description="Whether this was a cold bore shot")
    shot_notes: Optional[str] = Field(None, max_length=500, description="Notes about this shot")

    @validator('speed_mps')
    def validate_speed_range(cls, v):
        """Validate that speed is within reasonable chronograph range"""
        if v < 50 or v > 2000:  # 50-2000 m/s covers most projectiles
            raise ValueError('Velocity must be between 50 and 2000 m/s')
        return v

    class Config:
        schema_extra = {
            "example": {
                "chrono_session_id": "550e8400-e29b-41d4-a716-446655440000",
                "shot_number": 1,
                "speed_mps": 762.5,
                "datetime_local": "2025-01-15T14:30:15",
                "delta_avg_mps": -2.1,
                "ke_j": 3456.2,
                "power_factor_kgms": 0.0123,
                "clean_bore": True,
                "cold_bore": True,
                "shot_notes": "First shot of the day"
            }
        }


class ChronographMeasurementResponse(BaseModel):
    """Response model for chronograph measurements"""
    id: str
    user_id: str
    chrono_session_id: str
    shot_number: int
    speed_mps: float = Field(..., description="Velocity in meters per second")
    datetime_local: datetime
    delta_avg_mps: Optional[float] = Field(None, description="Delta from average velocity in m/s")
    ke_j: Optional[float] = Field(None, description="Kinetic energy in joules")
    power_factor_kgms: Optional[float] = Field(None, description="Power factor in kg⋅m/s")
    clean_bore: Optional[bool]
    cold_bore: Optional[bool]
    shot_notes: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "user_id": "user_123",
                "chrono_session_id": "550e8400-e29b-41d4-a716-446655440000",
                "shot_number": 1,
                "speed_mps": 762.5,
                "datetime_local": "2025-01-15T14:30:15Z",
                "delta_avg_mps": -2.1,
                "ke_j": 3456.2,
                "power_factor_kgms": 0.0123,
                "clean_bore": True,
                "cold_bore": True,
                "shot_notes": "First shot of the day"
            }
        }


class ChronographSourceRequest(BaseModel):
    """Request model for creating/updating chronograph sources"""
    name: str = Field(..., min_length=1, max_length=100, description="User-friendly name for the chronograph")
    source_type: str = Field(default="chronograph", description="Type of source device")
    device_name: Optional[str] = Field(None, max_length=100, description="Device name from file")
    make: Optional[str] = Field(None, max_length=50, description="Manufacturer")
    model: Optional[str] = Field(None, max_length=50, description="Model number")
    serial_number: Optional[str] = Field(None, max_length=50, description="Serial number")

    class Config:
        schema_extra = {
            "example": {
                "name": "My Garmin Xero C1",
                "source_type": "chronograph",
                "device_name": "Garmin Xero C1",
                "make": "Garmin",
                "model": "Xero C1",
                "serial_number": "123456789"
            }
        }


class ChronographSourceResponse(BaseModel):
    """Response model for chronograph sources"""
    id: str
    user_id: str
    name: str
    source_type: str
    device_name: Optional[str]
    make: Optional[str]
    model: Optional[str]
    serial_number: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "user_123",
                "name": "My Garmin Xero C1",
                "source_type": "chronograph",
                "device_name": "Garmin Xero C1",
                "make": "Garmin",
                "model": "Xero C1",
                "serial_number": "123456789",
                "created_at": "2025-01-15T10:00:00Z",
                "updated_at": "2025-01-15T10:00:00Z"
            }
        }


class SessionStatisticsResponse(BaseModel):
    """Response model for session statistics"""
    session_id: str
    shot_count: int
    avg_speed_mps: float = Field(..., description="Average velocity in meters per second")
    std_dev_mps: float = Field(..., description="Standard deviation in meters per second")
    min_speed_mps: float = Field(..., description="Minimum velocity in meters per second")
    max_speed_mps: float = Field(..., description="Maximum velocity in meters per second")
    extreme_spread_mps: float = Field(..., description="Extreme spread (max - min) in m/s")
    coefficient_of_variation: float = Field(..., description="Coefficient of variation as percentage")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "shot_count": 10,
                "avg_speed_mps": 762.5,
                "std_dev_mps": 8.2,
                "min_speed_mps": 751.3,
                "max_speed_mps": 775.1,
                "extreme_spread_mps": 23.8,
                "coefficient_of_variation": 1.08
            }
        }


class PaginationParams(BaseModel):
    """Model for pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")


class SessionFilterParams(BaseModel):
    """Model for session filtering parameters"""
    bullet_type: Optional[str] = Field(None, description="Filter by bullet type")
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")
    chronograph_source_id: Optional[str] = Field(None, description="Filter by chronograph source")


class PaginatedResponse(BaseModel):
    """Generic paginated response model"""
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        schema_extra = {
            "example": {
                "items": [],
                "total": 50,
                "page": 1,
                "size": 20,
                "pages": 3
            }
        }


class BulkMeasurementRequest(BaseModel):
    """Request model for bulk creating measurements"""
    measurements: List[ChronographMeasurementRequest] = Field(..., min_items=1, max_items=1000)

    class Config:
        schema_extra = {
            "example": {
                "measurements": [
                    {
                        "chrono_session_id": "550e8400-e29b-41d4-a716-446655440000",
                        "shot_number": 1,
                        "speed_mps": 762.5,
                        "datetime_local": "2025-01-15T14:30:15"
                    },
                    {
                        "chrono_session_id": "550e8400-e29b-41d4-a716-446655440000",
                        "shot_number": 2,
                        "speed_mps": 765.1,
                        "datetime_local": "2025-01-15T14:30:45"
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    message: str
    details: Optional[dict] = None

    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "details": {
                    "field": "speed_mps",
                    "issue": "Value must be greater than 0"
                }
            }
        }