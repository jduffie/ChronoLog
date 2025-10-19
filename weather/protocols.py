"""
Protocol definitions for Weather API.

This module defines the WeatherAPIProtocol, which specifies the interface
for all weather-related operations in the ChronoLog application.

The protocol uses Python's typing.Protocol for structural subtyping,
allowing any class that implements these methods to be used as a
weather API, regardless of inheritance.
"""

from typing import List, Optional, Protocol

from .models import WeatherMeasurement, WeatherSource


class WeatherAPIProtocol(Protocol):
    """
    Protocol defining the interface for weather operations.

    This protocol specifies all methods required for managing weather sources
    (meters/devices) and their measurements. Any class implementing this
    protocol can be used interchangeably throughout the application.

    The protocol supports:
    - Weather source (device) management
    - Weather measurement storage and retrieval
    - Filtering and querying measurements
    - Batch operations for efficiency
    - Device info-based source creation/retrieval
    """

    # ==================== Weather Source Operations ====================

    def get_all_sources(self, user_id: str) -> List[WeatherSource]:
        """
        Get all weather sources for a user.

        Args:
            user_id: User identifier

        Returns:
            List of WeatherSource objects owned by the user,
            ordered by name

        Example:
            >>> sources = api.get_all_sources("user-123")
            >>> for source in sources:
            ...     print(source.display_name())
        """
        ...

    def get_source_by_id(
        self, source_id: str, user_id: str
    ) -> Optional[WeatherSource]:
        """
        Get a specific weather source by ID.

        Args:
            source_id: Weather source identifier
            user_id: User identifier (for access control)

        Returns:
            WeatherSource if found and owned by user, None otherwise

        Example:
            >>> source = api.get_source_by_id("source-123", "user-123")
            >>> if source:
            ...     print(source.device_display())
        """
        ...

    def get_source_by_name(
        self, user_id: str, name: str
    ) -> Optional[WeatherSource]:
        """
        Get a weather source by name.

        Args:
            user_id: User identifier
            name: Source name to search for

        Returns:
            WeatherSource if found, None otherwise

        Example:
            >>> source = api.get_source_by_name("user-123", "My Kestrel")
            >>> if source:
            ...     print(f"Found: {source.id}")
        """
        ...

    def create_source(
        self, source_data: dict, user_id: str
    ) -> WeatherSource:
        """
        Create a new weather source.

        Args:
            source_data: Dictionary containing source information
                Required: name
                Optional: device_name, make, model, serial_number
            user_id: User identifier

        Returns:
            Created WeatherSource with generated ID and timestamps

        Raises:
            Exception: If creation fails

        Example:
            >>> source_data = {
            ...     "name": "My Kestrel",
            ...     "device_name": "Kestrel 5700",
            ...     "model": "5700 Elite",
            ...     "serial_number": "K123456"
            ... }
            >>> source = api.create_source(source_data, "user-123")
            >>> print(source.id)
        """
        ...

    def update_source(
        self, source_id: str, updates: dict, user_id: str
    ) -> WeatherSource:
        """
        Update an existing weather source.

        Args:
            source_id: Weather source identifier
            updates: Dictionary of fields to update
            user_id: User identifier (for access control)

        Returns:
            Updated WeatherSource

        Raises:
            Exception: If source not found or update fails

        Example:
            >>> updates = {"name": "Updated Name", "make": "Kestrel"}
            >>> source = api.update_source("source-123", updates, "user-123")
        """
        ...

    def delete_source(self, source_id: str, user_id: str) -> bool:
        """
        Delete a weather source and all its measurements.

        Args:
            source_id: Weather source identifier
            user_id: User identifier (for access control)

        Returns:
            True if deleted successfully

        Raises:
            Exception: If deletion fails

        Note:
            Deleting a source will cascade delete all associated measurements

        Example:
            >>> success = api.delete_source("source-123", "user-123")
            >>> print(f"Deleted: {success}")
        """
        ...

    def create_or_get_source_from_device_info(
        self,
        user_id: str,
        device_name: str,
        device_model: str,
        serial_number: str,
    ) -> WeatherSource:
        """
        Create or retrieve existing weather source from device information.

        This method intelligently handles device identification:
        1. Searches for existing source by serial number
        2. If not found, searches by generated name
        3. If still not found, creates new source

        Args:
            user_id: User identifier
            device_name: Device name from import
            device_model: Device model from import
            serial_number: Device serial number from import

        Returns:
            Existing or newly created WeatherSource

        Example:
            >>> source = api.create_or_get_source_from_device_info(
            ...     "user-123",
            ...     "Kestrel 5700",
            ...     "5700 Elite",
            ...     "K123456"
            ... )
        """
        ...

    # ==================== Weather Measurement Operations ====================

    def get_measurements_for_source(
        self, source_id: str, user_id: str
    ) -> List[WeatherMeasurement]:
        """
        Get all measurements for a specific weather source.

        Args:
            source_id: Weather source identifier
            user_id: User identifier (for access control)

        Returns:
            List of WeatherMeasurement objects, ordered by timestamp

        Example:
            >>> measurements = api.get_measurements_for_source(
            ...     "source-123", "user-123"
            ... )
            >>> for m in measurements:
            ...     print(f"{m.measurement_timestamp}: {m.temperature_c}°C")
        """
        ...

    def get_all_measurements(
        self, user_id: str, limit: Optional[int] = None
    ) -> List[WeatherMeasurement]:
        """
        Get all weather measurements for a user.

        Args:
            user_id: User identifier
            limit: Optional maximum number of measurements to return

        Returns:
            List of WeatherMeasurement objects, ordered by timestamp (desc)

        Example:
            >>> # Get last 100 measurements
            >>> measurements = api.get_all_measurements("user-123", limit=100)
        """
        ...

    def filter_measurements(
        self,
        user_id: str,
        source_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[WeatherMeasurement]:
        """
        Get filtered weather measurements.

        Args:
            user_id: User identifier
            source_id: Optional source ID filter
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)

        Returns:
            List of filtered WeatherMeasurement objects

        Example:
            >>> measurements = api.filter_measurements(
            ...     "user-123",
            ...     source_id="source-123",
            ...     start_date="2024-01-01T00:00:00",
            ...     end_date="2024-01-31T23:59:59"
            ... )
        """
        ...

    def create_measurement(
        self, measurement_data: dict, user_id: str
    ) -> WeatherMeasurement:
        """
        Create a new weather measurement.

        Args:
            measurement_data: Dictionary containing measurement data
                Required: weather_source_id, measurement_timestamp
                Optional: temperature_c, relative_humidity_pct,
                         barometric_pressure_hpa, wind_speed_mps, etc.
            user_id: User identifier

        Returns:
            Created WeatherMeasurement with generated ID

        Raises:
            Exception: If creation fails

        Example:
            >>> measurement_data = {
            ...     "weather_source_id": "source-123",
            ...     "measurement_timestamp": "2024-01-15T10:00:00",
            ...     "temperature_c": 22.5,
            ...     "relative_humidity_pct": 65.0,
            ...     "barometric_pressure_hpa": 1013.25
            ... }
            >>> measurement = api.create_measurement(
            ...     measurement_data, "user-123"
            ... )
        """
        ...

    def create_measurements_batch(
        self, measurements_data: List[dict], user_id: str
    ) -> List[WeatherMeasurement]:
        """
        Create multiple weather measurements in a single batch operation.

        Args:
            measurements_data: List of measurement data dictionaries
            user_id: User identifier

        Returns:
            List of created WeatherMeasurement objects

        Raises:
            Exception: If batch creation fails

        Note:
            This is more efficient than creating measurements one at a time

        Example:
            >>> batch_data = [
            ...     {"weather_source_id": "source-123",
            ...      "measurement_timestamp": "2024-01-15T10:00:00",
            ...      "temperature_c": 22.5},
            ...     {"weather_source_id": "source-123",
            ...      "measurement_timestamp": "2024-01-15T10:01:00",
            ...      "temperature_c": 22.6},
            ... ]
            >>> measurements = api.create_measurements_batch(
            ...     batch_data, "user-123"
            ... )
        """
        ...

    def measurement_exists(
        self, user_id: str, source_id: str, measurement_timestamp: str
    ) -> bool:
        """
        Check if a measurement already exists.

        Args:
            user_id: User identifier
            source_id: Weather source identifier
            measurement_timestamp: Timestamp to check (ISO format)

        Returns:
            True if measurement exists, False otherwise

        Example:
            >>> exists = api.measurement_exists(
            ...     "user-123",
            ...     "source-123",
            ...     "2024-01-15T10:00:00"
            ... )
            >>> if not exists:
            ...     # Safe to create measurement
        """
        ...