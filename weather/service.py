from typing import List, Optional

from .models import WeatherMeasurement, WeatherSource


class WeatherService:
    """Service class for weather database operations"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    # Weather Source Management
    def get_sources_for_user(self, user_id: str) -> List[WeatherSource]:
        """Get all weather sources for a user"""
        try:
            response = (
                self.supabase.table("weather_source")
                .select("*")
                .eq("user_id", user_id)
                .order("name")
                .execute()
            )

            if not response.data:
                return []

            return WeatherSource.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error fetching weather sources: {str(e)}")

    def get_source_by_id(self, source_id: str, user_id: str) -> Optional[WeatherSource]:
        """Get a specific weather source by ID"""
        try:
            response = (
                self.supabase.table("weather_source")
                .select("*")
                .eq("id", source_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )

            if not response.data:
                return None

            return WeatherSource.from_supabase_record(response.data)

        except Exception as e:
            raise Exception(f"Error fetching weather source: {str(e)}")

    def get_source_by_name(self, user_id: str, name: str) -> Optional[WeatherSource]:
        """Get a weather source by name"""
        try:
            response = (
                self.supabase.table("weather_source")
                .select("*")
                .eq("user_id", user_id)
                .eq("name", name)
                .single()
                .execute()
            )

            if not response.data:
                return None

            return WeatherSource.from_supabase_record(response.data)

        except Exception as e:
            # Source doesn't exist
            return None

    def create_source(self, source_data: dict) -> str:
        """Create a new weather source"""
        try:
            response = (
                self.supabase.table("weather_source").insert(source_data).execute()
            )

            if not response.data:
                raise Exception("Failed to create weather source")

            return response.data[0]["id"]

        except Exception as e:
            raise Exception(f"Error creating weather source: {str(e)}")

    def update_source(self, source_id: str, user_id: str, updates: dict) -> None:
        """Update weather source information"""
        try:
            updates["updated_at"] = "NOW()"
            self.supabase.table("weather_source").update(updates).eq(
                "id", source_id
            ).eq("user_id", user_id).execute()

        except Exception as e:
            raise Exception(f"Error updating weather source: {str(e)}")

    def delete_source(self, source_id: str, user_id: str) -> None:
        """Delete a weather source and all its measurements"""
        try:
            self.supabase.table("weather_source").delete().eq("id", source_id).eq(
                "user_email", user_email
            ).execute()

        except Exception as e:
            raise Exception(f"Error deleting weather source: {str(e)}")

    # Weather Measurements
    def get_measurements_for_source(
        self, source_id: str, user_id: str
    ) -> List[WeatherMeasurement]:
        """Get all measurements for a specific weather source"""
        try:
            response = (
                self.supabase.table("weather_measurements")
                .select("*")
                .eq("weather_source_id", source_id)
                .eq("user_id", user_id)
                .order("measurement_timestamp")
                .execute()
            )

            if not response.data:
                return []

            return WeatherMeasurement.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error fetching measurements: {str(e)}")

    def get_all_measurements_for_user(self, user_id: str) -> List[WeatherMeasurement]:
        """Get all weather measurements for a user"""
        try:
            response = (
                self.supabase.table("weather_measurements")
                .select("*")
                .eq("user_id", user_id)
                .order("measurement_timestamp", desc=True)
                .execute()
            )

            if not response.data:
                return []

            return WeatherMeasurement.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error fetching measurements: {str(e)}")

    def get_measurements_filtered(
        self,
        user_id: str,
        source_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[WeatherMeasurement]:
        """Get filtered weather measurements"""
        try:
            query = (
                self.supabase.table("weather_measurements")
                .select("*")
                .eq("user_id", user_id)
            )

            if source_id:
                query = query.eq("weather_source_id", source_id)

            if start_date:
                query = query.gte("measurement_timestamp", start_date)

            if end_date:
                query = query.lte("measurement_timestamp", end_date)

            response = query.order("measurement_timestamp", desc=True).execute()

            if not response.data:
                return []

            return WeatherMeasurement.from_supabase_records(response.data)

        except Exception as e:
            raise Exception(f"Error fetching filtered measurements: {str(e)}")

    def create_measurement(self, measurement_data: dict) -> str:
        """Create a new weather measurement"""
        try:
            response = (
                self.supabase.table("weather_measurements")
                .insert(measurement_data)
                .execute()
            )

            if not response.data:
                raise Exception("Failed to create measurement")

            return response.data[0]["id"]

        except Exception as e:
            raise Exception(f"Error creating measurement: {str(e)}")

    def measurement_exists(
        self, user_id: str, source_id: str, measurement_timestamp: str
    ) -> bool:
        """Check if a measurement already exists"""
        try:
            response = (
                self.supabase.table("weather_measurements")
                .select("id")
                .eq("user_id", user_id)
                .eq("weather_source_id", source_id)
                .eq("measurement_timestamp", measurement_timestamp)
                .execute()
            )

            return len(response.data) > 0

        except Exception as e:
            raise Exception(f"Error checking measurement existence: {str(e)}")

    def update_source_with_device_info(
        self,
        source_id: str,
        user_id: str,
        device_name: str,
        device_model: str,
        serial_number: str,
    ) -> None:
        """Update an existing weather source with device information from CSV"""
        try:
            updates = {
                "device_name": device_name if device_name else None,
                "model": device_model if device_model else None,
                "serial_number": serial_number if serial_number else None,
                "updated_at": "NOW()",
            }

            self.supabase.table("weather_source").update(updates).eq(
                "id", source_id
            ).eq("user_id", user_id).execute()

        except Exception as e:
            raise Exception(f"Error updating weather source with device info: {str(e)}")

    def create_or_get_source_from_device_info(
        self, user_id: str, device_name: str, device_model: str, serial_number: str
    ) -> str:
        """Create or get existing weather source from device information"""
        try:
            # First try to find existing source by serial number
            if serial_number:
                response = (
                    self.supabase.table("weather_source")
                    .select("*")
                    .eq("user_id", user_id)
                    .eq("serial_number", serial_number)
                    .execute()
                )
                if response.data:
                    return response.data[0]["id"]

            # Generate a name from device info
            source_name = f"{device_name}" if device_name else f"{device_model}"
            if serial_number:
                source_name += f" ({serial_number[-4:]})"  # Last 4 digits of serial

            # Check if source with this name already exists
            existing = self.get_source_by_name(user_id, source_name)
            if existing:
                return existing.id

            # Create new source
            source_data = {
                "user_id": user_id,
                "name": source_name,
                "device_name": device_name,
                "model": device_model,
                "serial_number": serial_number,
            }

            return self.create_source(source_data)

        except Exception as e:
            raise Exception(f"Error creating/getting weather source: {str(e)}")
