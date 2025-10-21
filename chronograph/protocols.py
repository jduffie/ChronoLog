"""
Protocol definitions for Chronograph API.

This module defines the ChronographAPIProtocol, which specifies the interface
for all chronograph-related operations in the ChronoLog application.

The protocol uses Python's typing.Protocol for structural subtyping,
allowing any class that implements these methods to be used as a
chronograph API, regardless of inheritance.
"""

from datetime import datetime
from typing import List, Optional, Protocol, Tuple

from .chronograph_session_models import ChronographMeasurement, ChronographSession
from .chronograph_source_models import ChronographSource


class ChronographAPIProtocol(Protocol):
    """
    Protocol defining the interface for chronograph operations.

    This protocol specifies all methods required for managing chronograph sources
    (devices), sessions (shooting sessions), and measurements (individual shots).
    Any class implementing this protocol can be used interchangeably throughout
    the application.

    The protocol supports:
    - Chronograph source (device) management
    - Session management with statistics
    - Measurement storage and retrieval
    - Filtering and querying
    - Batch operations
    """

    # ==================== Chronograph Source Operations ====================

    def get_all_sources(self, user_id: str) -> List[ChronographSource]:
        """
        Get all chronograph sources for a user.

        Args:
            user_id: User identifier

        Returns:
            List of ChronographSource objects owned by the user

        Example:
            >>> sources = api.get_all_sources("user-123")
            >>> for source in sources:
            ...     print(source.display_name())
        """
        ...

    def get_source_by_id(
        self, source_id: str, user_id: str
    ) -> Optional[ChronographSource]:
        """
        Get a specific chronograph source by ID.

        Args:
            source_id: Chronograph source identifier
            user_id: User identifier (for access control)

        Returns:
            ChronographSource if found and owned by user, None otherwise

        Example:
            >>> source = api.get_source_by_id("source-123", "user-123")
            >>> if source:
            ...     print(source.device_display())
        """
        ...

    def get_source_by_name(
        self, user_id: str, name: str
    ) -> Optional[ChronographSource]:
        """
        Get a chronograph source by name.

        Args:
            user_id: User identifier
            name: Source name to search for

        Returns:
            ChronographSource if found, None otherwise

        Example:
            >>> source = api.get_source_by_name("user-123", "Garmin Xero C1")
        """
        ...

    def create_source(
        self, source_data: dict, user_id: str
    ) -> ChronographSource:
        """
        Create a new chronograph source.

        Args:
            source_data: Dictionary containing source information
                Required: name
                Optional: device_name, make, model, serial_number
            user_id: User identifier

        Returns:
            Created ChronographSource with generated ID and timestamps

        Raises:
            Exception: If creation fails

        Example:
            >>> source_data = {
            ...     "name": "My Garmin",
            ...     "make": "Garmin",
            ...     "model": "Xero C1",
            ...     "serial_number": "G123456"
            ... }
            >>> source = api.create_source(source_data, "user-123")
        """
        ...

    def update_source(
        self, source_id: str, updates: dict, user_id: str
    ) -> ChronographSource:
        """
        Update an existing chronograph source.

        Args:
            source_id: Chronograph source identifier
            updates: Dictionary of fields to update
            user_id: User identifier (for access control)

        Returns:
            Updated ChronographSource

        Raises:
            Exception: If source not found or update fails

        Example:
            >>> updates = {"name": "Updated Name", "make": "Garmin"}
            >>> source = api.update_source("source-123", updates, "user-123")
        """
        ...

    def delete_source(self, source_id: str, user_id: str) -> bool:
        """
        Delete a chronograph source.

        Args:
            source_id: Chronograph source identifier
            user_id: User identifier (for access control)

        Returns:
            True if deleted successfully

        Raises:
            Exception: If deletion fails

        Example:
            >>> success = api.delete_source("source-123", "user-123")
        """
        ...

    # ==================== Session Operations ====================

    def get_all_sessions(self, user_id: str) -> List[ChronographSession]:
        """
        Get all chronograph sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            List of ChronographSession objects, ordered by date descending

        Example:
            >>> sessions = api.get_all_sessions("user-123")
            >>> for session in sessions:
            ...     print(session.display_name())
        """
        ...

    def get_session_by_id(
        self, session_id: str, user_id: str
    ) -> Optional[ChronographSession]:
        """
        Get a specific chronograph session by ID.

        Args:
            session_id: Session identifier
            user_id: User identifier (for access control)

        Returns:
            ChronographSession if found and owned by user, None otherwise

        Example:
            >>> session = api.get_session_by_id("session-123", "user-123")
            >>> if session:
            ...     print(f"Shots: {session.shot_count}")
        """
        ...

    def filter_sessions(
        self,
        user_id: str,
        bullet_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[ChronographSession]:
        """
        Get filtered chronograph sessions.

        Args:
            user_id: User identifier
            bullet_type: Optional bullet type filter
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)

        Returns:
            List of filtered ChronographSession objects

        Example:
            >>> sessions = api.filter_sessions(
            ...     "user-123",
            ...     bullet_type="168gr HPBT",
            ...     start_date="2024-01-01T00:00:00",
            ...     end_date="2024-01-31T23:59:59"
            ... )
        """
        ...

    def create_session(
        self, session_data: dict, user_id: str
    ) -> ChronographSession:
        """
        Create a new chronograph session.

        Args:
            session_data: Dictionary containing session information
                Required: tab_name, session_name, datetime_local
                Optional: file_path, chronograph_source_id
            user_id: User identifier

        Returns:
            Created ChronographSession with generated ID

        Raises:
            Exception: If creation fails

        Example:
            >>> session_data = {
            ...     "tab_name": "168gr HPBT",
            ...     "session_name": "Range Day 1",
            ...     "datetime_local": "2024-01-15T10:00:00",
            ...     "chronograph_source_id": "source-123"
            ... }
            >>> session = api.create_session(session_data, "user-123")
        """
        ...

    def session_exists(
        self, user_id: str, tab_name: str, datetime_local: str
    ) -> bool:
        """
        Check if a session already exists.

        Args:
            user_id: User identifier
            tab_name: Tab name to check
            datetime_local: Datetime to check (ISO format)

        Returns:
            True if session exists, False otherwise

        Example:
            >>> exists = api.session_exists(
            ...     "user-123",
            ...     "168gr HPBT",
            ...     "2024-01-15T10:00:00"
            ... )
        """
        ...

    # ==================== Measurement Operations ====================

    def get_measurements_for_session(
        self, session_id: str, user_id: str
    ) -> List[ChronographMeasurement]:
        """
        Get all measurements for a specific session.

        Args:
            session_id: Session identifier
            user_id: User identifier (for access control)

        Returns:
            List of ChronographMeasurement objects, ordered by shot number

        Example:
            >>> measurements = api.get_measurements_for_session(
            ...     "session-123", "user-123"
            ... )
            >>> for m in measurements:
            ...     print(f"Shot {m.shot_number}: {m.speed_mps} m/s")
        """
        ...

    def create_measurement(
        self, measurement_data: dict, user_id: str
    ) -> ChronographMeasurement:
        """
        Create a new chronograph measurement.

        Args:
            measurement_data: Dictionary containing measurement data
                Required: chrono_session_id, shot_number, speed_mps, datetime_local
                Optional: ke_j, power_factor_kgms, clean_bore, cold_bore, shot_notes
            user_id: User identifier

        Returns:
            Created ChronographMeasurement with generated ID

        Raises:
            Exception: If creation fails

        Example:
            >>> measurement_data = {
            ...     "chrono_session_id": "session-123",
            ...     "shot_number": 1,
            ...     "speed_mps": 792.5,
            ...     "datetime_local": "2024-01-15T10:00:00"
            ... }
            >>> measurement = api.create_measurement(
            ...     measurement_data, "user-123"
            ... )
        """
        ...

    def create_measurements_batch(
        self, measurements_data: List[dict], user_id: str
    ) -> List[ChronographMeasurement]:
        """
        Create multiple chronograph measurements in a single batch.

        Args:
            measurements_data: List of measurement data dictionaries
            user_id: User identifier

        Returns:
            List of created ChronographMeasurement objects

        Raises:
            Exception: If batch creation fails

        Note:
            This method also updates session statistics for all affected sessions

        Example:
            >>> batch_data = [
            ...     {
            ...         "chrono_session_id": "session-123",
            ...         "shot_number": 1,
            ...         "speed_mps": 792.5,
            ...         "datetime_local": "2024-01-15T10:00:00"
            ...     },
            ...     {
            ...         "chrono_session_id": "session-123",
            ...         "shot_number": 2,
            ...         "speed_mps": 794.2,
            ...         "datetime_local": "2024-01-15T10:00:05"
            ...     }
            ... ]
            >>> measurements = api.create_measurements_batch(
            ...     batch_data, "user-123"
            ... )
        """
        ...

    # ==================== Statistics and Utility Operations ====================

    def calculate_session_statistics(
        self, session_id: str, user_id: str
    ) -> dict:
        """
        Calculate statistics for a session.

        Args:
            session_id: Session identifier
            user_id: User identifier (for access control)

        Returns:
            Dictionary with statistics:
                - shot_count: Number of shots
                - avg_speed_mps: Average velocity
                - std_dev_mps: Standard deviation
                - min_speed_mps: Minimum velocity
                - max_speed_mps: Maximum velocity
                - extreme_spread_mps: Max - Min velocity
                - coefficient_of_variation: (std_dev / avg) * 100

        Example:
            >>> stats = api.calculate_session_statistics(
            ...     "session-123", "user-123"
            ... )
            >>> print(f"Average: {stats['avg_speed_mps']} m/s")
            >>> print(f"SD: {stats['std_dev_mps']} m/s")
        """
        ...

    def get_unique_bullet_types(self, user_id: str) -> List[str]:
        """
        Get a list of unique bullet types used by the user.

        Args:
            user_id: User identifier

        Returns:
            List of unique bullet type strings (from session tab_name)

        Example:
            >>> bullet_types = api.get_unique_bullet_types("user-123")
            >>> print(bullet_types)
            ['168gr HPBT', '175gr SMK', '140gr ELD-M']
        """
        ...

    def get_time_window(
        self, user_id: str, days: int = 30
    ) -> Tuple[datetime, datetime]:
        """
        Get a time window for recent sessions.

        Args:
            user_id: User identifier
            days: Number of days to look back (default: 30)

        Returns:
            Tuple of (start_datetime, end_datetime)

        Example:
            >>> start, end = api.get_time_window("user-123", days=7)
            >>> # Get sessions from last 7 days
            >>> sessions = api.filter_sessions(
            ...     "user-123",
            ...     start_date=start.isoformat(),
            ...     end_date=end.isoformat()
            ... )
        """
        ...