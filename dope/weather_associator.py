"""
Weather Session Associator

This class handles the association of weather measurements with DOPE sessions
based on chronograph session time windows and shot timestamps.
"""

import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from weather.service import WeatherService


class WeatherSessionAssociator:
    """Associates weather measurements with DOPE sessions based on time windows"""

    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.weather_service = WeatherService(supabase_client)

    def get_chrono_session_time_window(self,
                                       user_id: str,
                                       chrono_session_id: str,
                                       buffer_minutes: int = 30) -> Optional[Tuple[datetime,
                                                                                   datetime]]:
        """
        Get the time window for a chronograph session based on shot measurements

        Args:
            user_id: User identifier
            chrono_session_id: Chronograph session ID
            buffer_minutes: Buffer time in minutes to add before/after

        Returns:
            Tuple of (start_time, end_time) or None if no measurements found
        """
        try:
            # Get all measurements for the chrono session
            response = (
                self.supabase.table("chrono_measurements")
                .select("datetime_local")
                .eq("user_id", user_id)
                .eq("chrono_session_id", chrono_session_id)
                .order("datetime_local")
                .execute()
            )

            if not response.data:
                return None

            # Extract timestamps
            timestamps = [
                datetime.fromisoformat(record["datetime_local"].replace('Z', '+00:00'))
                for record in response.data
                if record.get("datetime_local")
            ]

            if not timestamps:
                return None

            # Calculate time window with buffer
            start_time = min(timestamps) - timedelta(minutes=buffer_minutes)
            end_time = max(timestamps) + timedelta(minutes=buffer_minutes)

            return (start_time, end_time)

        except Exception as e:
            raise Exception(
                f"Error getting chrono session time window: {str(e)}")

    def get_weather_sources_with_measurements(
            self,
            user_id: str,
            start_time: datetime,
            end_time: datetime) -> List[Dict]:
        """
        Get weather sources that have measurements within the specified time window

        Args:
            user_id: User identifier
            start_time: Start of time window
            end_time: End of time window

        Returns:
            List of weather sources with measurement counts
        """
        try:
            # Get all weather sources for user
            weather_sources = self.weather_service.get_sources_for_user(
                user_id)

            sources_with_measurements = []

            for source in weather_sources:
                # Count measurements in time window for this source
                response = (
                    self.supabase.table("weather_measurements")
                    .select("id", count="exact")
                    .eq("user_id", user_id)
                    .eq("weather_source_id", source.id)
                    .gte("measurement_timestamp", start_time.isoformat())
                    .lte("measurement_timestamp", end_time.isoformat())
                    .execute()
                )

                measurement_count = response.count if response.count else 0

                if measurement_count > 0:
                    source_dict = {
                        "source": source,
                        "measurement_count": measurement_count
                    }
                    sources_with_measurements.append(source_dict)

            return sources_with_measurements

        except Exception as e:
            raise Exception(
                f"Error getting weather sources with measurements: {str(e)}")

    def get_weather_measurements_for_window(
            self,
            user_id: str,
            weather_source_id: str,
            start_time: datetime,
            end_time: datetime) -> List[Dict]:
        """
        Get weather measurements for a specific source within time window

        Args:
            user_id: User identifier
            weather_source_id: Weather source ID
            start_time: Start of time window
            end_time: End of time window

        Returns:
            List of weather measurement records
        """
        try:
            response = (
                self.supabase.table("weather_measurements")
                .select("*")
                .eq("user_id", user_id)
                .eq("weather_source_id", weather_source_id)
                .gte("measurement_timestamp", start_time.isoformat())
                .lte("measurement_timestamp", end_time.isoformat())
                .order("measurement_timestamp")
                .execute()
            )

            return response.data if response.data else []

        except Exception as e:
            raise Exception(f"Error getting weather measurements: {str(e)}")

    def calculate_median_weather_values(
            self, measurements: List[Dict]) -> Dict:
        """
        Calculate median weather values from a list of measurements

        Args:
            measurements: List of weather measurement records

        Returns:
            Dictionary with median weather values
        """
        if not measurements:
            return {}

        # Extract numeric values for each weather parameter
        weather_fields = [
            'temperature_f',
            'relative_humidity_pct',
            'barometric_pressure_inhg',
            'altitude_ft',
            'wind_speed_mph',
            'density_altitude_ft']

        median_values = {}

        for field in weather_fields:
            values = [
                m[field] for m in measurements
                if m.get(field) is not None
            ]

            if values:
                median_values[field] = statistics.median(values)

        return median_values

    def find_closest_weather_measurement(
            self,
            shot_timestamp: datetime,
            measurements: List[Dict]) -> Optional[str]:
        """
        Find the closest weather measurement to a shot timestamp

        Args:
            shot_timestamp: Timestamp of the shot
            measurements: List of weather measurement records

        Returns:
            Weather measurement ID of closest match or None
        """
        if not measurements:
            return None

        # Find measurement with smallest time difference
        closest_measurement = None
        smallest_diff = None

        for measurement in measurements:
            if not measurement.get("measurement_timestamp"):
                continue

            measurement_time = datetime.fromisoformat(
                measurement["measurement_timestamp"].replace('Z', '+00:00')
            )

            time_diff = abs(
                (shot_timestamp - measurement_time).total_seconds())

            if smallest_diff is None or time_diff < smallest_diff:
                smallest_diff = time_diff
                closest_measurement = measurement

        return closest_measurement["id"] if closest_measurement else None

    def associate_weather_with_dope_session(
            self,
            user_id: str,
            dope_session_id: str,
            weather_source_id: str,
            start_time: datetime,
            end_time: datetime) -> Dict:
        """
        Associate weather measurements with a DOPE session and its measurements

        Args:
            user_id: User identifier
            dope_session_id: DOPE session ID
            weather_source_id: Selected weather source ID
            start_time: Session start time
            end_time: Session end time

        Returns:
            Dictionary with median weather values and association results
        """
        try:
            # Get weather measurements for the time window
            weather_measurements = self.get_weather_measurements_for_window(
                user_id, weather_source_id, start_time, end_time
            )

            if not weather_measurements:
                return {
                    "error": "No weather measurements found for time window"}

            # Calculate median weather values
            median_weather = self.calculate_median_weather_values(
                weather_measurements)

            # Get DOPE measurements that need weather association
            dope_measurements_response = (
                self.supabase.table("dope_measurements")
                .select("id, datetime_shot")
                .eq("user_id", user_id)
                .eq("dope_session_id", dope_session_id)
                .execute()
            )

            dope_measurements = dope_measurements_response.data if dope_measurements_response.data else []

            # Associate each DOPE measurement with closest weather measurement
            associations = []
            for dope_measurement in dope_measurements:
                if not dope_measurement.get("datetime_shot"):
                    continue

                shot_time = datetime.fromisoformat(
                    dope_measurement["datetime_shot"].replace('Z', '+00:00')
                )

                closest_weather_id = self.find_closest_weather_measurement(
                    shot_time, weather_measurements
                )

                if closest_weather_id:
                    associations.append({
                        "dope_measurement_id": dope_measurement["id"],
                        "weather_measurement_id": closest_weather_id
                    })

            return {
                "median_weather": median_weather,
                "weather_associations": associations,
                "weather_measurement_count": len(weather_measurements),
                "dope_measurement_count": len(dope_measurements),
                "associations_made": len(associations)
            }

        except Exception as e:
            raise Exception(
                f"Error associating weather with DOPE session: {str(e)}")
