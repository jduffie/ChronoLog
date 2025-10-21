"""
Chronograph Module for ChronoLog.

This module provides comprehensive chronograph data management including:
- Chronograph source (device) management
- Session management with statistics
- Measurement storage and retrieval
- CSV import from chronograph devices (Garmin Xero, etc.)
- Statistical analysis and filtering

Main Components:
    - ChronographAPI: Main API facade for all chronograph operations
    - ChronographSession: Model representing a shooting session
    - ChronographMeasurement: Model representing a single shot
    - ChronographSource: Model representing a chronograph device
    - ChronographAPIProtocol: Protocol defining the API interface

Example:
    from chronograph import ChronographAPI
    from supabase import create_client

    supabase = create_client(url, key)
    chrono_api = ChronographAPI(supabase)

    # Create a session
    session = chrono_api.create_session(
        {
            "tab_name": "168gr HPBT",
            "session_name": "Range Day 1",
            "datetime_local": "2024-01-15T10:00:00"
        },
        user_id
    )

    # Create a measurement
    measurement = chrono_api.create_measurement(
        {
            "chrono_session_id": session.id,
            "shot_number": 1,
            "speed_mps": 792.5,
            "datetime_local": "2024-01-15T10:00:00"
        },
        user_id
    )
"""

from .chronograph_session_models import ChronographMeasurement, ChronographSession
from .chronograph_source_models import ChronographSource
from .client_api import ChronographAPI
from .protocols import ChronographAPIProtocol

__all__ = [
    "ChronographAPI",
    "ChronographSession",
    "ChronographMeasurement",
    "ChronographSource",
    "ChronographAPIProtocol",
]

__version__ = "1.0.0"
__author__ = "ChronoLog Team"
