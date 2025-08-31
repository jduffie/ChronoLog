from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import ChronographMeasurement, ChronographSession
from .business_logic import ChronographDataProcessor, SessionStatisticsCalculator
from .unit_mapping_service import UnitMappingService
from .device_adapters import ChronographDeviceFactory


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
            raise Exception(f"Error fetching measurements by session ID: {str(e)}")

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

    def session_exists(self, user_id: str, tab_name: str, datetime_local: str) -> bool:
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

    def get_measurements_for_stats(self, user_id: str, session_id: str) -> List[float]:
        """Get speed measurements for calculating session statistics"""
        try:
            response = (
                self.supabase.table("chrono_measurements")
                .select("speed_fps")
                .eq("user_id", user_id)
                .eq("chrono_session_id", session_id)
                .execute()
            )

            if not response.data:
                return []

            speeds = [
                record["speed_fps"]
                for record in response.data
                if record.get("speed_fps") is not None
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
                "bullet_type": session.bullet_type,
                "bullet_grain": session.bullet_grain,
                "datetime_local": session.datetime_local.isoformat(),
                "uploaded_at": session.uploaded_at.isoformat(),
                "file_path": session.file_path,
                "shot_count": session.shot_count,
                "avg_speed_fps": session.avg_speed_fps,
                "std_dev_fps": session.std_dev_fps,
                "min_speed_fps": session.min_speed_fps,
                "max_speed_fps": session.max_speed_fps,
            }
            
            response = self.supabase.table("chrono_sessions").insert(session_data).execute()
            
            if not response.data:
                raise Exception("Failed to save session")
            
            return response.data[0]["id"]
            
        except Exception as e:
            raise Exception(f"Error saving session: {str(e)}")
    
    def save_chronograph_measurement(self, measurement: ChronographMeasurement) -> str:
        """Save a ChronographMeasurement entity to Supabase"""
        try:
            measurement_data = {
                "id": measurement.id,
                "user_id": measurement.user_id,
                "chrono_session_id": measurement.chrono_session_id,
                "shot_number": measurement.shot_number,
                "speed_fps": measurement.speed_fps,
                "speed_mps": measurement.speed_mps,
                "delta_avg_fps": measurement.delta_avg_fps,
                "delta_avg_mps": measurement.delta_avg_mps,
                "ke_ft_lb": measurement.ke_ft_lb,
                "ke_j": measurement.ke_j,
                "power_factor": measurement.power_factor,
                "power_factor_kgms": measurement.power_factor_kgms,
                "datetime_local": measurement.datetime_local.isoformat() if measurement.datetime_local else None,
                "clean_bore": measurement.clean_bore,
                "cold_bore": measurement.cold_bore,
                "shot_notes": measurement.shot_notes,
            }
            
            response = self.supabase.table("chrono_measurements").insert(measurement_data).execute()
            
            if not response.data:
                raise Exception("Failed to save measurement")
            
            return response.data[0]["id"]
            
        except Exception as e:
            raise Exception(f"Error saving measurement: {str(e)}")
    
    def calculate_and_update_session_stats(self, user_id: str, session_id: str) -> None:
        """Calculate and update session statistics"""
        speeds = self.get_measurements_for_stats(user_id, session_id)
        if speeds:
            stats = SessionStatisticsCalculator.calculate_session_stats(speeds)
            self.update_session_stats(session_id, stats)
