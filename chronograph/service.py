from datetime import datetime
from typing import List, Optional

from .business_logic import SessionStatisticsCalculator
from .chronograph_session_models import ChronographMeasurement, ChronographSession
from .chronograph_source_models import ChronographSource


class ChronographService:
    """Service class for chronograph database operations"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_sessions_for_user(self, user_id: str) -> List[ChronographSession]:
        """Get all chronograph sessions for a user, ordered by date descending"""
        try:
            response = (
                self.supabase.table("chrono_sessions")
                .select("*")
                .eq("user_id", user_id)
                .order("datetime_local", desc=True)
                .execute()
            )

            if not response.data:
                return []

            return ChronographSession.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error fetching sessions: {str(e)}")

    def get_session_by_id(
        self, session_id: str, user_id: str
    ) -> Optional[ChronographSession]:
        """Get a specific chronograph session by ID"""
        try:
            response = (
                self.supabase.table("chrono_sessions")
                .select("*")
                .eq("id", session_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )

            if not response.data:
                return None

            return ChronographSession.from_supabase_record(response.data)

        except Exception as e:
            raise Exception(f"Error fetching session: {str(e)}")

    def get_measurements_for_session(
        self, user_id: str, session_id: str
    ) -> List[ChronographMeasurement]:
        """Get all measurements for a specific session"""
        try:
            response = (
                self.supabase.table("chrono_measurements")
                .select("*")
                .eq("user_id", user_id)
                .eq("chrono_session_id", session_id)
                .order("shot_number")
                .execute()
            )

            if not response.data:
                return []

            return ChronographMeasurement.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error fetching measurements: {str(e)}")

    def get_measurements_by_session_id(
        self, session_id: str, user_id: str
    ) -> List[ChronographMeasurement]:
        """Get measurements for a session by session ID"""
        try:
            return self.get_measurements_for_session(user_id, session_id)

        except Exception as e:
            raise Exception(
                f"Error fetching measurements by session ID: {str(e)}")

    def get_sessions_filtered(
        self,
        user_id: str,
        bullet_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[ChronographSession]:
        """Get filtered chronograph sessions"""
        try:
            query = (
                self.supabase.table("chrono_sessions")
                .select("*")
                .eq("user_id", user_id)
            )

            if bullet_type and bullet_type != "All":
                query = query.eq("bullet_type", bullet_type)

            if start_date:
                query = query.gte("datetime_local", start_date)

            if end_date:
                query = query.lte("datetime_local", end_date)

            response = query.order("datetime_local", desc=True).execute()

            if not response.data:
                return []

            return ChronographSession.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error fetching filtered sessions: {str(e)}")

    def get_unique_bullet_types(self, user_id: str) -> List[str]:
        """Get unique bullet types for a user"""
        try:
            response = (
                self.supabase.table("chrono_sessions")
                .select("bullet_type")
                .eq("user_id", user_id)
                .execute()
            )

            if not response.data:
                return []

            bullet_types = list(
                set(
                    [
                        record["bullet_type"]
                        for record in response.data
                        if record.get("bullet_type")
                    ]
                )
            )
            return sorted(bullet_types)

        except Exception as e:
            raise Exception(f"Error fetching bullet types: {str(e)}")

    def session_exists(
            self,
            user_id: str,
            tab_name: str,
            datetime_local: str) -> bool:
        """Check if a session already exists"""
        try:
            response = (
                self.supabase.table("chrono_sessions")
                .select("id")
                .eq("user_id", user_id)
                .eq("tab_name", tab_name)
                .eq("datetime_local", datetime_local)
                .execute()
            )

            return len(response.data) > 0

        except Exception as e:
            raise Exception(f"Error checking session existence: {str(e)}")

    def update_session_stats(self, session_id: str, stats: dict) -> None:
        """Update session statistics"""
        try:
            self.supabase.table("chrono_sessions").update(stats).eq(
                "id", session_id
            ).execute()

        except Exception as e:
            raise Exception(f"Error updating session stats: {str(e)}")

    def create_measurement(self, measurement_data: dict) -> str:
        """Create a new chronograph measurement"""
        try:
            response = (
                self.supabase.table("chrono_measurements")
                .insert(measurement_data)
                .execute()
            )

            if not response.data:
                raise Exception("Failed to create measurement")

            return response.data[0]["id"]

        except Exception as e:
            raise Exception(f"Error creating measurement: {str(e)}")

    def get_measurements_for_stats(
            self,
            user_id: str,
            session_id: str) -> List[float]:
        """Get speed measurements for calculating session statistics"""
        try:
            response = (
                self.supabase.table("chrono_measurements")
                .select("speed_mps")
                .eq("user_id", user_id)
                .eq("chrono_session_id", session_id)
                .execute()
            )

            if not response.data:
                return []

            speeds = [
                record["speed_mps"]
                for record in response.data
                if record.get("speed_mps") is not None
            ]
            return speeds

        except Exception as e:
            raise Exception(f"Error fetching measurements for stats: {str(e)}")

    def save_chronograph_session(self, session: ChronographSession) -> str:
        """Save a ChronographSession entity to Supabase"""
        try:
            session_data = {
                "id": session.id,
                "user_id": session.user_id,
                "tab_name": session.tab_name,
                "session_name": session.session_name,
                "bullet_type": "bullet_type_temp",
                "bullet_grain": 0.0,
                "datetime_local": session.datetime_local.isoformat(),
                "uploaded_at": session.uploaded_at.isoformat(),
                "file_path": session.file_path,
                "shot_count": session.shot_count,
                "avg_speed_mps": session.avg_speed_mps,
                "std_dev_mps": session.std_dev_mps,
                "min_speed_mps": session.min_speed_mps,
                "max_speed_mps": session.max_speed_mps,
            }

            response = self.supabase.table(
                "chrono_sessions").insert(session_data).execute()

            if not response.data:
                raise Exception("Failed to save session")

            return response.data[0]["id"]

        except Exception as e:
            raise Exception(f"Error saving session: {str(e)}")

    def save_chronograph_measurement(
            self, measurement: ChronographMeasurement) -> str:
        """Save a ChronographMeasurement entity to Supabase"""
        try:
            measurement_data = {
                "id": measurement.id,
                "user_id": measurement.user_id,
                "chrono_session_id": measurement.chrono_session_id,
                "shot_number": measurement.shot_number,
                "speed_mps": measurement.speed_mps,
                "delta_avg_mps": measurement.delta_avg_mps,
                "ke_j": measurement.ke_j,
                "power_factor_kgms": measurement.power_factor_kgms,
                "datetime_local": measurement.datetime_local.isoformat() if measurement.datetime_local else None,
                "clean_bore": measurement.clean_bore,
                "cold_bore": measurement.cold_bore,
                "shot_notes": measurement.shot_notes,
            }

            response = self.supabase.table(
                "chrono_measurements").insert(measurement_data).execute()

            if not response.data:
                raise Exception("Failed to save measurement")

            return response.data[0]["id"]

        except Exception as e:
            raise Exception(f"Error saving measurement: {str(e)}")

    def calculate_and_update_session_stats(
            self, user_id: str, session_id: str) -> None:
        """Calculate and update session statistics"""
        speeds = self.get_measurements_for_stats(user_id, session_id)
        if speeds:
            stats = SessionStatisticsCalculator.calculate_session_stats(speeds)
            self.update_session_stats(session_id, stats)

    def get_sources_for_user(self, user_id: str) -> List[ChronographSource]:
        """Get all chronograph sources for a user"""
        try:
            response = (
                self.supabase.table("chronograph_sources")
                .select("*")
                .eq("user_id", user_id)
                .order("name")
                .execute()
            )

            if not response.data:
                return []

            return ChronographSource.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error fetching chronograph sources: {str(e)}")

    def get_source_by_id(
            self,
            source_id: str,
            user_id: str) -> Optional[ChronographSource]:
        """Get a specific chronograph source by ID"""
        try:
            response = (
                self.supabase.table("chronograph_sources")
                .select("*")
                .eq("id", source_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )

            if not response.data:
                return None

            return ChronographSource.from_supabase_record(response.data)

        except Exception as e:
            raise Exception(f"Error fetching chronograph source: {str(e)}")

    def get_source_by_name(
            self,
            user_id: str,
            name: str) -> Optional[ChronographSource]:
        """Get a chronograph source by name"""
        try:
            response = (
                self.supabase.table("chronograph_sources")
                .select("*")
                .eq("user_id", user_id)
                .eq("name", name)
                .single()
                .execute()
            )

            if not response.data:
                return None

            return ChronographSource.from_supabase_record(response.data)

        except Exception as e:
            return None

    def create_source(self, source_data: dict) -> str:
        """Create a new chronograph source"""
        try:
            response = (self.supabase.table(
                "chronograph_sources").insert(source_data).execute())

            if not response.data:
                raise Exception("Failed to create chronograph source")

            return response.data[0]["id"]

        except Exception as e:
            raise Exception(f"Error creating chronograph source: {str(e)}")

    def update_source(
            self,
            source_id: str,
            user_id: str,
            updates: dict) -> None:
        """Update a chronograph source"""
        try:
            updates["updated_at"] = datetime.now().isoformat()
            self.supabase.table("chronograph_sources").update(updates).eq(
                "id", source_id).eq("user_id", user_id).execute()

        except Exception as e:
            raise Exception(f"Error updating chronograph source: {str(e)}")

    def delete_source(self, source_id: str, user_id: str) -> None:
        """Delete a chronograph source"""
        try:
            self.supabase.table("chronograph_sources").delete().eq(
                "id", source_id).eq("user_id", user_id).execute()

        except Exception as e:
            raise Exception(f"Error deleting chronograph source: {str(e)}")

    def update_source_with_device_info(
            self,
            source_id: str,
            user_id: str,
            device_name: str,
            device_model: str,
            serial_number: str) -> None:
        """Update chronograph source with device info from uploaded file"""
        try:
            updates = {
                "device_name": device_name if device_name else None,
                "model": device_model if device_model else None,
                "serial_number": serial_number if serial_number else None,
                "updated_at": datetime.now().isoformat()
            }

            self.supabase.table("chronograph_sources").update(updates).eq(
                "id", source_id).eq("user_id", user_id).execute()

        except Exception as e:
            raise Exception(
                f"Error updating chronograph source with device info: {str(e)}")
