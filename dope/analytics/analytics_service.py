"""
DOPE Analytics Service

Business logic for fetching and filtering DOPE sessions for analysis.
"""

from typing import List

from dope.api import DopeAPI
from dope.models import DopeMeasurementModel, DopeSessionModel

from .filters import SessionFilter


class AnalyticsService:
    """Service for fetching and filtering DOPE data for analytics"""

    def __init__(self, supabase_client):
        """
        Initialize the analytics service.

        Args:
            supabase_client: Supabase client instance
        """
        if not supabase_client:
            raise ValueError("Supabase client is required")

        self._supabase = supabase_client
        self._dope_api = DopeAPI(supabase_client)

    def get_sessions_for_analysis(
        self, user_id: str, filters: SessionFilter = None
    ) -> List[DopeSessionModel]:
        """
        Get DOPE sessions for analysis with optional filtering.

        Args:
            user_id: Auth0 user ID
            filters: Optional SessionFilter with filter criteria

        Returns:
            List[DopeSessionModel]: Filtered sessions (empty if none match)

        Raises:
            Exception: If database query fails

        Example:
            >>> service = AnalyticsService(supabase_client)
            >>> filters = SessionFilter(rifle_id="rifle-uuid")
            >>> sessions = service.get_sessions_for_analysis("auth0|123", filters)
        """
        # Get all sessions for user
        all_sessions = self._dope_api.get_sessions_for_user(user_id)

        # If no filters, return all
        if not filters or not filters.has_filters():
            return all_sessions

        # Apply filters
        return self._apply_filters(all_sessions, filters)

    def get_measurements_for_sessions(
        self, session_ids: List[str], user_id: str
    ) -> List[DopeMeasurementModel]:
        """
        Get all measurements for multiple DOPE sessions.

        Args:
            session_ids: List of DOPE session UUIDs
            user_id: Auth0 user ID (security check)

        Returns:
            List[DopeMeasurementModel]: All measurements from all sessions

        Raises:
            Exception: If database query fails

        Example:
            >>> service = AnalyticsService(supabase_client)
            >>> measurements = service.get_measurements_for_sessions(
            ...     ["session1", "session2"], "auth0|123"
            ... )
        """
        all_measurements = []

        for session_id in session_ids:
            measurements = self._dope_api.get_measurements_for_dope_session(
                session_id, user_id
            )
            all_measurements.extend(measurements)

        return all_measurements

    def _apply_filters(
        self, sessions: List[DopeSessionModel], filters: SessionFilter
    ) -> List[DopeSessionModel]:
        """
        Apply filters to session list.

        Args:
            sessions: List of sessions to filter
            filters: Filter criteria

        Returns:
            List[DopeSessionModel]: Filtered sessions
        """
        filtered = sessions

        # Filter by specific session IDs
        if filters.session_ids:
            filtered = [s for s in filtered if s.id in filters.session_ids]

        # Exclude specific session IDs
        if filters.exclude_session_ids:
            filtered = [s for s in filtered if s.id not in filters.exclude_session_ids]

        # Filter by rifle
        if filters.rifle_id:
            filtered = [s for s in filtered if s.rifle_id == filters.rifle_id]
        elif filters.rifle_ids:
            filtered = [s for s in filtered if s.rifle_id in filters.rifle_ids]

        # Filter by cartridge
        if filters.cartridge_id:
            filtered = [s for s in filtered if s.cartridge_id == filters.cartridge_id]
        elif filters.cartridge_ids:
            filtered = [s for s in filtered if s.cartridge_id in filters.cartridge_ids]

        # Filter by bullet
        if filters.bullet_id:
            filtered = [s for s in filtered if s.bullet_id == filters.bullet_id]
        elif filters.bullet_ids:
            filtered = [s for s in filtered if s.bullet_id in filters.bullet_ids]

        # Filter by cartridge type
        if filters.cartridge_type:
            filtered = [
                s for s in filtered if s.cartridge_type == filters.cartridge_type
            ]

        # Filter by date range
        if filters.start_date:
            filtered = [
                s
                for s in filtered
                if s.start_time and s.start_time >= filters.start_date
            ]

        if filters.end_date:
            filtered = [
                s for s in filtered if s.start_time and s.start_time <= filters.end_date
            ]

        # Filter by temperature range
        if filters.temperature_min_c is not None:
            filtered = [
                s
                for s in filtered
                if s.temperature_c_median is not None
                and s.temperature_c_median >= filters.temperature_min_c
            ]

        if filters.temperature_max_c is not None:
            filtered = [
                s
                for s in filtered
                if s.temperature_c_median is not None
                and s.temperature_c_median <= filters.temperature_max_c
            ]

        # Filter by humidity range
        if filters.humidity_min_pct is not None:
            filtered = [
                s
                for s in filtered
                if s.relative_humidity_pct_median is not None
                and s.relative_humidity_pct_median >= filters.humidity_min_pct
            ]

        if filters.humidity_max_pct is not None:
            filtered = [
                s
                for s in filtered
                if s.relative_humidity_pct_median is not None
                and s.relative_humidity_pct_median <= filters.humidity_max_pct
            ]

        # Filter by pressure range
        if filters.pressure_min_hpa is not None:
            filtered = [
                s
                for s in filtered
                if s.barometric_pressure_hpa_median is not None
                and s.barometric_pressure_hpa_median >= filters.pressure_min_hpa
            ]

        if filters.pressure_max_hpa is not None:
            filtered = [
                s
                for s in filtered
                if s.barometric_pressure_hpa_median is not None
                and s.barometric_pressure_hpa_median <= filters.pressure_max_hpa
            ]

        # Filter by range
        if filters.range_submission_id:
            filtered = [
                s
                for s in filtered
                if s.range_submission_id == filters.range_submission_id
            ]

        if filters.range_distance_min_m is not None:
            filtered = [
                s
                for s in filtered
                if s.range_distance_m is not None
                and s.range_distance_m >= filters.range_distance_min_m
            ]

        if filters.range_distance_max_m is not None:
            filtered = [
                s
                for s in filtered
                if s.range_distance_m is not None
                and s.range_distance_m <= filters.range_distance_max_m
            ]

        # Filter by velocity range (using avg velocity)
        if filters.velocity_min_mps is not None:
            filtered = [
                s
                for s in filtered
                if s.speed_mps_avg is not None
                and s.speed_mps_avg >= filters.velocity_min_mps
            ]

        if filters.velocity_max_mps is not None:
            filtered = [
                s
                for s in filtered
                if s.speed_mps_avg is not None
                and s.speed_mps_avg <= filters.velocity_max_mps
            ]

        return filtered