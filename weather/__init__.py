"""
Weather Module for ChronoLog.

This module provides comprehensive weather data management including:
- Weather source (device/meter) management
- Weather measurement storage and retrieval
- CSV import from weather meters (Kestrel, etc.)
- Filtering and querying capabilities

Main Components:
    - WeatherAPI: Main API facade for all weather operations
    - WeatherSource: Model representing a weather meter/device
    - WeatherMeasurement: Model representing a single weather reading
    - WeatherAPIProtocol: Protocol defining the API interface

Example:
    from weather import WeatherAPI
    from supabase import create_client

    supabase = create_client(url, key)
    weather_api = WeatherAPI(supabase)

    # Create a weather source
    source = weather_api.create_source(
        {"name": "My Kestrel", "model": "5700 Elite"},
        user_id
    )

    # Create a measurement
    measurement = weather_api.create_measurement(
        {
            "weather_source_id": source.id,
            "measurement_timestamp": "2024-01-15T10:00:00",
            "temperature_c": 22.5,
            "relative_humidity_pct": 65.0
        },
        user_id
    )
"""

from .api import WeatherAPI
from .models import WeatherMeasurement, WeatherSource
from .protocols import WeatherAPIProtocol

__all__ = [
    "WeatherAPI",
    "WeatherSource",
    "WeatherMeasurement",
    "WeatherAPIProtocol",
]

__version__ = "1.0.0"
__author__ = "ChronoLog Team"
