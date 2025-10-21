"""
Protocol definitions for the DOPE API.

This module defines the type contract for the DOPE (Data On Previous Engagement) module API.
All implementations of the DOPE API must conform to this protocol.

DOPE is the convergence point that aggregates data from all other modules:
- Chronograph (velocity measurements)
- Cartridges (with bullet specifications)
- Rifles (firearm configurations)
- Weather (environmental conditions)
- Ranges (location and distance)
"""

from typing import Dict, List, Optional, Protocol, Any
from .models import DopeSessionModel, DopeMeasurementModel
from .filters import DopeSessionFilter


class DopeAPIProtocol(Protocol):
    """
    Protocol defining the public API for the DOPE module.

    DOPE (Data On Previous Engagement) is the central aggregation layer that brings
    together chronograph data, cartridges, rifles, weather, and range information
    into unified sessions for ballistic analysis.

    Access model:
    - All operations are user-scoped (user_id required)
    - Users can only access their own DOPE sessions and measurements
    - DOPE sessions reference admin-owned data (bullets, cartridges) via foreign keys
    - DOPE sessions reference user-owned data (rifles, chronograph, weather, ranges) via foreign keys

    All ballistic data is stored in metric units internally.
    """

    # -------------------------------------------------------------------------
    # Session Management
    # -------------------------------------------------------------------------

    def get_sessions_for_user(self, user_id: str) -> List[DopeSessionModel]:
        """
        Get all DOPE sessions for a specific user with joined data.

        Returns sessions with denormalized data from related tables including:
        - Cartridge and bullet information
        - Rifle specifications
        - Range location and geometry
        - Weather conditions (median values)
        - Chronograph session statistics

        Args:
            user_id: Auth0 user ID to filter sessions

        Returns:
            List[DopeSessionModel]: List of sessions ordered by created_at desc (empty list if none)

        Raises:
            Exception: If database query fails

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> sessions = api.get_sessions_for_user("auth0|123456")
            >>> len(sessions)
            15
            >>> sessions[0].session_name
            '308 Win @ 100m - 2025-08-10'
        """
        ...

    def get_session_by_id(
        self, session_id: str, user_id: str
    ) -> Optional[DopeSessionModel]:
        """
        Get a specific DOPE session by ID with joined data.

        Args:
            session_id: UUID of the DOPE session
            user_id: Auth0 user ID (security check)

        Returns:
            Optional[DopeSessionModel]: Session if found and owned by user, None otherwise

        Raises:
            Exception: If database query fails

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> session = api.get_session_by_id("123e4567-...", "auth0|123456")
            >>> session.rifle_name
            'Remington 700'
        """
        ...

    def create_session(
        self,
        session_data: Dict[str, Any],
        user_id: str,
        auto_create_measurements: bool = True
    ) -> DopeSessionModel:
        """
        Create a new DOPE session.

        Args:
            session_data: Dict with session fields (metric units). Required fields:
                - session_name: str
                - cartridge_id: str (FK to cartridges)
                - rifle_id: str (FK to rifles)
                - chrono_session_id: str (FK to chrono_sessions)
                - range_submission_id: str (FK to ranges_submissions)
                Optional fields:
                - weather_source_id: str (FK to weather_source)
                - notes: str
            user_id: Auth0 user ID (owner of session)
            auto_create_measurements: If True, automatically create dope_measurements
                from chronograph measurements

        Returns:
            DopeSessionModel: Created session with generated ID and joined data

        Raises:
            ValueError: If required fields missing or invalid
            Exception: If creation fails

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> session_data = {
            ...     "session_name": "308 Win @ 100m",
            ...     "cartridge_id": "cart-uuid",
            ...     "rifle_id": "rifle-uuid",
            ...     "chrono_session_id": "chrono-uuid",
            ...     "range_submission_id": "range-uuid",
            ... }
            >>> session = api.create_session(session_data, "auth0|123456")
            >>> session.id
            '123e4567-e89b-12d3-a456-426614174000'
        """
        ...

    def update_session(
        self,
        session_id: str,
        session_data: Dict[str, Any],
        user_id: str
    ) -> Optional[DopeSessionModel]:
        """
        Update an existing DOPE session.

        Args:
            session_id: UUID of session to update
            session_data: Dict with fields to update (metric units)
            user_id: Auth0 user ID (security check)

        Returns:
            Optional[DopeSessionModel]: Updated session if successful, None if not found/not owned

        Raises:
            Exception: If update fails

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> update_data = {"notes": "Windy conditions"}
            >>> session = api.update_session(session_id, update_data, "auth0|123456")
        """
        ...

    def delete_session(self, session_id: str, user_id: str) -> bool:
        """
        Delete a DOPE session and all its measurements.

        Args:
            session_id: UUID of session to delete
            user_id: Auth0 user ID (security check)

        Returns:
            bool: True if deleted, False if not found/not owned

        Raises:
            Exception: If delete fails

        Note:
            This will cascade delete all dope_measurements for this session.

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> deleted = api.delete_session(session_id, "auth0|123456")
            >>> if deleted:
            ...     print("Session deleted successfully")
        """
        ...

    def delete_sessions_bulk(
        self, session_ids: List[str], user_id: str
    ) -> Dict[str, Any]:
        """
        Delete multiple DOPE sessions in bulk.

        Args:
            session_ids: List of session UUIDs to delete
            user_id: Auth0 user ID (security check)

        Returns:
            Dict with:
                - deleted_count: int - Number of sessions deleted
                - failed_ids: List[str] - IDs that failed to delete

        Raises:
            Exception: If bulk delete fails

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> result = api.delete_sessions_bulk(["id1", "id2"], "auth0|123456")
            >>> result['deleted_count']
            2
        """
        ...

    # -------------------------------------------------------------------------
    # Session Querying & Filtering
    # -------------------------------------------------------------------------

    def search_sessions(
        self,
        user_id: str,
        search_term: str,
        search_fields: Optional[List[str]] = None
    ) -> List[DopeSessionModel]:
        """
        Search DOPE sessions by text across multiple fields.

        Args:
            user_id: Auth0 user ID to filter sessions
            search_term: Text to search for (case-insensitive)
            search_fields: Optional list of field names to search in.
                Defaults to: session_name, notes, cartridge_make, cartridge_model,
                bullet_make, bullet_model, rifle_name

        Returns:
            List[DopeSessionModel]: Matching sessions (empty list if no matches)

        Raises:
            Exception: If search fails

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> sessions = api.search_sessions("auth0|123456", "Sierra 168")
            >>> all("sierra" in s.bullet_make.lower() for s in sessions)
            True
        """
        ...

    def filter_sessions(
        self,
        user_id: str,
        filters: DopeSessionFilter
    ) -> List[DopeSessionModel]:
        """
        Filter DOPE sessions by multiple criteria.

        Args:
            user_id: Auth0 user ID to filter sessions
            filters: DopeSessionFilter instance with filter criteria

        Returns:
            List[DopeSessionModel]: Filtered sessions (empty list if no matches)

        Raises:
            Exception: If filtering fails

        Example:
            >>> from dope.filters import DopeSessionFilter
            >>> api = DopeAPI(supabase_client)
            >>> filters = DopeSessionFilter(
            ...     cartridge_type="308 Winchester",
            ...     rifle_id="rifle-uuid"
            ... )
            >>> sessions = api.filter_sessions("auth0|123456", filters)
        """
        ...

    def get_unique_values(self, user_id: str, field_name: str) -> List[str]:
        """
        Get unique values for a specific field across user's sessions.

        Useful for populating UI dropdowns and filters.

        Args:
            user_id: Auth0 user ID to filter sessions
            field_name: Name of field to get unique values for
                (e.g., "cartridge_type", "rifle_name", "bullet_make")

        Returns:
            List[str]: Sorted list of unique values (empty list if none)

        Raises:
            ValueError: If field_name is invalid
            Exception: If query fails

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> cartridge_types = api.get_unique_values("auth0|123456", "cartridge_type")
            >>> cartridge_types
            ['223 Remington', '308 Winchester', '6.5 Creedmoor']
        """
        ...

    def get_session_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get aggregate statistics across all user's DOPE sessions.

        Returns:
            Dict with statistics including:
                - total_sessions: int
                - total_measurements: int
                - unique_rifles: int
                - unique_cartridges: int
                - date_range: Dict[str, datetime]

        Raises:
            Exception: If statistics calculation fails

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> stats = api.get_session_statistics("auth0|123456")
            >>> stats['total_sessions']
            42
        """
        ...

    # -------------------------------------------------------------------------
    # Measurement Management
    # -------------------------------------------------------------------------

    def get_measurements_for_dope_session(
        self, dope_session_id: str, user_id: str
    ) -> List[DopeMeasurementModel]:
        """
        Get all measurements for a specific DOPE session.

        Args:
            dope_session_id: UUID of the DOPE session
            user_id: Auth0 user ID (security check)

        Returns:
            List[DopeMeasurementModel]: List of measurements ordered by shot_number (empty if none)

        Raises:
            Exception: If database query fails

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> measurements = api.get_measurements_for_dope_session(session_id, "auth0|123456")
            >>> len(measurements)
            10
            >>> measurements[0].speed_mps
            792.5
        """
        ...

    def create_measurement(
        self, measurement_data: Dict[str, Any], user_id: str
    ) -> DopeMeasurementModel:
        """
        Create a new DOPE measurement.

        Args:
            measurement_data: Dict with measurement fields (metric units). Required:
                - dope_session_id: str
                Optional fields include: shot_number, speed_mps, ke_j, temperature_c, etc.
            user_id: Auth0 user ID (security check)

        Returns:
            DopeMeasurementModel: Created measurement with generated ID

        Raises:
            ValueError: If required fields missing or invalid
            Exception: If creation fails

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> measurement_data = {
            ...     "dope_session_id": "session-uuid",
            ...     "shot_number": 1,
            ...     "speed_mps": 792.5,
            ...     "temperature_c": 21.0,
            ... }
            >>> measurement = api.create_measurement(measurement_data, "auth0|123456")
        """
        ...

    def update_measurement(
        self,
        measurement_id: str,
        measurement_data: Dict[str, Any],
        user_id: str
    ) -> Optional[DopeMeasurementModel]:
        """
        Update an existing DOPE measurement.

        Args:
            measurement_id: UUID of measurement to update
            measurement_data: Dict with fields to update (metric units)
            user_id: Auth0 user ID (security check)

        Returns:
            Optional[DopeMeasurementModel]: Updated measurement if successful, None if not found/not owned

        Raises:
            Exception: If update fails

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> update_data = {"shot_notes": "Flyer - wind gust"}
            >>> measurement = api.update_measurement(meas_id, update_data, "auth0|123456")
        """
        ...

    def delete_measurement(self, measurement_id: str, user_id: str) -> bool:
        """
        Delete a DOPE measurement.

        Args:
            measurement_id: UUID of measurement to delete
            user_id: Auth0 user ID (security check)

        Returns:
            bool: True if deleted, False if not found/not owned

        Raises:
            Exception: If delete fails

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> deleted = api.delete_measurement(meas_id, "auth0|123456")
        """
        ...

    # -------------------------------------------------------------------------
    # UI Helper Methods
    # -------------------------------------------------------------------------

    def get_edit_dropdown_options(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get dropdown options for editing DOPE sessions.

        Returns options for rifles, cartridges, chronograph sessions, weather sources, and ranges.

        Args:
            user_id: Auth0 user ID to filter user-owned data

        Returns:
            Dict with keys:
                - rifles: List[Dict] with id, name
                - cartridges: List[Dict] with id, display_name
                - chrono_sessions: List[Dict] with id, session_name
                - weather_sources: List[Dict] with id, name
                - ranges: List[Dict] with id, display_name

        Raises:
            Exception: If query fails

        Example:
            >>> api = DopeAPI(supabase_client)
            >>> options = api.get_edit_dropdown_options("auth0|123456")
            >>> len(options['rifles'])
            5
        """
        ...