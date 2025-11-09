"""
Integration tests for weather UI to API layer.

These tests verify that UI code correctly uses API methods.
They catch issues like:
- Calling non-existent API methods
- Wrong number of arguments
- Wrong method names

These are NOT full UI tests - they just verify API method calls work.
"""

import os
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather.api import WeatherAPI
from weather.models import WeatherMeasurement, WeatherSource


class TestWeatherUIIntegration(unittest.TestCase):
    """Test UI to API integration for weather"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.weather_api = WeatherAPI(self.mock_supabase)
        self.test_user_id = "test-user-123"

    def test_view_tab_can_get_all_sources(self):
        """Test that view_tab can call get_all_sources() correctly"""
        # view_tab.py line 25 calls: weather_service.get_sources_for_user(user["id"])
        # API has: get_all_sources(user_id)
        try:
            # Mock the service method
            self.weather_api._service.get_sources_for_user = MagicMock(return_value=[])

            result = self.weather_api.get_all_sources(self.test_user_id)

            # Should return a list
            self.assertIsInstance(result, list)
        except AttributeError as e:
            self.fail(f"API method call failed: {e}")

    def test_view_tab_can_filter_measurements(self):
        """Test that view_tab can call filter_measurements() correctly"""
        # view_tab.py line 83 calls: weather_service.get_measurements_filtered()
        # API has: filter_measurements(user_id, source_id, start_date, end_date)
        try:
            # Mock the service method
            self.weather_api._service.get_measurements_filtered = MagicMock(return_value=[])

            result = self.weather_api.filter_measurements(
                user_id=self.test_user_id,
                source_id="source-123",
                start_date="2024-01-01T00:00:00",
                end_date="2024-01-31T23:59:59"
            )

            # Should return a list
            self.assertIsInstance(result, list)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_import_tab_can_get_source_by_name(self):
        """Test that import_tab can call get_source_by_name() correctly"""
        # import_tab.py line 312 calls: weather_service.get_source_by_name()
        # API has: get_source_by_name(user_id, name)
        try:
            # Mock the service method
            self.weather_api._service.get_source_by_name = MagicMock(return_value=None)

            result = self.weather_api.get_source_by_name(
                user_id=self.test_user_id,
                name="Test Source"
            )

            # Should return None (or a WeatherSource)
            self.assertTrue(result is None or isinstance(result, WeatherSource))
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_import_tab_can_create_source(self):
        """Test that import_tab can call create_source() correctly"""
        # import_tab.py line 325 calls: weather_service.create_source()
        # API has: create_source(source_data, user_id)
        source_data = {
            "name": "Test Kestrel",
            "device_name": "Kestrel 5700",
            "model": "5700 Elite"
        }

        try:
            # Mock the table response
            mock_record = {
                "id": "source-123",
                "user_id": self.test_user_id,
                **source_data,
                "source_type": "meter",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [mock_record]

            result = self.weather_api.create_source(source_data, self.test_user_id)

            # Should return a WeatherSource
            self.assertIsInstance(result, WeatherSource)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_import_tab_can_get_source_by_id(self):
        """Test that import_tab can call get_source_by_id() correctly"""
        # import_tab.py line 338 calls: weather_service.get_source_by_id()
        # API has: get_source_by_id(source_id, user_id)
        try:
            # Mock the service method
            self.weather_api._service.get_source_by_id = MagicMock(return_value=None)

            result = self.weather_api.get_source_by_id("source-123", self.test_user_id)

            # Should return None (or a WeatherSource)
            self.assertTrue(result is None or isinstance(result, WeatherSource))
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_import_tab_can_create_measurements_batch(self):
        """Test that import_tab can call create_measurements_batch() correctly"""
        # import_tab.py line 572 calls: weather_service.create_measurements_batch()
        # API has: create_measurements_batch(measurements_data, user_id)
        batch_data = [
            {
                "weather_source_id": "source-123",
                "measurement_timestamp": "2024-01-15T10:00:00",
                "temperature_c": 22.5
            },
            {
                "weather_source_id": "source-123",
                "measurement_timestamp": "2024-01-15T10:01:00",
                "temperature_c": 22.6
            }
        ]

        try:
            # Mock the table response
            mock_records = []
            for data in batch_data:
                mock_records.append({
                    "id": f"measurement-{len(mock_records)}",
                    "user_id": self.test_user_id,
                    **data,
                    "uploaded_at": datetime.now().isoformat()
                })
            self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = mock_records

            result = self.weather_api.create_measurements_batch(batch_data, self.test_user_id)

            # Should return a list of WeatherMeasurement objects
            self.assertIsInstance(result, list)
            if len(result) > 0:
                self.assertIsInstance(result[0], WeatherMeasurement)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_weather_source_model_has_required_fields(self):
        """Test that WeatherSource has all fields the UI expects"""
        source = WeatherSource(
            id="source-123",
            user_id=self.test_user_id,
            name="Test Kestrel",
            source_type="meter",
            device_name="Kestrel 5700",
            make="Kestrel",
            model="5700 Elite"
        )

        try:
            # UI accesses these fields directly
            self.assertEqual(source.id, "source-123")
            self.assertEqual(source.name, "Test Kestrel")
            self.assertEqual(source.device_name, "Kestrel 5700")
            self.assertEqual(source.model, "5700 Elite")

            # UI uses helper methods
            self.assertIsInstance(source.display_name(), str)
            self.assertIsInstance(source.device_display(), str)

        except AttributeError as e:
            self.fail(f"WeatherSource missing required field or method: {e}")

    def test_weather_measurement_model_has_required_fields(self):
        """Test that WeatherMeasurement has all fields the UI expects"""
        measurement = WeatherMeasurement(
            id="measurement-123",
            user_id=self.test_user_id,
            weather_source_id="source-123",
            measurement_timestamp="2024-01-15T10:00:00",
            temperature_c=22.5,
            relative_humidity_pct=65.0,
            barometric_pressure_hpa=1013.25,
            uploaded_at="2024-01-15T10:00:00"
        )

        try:
            # UI accesses these fields directly
            self.assertEqual(measurement.id, "measurement-123")
            self.assertEqual(measurement.temperature_c, 22.5)
            self.assertEqual(measurement.relative_humidity_pct, 65.0)
            self.assertEqual(measurement.barometric_pressure_hpa, 1013.25)

        except AttributeError as e:
            self.fail(f"WeatherMeasurement missing required field: {e}")

    def test_get_all_sources_returns_weather_source_models(self):
        """Test that get_all_sources returns WeatherSource instances not dicts"""
        # Ensures UI gets model instances with properties, not raw dicts
        try:
            # Mock the service method
            mock_source = WeatherSource(
                id="source-123",
                user_id=self.test_user_id,
                name="Test Kestrel",
                source_type="meter"
            )
            self.weather_api._service.get_sources_for_user = MagicMock(return_value=[mock_source])

            result = self.weather_api.get_all_sources(self.test_user_id)

            # Should return list of WeatherSource instances
            self.assertIsInstance(result, list)
            if len(result) > 0:
                self.assertIsInstance(result[0], WeatherSource)
                # UI expects to access properties
                self.assertEqual(result[0].name, "Test Kestrel")

        except (AttributeError, TypeError) as e:
            self.fail(f"API method return type incorrect: {e}")


if __name__ == "__main__":
    unittest.main()
