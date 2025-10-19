"""
Chronograph Client API Facade.

This module provides a synchronous API for chronograph operations within
the ChronoLog application. It implements the ChronographAPIProtocol and wraps
the ChronographService to provide a clean, type-safe interface.

Usage:
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

    # Create measurements
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

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from .business_logic import SessionStatisticsCalculator
from .chronograph_session_models import ChronographMeasurement, ChronographSession
from .chronograph_source_models import ChronographSource
from .service import ChronographService


class ChronographAPI:
    """
    Main API facade for chronograph operations.

    This class provides a clean interface for all chronograph-related operations,
    handling ID generation, timestamps, and user access control automatically.

    Attributes:
        _supabase: Supabase client instance
        _service: ChronographService instance for database operations
    """

    def __init__(self, supabase_client):
        """
        Initialize Chronograph API.

        Args:
            supabase_client: Authenticated Supabase client
        """
        self._supabase = supabase_client
        self._service = ChronographService(supabase_client)

    # ==================== Chronograph Source Operations ====================

    def get_all_sources(self, user_id: str) -> List[ChronographSource]:
        """Get all chronograph sources for a user."""
        try:
            return self._service.get_sources_for_user(user_id)
        except Exception as e:
            raise Exception(f"Error getting chronograph sources: {str(e)}")

    def get_source_by_id(
        self, source_id: str, user_id: str
    ) -> Optional[ChronographSource]:
        """Get a specific chronograph source by ID."""
        try:
            return self._service.get_source_by_id(source_id, user_id)
        except Exception as e:
            if "PGRST116" in str(e) or "0 rows" in str(e):
                return None
            raise Exception(f"Error getting chronograph source: {str(e)}")

    def get_source_by_name(
        self, user_id: str, name: str
    ) -> Optional[ChronographSource]:
        """Get a chronograph source by name."""
        try:
            return self._service.get_source_by_name(user_id, name)
        except Exception:
            return None

    def create_source(
        self, source_data: dict, user_id: str
    ) -> ChronographSource:
        """Create a new chronograph source with auto-generated ID and timestamps."""
        try:
            insert_data = source_data.copy()
            insert_data["id"] = str(uuid.uuid4())
            insert_data["user_id"] = user_id
            insert_data["created_at"] = datetime.now().isoformat()
            insert_data["updated_at"] = datetime.now().isoformat()

            if "source_type" not in insert_data:
                insert_data["source_type"] = "chronograph"

            source_id = self._service.create_source(insert_data)

            source = self._service.get_source_by_id(source_id, user_id)
            if not source:
                raise Exception(f"Failed to retrieve created source {source_id}")

            return source

        except Exception as e:
            raise Exception(f"Error creating chronograph source: {str(e)}")

    def update_source(
        self, source_id: str, updates: dict, user_id: str
    ) -> ChronographSource:
        """Update an existing chronograph source with auto-updated timestamp."""
        try:
            update_data = updates.copy()
            update_data["updated_at"] = datetime.now().isoformat()

            self._service.update_source(source_id, user_id, update_data)

            updated_source = self._service.get_source_by_id(source_id, user_id)
            if not updated_source:
                raise Exception(f"Source {source_id} not found or not owned by user")

            return updated_source

        except Exception as e:
            raise Exception(f"Error updating chronograph source: {str(e)}")

    def delete_source(self, source_id: str, user_id: str) -> bool:
        """Delete a chronograph source."""
        try:
            self._service.delete_source(source_id, user_id)
            return True
        except Exception as e:
            raise Exception(f"Error deleting chronograph source: {str(e)}")

    def create_or_get_source_from_device_info(
        self,
        user_id: str,
        device_name: str,
        device_model: str,
        serial_number: str,
    ) -> str:
        """
        Create or retrieve existing chronograph source from device information.

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
            Source ID (existing or newly created)
        """
        try:
            return self._service.create_or_get_source_from_device_info(
                user_id, device_name, device_model, serial_number
            )
        except Exception as e:
            raise Exception(
                f"Error creating/getting source from device info: {str(e)}"
            )

    # ==================== Session Operations ====================

    def get_all_sessions(self, user_id: str) -> List[ChronographSession]:
        """Get all chronograph sessions for a user."""
        try:
            return self._service.get_sessions_for_user(user_id)
        except Exception as e:
            raise Exception(f"Error getting sessions: {str(e)}")

    def get_session_by_id(
        self, session_id: str, user_id: str
    ) -> Optional[ChronographSession]:
        """Get a specific chronograph session by ID."""
        try:
            return self._service.get_session_by_id(session_id, user_id)
        except Exception as e:
            if "PGRST116" in str(e) or "0 rows" in str(e):
                return None
            raise Exception(f"Error getting session: {str(e)}")

    def filter_sessions(
        self,
        user_id: str,
        bullet_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[ChronographSession]:
        """Get filtered chronograph sessions."""
        try:
            return self._service.get_sessions_filtered(
                user_id, bullet_type, start_date, end_date
            )
        except Exception as e:
            raise Exception(f"Error filtering sessions: {str(e)}")

    def create_session(
        self, session_data: dict, user_id: str
    ) -> ChronographSession:
        """Create a new chronograph session with auto-generated ID and timestamps."""
        try:
            # Convert datetime_local from string to datetime if needed
            datetime_local = session_data["datetime_local"]
            if isinstance(datetime_local, str):
                datetime_local = datetime.fromisoformat(datetime_local)

            session = ChronographSession(
                id=str(uuid.uuid4()),
                user_id=user_id,
                tab_name=session_data["tab_name"],
                session_name=session_data.get("session_name", ""),
                datetime_local=datetime_local,
                uploaded_at=datetime.now(),
                file_path=session_data.get("file_path"),
                chronograph_source_id=session_data.get("chronograph_source_id"),
            )

            session_id = self._service.save_chronograph_session(session)
            session.id = session_id

            return session

        except Exception as e:
            raise Exception(f"Error creating session: {str(e)}")

    def session_exists(
        self, user_id: str, tab_name: str, datetime_local: str
    ) -> bool:
        """Check if a session already exists."""
        try:
            return self._service.session_exists(user_id, tab_name, datetime_local)
        except Exception as e:
            raise Exception(f"Error checking session existence: {str(e)}")

    # ==================== Measurement Operations ====================

    def get_measurements_for_session(
        self, session_id: str, user_id: str
    ) -> List[ChronographMeasurement]:
        """Get all measurements for a specific session."""
        try:
            return self._service.get_measurements_for_session(user_id, session_id)
        except Exception as e:
            raise Exception(f"Error getting measurements for session: {str(e)}")

    def create_measurement(
        self, measurement_data: dict, user_id: str
    ) -> ChronographMeasurement:
        """Create a new chronograph measurement with auto-generated ID."""
        try:
            measurement = ChronographMeasurement(
                id=str(uuid.uuid4()),
                user_id=user_id,
                chrono_session_id=measurement_data["chrono_session_id"],
                shot_number=measurement_data["shot_number"],
                speed_mps=measurement_data["speed_mps"],
                datetime_local=measurement_data["datetime_local"],
                delta_avg_mps=measurement_data.get("delta_avg_mps"),
                ke_j=measurement_data.get("ke_j"),
                power_factor_kgms=measurement_data.get("power_factor_kgms"),
                clean_bore=measurement_data.get("clean_bore", False),
                cold_bore=measurement_data.get("cold_bore", False),
                shot_notes=measurement_data.get("shot_notes"),
            )

            measurement_id = self._service.save_chronograph_measurement(measurement)
            measurement.id = measurement_id

            # Update session statistics
            self._service.calculate_and_update_session_stats(
                user_id, measurement_data["chrono_session_id"]
            )

            return measurement

        except Exception as e:
            raise Exception(f"Error creating measurement: {str(e)}")

    def create_measurements_batch(
        self, measurements_data: List[dict], user_id: str
    ) -> List[ChronographMeasurement]:
        """Create multiple chronograph measurements in a batch."""
        try:
            created_measurements = []
            session_ids_to_update = set()

            for measurement_data in measurements_data:
                measurement = ChronographMeasurement(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    chrono_session_id=measurement_data["chrono_session_id"],
                    shot_number=measurement_data["shot_number"],
                    speed_mps=measurement_data["speed_mps"],
                    datetime_local=measurement_data["datetime_local"],
                    delta_avg_mps=measurement_data.get("delta_avg_mps"),
                    ke_j=measurement_data.get("ke_j"),
                    power_factor_kgms=measurement_data.get("power_factor_kgms"),
                    clean_bore=measurement_data.get("clean_bore", False),
                    cold_bore=measurement_data.get("cold_bore", False),
                    shot_notes=measurement_data.get("shot_notes"),
                )

                measurement_id = self._service.save_chronograph_measurement(measurement)
                measurement.id = measurement_id
                created_measurements.append(measurement)
                session_ids_to_update.add(measurement_data["chrono_session_id"])

            # Update statistics for all affected sessions
            for session_id in session_ids_to_update:
                self._service.calculate_and_update_session_stats(user_id, session_id)

            return created_measurements

        except Exception as e:
            raise Exception(f"Error creating measurements batch: {str(e)}")

    # ==================== Statistics and Utility Operations ====================

    def calculate_session_statistics(
        self, session_id: str, user_id: str
    ) -> dict:
        """Calculate statistics for a session."""
        try:
            speeds = self._service.get_measurements_for_stats(user_id, session_id)
            if not speeds:
                return {
                    "shot_count": 0,
                    "avg_speed_mps": 0.0,
                    "std_dev_mps": 0.0,
                    "min_speed_mps": 0.0,
                    "max_speed_mps": 0.0,
                    "extreme_spread_mps": 0.0,
                    "coefficient_of_variation": 0.0,
                }

            stats = SessionStatisticsCalculator.calculate_session_stats(speeds)

            return {
                "shot_count": len(speeds),
                "avg_speed_mps": stats["avg_speed_mps"],
                "std_dev_mps": stats["std_dev_mps"],
                "min_speed_mps": stats["min_speed_mps"],
                "max_speed_mps": stats["max_speed_mps"],
                "extreme_spread_mps": stats["max_speed_mps"] - stats["min_speed_mps"],
                "coefficient_of_variation": (stats["std_dev_mps"] / stats["avg_speed_mps"]) * 100
                if stats["avg_speed_mps"] > 0
                else 0.0,
            }

        except Exception as e:
            raise Exception(f"Error calculating session statistics: {str(e)}")

    def get_unique_bullet_types(self, user_id: str) -> List[str]:
        """Get a list of unique bullet types used by the user."""
        try:
            return self._service.get_unique_bullet_types(user_id)
        except Exception as e:
            raise Exception(f"Error getting unique bullet types: {str(e)}")

    def get_time_window(
        self, user_id: str, days: int = 30
    ) -> Tuple[datetime, datetime]:
        """Get a time window for recent sessions."""
        try:
            return self._service.get_time_window(user_id, days)
        except Exception as e:
            raise Exception(f"Error getting time window: {str(e)}")
