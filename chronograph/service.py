from typing import List, Optional

from .models import ChronographMeasurement, ChronographSession


class ChronographService:
    """Service class for chronograph database operations"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_sessions_for_user(self, user_email: str) -> List[ChronographSession]:
        """Get all chronograph sessions for a user, ordered by date descending"""
        try:
            response = (
                self.supabase.table("chrono_sessions")
                .select("*")
                .eq("user_email", user_email)
                .order("datetime_local", desc=True)
                .execute()
            )

            if not response.data:
                return []

            return ChronographSession.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error fetching sessions: {str(e)}")

    def get_session_by_id(
        self, session_id: str, user_email: str
    ) -> Optional[ChronographSession]:
        """Get a specific chronograph session by ID"""
        try:
            response = (
                self.supabase.table("chrono_sessions")
                .select("*")
                .eq("id", session_id)
                .eq("user_email", user_email)
                .single()
                .execute()
            )

            if not response.data:
                return None

            return ChronographSession.from_supabase_record(response.data)

        except Exception as e:
            raise Exception(f"Error fetching session: {str(e)}")

    def get_measurements_for_session(
        self, user_email: str, session_id: str
    ) -> List[ChronographMeasurement]:
        """Get all measurements for a specific session"""
        try:
            response = (
                self.supabase.table("chrono_measurements")
                .select("*")
                .eq("user_email", user_email)
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
        self, session_id: str, user_email: str
    ) -> List[ChronographMeasurement]:
        """Get measurements for a session by session ID"""
        try:
            return self.get_measurements_for_session(user_email, session_id)

        except Exception as e:
            raise Exception(f"Error fetching measurements by session ID: {str(e)}")

    def get_sessions_filtered(
        self,
        user_email: str,
        bullet_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[ChronographSession]:
        """Get filtered chronograph sessions"""
        try:
            query = (
                self.supabase.table("chrono_sessions")
                .select("*")
                .eq("user_email", user_email)
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

    def get_unique_bullet_types(self, user_email: str) -> List[str]:
        """Get unique bullet types for a user"""
        try:
            response = (
                self.supabase.table("chrono_sessions")
                .select("bullet_type")
                .eq("user_email", user_email)
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
        self, user_email: str, tab_name: str, datetime_local: str
    ) -> bool:
        """Check if a session already exists"""
        try:
            response = (
                self.supabase.table("chrono_sessions")
                .select("id")
                .eq("user_email", user_email)
                .eq("tab_name", tab_name)
                .eq("datetime_local", datetime_local)
                .execute()
            )

            return len(response.data) > 0

        except Exception as e:
            raise Exception(f"Error checking session existence: {str(e)}")

    def create_session(self, session_data: dict) -> str:
        """Create a new chronograph session"""
        try:
            response = (
                self.supabase.table("chrono_sessions").insert(session_data).execute()
            )

            if not response.data:
                raise Exception("Failed to create session")

            return response.data[0]["id"]

        except Exception as e:
            raise Exception(f"Error creating session: {str(e)}")

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
        self, user_email: str, session_id: str
    ) -> List[float]:
        """Get speed measurements for calculating session statistics"""
        try:
            response = (
                self.supabase.table("chrono_measurements")
                .select("speed_fps")
                .eq("user_email", user_email)
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
