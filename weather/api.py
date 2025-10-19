"""
Weather API Facade.

This module provides the main API for weather operations in ChronoLog.
It implements the WeatherAPIProtocol and wraps the WeatherService
to provide a clean, type-safe interface.

Usage:
    from weather import WeatherAPI
    from supabase import create_client

    supabase = create_client(url, key)
    weather_api = WeatherAPI(supabase)

    # Create a weather source
    source = weather_api.create_source(
        {"name": "My Kestrel", "model": "5700 Elite"},
        user_id
    )

    # Create measurements
    measurement = weather_api.create_measurement(
        {
            "weather_source_id": source.id,
            "measurement_timestamp": "2024-01-15T10:00:00",
            "temperature_c": 22.5
        },
        user_id
    )
"""

import uuid
from datetime import datetime
from typing import List, Optional

from .models import WeatherMeasurement, WeatherSource
from .service import WeatherService


class WeatherAPI:
    """
    Main API facade for weather operations.

    This class provides a clean interface for all weather-related operations,
    handling ID generation, timestamps, and user access control automatically.

    Attributes:
        _supabase: Supabase client instance
        _service: WeatherService instance for database operations
    """

    def __init__(self, supabase_client):
        """
        Initialize Weather API.

        Args:
            supabase_client: Authenticated Supabase client
        """
        self._supabase = supabase_client
        self._service = WeatherService(supabase_client)

    # ==================== Weather Source Operations ====================

    def get_all_sources(self, user_id: str) -> List[WeatherSource]:
        """
        Get all weather sources for a user.

        Args:
            user_id: User identifier

        Returns:
            List of WeatherSource objects owned by the user, ordered by name

        Example:
            >>> sources = api.get_all_sources("user-123")
            >>> for source in sources:
            ...     print(source.display_name())
        """
        try:
            return self._service.get_sources_for_user(user_id)
        except Exception as e:
            raise Exception(f"Error getting weather sources: {str(e)}")

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
        try:
            return self._service.get_source_by_id(source_id, user_id)
        except Exception as e:
            # Return None for not found errors
            if "PGRST116" in str(e) or "0 rows" in str(e):
                return None
            raise Exception(f"Error getting weather source: {str(e)}")

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
        try:
            return self._service.get_source_by_name(user_id, name)
        except Exception:
            # Service already returns None for not found
            return None

    def create_source(
        self, source_data: dict, user_id: str
    ) -> WeatherSource:
        """
        Create a new weather source with auto-generated ID and timestamps.

        Args:
            source_data: Dictionary containing source information
                Required: name
                Optional: device_name, make, model, serial_number
            user_id: User identifier

        Returns:
            Created WeatherSource

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
        """
        try:
            # Prepare insert data with generated fields
            insert_data = source_data.copy()
            insert_data["id"] = str(uuid.uuid4())
            insert_data["user_id"] = user_id
            insert_data["created_at"] = datetime.now().isoformat()
            insert_data["updated_at"] = datetime.now().isoformat()

            # Ensure source_type is set
            if "source_type" not in insert_data:
                insert_data["source_type"] = "meter"

            # Insert into database
            response = (
                self._supabase.table("weather_source")
                .insert(insert_data)
                .execute()
            )

            if not response.data:
                raise Exception("Failed to create weather source - no data returned")

            return WeatherSource.from_supabase_record(response.data[0])

        except Exception as e:
            raise Exception(f"Error creating weather source: {str(e)}")

    def update_source(
        self, source_id: str, updates: dict, user_id: str
    ) -> WeatherSource:
        """
        Update an existing weather source with auto-updated timestamp.

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
        try:
            # Add updated timestamp
            update_data = updates.copy()
            update_data["updated_at"] = datetime.now().isoformat()

            # Update in database
            response = (
                self._supabase.table("weather_source")
                .update(update_data)
                .eq("id", source_id)
                .eq("user_id", user_id)
                .execute()
            )

            if not response.data or len(response.data) == 0:
                raise Exception(
                    f"Weather source {source_id} not found or not owned by user"
                )

            return WeatherSource.from_supabase_record(response.data[0])

        except Exception as e:
            raise Exception(f"Error updating weather source: {str(e)}")

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
        """
        try:
            self._service.delete_source(source_id, user_id)
            return True
        except Exception as e:
            raise Exception(f"Error deleting weather source: {str(e)}")

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
        try:
            # Use service method to find or create
            source_id = self._service.create_or_get_source_from_device_info(
                user_id, device_name, device_model, serial_number
            )

            # Return the full source object
            source = self._service.get_source_by_id(source_id, user_id)
            if not source:
                raise Exception(
                    f"Failed to retrieve created/found source {source_id}"
                )

            return source

        except Exception as e:
            raise Exception(
                f"Error creating/getting source from device info: {str(e)}"
            )

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
        try:
            return self._service.get_measurements_for_source(source_id, user_id)
        except Exception as e:
            raise Exception(f"Error getting measurements for source: {str(e)}")

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
            >>> measurements = api.get_all_measurements("user-123", limit=100)
        """
        try:
            return self._service.get_all_measurements_for_user(user_id, limit)
        except Exception as e:
            raise Exception(f"Error getting all measurements: {str(e)}")

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
        try:
            return self._service.get_measurements_filtered(
                user_id, source_id, start_date, end_date
            )
        except Exception as e:
            raise Exception(f"Error filtering measurements: {str(e)}")

    def create_measurement(
        self, measurement_data: dict, user_id: str
    ) -> WeatherMeasurement:
        """
        Create a new weather measurement with auto-generated ID and timestamp.

        Args:
            measurement_data: Dictionary containing measurement data
                Required: weather_source_id, measurement_timestamp
                Optional: temperature_c, relative_humidity_pct,
                         barometric_pressure_hpa, wind_speed_mps, etc.
            user_id: User identifier

        Returns:
            Created WeatherMeasurement

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
        try:
            # Prepare insert data with generated fields
            insert_data = measurement_data.copy()
            insert_data["id"] = str(uuid.uuid4())
            insert_data["user_id"] = user_id
            insert_data["uploaded_at"] = datetime.now().isoformat()

            # Insert into database
            response = (
                self._supabase.table("weather_measurements")
                .insert(insert_data)
                .execute()
            )

            if not response.data:
                raise Exception("Failed to create measurement - no data returned")

            return WeatherMeasurement.from_supabase_record(response.data[0])

        except Exception as e:
            raise Exception(f"Error creating measurement: {str(e)}")

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
        try:
            # Prepare batch insert data with generated fields
            insert_batch = []
            uploaded_at = datetime.now().isoformat()

            for measurement_data in measurements_data:
                insert_data = measurement_data.copy()
                insert_data["id"] = str(uuid.uuid4())
                insert_data["user_id"] = user_id
                insert_data["uploaded_at"] = uploaded_at
                insert_batch.append(insert_data)

            # Batch insert into database
            response = (
                self._supabase.table("weather_measurements")
                .insert(insert_batch)
                .execute()
            )

            if not response.data:
                raise Exception("Failed to create measurements batch - no data returned")

            return WeatherMeasurement.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error creating measurements batch: {str(e)}")

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
        try:
            return self._service.measurement_exists(
                user_id, source_id, measurement_timestamp
            )
        except Exception as e:
            raise Exception(f"Error checking measurement existence: {str(e)}")