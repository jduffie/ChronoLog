from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from .models import DopeSessionModel


class DopeService:
    """Service class for DOPE sessions database operations"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_sessions_for_user(self, user_id: str) -> List[DopeSessionModel]:
        """Get all DOPE sessions for a specific user"""
        # TODO: Replace with actual Supabase query
        # response = (
        #     self.supabase.table("dope_sessions")
        #     .select("*")
        #     .eq("user_id", user_id)
        #     .order("datetime_local", desc=True)
        #     .execute()
        # )
        # return DopeSessionModel.from_supabase_records(response.data)
        
        return self._get_mock_sessions(user_id)

    def get_session_by_id(self, session_id: str, user_id: str) -> Optional[DopeSessionModel]:
        """Get a specific DOPE session by ID"""
        # TODO: Replace with actual Supabase query
        # response = (
        #     self.supabase.table("dope_sessions")
        #     .select("*")
        #     .eq("id", session_id)
        #     .eq("user_id", user_id)
        #     .single()
        #     .execute()
        # )
        # return DopeSessionModel.from_supabase_record(response.data) if response.data else None
        
        mock_sessions = self._get_mock_sessions(user_id)
        return next((session for session in mock_sessions if session.id == session_id), None)

    def create_session(self, session_data: Dict[str, Any], user_id: str) -> DopeSessionModel:
        """Create a new DOPE session"""
        # TODO: Replace with actual Supabase insert
        # session_data["user_id"] = user_id
        # session_data["datetime_local"] = datetime.now()
        # response = (
        #     self.supabase.table("dope_sessions")
        #     .insert(session_data)
        #     .execute()
        # )
        # return DopeSessionModel.from_supabase_record(response.data[0])
        
        # Mock implementation
        new_session = DopeSessionModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            datetime_local=datetime.now(),
            **session_data
        )
        return new_session

    def update_session(self, session_id: str, session_data: Dict[str, Any], user_id: str) -> DopeSessionModel:
        """Update an existing DOPE session"""
        # TODO: Replace with actual Supabase update
        # response = (
        #     self.supabase.table("dope_sessions")
        #     .update(session_data)
        #     .eq("id", session_id)
        #     .eq("user_id", user_id)
        #     .execute()
        # )
        # return DopeSessionModel.from_supabase_record(response.data[0])
        
        # Mock implementation
        existing_session = self.get_session_by_id(session_id, user_id)
        if existing_session:
            # Update fields
            for key, value in session_data.items():
                if hasattr(existing_session, key):
                    setattr(existing_session, key, value)
            return existing_session
        raise Exception(f"Session {session_id} not found")

    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a DOPE session"""
        # TODO: Replace with actual Supabase delete
        # response = (
        #     self.supabase.table("dope_sessions")
        #     .delete()
        #     .eq("id", session_id)
        #     .eq("user_id", user_id)
        #     .execute()
        # )
        # return len(response.data) > 0
        
        # Mock implementation
        return True

    def search_sessions(self, user_id: str, search_term: str) -> List[DopeSessionModel]:
        """Search DOPE sessions by text across multiple fields"""
        # TODO: Replace with actual Supabase query with text search
        # response = (
        #     self.supabase.table("dope_sessions")
        #     .select("*")
        #     .eq("user_id", user_id)
        #     .or_(f"session_name.ilike.%{search_term}%,"
        #          f"cartridge_make.ilike.%{search_term}%,"
        #          f"cartridge_model.ilike.%{search_term}%,"
        #          f"bullet_make.ilike.%{search_term}%,"
        #          f"bullet_model.ilike.%{search_term}%,"
        #          f"range_name.ilike.%{search_term}%,"
        #          f"notes.ilike.%{search_term}%")
        #     .execute()
        # )
        # return DopeSessionModel.from_supabase_records(response.data)
        
        # Mock implementation
        all_sessions = self._get_mock_sessions(user_id)
        search_lower = search_term.lower()
        filtered_sessions = []
        
        for session in all_sessions:
            if (search_lower in session.session_name.lower() or
                search_lower in session.cartridge_make.lower() or
                search_lower in session.cartridge_model.lower() or
                search_lower in session.bullet_make.lower() or
                search_lower in session.bullet_model.lower() or
                (session.range_name and search_lower in session.range_name.lower()) or
                (session.notes and search_lower in session.notes.lower())):
                filtered_sessions.append(session)
        
        return filtered_sessions

    def filter_sessions(self, user_id: str, filters: Dict[str, Any]) -> List[DopeSessionModel]:
        """Filter DOPE sessions based on various criteria"""
        # TODO: Replace with actual Supabase query with filters
        # query = self.supabase.table("dope_sessions").select("*").eq("user_id", user_id)
        # 
        # Apply filters
        # if filters.get("status"):
        #     query = query.eq("status", filters["status"])
        # if filters.get("cartridge_type"):
        #     query = query.eq("cartridge_type", filters["cartridge_type"])
        # if filters.get("date_from"):
        #     query = query.gte("datetime_local", filters["date_from"])
        # if filters.get("date_to"):
        #     query = query.lte("datetime_local", filters["date_to"])
        # etc...
        # 
        # response = query.execute()
        # return DopeSessionModel.from_supabase_records(response.data)
        
        # Mock implementation
        all_sessions = self._get_mock_sessions(user_id)
        filtered_sessions = all_sessions
        
        # Apply status filter
        if filters.get("status") and filters["status"] != "All":
            filtered_sessions = [s for s in filtered_sessions if s.status == filters["status"]]
        
        # Apply cartridge type filter
        if filters.get("cartridge_type"):
            filtered_sessions = [s for s in filtered_sessions if s.cartridge_type == filters["cartridge_type"]]
        
        # Apply date range filter
        if filters.get("date_from"):
            filtered_sessions = [s for s in filtered_sessions if s.datetime_local and s.datetime_local >= filters["date_from"]]
        if filters.get("date_to"):
            filtered_sessions = [s for s in filtered_sessions if s.datetime_local and s.datetime_local <= filters["date_to"]]
        
        # Apply rifle filter
        if filters.get("rifle_name"):
            filtered_sessions = [s for s in filtered_sessions if s.rifle_name == filters["rifle_name"]]
        
        # Apply distance range filter
        if filters.get("distance_range"):
            min_dist, max_dist = filters["distance_range"]
            filtered_sessions = [s for s in filtered_sessions 
                               if s.distance_m and min_dist <= s.distance_m <= max_dist]
        
        # Apply cartridge make filter
        if filters.get("cartridge_make"):
            filtered_sessions = [s for s in filtered_sessions if s.cartridge_make == filters["cartridge_make"]]
        
        # Apply bullet make filter
        if filters.get("bullet_make"):
            filtered_sessions = [s for s in filtered_sessions if s.bullet_make == filters["bullet_make"]]
        
        # Apply range name filter
        if filters.get("range_name"):
            filtered_sessions = [s for s in filtered_sessions if s.range_name == filters["range_name"]]
        
        # Apply bullet weight range filter
        if filters.get("bullet_weight_range"):
            min_weight, max_weight = filters["bullet_weight_range"]
            filtered_sessions = [s for s in filtered_sessions 
                               if s.bullet_weight and min_weight <= float(s.bullet_weight) <= max_weight]
        
        # Apply temperature range filter
        if filters.get("temperature_range"):
            min_temp, max_temp = filters["temperature_range"]
            filtered_sessions = [s for s in filtered_sessions 
                               if s.temperature_c is not None and min_temp <= s.temperature_c <= max_temp]
        
        # Apply humidity range filter
        if filters.get("humidity_range"):
            min_humidity, max_humidity = filters["humidity_range"]
            filtered_sessions = [s for s in filtered_sessions 
                               if s.relative_humidity_pct is not None and min_humidity <= s.relative_humidity_pct <= max_humidity]
        
        # Apply wind speed range filter
        if filters.get("wind_speed_range"):
            min_wind, max_wind = filters["wind_speed_range"]
            filtered_sessions = [s for s in filtered_sessions 
                               if s.wind_speed_1_kmh is not None and min_wind <= s.wind_speed_1_kmh <= max_wind]
        
        return filtered_sessions

    def get_unique_values(self, user_id: str, field_name: str) -> List[str]:
        """Get unique values for a specific field for autocomplete filters"""
        # TODO: Replace with actual Supabase query
        # response = (
        #     self.supabase.table("dope_sessions")
        #     .select(field_name)
        #     .eq("user_id", user_id)
        #     .not_.is_(field_name, "null")
        #     .execute()
        # )
        # unique_values = list(set([row[field_name] for row in response.data if row[field_name]]))
        # return sorted(unique_values)
        
        # Mock implementation
        all_sessions = self._get_mock_sessions(user_id)
        values = set()
        
        for session in all_sessions:
            value = getattr(session, field_name, None)
            if value and isinstance(value, str) and value.strip():
                values.add(value)
        
        return sorted(list(values))

    def get_session_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about user's DOPE sessions"""
        # TODO: Replace with actual Supabase aggregation queries
        
        # Mock implementation
        sessions = self._get_mock_sessions(user_id)
        
        total_sessions = len(sessions)
        active_sessions = len([s for s in sessions if s.status == "active"])
        
        cartridge_types = set(s.cartridge_type for s in sessions if s.cartridge_type)
        bullet_makes = set(s.bullet_make for s in sessions if s.bullet_make)
        ranges = set(s.range_name for s in sessions if s.range_name)
        
        distances = [s.distance_m for s in sessions if s.distance_m]
        avg_distance = sum(distances) / len(distances) if distances else 0
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "archived_sessions": total_sessions - active_sessions,
            "unique_cartridge_types": len(cartridge_types),
            "unique_bullet_makes": len(bullet_makes),
            "unique_ranges": len(ranges),
            "average_distance_m": round(avg_distance, 1),
            "distance_range": f"{min(distances)}-{max(distances)}m" if distances else "No data"
        }

    def _get_mock_sessions(self, user_id: str) -> List[DopeSessionModel]:
        """Generate mock DOPE sessions for development/testing"""
        base_date = datetime.now()
        
        # Only return mock data for the specific user ID, otherwise return empty list
        if user_id != "google-oauth2|111273793361054745867":
            return []
        
        mock_sessions = [
            DopeSessionModel(
                id="session_001",
                user_id="google-oauth2|111273793361054745867",
                session_name="Morning Range Session",
                datetime_local=base_date - timedelta(days=1),
                cartridge_spec_id="spec_001",
                status="active",
                rifle_name="AR-15 SPR",
                rifle_barrel_length_cm=50.8,
                rifle_barrel_twist_in_per_rev=8.0,
                cartridge_make="Federal",
                cartridge_model="Gold Medal Match",
                cartridge_type="223 Remington",
                cartridge_lot_number="LT2024001",
                bullet_make="Sierra",
                bullet_model="MatchKing",
                bullet_weight="77",
                bullet_length_mm="23.1",
                ballistic_coefficient_g1="0.372",
                ballistic_coefficient_g7="0.190",
                sectional_density="0.220",
                bullet_diameter_groove_mm="5.69",
                bore_diameter_land_mm="5.56",
                range_name="Pine Valley Range",
                distance_m=100.0,
                temperature_c=22.0,
                relative_humidity_pct=65.0,
                barometric_pressure_inhg=30.15,
                wind_speed_1_kmh=8.0,
                wind_direction_deg=270.0,
                notes="Excellent conditions, consistent groups"
            ),
            DopeSessionModel(
                id="session_002",
                user_id="google-oauth2|111273793361054745867",
                session_name="Long Range Practice",
                datetime_local=base_date - timedelta(days=3),
                cartridge_spec_id="spec_002",
                status="active",
                rifle_name="Precision .308",
                rifle_barrel_length_cm=61.0,
                rifle_barrel_twist_in_per_rev=10.0,
                cartridge_make="Hornady",
                cartridge_model="Match",
                cartridge_type="308 Winchester",
                bullet_make="Hornady",
                bullet_model="ELD Match",
                bullet_weight="168",
                ballistic_coefficient_g1="0.523",
                ballistic_coefficient_g7="0.268",
                range_name="Mountain Ridge Range",
                distance_m=300.0,
                temperature_c=18.0,
                relative_humidity_pct=45.0,
                barometric_pressure_inhg=29.92,
                wind_speed_1_kmh=12.0,
                wind_direction_deg=135.0,
                notes="Windy conditions, good for practice"
            ),
            DopeSessionModel(
                id="session_003",
                user_id="google-oauth2|111273793361054745867",
                session_name="Competition Prep",
                datetime_local=base_date - timedelta(days=7),
                cartridge_spec_id="spec_003",
                status="archived",
                rifle_name="Match AR-15",
                cartridge_make="Black Hills",
                cartridge_model="Match",
                cartridge_type="223 Remington",
                bullet_make="Sierra",
                bullet_model="MatchKing",
                bullet_weight="69",
                range_name="Competition Range",
                distance_m=200.0,
                temperature_c=25.0,
                notes="Final preparation before match"
            ),
            DopeSessionModel(
                id="session_004",
                user_id="google-oauth2|111273793361054745867",
                session_name="Cold Weather Test",
                datetime_local=base_date - timedelta(days=14),
                cartridge_spec_id="spec_004",
                status="active",
                rifle_name="AR-15 SPR",
                cartridge_make="Federal",
                cartridge_model="Gold Medal Match",
                cartridge_type="223 Remington",
                bullet_make="Sierra",
                bullet_model="MatchKing",
                bullet_weight="77",
                range_name="Winter Range",
                distance_m=100.0,
                temperature_c=-5.0,
                relative_humidity_pct=80.0,
                wind_speed_1_kmh=15.0,
                notes="Testing cold weather performance"
            ),
            DopeSessionModel(
                id="session_005",
                user_id="google-oauth2|111273793361054745867",
                session_name="New Load Development",
                datetime_local=base_date - timedelta(days=21),
                cartridge_spec_id="spec_005",
                status="active",
                rifle_name="Custom .300 WM",
                cartridge_make="Custom",
                cartridge_model="Handload",
                cartridge_type="300 Winchester Magnum",
                bullet_make="Berger",
                bullet_model="VLD Target",
                bullet_weight="210",
                range_name="Private Range",
                distance_m=600.0,
                temperature_c=20.0,
                notes="Load development session"
            )
        ]
        
        return mock_sessions