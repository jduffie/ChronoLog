import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from chronograph.service import ChronographService

from .filters import DopeSessionFilter
from .models import DopeMeasurementModel, DopeSessionModel


class DopeService:
    """Service class for DOPE sessions database operations"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_sessions_for_user(self, user_id: str) -> List[DopeSessionModel]:
        """Get all DOPE sessions for a specific user with joined data"""
        if not self.supabase or str(
                type(self.supabase).__name__) == "MagicMock":
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
                sessions.append(
                    DopeSessionModel.from_supabase_record(session_data))

            return sessions

        except Exception as e:
            print(f"Error fetching DOPE sessions: {e}")
            # Fallback to mock data for development
            return self._get_mock_sessions(user_id)

    def get_session_by_id(
        self, session_id: str, user_id: str
    ) -> Optional[DopeSessionModel]:
        """Get a specific DOPE session by ID with joined data"""
        if not self.supabase or str(
                type(self.supabase).__name__) == "MagicMock":
            mock_sessions = self._get_mock_sessions(user_id)
            return next(
                (session for session in mock_sessions if session.id == session_id),
                None)

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
                (session for session in mock_sessions if session.id == session_id),
                None)

    def get_measurements_for_dope_session(
            self, dope_session_id: str, user_id: str) -> List[DopeMeasurementModel]:
        """Get all measurements for a specific DOPE session"""
        try:
            if not self.supabase or str(
                    type(self.supabase).__name__) == "MagicMock":
                return self._get_mock_measurements(dope_session_id, user_id)

            response = (
                self.supabase.table("dope_measurements")
                .select("*")
                .eq("dope_session_id", dope_session_id)
                .eq("user_id", user_id)
                .order("shot_number", desc=False)
                .execute()
            )

            if response.data:
                # Convert database records directly to models (field names now aligned)
                return DopeMeasurementModel.from_supabase_records(response.data)
            return []

        except Exception as e:
            print(
                f"Error fetching DOPE measurements for session {dope_session_id}: {e}")
            return self._get_mock_measurements(dope_session_id, user_id)

    def create_measurement(self, measurement_data: Dict[str, Any], user_id: str) -> DopeMeasurementModel:
        """Create a new DOPE measurement"""
        if not self.supabase or str(type(self.supabase).__name__) == "MagicMock":
            # Mock implementation
            new_measurement = DopeMeasurementModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                **measurement_data,
            )
            return new_measurement

        try:
            # Prepare data for insertion
            insert_data = measurement_data.copy()
            insert_data["user_id"] = user_id

            # Set creation timestamp if not provided
            if "created_at" not in insert_data:
                insert_data["created_at"] = datetime.now().isoformat()
            if "updated_at" not in insert_data:
                insert_data["updated_at"] = datetime.now().isoformat()

            # Field names are now aligned between model and database

            response = (
                self.supabase.table("dope_measurements")
                .insert(insert_data)
                .execute()
            )

            if response.data:
                # Convert back to model (field names now aligned)
                return DopeMeasurementModel.from_supabase_record(response.data[0])
            else:
                raise Exception("Failed to create measurement")

        except Exception as e:
            print(f"Error creating DOPE measurement: {e}")
            # Fallback to mock implementation
            new_measurement = DopeMeasurementModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                **measurement_data,
            )
            return new_measurement

    def update_measurement(
        self, measurement_id: str, measurement_data: Dict[str, Any], user_id: str
    ) -> DopeMeasurementModel:
        """Update an existing DOPE measurement"""
        if not self.supabase or str(type(self.supabase).__name__) == "MagicMock":
            # Mock implementation - just return a measurement with updated data
            return DopeMeasurementModel(
                id=measurement_id,
                user_id=user_id,
                **measurement_data,
            )

        try:
            # Prepare data for update
            update_data = measurement_data.copy()
            update_data["updated_at"] = datetime.now().isoformat()

            # Field names are now aligned between model and database

            response = (
                self.supabase.table("dope_measurements")
                .update(update_data)
                .eq("id", measurement_id)
                .eq("user_id", user_id)
                .execute()
            )

            if response.data:
                # Convert back to model (field names now aligned)
                return DopeMeasurementModel.from_supabase_record(response.data[0])
            else:
                raise Exception(f"Measurement {measurement_id} not found")

        except Exception as e:
            print(f"Error updating DOPE measurement: {e}")
            raise Exception(f"Failed to update measurement {measurement_id}: {str(e)}")

    def delete_measurement(self, measurement_id: str, user_id: str) -> bool:
        """Delete a DOPE measurement"""
        if not self.supabase or str(type(self.supabase).__name__) == "MagicMock":
            # Mock implementation
            return True

        try:
            response = (
                self.supabase.table("dope_measurements")
                .delete()
                .eq("id", measurement_id)
                .eq("user_id", user_id)
                .execute()
            )
            return len(response.data) > 0

        except Exception as e:
            print(f"Error deleting DOPE measurement: {e}")
            return False

    def create_session(
        self, session_data: Dict[str, Any], user_id: str
    ) -> DopeSessionModel:
        """Create a new DOPE session"""
        if not self.supabase or str(
                type(self.supabase).__name__) == "MagicMock":
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

            response = (self.supabase.table(
                "dope_sessions").insert(insert_data).execute())

            if response.data:
                new_session_id = response.data[0]["id"]

                # Copy chronograph measurements to DOPE measurements if
                # chrono_session_id is provided
                if session_data.get("chrono_session_id"):
                    self._create_dope_measurements_from_chrono(
                        new_session_id,
                        session_data["chrono_session_id"],
                        user_id
                    )

                # Fetch the complete session with joined data
                return self.get_session_by_id(new_session_id, user_id)
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

    def search_sessions(
            self,
            user_id: str,
            search_term: str) -> List[DopeSessionModel]:
        """Search DOPE sessions by text across multiple fields"""
        if not self.supabase or str(
                type(self.supabase).__name__) == "MagicMock":
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
            # Use text search with PostgreSQL's ilike operator across joined
            # tables
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
                    sessions.append(
                        DopeSessionModel.from_supabase_record(session_data))

                # Additional filtering on joined data that can't be done in the
                # SQL query
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
            # Mock implementation using filter helper
            all_sessions = self._get_mock_sessions(user_id)
            return DopeSessionFilter(all_sessions).apply_all_filters(filters).get_results()

        try:
            # Get all sessions with database-level filtering where possible
            sessions = self._get_sessions_with_db_filters(user_id, filters)
            
            # Apply remaining filters using the filter helper
            return DopeSessionFilter(sessions).apply_all_filters(filters).get_results()

        except Exception as e:
            print(f"Error filtering DOPE sessions: {e}")
            # Fallback to mock implementation
            all_sessions = self._get_mock_sessions(user_id)
            return DopeSessionFilter(all_sessions).apply_all_filters(filters).get_results()

    def _get_sessions_with_db_filters(self, user_id: str, filters: Dict[str, Any]) -> List[DopeSessionModel]:
        """Get sessions with database-level filtering applied"""
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

        # Apply database-level filters (status field removed)

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
            return sessions
        
        return []

    def get_unique_values(self, user_id: str, field_name: str) -> List[str]:
        """Get unique values for a specific field for autocomplete filters"""
        if not self.supabase or str(
                type(self.supabase).__name__) == "MagicMock":
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
            # This is more efficient than querying each field separately since
            # we need JOIN data
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
        active_sessions = len(sessions)  # No status field in new schema

        cartridge_types = set(
            s.cartridge_type for s in sessions if s.cartridge_type)
        bullet_makes = set(s.bullet_make for s in sessions if s.bullet_make)
        ranges = set(s.range_name for s in sessions if s.range_name)

        distances = [s.range_distance_m for s in sessions if s.range_distance_m]
        avg_distance = sum(distances) / len(distances) if distances else 0

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "archived_sessions": total_sessions -
            active_sessions,
            "unique_cartridge_types": len(cartridge_types),
            "unique_bullet_makes": len(bullet_makes),
            "unique_ranges": len(ranges),
            "average_distance_m": round(
                avg_distance,
                1),
            "distance_range": (
                f"{min(distances)}-{max(distances)}m" if distances else "No data"),
        }

    def _get_mock_sessions(self, user_id: str) -> List[DopeSessionModel]:
        """Generate mock DOPE sessions for development/testing"""
        base_date = datetime.now()

        # Only return mock data for the specific user ID, otherwise return
        # empty list
        if user_id != "google-oauth2|111273793361054745867":
            return []

        mock_sessions = [
            DopeSessionModel(
                id="session_001",
                user_id="google-oauth2|111273793361054745867",
                session_name="Morning Range Session",
                datetime_local=base_date - timedelta(days=1),
                cartridge_id="cartridge_001",
                # status field removed from schema
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
                range_distance_m=100.0,
                temperature_c_median=22.0,
                start_time=base_date - timedelta(days=1),
                end_time=base_date - timedelta(days=1) + timedelta(hours=2),
                relative_humidity_pct_median=65.0,
                barometric_pressure_hpa_median=1020.1,  # Store in metric (hPa)
                wind_speed_mps_median=2.2,
                wind_direction_deg_median=270.0,
                notes="Excellent conditions, consistent groups",
            ),
            DopeSessionModel(
                id="session_002",
                user_id="google-oauth2|111273793361054745867",
                session_name="Long Range Practice",
                datetime_local=base_date - timedelta(days=3),
                cartridge_id="cartridge_002",
                # status field removed from schema
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
                range_distance_m=300.0,
                temperature_c_median=18.0,
                start_time=base_date - timedelta(days=3),
                end_time=base_date - timedelta(days=3) + timedelta(hours=2),
                relative_humidity_pct_median=45.0,
                barometric_pressure_hpa_median=1013.2,  # Store in metric (hPa)
                wind_speed_mps_median=3.3,
                wind_direction_deg_median=135.0,
                notes="Windy conditions, good for practice",
            ),
            DopeSessionModel(
                id="session_003",
                user_id="google-oauth2|111273793361054745867",
                session_name="Competition Prep",
                datetime_local=base_date - timedelta(days=7),
                cartridge_id="cartridge_003",
                # status field removed from schema
                rifle_name="Match AR-15",
                cartridge_make="Black Hills",
                cartridge_model="Match",
                cartridge_type="223 Remington",
                bullet_make="Sierra",
                bullet_model="MatchKing",
                bullet_weight="69",
                range_name="Competition Range",
                range_distance_m=200.0,
                temperature_c_median=25.0,
                start_time=base_date - timedelta(days=7),
                end_time=base_date - timedelta(days=7) + timedelta(hours=2),
                notes="Final preparation before match",
            ),
            DopeSessionModel(
                id="session_004",
                user_id="google-oauth2|111273793361054745867",
                session_name="Cold Weather Test",
                datetime_local=base_date - timedelta(days=14),
                cartridge_id="cartridge_004",
                # status field removed from schema
                rifle_name="AR-15 SPR",
                cartridge_make="Federal",
                cartridge_model="Gold Medal Match",
                cartridge_type="223 Remington",
                bullet_make="Sierra",
                bullet_model="MatchKing",
                bullet_weight="77",
                range_name="Winter Range",
                range_distance_m=100.0,
                temperature_c_median=-5.0,
                start_time=base_date - timedelta(days=14),
                end_time=base_date - timedelta(days=14) + timedelta(hours=2),
                relative_humidity_pct_median=80.0,
                wind_speed_mps_median=4.2,
                notes="Testing cold weather performance",
            ),
            DopeSessionModel(
                id="session_005",
                user_id="google-oauth2|111273793361054745867",
                session_name="New Load Development",
                datetime_local=base_date - timedelta(days=21),
                cartridge_id="cartridge_005",
                # status field removed from schema
                rifle_name="Custom .300 WM",
                cartridge_make="Custom",
                cartridge_model="Handload",
                cartridge_type="300 Winchester Magnum",
                bullet_make="Berger",
                bullet_model="VLD Target",
                bullet_weight="210",
                range_name="Private Range",
                range_distance_m=600.0,
                temperature_c_median=20.0,
                start_time=base_date - timedelta(days=21),
                end_time=base_date - timedelta(days=21) + timedelta(hours=2),
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
                flattened["bullet_weight"] = str(
                    bullet.get("weight_grains", ""))
                flattened["bullet_length_mm"] = str(
                    bullet.get("bullet_length_mm", ""))
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
            flattened["rifle_barrel_twist_in_per_rev"] = rifle.get(
                "barrel_twist_ratio")
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
            flattened["elevation_angle_deg"] = range_data.get(
                "elevation_angle_deg")
            del flattened["ranges_submissions"]

        # Extract weather source data
        if "weather_source" in record and record["weather_source"]:
            weather_source = record["weather_source"]
            flattened["weather_source_name"] = weather_source.get("name")
            del flattened["weather_source"]

        return flattened

    def _get_weather_for_timestamp(self, weather_source_id: str, timestamp: datetime) -> Optional[Dict[str, Any]]:
        """Get weather data for a specific timestamp from weather_measurements table"""
        try:
            if not self.supabase:
                return None

            # Find weather measurement closest to the given timestamp
            # Look within ±30 minutes of the shot time
            start_time = timestamp - timedelta(minutes=30)
            end_time = timestamp + timedelta(minutes=30)

            response = (
                self.supabase.table("weather_measurements")
                .select("temperature_c, barometric_pressure_hpa, relative_humidity_pct, measurement_timestamp")
                .eq("weather_source_id", weather_source_id)
                .gte("measurement_timestamp", start_time.isoformat())
                .lte("measurement_timestamp", end_time.isoformat())
                .order("measurement_timestamp")
                .limit(1)
                .execute()
            )

            if response.data:
                weather_record = response.data[0]
                return {
                    "temperature_c": weather_record.get("temperature_c"),
                    "pressure_hpa": weather_record.get("barometric_pressure_hpa"),
                    "humidity_pct": weather_record.get("relative_humidity_pct")
                }

            return None

        except Exception as e:
            print(f"Error getting weather data for timestamp {timestamp}: {e}")
            return None

    def _create_dope_measurements_from_chrono(
            self,
            dope_session_id: str,
            chrono_session_id: str,
            user_id: str) -> None:
        """Copy chronograph measurements to DOPE measurements"""
        try:
            # Get chronograph measurements
            chrono_service = ChronographService(self.supabase)
            chrono_measurements = chrono_service.get_measurements_by_session_id(
                chrono_session_id, user_id)

            if not chrono_measurements:
                return

            # Get the DOPE session to find the weather source
            dope_session = self.get_session_by_id(dope_session_id, user_id)
            if not dope_session or not dope_session.weather_source_id:
                print(f"No weather source found for DOPE session {dope_session_id}")
                weather_source_id = None
            else:
                weather_source_id = dope_session.weather_source_id

            # Prepare DOPE measurement records using correct database field names
            dope_measurement_records = []
            for measurement in chrono_measurements:
                # Get weather data for this shot timestamp
                weather_data = None
                if weather_source_id and measurement.datetime_local:
                    weather_data = self._get_weather_for_timestamp(
                        weather_source_id, measurement.datetime_local)

                dope_record = {
                    "dope_session_id": dope_session_id,
                    "user_id": user_id,
                    "shot_number": measurement.shot_number,
                    "datetime_shot": measurement.datetime_local.isoformat() if measurement.datetime_local else None,
                    # Metric ballistic data only
                    "speed_mps": measurement.speed_mps,
                    "ke_j": measurement.ke_j,
                    "power_factor_kgms": measurement.power_factor_kgms,
                    # Bore conditions as text
                    "clean_bore": "yes" if measurement.clean_bore else "no" if measurement.clean_bore is False else None,
                    "cold_bore": "yes" if measurement.cold_bore else "no" if measurement.cold_bore is False else None,
                    # Weather data from weather_measurements table
                    "temperature_c": weather_data.get("temperature_c") if weather_data else None,
                    "pressure_hpa": weather_data.get("pressure_hpa") if weather_data else None,
                    "humidity_pct": weather_data.get("humidity_pct") if weather_data else None,
                    # Notes
                    "shot_notes": measurement.shot_notes,
                    # Timestamps
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                dope_measurement_records.append(dope_record)

            # Insert all DOPE measurements in batch
            if dope_measurement_records:
                self.supabase.table("dope_measurements").insert(
                    dope_measurement_records).execute()

        except Exception as e:
            raise Exception(
                f"Error creating DOPE measurements from chronograph: {str(e)}")

    def _get_mock_measurements(self, dope_session_id: str, user_id: str) -> List[DopeMeasurementModel]:
        """Generate mock DOPE measurements for development/testing"""
        # Only return mock data for the specific user ID, otherwise return empty list
        if user_id != "google-oauth2|111273793361054745867":
            return []

        # Return mock measurements only for known session IDs
        if dope_session_id not in ["session_001", "session_002", "session_003"]:
            return []

        base_datetime = datetime.now() - timedelta(hours=2)
        
        mock_measurements = []
        
        # Create different mock data based on session ID
        if dope_session_id == "session_001":
            # AR-15 .223 Remington measurements - 10 shots
            for i in range(1, 11):
                measurement = DopeMeasurementModel(
                    id=f"measurement_{dope_session_id}_{i:03d}",
                    dope_session_id=dope_session_id,
                    user_id=user_id,
                    shot_number=i,
                    datetime_shot=base_datetime + timedelta(minutes=i * 2),
                    # Metric ballistic data only
                    speed_mps=838.2 + (i * 1.5) + ((-1) ** i) * 3.0,  # Varying speeds around 838 m/s (~2750 fps)
                    ke_j=1742 + (i * 3) + ((-1) ** i) * 11,
                    power_factor_kgms=0.0646 + (i * 0.0001) + ((-1) ** i) * 0.0002,
                    # Environmental conditions in metric
                    temperature_c=22.2,
                    pressure_hpa=1021.0,
                    humidity_pct=65.0,
                    # Bore conditions
                    clean_bore="yes" if i == 1 else "no",
                    cold_bore="yes" if i == 1 else "no",
                    # Targeting data in metric
                    distance_m=91.44,  # 100 yards converted to meters
                    elevation_adjustment=0.0 if i <= 3 else 0.072,  # 0.25 MOA ≈ 0.072 mrad
                    windage_adjustment=0.0 if i <= 5 else -0.036,  # 0.125 MOA left ≈ -0.036 mrad
                    shot_notes=f"Good shot, tight group" if i % 3 == 0 else None,
                    created_at=base_datetime + timedelta(minutes=i * 2),
                    updated_at=base_datetime + timedelta(minutes=i * 2),
                )
                mock_measurements.append(measurement)
                
        elif dope_session_id == "session_002":
            # .308 Winchester measurements - 8 shots
            for i in range(1, 9):
                measurement = DopeMeasurementModel(
                    id=f"measurement_{dope_session_id}_{i:03d}",
                    dope_session_id=dope_session_id,
                    user_id=user_id,
                    shot_number=i,
                    datetime_shot=base_datetime + timedelta(minutes=i * 3),
                    # Metric ballistic data only
                    speed_mps=807.7 + (i * 0.9) + ((-1) ** i) * 3.7,  # Varying speeds around 808 m/s (~2650 fps)
                    ke_j=3549 + (i * 7) + ((-1) ** i) * 20,
                    power_factor_kgms=0.1356 + (i * 0.0002) + ((-1) ** i) * 0.0006,
                    # Environmental conditions in metric
                    temperature_c=18.0,
                    pressure_hpa=1013.0,
                    humidity_pct=45.0,
                    # Targeting data
                    azimuth_deg=90.0 + (i * 0.1),
                    elevation_angle_deg=2.5 + (i * 0.05),
                    # Bore conditions
                    clean_bore="yes" if i == 1 else "no",
                    cold_bore="yes" if i == 1 else "no",
                    # Range data in metric
                    distance_m=274.32,  # 300 yards converted to meters
                    elevation_adjustment=0.726 if i <= 2 else 0.799,  # 2.5-2.75 MOA ≈ 0.726-0.799 mrad
                    windage_adjustment=0.145 if i <= 4 else 0.218,  # 0.5-0.75 MOA right ≈ 0.145-0.218 mrad
                    shot_notes=f"Wind effect visible" if i > 5 else None,
                    created_at=base_datetime + timedelta(minutes=i * 3),
                    updated_at=base_datetime + timedelta(minutes=i * 3),
                )
                mock_measurements.append(measurement)
                
        elif dope_session_id == "session_003":
            # Competition prep measurements - 15 shots
            for i in range(1, 16):
                measurement = DopeMeasurementModel(
                    id=f"measurement_{dope_session_id}_{i:03d}",
                    dope_session_id=dope_session_id,
                    user_id=user_id,
                    shot_number=i,
                    datetime_shot=base_datetime + timedelta(minutes=i * 1.5),
                    # Metric ballistic data only
                    speed_mps=847.3 + (i * 0.6) + ((-1) ** i) * 2.4,  # Very consistent speeds around 847 m/s (~2780 fps)
                    ke_j=1570 + (i * 1.4) + ((-1) ** i) * 5.4,
                    power_factor_kgms=0.0584 + (i * 0.00003) + ((-1) ** i) * 0.0001,
                    # Environmental conditions in metric
                    temperature_c=25.0,
                    pressure_hpa=1017.7,
                    humidity_pct=55.0,
                    # Bore conditions
                    clean_bore="fouled" if i > 3 else ("yes" if i == 1 else "no"),
                    cold_bore="yes" if i == 1 else "no",
                    # Range data in metric
                    distance_m=182.88,  # 200 yards converted to meters
                    elevation_adjustment=0.436,  # 1.5 MOA ≈ 0.436 mrad
                    windage_adjustment=0.0,
                    shot_notes=f"Competition simulation shot {i}" if i % 5 == 0 else None,
                    created_at=base_datetime + timedelta(minutes=i * 1.5),
                    updated_at=base_datetime + timedelta(minutes=i * 1.5),
                )
                mock_measurements.append(measurement)
                
        return mock_measurements
