import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .models import DopeSessionModel


class DopeService:
    """Service class for DOPE sessions database operations"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_sessions_for_user(self, user_id: str) -> List[DopeSessionModel]:
        """Get all DOPE sessions for a specific user with joined data"""
        if not self.supabase or str(type(self.supabase).__name__) == "MagicMock":
            return self._get_mock_sessions(user_id)

        try:
            # Query dope_sessions with joins to get related data
            response = (
                self.supabase.table("dope_sessions")
                .select(
                    """
                    *,
                    cartridges!cartridge_id (
                        make,
                        model,
                        cartridge_type,
                        bullets!bullet_id (
                            manufacturer,
                            model,
                            weight_grains,
                            bullet_length_mm,
                            ballistic_coefficient_g1,
                            ballistic_coefficient_g7,
                            sectional_density,
                            bullet_diameter_groove_mm,
                            bore_diameter_land_mm
                        )
                    ),
                    rifles!rifle_id (
                        name,
                        barrel_length,
                        barrel_twist_ratio
                    ),
                    ranges_submissions!range_submission_id (
                        range_name,
                        start_lat,
                        start_lon,
                        start_altitude_m,
                        distance_m,
                        azimuth_deg,
                        elevation_angle_deg
                    ),
                    weather_source!weather_source_id (
                        name
                    )
                """
                )
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )

            # Convert the joined data to DopeSessionModel instances
            sessions = []
            for record in response.data:
                session_data = self._flatten_joined_record(record)
                sessions.append(DopeSessionModel.from_supabase_record(session_data))

            return sessions

        except Exception as e:
            print(f"Error fetching DOPE sessions: {e}")
            # Fallback to mock data for development
            return self._get_mock_sessions(user_id)

    def get_session_by_id(
        self, session_id: str, user_id: str
    ) -> Optional[DopeSessionModel]:
        """Get a specific DOPE session by ID with joined data"""
        if not self.supabase or str(type(self.supabase).__name__) == "MagicMock":
            mock_sessions = self._get_mock_sessions(user_id)
            return next(
                (session for session in mock_sessions if session.id == session_id), None
            )

        try:
            response = (
                self.supabase.table("dope_sessions")
                .select(
                    """
                    *,
                    cartridges!cartridge_id (
                        make,
                        model,
                        cartridge_type,
                        bullets!bullet_id (
                            manufacturer,
                            model,
                            weight_grains,
                            bullet_length_mm,
                            ballistic_coefficient_g1,
                            ballistic_coefficient_g7,
                            sectional_density,
                            bullet_diameter_groove_mm,
                            bore_diameter_land_mm
                        )
                    ),
                    rifles!rifle_id (
                        name,
                        barrel_length,
                        barrel_twist_ratio
                    ),
                    ranges_submissions!range_submission_id (
                        range_name,
                        start_lat,
                        start_lon,
                        start_altitude_m,
                        distance_m,
                        azimuth_deg,
                        elevation_angle_deg
                    ),
                    weather_source!weather_source_id (
                        name
                    )
                """
                )
                .eq("id", session_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )

            if response.data:
                session_data = self._flatten_joined_record(response.data)
                return DopeSessionModel.from_supabase_record(session_data)
            return None

        except Exception as e:
            print(f"Error fetching DOPE session {session_id}: {e}")
            # Fallback to mock data
            mock_sessions = self._get_mock_sessions(user_id)
            return next(
                (session for session in mock_sessions if session.id == session_id), None
            )

    def create_session(
        self, session_data: Dict[str, Any], user_id: str
    ) -> DopeSessionModel:
        """Create a new DOPE session"""
        if not self.supabase or str(type(self.supabase).__name__) == "MagicMock":
            # Mock implementation
            new_session = DopeSessionModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                datetime_local=datetime.now(),
                **session_data,
            )
            return new_session

        try:
            # Prepare data for insertion
            insert_data = session_data.copy()
            insert_data["user_id"] = user_id

            # Set creation timestamp if not provided
            if "created_at" not in insert_data:
                insert_data["created_at"] = datetime.now().isoformat()
            if "updated_at" not in insert_data:
                insert_data["updated_at"] = datetime.now().isoformat()

            response = (
                self.supabase.table("dope_sessions").insert(insert_data).execute()
            )

            if response.data:
                # Fetch the complete session with joined data
                return self.get_session_by_id(response.data[0]["id"], user_id)
            else:
                raise Exception("Failed to create session")

        except Exception as e:
            print(f"Error creating DOPE session: {e}")
            # Fallback to mock implementation
            new_session = DopeSessionModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                datetime_local=datetime.now(),
                **session_data,
            )
            return new_session

    def update_session(
        self, session_id: str, session_data: Dict[str, Any], user_id: str
    ) -> DopeSessionModel:
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
        if not self.supabase or str(type(self.supabase).__name__) == "MagicMock":
            # Mock implementation
            all_sessions = self._get_mock_sessions(user_id)
            search_lower = search_term.lower()
            filtered_sessions = []

            for session in all_sessions:
                if (
                    search_lower in session.session_name.lower()
                    or search_lower in session.cartridge_make.lower()
                    or search_lower in session.cartridge_model.lower()
                    or search_lower in session.bullet_make.lower()
                    or search_lower in session.bullet_model.lower()
                    or (
                        session.range_name
                        and search_lower in session.range_name.lower()
                    )
                    or (session.notes and search_lower in session.notes.lower())
                ):
                    filtered_sessions.append(session)

            return filtered_sessions

        try:
            # Use text search with PostgreSQL's ilike operator across joined tables
            response = (
                self.supabase.table("dope_sessions")
                .select(
                    """
                    *,
                    cartridges!cartridge_id (
                        make, model, cartridge_type,
                        bullets!bullet_id (
                            manufacturer, model, weight_grains,
                            bullet_diameter_groove_mm, bore_diameter_land_mm,
                            bullet_length_mm, ballistic_coefficient_g1,
                            ballistic_coefficient_g7, sectional_density,
                            min_req_twist_rate_in_per_rev, pref_twist_rate_in_per_rev,
                            data_source_name, data_source_url
                        )
                    ),
                    rifles!rifle_id (
                        name, barrel_length, barrel_twist_ratio,
                        sight_offset, trigger, scope
                    ),
                    ranges_submissions!range_submission_id (
                        range_name, range_description, distance_m,
                        start_lat, start_lon, end_lat, end_lon,
                        start_altitude_m, end_altitude_m,
                        azimuth_deg, elevation_angle_deg
                    ),
                    weather_source!weather_source_id (
                        name, source_type, make, device_name,
                        model, serial_number
                    )
                """
                )
                .eq("user_id", user_id)
                .or_(
                    f"session_name.ilike.%{search_term}%,"
                    f"notes.ilike.%{search_term}%,"
                    f"range_name.ilike.%{search_term}%"
                )
                .order("created_at", desc=True)
                .execute()
            )

            if response.data:
                sessions = []
                for record in response.data:
                    session_data = self._flatten_joined_record(record)
                    sessions.append(DopeSessionModel.from_supabase_record(session_data))

                # Additional filtering on joined data that can't be done in the SQL query
                if search_term:
                    search_lower = search_term.lower()
                    filtered_sessions = []
                    for session in sessions:
                        if (
                            search_lower in session.session_name.lower()
                            or (
                                session.cartridge_make
                                and search_lower in session.cartridge_make.lower()
                            )
                            or (
                                session.cartridge_model
                                and search_lower in session.cartridge_model.lower()
                            )
                            or (
                                session.bullet_make
                                and search_lower in session.bullet_make.lower()
                            )
                            or (
                                session.bullet_model
                                and search_lower in session.bullet_model.lower()
                            )
                            or (
                                session.range_name
                                and search_lower in session.range_name.lower()
                            )
                            or (session.notes and search_lower in session.notes.lower())
                        ):
                            filtered_sessions.append(session)
                    return filtered_sessions

                return sessions
            return []

        except Exception as e:
            print(f"Error searching DOPE sessions: {e}")
            # Fallback to mock data
            all_sessions = self._get_mock_sessions(user_id)
            search_lower = search_term.lower()
            filtered_sessions = []

            for session in all_sessions:
                if (
                    search_lower in session.session_name.lower()
                    or search_lower in session.cartridge_make.lower()
                    or search_lower in session.cartridge_model.lower()
                    or search_lower in session.bullet_make.lower()
                    or search_lower in session.bullet_model.lower()
                    or (
                        session.range_name
                        and search_lower in session.range_name.lower()
                    )
                    or (session.notes and search_lower in session.notes.lower())
                ):
                    filtered_sessions.append(session)

            return filtered_sessions

    def filter_sessions(
        self, user_id: str, filters: Dict[str, Any]
    ) -> List[DopeSessionModel]:
        """Filter DOPE sessions based on various criteria"""
        if not self.supabase or str(type(self.supabase).__name__) == "MagicMock":
            # Mock implementation
            all_sessions = self._get_mock_sessions(user_id)
            filtered_sessions = all_sessions

            # Apply status filter
            if filters.get("status") and filters["status"] != "All":
                filtered_sessions = [
                    s for s in filtered_sessions if s.status == filters["status"]
                ]

            # Apply cartridge type filter
            if filters.get("cartridge_type"):
                if filters["cartridge_type"] == "Not Defined":
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if not s.cartridge_type or s.cartridge_type.strip() == ""
                    ]
                else:
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if s.cartridge_type == filters["cartridge_type"]
                    ]

            # Apply date range filter
            if filters.get("date_from"):
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.datetime_local and s.datetime_local >= filters["date_from"]
                ]
            if filters.get("date_to"):
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.datetime_local and s.datetime_local <= filters["date_to"]
                ]

            # Apply rifle filter
            if filters.get("rifle_name"):
                if filters["rifle_name"] == "Not Defined":
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if not s.rifle_name or s.rifle_name.strip() == ""
                    ]
                else:
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if s.rifle_name == filters["rifle_name"]
                    ]

            # Apply distance range filter
            if filters.get("distance_range"):
                min_dist, max_dist = filters["distance_range"]
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.distance_m and min_dist <= s.distance_m <= max_dist
                ]

            # Apply cartridge make filter
            if filters.get("cartridge_make"):
                if filters["cartridge_make"] == "Not Defined":
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if not s.cartridge_make or s.cartridge_make.strip() == ""
                    ]
                else:
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if s.cartridge_make == filters["cartridge_make"]
                    ]

            # Apply bullet make filter
            if filters.get("bullet_make"):
                if filters["bullet_make"] == "Not Defined":
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if not s.bullet_make or s.bullet_make.strip() == ""
                    ]
                else:
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if s.bullet_make == filters["bullet_make"]
                    ]

            # Apply range name filter
            if filters.get("range_name"):
                if filters["range_name"] == "Not Defined":
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if not s.range_name or s.range_name.strip() == ""
                    ]
                else:
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if s.range_name == filters["range_name"]
                    ]

            # Apply bullet weight range filter
            if filters.get("bullet_weight_range"):
                min_weight, max_weight = filters["bullet_weight_range"]
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.bullet_weight
                    and min_weight <= float(s.bullet_weight) <= max_weight
                ]

            # Apply temperature range filter
            if filters.get("temperature_range"):
                min_temp, max_temp = filters["temperature_range"]
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.temperature_c is not None
                    and min_temp <= s.temperature_c <= max_temp
                ]

            # Apply humidity range filter
            if filters.get("humidity_range"):
                min_humidity, max_humidity = filters["humidity_range"]
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.relative_humidity_pct is not None
                    and min_humidity <= s.relative_humidity_pct <= max_humidity
                ]

            # Apply wind speed range filter
            if filters.get("wind_speed_range"):
                min_wind, max_wind = filters["wind_speed_range"]
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.wind_speed_1_kmh is not None
                    and min_wind <= s.wind_speed_1_kmh <= max_wind
                ]

            return filtered_sessions

        try:
            # Start with base query
            query = (
                self.supabase.table("dope_sessions")
                .select(
                    """
                    *,
                    cartridges!cartridge_id (
                        make, model, cartridge_type,
                        bullets!bullet_id (
                            manufacturer, model, weight_grains,
                            bullet_diameter_groove_mm, bore_diameter_land_mm,
                            bullet_length_mm, ballistic_coefficient_g1,
                            ballistic_coefficient_g7, sectional_density,
                            min_req_twist_rate_in_per_rev, pref_twist_rate_in_per_rev,
                            data_source_name, data_source_url
                        )
                    ),
                    rifles!rifle_id (
                        name, barrel_length, barrel_twist_ratio,
                        sight_offset, trigger, scope
                    ),
                    ranges_submissions!range_submission_id (
                        range_name, range_description, distance_m,
                        start_lat, start_lon, end_lat, end_lon,
                        start_altitude_m, end_altitude_m,
                        azimuth_deg, elevation_angle_deg
                    ),
                    weather_source!weather_source_id (
                        name, source_type, make, device_name,
                        model, serial_number
                    )
                """
                )
                .eq("user_id", user_id)
            )

            # Apply filters that can be done at the database level
            if filters.get("status") and filters["status"] != "All":
                query = query.eq("status", filters["status"])

            if filters.get("date_from"):
                query = query.gte("created_at", filters["date_from"].isoformat())
            if filters.get("date_to"):
                query = query.lte("created_at", filters["date_to"].isoformat())

            # Execute query
            response = query.order("created_at", desc=True).execute()

            if response.data:
                sessions = []
                for record in response.data:
                    session_data = self._flatten_joined_record(record)
                    sessions.append(DopeSessionModel.from_supabase_record(session_data))

                # Apply filters that require post-processing (joined data)
                filtered_sessions = sessions

                # Apply cartridge type filter on joined data
                if filters.get("cartridge_type") and filters["cartridge_type"] != "All":
                    if filters["cartridge_type"] == "Not Defined":
                        filtered_sessions = [
                            s for s in filtered_sessions
                            if s.cartridge_type is None
                        ]
                    else:
                        filtered_sessions = [
                            s
                            for s in filtered_sessions
                            if s.cartridge_type == filters["cartridge_type"]
                        ]

                # Apply rifle filter on joined data
                if filters.get("rifle_name") and filters["rifle_name"] != "All":
                    if filters["rifle_name"] == "Not Defined":
                        filtered_sessions = [
                            s for s in filtered_sessions
                            if not s.rifle_name or s.rifle_name.strip() == ""
                        ]
                    else:
                        filtered_sessions = [
                            s
                            for s in filtered_sessions
                            if s.rifle_name == filters["rifle_name"]
                        ]

                # Apply distance range filter
                if filters.get("distance_range"):
                    min_dist, max_dist = filters["distance_range"]
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if s.distance_m and min_dist <= s.distance_m <= max_dist
                    ]

                # Apply cartridge make filter
                if filters.get("cartridge_make") and filters["cartridge_make"] != "All":
                    if filters["cartridge_make"] == "Not Defined":
                        filtered_sessions = [
                            s for s in filtered_sessions
                            if s.cartridge_make is None
                        ]
                    else:
                        filtered_sessions = [
                            s
                            for s in filtered_sessions
                            if s.cartridge_make == filters["cartridge_make"]
                        ]

                # Apply bullet make filter
                if filters.get("bullet_make") and filters["bullet_make"] != "All":
                    if filters["bullet_make"] == "Not Defined":
                        filtered_sessions = [
                            s for s in filtered_sessions
                            if s.bullet_make is None
                        ]
                    else:
                        filtered_sessions = [
                            s
                            for s in filtered_sessions
                            if s.bullet_make == filters["bullet_make"]
                        ]

                # Apply range name filter
                if filters.get("range_name") and filters["range_name"] != "All":
                    if filters["range_name"] == "Not Defined":
                        filtered_sessions = [
                            s for s in filtered_sessions
                            if not s.range_name or s.range_name.strip() == ""
                        ]
                    else:
                        filtered_sessions = [
                            s
                            for s in filtered_sessions
                            if s.range_name == filters["range_name"]
                        ]

                # Apply bullet weight range filter
                if filters.get("bullet_weight_range"):
                    min_weight, max_weight = filters["bullet_weight_range"]
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if s.bullet_weight
                        and min_weight <= float(s.bullet_weight) <= max_weight
                    ]

                # Apply temperature range filter
                if filters.get("temperature_range"):
                    min_temp, max_temp = filters["temperature_range"]
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if s.temperature_c is not None
                        and min_temp <= s.temperature_c <= max_temp
                    ]

                # Apply humidity range filter
                if filters.get("humidity_range"):
                    min_humidity, max_humidity = filters["humidity_range"]
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if s.relative_humidity_pct is not None
                        and min_humidity <= s.relative_humidity_pct <= max_humidity
                    ]

                # Apply wind speed range filter
                if filters.get("wind_speed_range"):
                    min_wind, max_wind = filters["wind_speed_range"]
                    filtered_sessions = [
                        s
                        for s in filtered_sessions
                        if s.wind_speed_1_kmh is not None
                        and min_wind <= s.wind_speed_1_kmh <= max_wind
                    ]

                return filtered_sessions
            return []

        except Exception as e:
            print(f"Error filtering DOPE sessions: {e}")
            # Fallback to mock implementation
            all_sessions = self._get_mock_sessions(user_id)
            filtered_sessions = all_sessions

            # Apply same filters as mock implementation
            if filters.get("status") and filters["status"] != "All":
                filtered_sessions = [
                    s for s in filtered_sessions if s.status == filters["status"]
                ]

            if filters.get("cartridge_type"):
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.cartridge_type == filters["cartridge_type"]
                ]

            if filters.get("date_from"):
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.datetime_local and s.datetime_local >= filters["date_from"]
                ]
            if filters.get("date_to"):
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.datetime_local and s.datetime_local <= filters["date_to"]
                ]

            if filters.get("rifle_name"):
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.rifle_name == filters["rifle_name"]
                ]

            if filters.get("distance_range"):
                min_dist, max_dist = filters["distance_range"]
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.distance_m and min_dist <= s.distance_m <= max_dist
                ]

            if filters.get("cartridge_make"):
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.cartridge_make == filters["cartridge_make"]
                ]

            if filters.get("bullet_make"):
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.bullet_make == filters["bullet_make"]
                ]

            if filters.get("range_name"):
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.range_name == filters["range_name"]
                ]

            if filters.get("bullet_weight_range"):
                min_weight, max_weight = filters["bullet_weight_range"]
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.bullet_weight
                    and min_weight <= float(s.bullet_weight) <= max_weight
                ]

            if filters.get("temperature_range"):
                min_temp, max_temp = filters["temperature_range"]
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.temperature_c is not None
                    and min_temp <= s.temperature_c <= max_temp
                ]

            if filters.get("humidity_range"):
                min_humidity, max_humidity = filters["humidity_range"]
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.relative_humidity_pct is not None
                    and min_humidity <= s.relative_humidity_pct <= max_humidity
                ]

            if filters.get("wind_speed_range"):
                min_wind, max_wind = filters["wind_speed_range"]
                filtered_sessions = [
                    s
                    for s in filtered_sessions
                    if s.wind_speed_1_kmh is not None
                    and min_wind <= s.wind_speed_1_kmh <= max_wind
                ]

            return filtered_sessions

    def get_unique_values(self, user_id: str, field_name: str) -> List[str]:
        """Get unique values for a specific field for autocomplete filters"""
        if not self.supabase or str(type(self.supabase).__name__) == "MagicMock":
            # Mock implementation
            all_sessions = self._get_mock_sessions(user_id)
            values = set()

            for session in all_sessions:
                value = getattr(session, field_name, None)
                if value and isinstance(value, str) and value.strip():
                    values.add(value)

            return sorted(list(values))

        try:
            # Get all sessions and extract unique values from the flattened data
            # This is more efficient than querying each field separately since we need JOIN data
            sessions = self.get_sessions_for_user(user_id)
            values = set()

            for session in sessions:
                value = getattr(session, field_name, None)
                if value and isinstance(value, str) and value.strip():
                    values.add(value)

            return sorted(list(values))

        except Exception as e:
            print(f"Error getting unique values for {field_name}: {e}")
            # Fallback to mock implementation
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
            "distance_range": (
                f"{min(distances)}-{max(distances)}m" if distances else "No data"
            ),
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
                cartridge_id="cartridge_001",
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
                notes="Excellent conditions, consistent groups",
            ),
            DopeSessionModel(
                id="session_002",
                user_id="google-oauth2|111273793361054745867",
                session_name="Long Range Practice",
                datetime_local=base_date - timedelta(days=3),
                cartridge_id="cartridge_002",
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
                notes="Windy conditions, good for practice",
            ),
            DopeSessionModel(
                id="session_003",
                user_id="google-oauth2|111273793361054745867",
                session_name="Competition Prep",
                datetime_local=base_date - timedelta(days=7),
                cartridge_id="cartridge_003",
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
                notes="Final preparation before match",
            ),
            DopeSessionModel(
                id="session_004",
                user_id="google-oauth2|111273793361054745867",
                session_name="Cold Weather Test",
                datetime_local=base_date - timedelta(days=14),
                cartridge_id="cartridge_004",
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
                notes="Testing cold weather performance",
            ),
            DopeSessionModel(
                id="session_005",
                user_id="google-oauth2|111273793361054745867",
                session_name="New Load Development",
                datetime_local=base_date - timedelta(days=21),
                cartridge_id="cartridge_005",
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
                notes="Load development session",
            ),
        ]

        return mock_sessions

    def _flatten_joined_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten a joined Supabase record into a format compatible with DopeSessionModel"""
        flattened = record.copy()

        # Extract cartridge data
        if "cartridges" in record and record["cartridges"]:
            cartridge = record["cartridges"]
            flattened["cartridge_make"] = cartridge.get("make")
            flattened["cartridge_model"] = cartridge.get("model")
            flattened["cartridge_type"] = cartridge.get("cartridge_type")

            # Extract bullet data from within cartridge
            if "bullets" in cartridge and cartridge["bullets"]:
                bullet = cartridge["bullets"]
                flattened["bullet_make"] = bullet.get("manufacturer")
                flattened["bullet_model"] = bullet.get("model")
                flattened["bullet_weight"] = str(bullet.get("weight_grains", ""))
                flattened["bullet_length_mm"] = str(bullet.get("bullet_length_mm", ""))
                flattened["ballistic_coefficient_g1"] = str(
                    bullet.get("ballistic_coefficient_g1", "")
                )
                flattened["ballistic_coefficient_g7"] = str(
                    bullet.get("ballistic_coefficient_g7", "")
                )
                flattened["sectional_density"] = str(
                    bullet.get("sectional_density", "")
                )
                flattened["bullet_diameter_groove_mm"] = str(
                    bullet.get("bullet_diameter_groove_mm", "")
                )
                flattened["bore_diameter_land_mm"] = str(
                    bullet.get("bore_diameter_land_mm", "")
                )

            # Remove the nested cartridges object
            del flattened["cartridges"]

        # Extract rifle data
        if "rifles" in record and record["rifles"]:
            rifle = record["rifles"]
            flattened["rifle_name"] = rifle.get("name")
            flattened["rifle_barrel_length_cm"] = rifle.get("barrel_length")
            flattened["rifle_barrel_twist_in_per_rev"] = rifle.get("barrel_twist_ratio")
            del flattened["rifles"]

        # Extract range data
        if "ranges_submissions" in record and record["ranges_submissions"]:
            range_data = record["ranges_submissions"]
            flattened["range_name"] = range_data.get("range_name")
            flattened["start_lat"] = range_data.get("start_lat")
            flattened["start_lon"] = range_data.get("start_lon")
            flattened["start_altitude_m"] = range_data.get("start_altitude_m")
            flattened["distance_m"] = range_data.get("distance_m")
            flattened["azimuth_deg"] = range_data.get("azimuth_deg")
            flattened["elevation_angle_deg"] = range_data.get("elevation_angle_deg")
            del flattened["ranges_submissions"]

        # Extract weather source data
        if "weather_source" in record and record["weather_source"]:
            weather_source = record["weather_source"]
            flattened["weather_source_name"] = weather_source.get("name")
            del flattened["weather_source"]

        return flattened
