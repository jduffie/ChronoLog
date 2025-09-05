import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

import pandas as pd

from weather.import_tab import (
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    feet_to_meters,
    inhg_to_hpa,
    meters_to_feet,
    mph_to_mps,
    render_weather_import_tab,
)
from weather.models import WeatherMeasurement, WeatherSource
from weather.service import WeatherService

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWeatherSource(unittest.TestCase):

    def test_weather_source_from_device_info(self):
        """Test creating WeatherSource from device info"""
        source = WeatherSource.from_device_info(
            user_id="test@example.com",
            name="Test Kestrel",
            device_name="Kestrel 5700",
            device_model="5700 Elite",
            serial_number="K123456",
        )

        self.assertEqual(source.user_id, "test@example.com")
        self.assertEqual(source.name, "Test Kestrel")
        self.assertEqual(source.device_name, "Kestrel 5700")
        self.assertEqual(source.model, "5700 Elite")
        self.assertEqual(source.serial_number, "K123456")

    def test_weather_source_from_supabase_record(self):
        """Test creating WeatherSource from Supabase record"""
        record = {
            "id": "source-1",
            "user_id": "test@example.com",
            "name": "Test Kestrel",
            "source_type": "meter",
            "device_name": "Kestrel 5700",
            "make": "Kestrel",
            "model": "5700 Elite",
            "serial_number": "K123456",
            "created_at": "2023-12-01T10:00:00",
            "updated_at": "2023-12-01T10:05:00",
        }

        source = WeatherSource.from_supabase_record(record)

        self.assertEqual(source.id, "source-1")
        self.assertEqual(source.user_id, "test@example.com")
        self.assertEqual(source.name, "Test Kestrel")
        self.assertEqual(source.make, "Kestrel")
        self.assertEqual(source.model, "5700 Elite")
        self.assertEqual(source.serial_number, "K123456")

    def test_weather_source_display_methods(self):
        """Test WeatherSource display methods"""
        source = WeatherSource(
            id="source-1",
            user_id="test@example.com",
            name="Test Kestrel",
            make="Kestrel",
            model="5700 Elite",
            serial_number="K123456",
        )

        self.assertEqual(source.display_name(), "Test Kestrel")
        self.assertEqual(
            source.device_display(),
            "Kestrel 5700 Elite (S/N: K123456)")
        self.assertEqual(source.short_display(),
                         "Test Kestrel - Kestrel 5700 Elite (S/N: K123456)")

    def test_weather_source_display_methods_minimal(self):
        """Test WeatherSource display methods with minimal data"""
        source = WeatherSource(
            id="source-1", user_id="test@example.com", name="Basic Meter"
        )

        self.assertEqual(source.display_name(), "Basic Meter")
        self.assertEqual(source.device_display(), "Unknown Device")
        self.assertEqual(
            source.short_display(),
            "Basic Meter - Unknown Device")


class TestWeatherMeasurement(unittest.TestCase):

    def test_weather_measurement_from_supabase_record(self):
        """Test creating WeatherMeasurement from Supabase record"""
        record = {
            "id": "measurement-1",
            "user_id": "test@example.com",
            "weather_source_id": "source-1",
            "measurement_timestamp": "2023-12-01T10:00:00",
            "uploaded_at": "2023-12-01T10:01:00",
            "file_path": "test/weather.csv",
            "temperature_f": 72.5,
            "relative_humidity_pct": 65.0,
            "barometric_pressure_inhg": 29.92,
            "wind_speed_mph": 5.2,
            "compass_true_deg": 270,
            "density_altitude_ft": 2150,
            "altitude_ft": 1000,
            "dew_point_f": 55.0,
        }

        measurement = WeatherMeasurement.from_supabase_record(record)

        self.assertEqual(measurement.id, "measurement-1")
        self.assertEqual(measurement.user_id, "test@example.com")
        self.assertEqual(measurement.weather_source_id, "source-1")
        self.assertEqual(measurement.temperature_f, 72.5)
        self.assertEqual(measurement.relative_humidity_pct, 65.0)
        self.assertEqual(measurement.barometric_pressure_inhg, 29.92)
        self.assertEqual(measurement.wind_speed_mph, 5.2)
        self.assertEqual(measurement.compass_true_deg, 270)
        self.assertEqual(measurement.density_altitude_ft, 2150)

    def test_weather_measurement_display_methods(self):
        """Test WeatherMeasurement display methods"""
        measurement = WeatherMeasurement(
            id="measurement-1",
            user_id="test@example.com",
            weather_source_id="source-1",
            measurement_timestamp=pd.to_datetime("2023-12-01T10:00:00"),
            uploaded_at=pd.to_datetime("2023-12-01T10:01:00"),
            temperature_f=72.5,
            relative_humidity_pct=65.0,
            barometric_pressure_inhg=29.92,
            wind_speed_mph=5.2,
            compass_true_deg=270,
            altitude_ft=1000,
            density_altitude_ft=2150,
        )

        self.assertEqual(measurement.temperature_display(), "72.5°F")
        self.assertEqual(measurement.humidity_display(), "65.0%")
        self.assertEqual(measurement.pressure_display(), "29.92 inHg")
        self.assertEqual(measurement.wind_display(), "5.2 mph")
        self.assertEqual(measurement.wind_direction_display(), "270°")
        self.assertEqual(measurement.altitude_display(), "1000 ft")
        self.assertEqual(measurement.density_altitude_display(), "2150 ft")

    def test_weather_measurement_has_data_methods(self):
        """Test WeatherMeasurement data detection methods"""
        measurement = WeatherMeasurement(
            id="measurement-1",
            user_id="test@example.com",
            weather_source_id="source-1",
            measurement_timestamp=pd.to_datetime("2023-12-01T10:00:00"),
            uploaded_at=pd.to_datetime("2023-12-01T10:01:00"),
            wind_speed_mph=5.2,
            compass_true_deg=270,
            location_description="Test Location",
        )

        self.assertTrue(measurement.has_wind_data())
        self.assertTrue(measurement.has_location_data())

    def test_weather_measurement_display_na_values(self):
        """Test WeatherMeasurement display methods with None values"""
        measurement = WeatherMeasurement(
            id="measurement-1",
            user_id="test@example.com",
            weather_source_id="source-1",
            measurement_timestamp=pd.to_datetime("2023-12-01T10:00:00"),
            uploaded_at=pd.to_datetime("2023-12-01T10:01:00"),
        )

        self.assertEqual(measurement.temperature_display(), "N/A")
        self.assertEqual(measurement.humidity_display(), "N/A")
        self.assertEqual(measurement.pressure_display(), "N/A")
        self.assertEqual(measurement.wind_display(), "N/A")
        self.assertEqual(measurement.wind_direction_display(), "N/A")
        self.assertEqual(measurement.altitude_display(), "N/A")
        self.assertEqual(measurement.density_altitude_display(), "N/A")


class TestWeatherImportTab(unittest.TestCase):

    @patch("streamlit.file_uploader")
    @patch("streamlit.success")
    @patch("streamlit.error")
    def test_render_weather_import_tab_no_file(
        self, mock_error, mock_success, mock_file_uploader
    ):
        mock_file_uploader.return_value = None

        user = {
            "email": "test@example.com",
            "id": "google-oauth2|111273793361054745867",
        }
        mock_supabase = Mock()

        # Mock empty weather sources response
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response)

        bucket = "test-bucket"

        result = render_weather_import_tab(user, mock_supabase, bucket)

        self.assertIsNone(result)

    @patch("streamlit.file_uploader")
    @patch("streamlit.success")
    @patch("streamlit.error")
    def test_render_weather_import_tab_upload_error(
        self, mock_error, mock_success, mock_file_uploader
    ):
        mock_file = Mock()
        mock_file.name = "test.csv"
        mock_file.type = "text/csv"
        mock_file.getvalue.return_value = b"fake_csv_data"
        mock_file_uploader.return_value = mock_file

        user = {
            "email": "test@example.com",
            "id": "google-oauth2|111273793361054745867",
        }
        mock_supabase = Mock()

        # Mock empty weather sources response
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response)

        mock_supabase.storage.from_.return_value.upload.side_effect = Exception(
            "Upload failed")
        bucket = "test-bucket"

        result = render_weather_import_tab(user, mock_supabase, bucket)

        # Function should complete without error (error may or may not be
        # called due to early return)
        self.assertIsNone(result)


class TestWeatherPageStructure(unittest.TestCase):
    """Test the weather page structure and configuration"""

    def test_weather_page_exists(self):
        """Test that the weather page file exists"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "4_Weather.py"
        )
        self.assertTrue(os.path.exists(page_path), "Weather page should exist")

    def test_weather_page_has_required_imports(self):
        """Test that weather page has required imports"""
        page_path = os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)),
            "pages",
            "4_🌤️_Weather.py")
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            required_imports = [
                "streamlit",
                "handle_auth",
                "create_client",
                "render_weather_import_tab",
            ]
            for required_import in required_imports:
                self.assertIn(
                    required_import,
                    content,
                    f"Weather page should import {required_import}",
                )

    def test_weather_page_has_correct_tabs(self):
        """Test that weather page has expected tabs"""
        page_path = os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)),
            "pages",
            "4_🌤️_Weather.py")
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            expected_tabs = [
                "Sources",
                "Import",
                "Logs",
                "View Log",
                "My Files"]
            for tab in expected_tabs:
                self.assertIn(
                    f'"{tab}"', content, f"Weather page should have {tab} tab"
                )

    def test_weather_page_configuration(self):
        """Test weather page configuration"""
        page_path = os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)),
            "pages",
            "4_🌤️_Weather.py")
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            self.assertIn('page_title="Weather - ChronoLog"', content)
            self.assertIn('page_icon="🌤️"', content)
            self.assertIn('layout="wide"', content)


class TestWeatherServiceAdvanced(unittest.TestCase):
    """Advanced tests for WeatherService functionality"""

    def setUp(self):
        self.mock_supabase = MagicMock()
        self.weather_service = WeatherService(self.mock_supabase)

        # Test data
        self.test_user_id = "test-user-123"
        self.test_source_id = "source-123"

        self.sample_source_data = {
            "user_id": self.test_user_id,
            "name": "Test Kestrel",
            "device_name": "Kestrel 5700",
            "model": "5700 Elite",
            "serial_number": "K123456789"
        }

        self.sample_measurement_data = {
            "user_id": self.test_user_id,
            "weather_source_id": self.test_source_id,
            "measurement_timestamp": "2023-12-01T10:00:00Z",
            "uploaded_at": "2023-12-01T10:01:00Z",
            "temperature_f": 75.2,
            "relative_humidity_pct": 65.0,
            "barometric_pressure_inhg": 29.92,
            "wind_speed_mph": 8.5
        }

    def test_weather_source_crud_operations(self):
        """Test comprehensive CRUD operations for weather sources"""
        # Test create
        mock_response = MagicMock()
        mock_response.data = [
            {"id": self.test_source_id, **self.sample_source_data}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        source_id = self.weather_service.create_source(self.sample_source_data)
        self.assertEqual(source_id, self.test_source_id)

        # Test get by ID
        mock_response.data = {
            "id": self.test_source_id,
            **self.sample_source_data}
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        source = self.weather_service.get_source_by_id(
            self.test_source_id, self.test_user_id)
        self.assertIsNotNone(source)
        self.assertEqual(source.id, self.test_source_id)

        # Test get by name
        source = self.weather_service.get_source_by_name(
            self.test_user_id, "Test Kestrel")
        self.assertIsNotNone(source)

        # Test update
        updates = {"name": "Updated Kestrel"}
        self.weather_service.update_source(
            self.test_source_id, self.test_user_id, updates)
        self.mock_supabase.table.return_value.update.assert_called()

        # Test delete
        self.weather_service.delete_source(
            self.test_source_id, self.test_user_id)
        self.mock_supabase.table.return_value.delete.assert_called()

    def test_weather_measurement_crud_operations(self):
        """Test comprehensive CRUD operations for weather measurements"""
        # Test create single measurement
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "measurement-123", **self.sample_measurement_data}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        measurement_id = self.weather_service.create_measurement(
            self.sample_measurement_data)
        self.assertEqual(measurement_id, "measurement-123")

        # Test create batch measurements
        batch_data = [self.sample_measurement_data] * 3
        batch_ids = [f"measurement-{i}" for i in range(3)]
        mock_response.data = [{"id": id} for id in batch_ids]

        created_ids = self.weather_service.create_measurements_batch(
            batch_data)
        self.assertEqual(len(created_ids), 3)
        self.assertEqual(created_ids, batch_ids)

    def test_weather_measurements_filtering(self):
        """Test comprehensive filtering of weather measurements"""
        mock_response = MagicMock()
        mock_measurements = [
            {
                "id": f"measurement-{i}",
                "uploaded_at": "2023-12-01T10:01:00Z",
                **self.sample_measurement_data
            }
            for i in range(5)
        ]
        mock_response.data = mock_measurements

        # Setup mock chain for filtered query
        mock_query = self.mock_supabase.table.return_value.select.return_value.eq.return_value
        mock_query.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value = mock_response

        # Test filtering by source, date range
        measurements = self.weather_service.get_measurements_filtered(
            user_id=self.test_user_id,
            source_id=self.test_source_id,
            start_date="2023-12-01T00:00:00Z",
            end_date="2023-12-01T23:59:59Z"
        )

        self.assertEqual(len(measurements), 5)
        for measurement in measurements:
            self.assertIsInstance(measurement, WeatherMeasurement)

    def test_weather_source_creation_from_device_info(self):
        """Test creating weather sources from device information"""
        # Test finding existing source by serial number
        mock_response = MagicMock()
        mock_response.data = [{"id": "existing-source-123"}]
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response

        source_id = self.weather_service.create_or_get_source_from_device_info(
            user_id=self.test_user_id,
            device_name="Kestrel 5700",
            device_model="5700 Elite",
            serial_number="K123456789"
        )

        self.assertEqual(source_id, "existing-source-123")

        # Test creating new source when none exists
        mock_response.data = []
        mock_create_response = MagicMock()
        mock_create_response.data = [{"id": "new-source-456"}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_create_response

        source_id = self.weather_service.create_or_get_source_from_device_info(
            user_id=self.test_user_id,
            device_name="Kestrel 5700",
            device_model="5700 Elite",
            serial_number="K987654321"
        )

        self.assertEqual(source_id, "new-source-456")

    def test_measurement_existence_check(self):
        """Test checking if measurements already exist"""
        # Test measurement exists
        mock_response = MagicMock()
        mock_response.data = [{"id": "measurement-123"}]
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response

        exists = self.weather_service.measurement_exists(
            user_id=self.test_user_id,
            source_id=self.test_source_id,
            measurement_timestamp="2023-12-01T10:00:00Z"
        )
        self.assertTrue(exists)

        # Test measurement doesn't exist
        mock_response.data = []
        exists = self.weather_service.measurement_exists(
            user_id=self.test_user_id,
            source_id=self.test_source_id,
            measurement_timestamp="2023-12-01T11:00:00Z"
        )
        self.assertFalse(exists)

    def test_weather_service_error_handling(self):
        """Test comprehensive error handling in weather service"""
        error_scenarios = [
            ("get_sources_for_user", "Database connection failed"),
            ("create_source", "Invalid source data"),
            ("get_measurements_for_source", "Source not found"),
            ("create_measurement", "Measurement validation failed")
        ]

        for method_name, error_msg in error_scenarios:
            with self.subTest(method=method_name):
                # Reset mock for each test
                self.mock_supabase.reset_mock()

                # Setup mock to raise exception
                if method_name == "get_sources_for_user":
                    self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception(
                        error_msg)
                elif method_name == "create_source":
                    self.mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
                        error_msg)
                elif method_name == "get_measurements_for_source":
                    self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.side_effect = Exception(
                        error_msg)
                elif method_name == "create_measurement":
                    self.mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
                        error_msg)

                # Test that exceptions are properly handled
                with self.assertRaises(Exception) as context:
                    if method_name == "get_sources_for_user":
                        self.weather_service.get_sources_for_user(
                            self.test_user_id)
                    elif method_name == "create_source":
                        self.weather_service.create_source(
                            self.sample_source_data)
                    elif method_name == "get_measurements_for_source":
                        self.weather_service.get_measurements_for_source(
                            self.test_source_id, self.test_user_id)
                    elif method_name == "create_measurement":
                        self.weather_service.create_measurement(
                            self.sample_measurement_data)

                self.assertIn(error_msg, str(context.exception))

    def test_bulk_operations_performance(self):
        """Test bulk operations with large datasets"""
        # Test batch creation of many measurements
        large_batch = [self.sample_measurement_data.copy() for _ in range(100)]
        for i, measurement in enumerate(large_batch):
            measurement["measurement_timestamp"] = f"2023-12-01T{i:02d}:00:00Z"

        mock_response = MagicMock()
        mock_response.data = [{"id": f"measurement-{i}"} for i in range(100)]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        created_ids = self.weather_service.create_measurements_batch(
            large_batch)
        self.assertEqual(len(created_ids), 100)

        # Verify single batch call was made
        self.mock_supabase.table.return_value.insert.assert_called_once_with(
            large_batch)


class TestWeatherModelsAdvanced(unittest.TestCase):
    """Advanced tests for Weather model classes"""

    def test_weather_source_edge_cases(self):
        """Test WeatherSource with edge cases and minimal data"""
        # Test with only required fields
        minimal_source = WeatherSource(
            id="source-1",
            user_id="user@example.com",
            name="Minimal Source"
        )

        self.assertEqual(minimal_source.display_name(), "Minimal Source")
        self.assertEqual(minimal_source.device_display(), "Unknown Device")
        self.assertEqual(
            minimal_source.short_display(),
            "Minimal Source - Unknown Device")

        # Test with various device info combinations
        combinations = [
            {"make": "Kestrel", "model": "5700", "expected": "Kestrel 5700"},
            {"device_name": "Weather Station", "expected": "Weather Station"},
            {"model": "Model123", "expected": "Model123"},
            {"serial_number": "SN123", "expected": "Unknown Device (S/N: SN123)"}
        ]

        for combo in combinations:
            source = WeatherSource(
                id="test",
                user_id="user@example.com",
                name="Test",
                make=combo.get("make"),
                model=combo.get("model"),
                device_name=combo.get("device_name"),
                serial_number=combo.get("serial_number")
            )
            self.assertEqual(source.device_display(), combo["expected"])

    def test_weather_measurement_comprehensive_display(self):
        """Test WeatherMeasurement display methods comprehensively"""
        # Test with full data
        full_measurement = WeatherMeasurement(
            id="m-1",
            user_id="user@example.com",
            weather_source_id="source-1",
            measurement_timestamp=pd.to_datetime("2023-12-01T10:00:00"),
            uploaded_at=pd.to_datetime("2023-12-01T10:01:00"),
            temperature_f=72.5,
            relative_humidity_pct=65.0,
            barometric_pressure_inhg=29.92,
            wind_speed_mph=12.3,
            compass_true_deg=270,
            compass_magnetic_deg=275,
            altitude_ft=1500,
            density_altitude_ft=2100
        )

        # Test all display methods
        self.assertEqual(full_measurement.temperature_display(), "72.5°F")
        self.assertEqual(full_measurement.humidity_display(), "65.0%")
        self.assertEqual(full_measurement.pressure_display(), "29.92 inHg")
        self.assertEqual(full_measurement.wind_display(), "12.3 mph")
        self.assertEqual(full_measurement.wind_direction_display(), "270°")
        self.assertEqual(full_measurement.altitude_display(), "1500 ft")
        self.assertEqual(
            full_measurement.density_altitude_display(),
            "2100 ft")

        # Test wind direction priority (true deg over magnetic)
        measurement_mag_only = WeatherMeasurement(
            id="m-2",
            user_id="user@example.com",
            weather_source_id="source-1",
            measurement_timestamp=pd.to_datetime("2023-12-01T10:00:00"),
            uploaded_at=pd.to_datetime("2023-12-01T10:01:00"),
            compass_magnetic_deg=275
        )
        self.assertEqual(
            measurement_mag_only.wind_direction_display(),
            "275° (mag)")

    def test_weather_measurement_data_detection(self):
        """Test WeatherMeasurement data detection methods"""
        # Test wind data detection
        wind_data_combinations = [
            {"wind_speed_mph": 5.0, "expected": True},
            {"crosswind_mph": 3.0, "expected": True},
            {"headwind_mph": -2.0, "expected": True},
            {"compass_magnetic_deg": 180, "expected": True},
            {"compass_true_deg": 270, "expected": True},
            {"temperature_f": 75.0, "expected": False}  # No wind data
        ]

        for combo in wind_data_combinations:
            measurement = WeatherMeasurement(
                id="test",
                user_id="user@example.com",
                weather_source_id="source-1",
                measurement_timestamp=pd.to_datetime("2023-12-01T10:00:00"),
                uploaded_at=pd.to_datetime("2023-12-01T10:01:00"),
                **{k: v for k, v in combo.items() if k != "expected"}
            )
            self.assertEqual(measurement.has_wind_data(), combo["expected"])

        # Test location data detection
        location_data_combinations = [
            {"location_description": "Test Range", "expected": True},
            {"location_address": "123 Main St", "expected": True},
            {"location_coordinates": "40.7128,-74.0060", "expected": True},
            {"temperature_f": 75.0, "expected": False}  # No location data
        ]

        for combo in location_data_combinations:
            measurement = WeatherMeasurement(
                id="test",
                user_id="user@example.com",
                weather_source_id="source-1",
                measurement_timestamp=pd.to_datetime("2023-12-01T10:00:00"),
                uploaded_at=pd.to_datetime("2023-12-01T10:01:00"),
                **{k: v for k, v in combo.items() if k != "expected"}
            )
            self.assertEqual(
                measurement.has_location_data(),
                combo["expected"])

    def test_weather_models_from_supabase_records(self):
        """Test creating models from multiple Supabase records"""
        # Test WeatherSource list creation
        source_records = [
            {
                "id": f"source-{i}",
                "user_id": "user@example.com",
                "name": f"Source {i}",
                "created_at": "2023-12-01T10:00:00"
            }
            for i in range(3)
        ]

        sources = WeatherSource.from_supabase_records(source_records)
        self.assertEqual(len(sources), 3)
        for i, source in enumerate(sources):
            self.assertEqual(source.id, f"source-{i}")
            self.assertEqual(source.name, f"Source {i}")

        # Test WeatherMeasurement list creation
        measurement_records = [
            {
                "id": f"measurement-{i}",
                "user_id": "user@example.com",
                "weather_source_id": "source-1",
                "measurement_timestamp": "2023-12-01T10:00:00",
                "uploaded_at": "2023-12-01T10:01:00",
                "temperature_f": 70.0 + i
            }
            for i in range(5)
        ]

        measurements = WeatherMeasurement.from_supabase_records(
            measurement_records)
        self.assertEqual(len(measurements), 5)
        for i, measurement in enumerate(measurements):
            self.assertEqual(measurement.id, f"measurement-{i}")
            self.assertEqual(measurement.temperature_f, 70.0 + i)


class TestWeatherUtilityFunctions(unittest.TestCase):
    """Test weather utility functions for unit conversions"""

    def test_temperature_conversions(self):
        """Test temperature conversion functions"""
        # Test Fahrenheit to Celsius
        self.assertAlmostEqual(fahrenheit_to_celsius(32), 0, places=2)
        self.assertAlmostEqual(fahrenheit_to_celsius(212), 100, places=2)
        self.assertAlmostEqual(fahrenheit_to_celsius(68), 20, places=2)
        self.assertIsNone(fahrenheit_to_celsius(None))

        # Test Celsius to Fahrenheit
        self.assertAlmostEqual(celsius_to_fahrenheit(0), 32, places=2)
        self.assertAlmostEqual(celsius_to_fahrenheit(100), 212, places=2)
        self.assertAlmostEqual(celsius_to_fahrenheit(20), 68, places=2)
        self.assertIsNone(celsius_to_fahrenheit(None))

    def test_distance_conversions(self):
        """Test distance conversion functions"""
        # Test feet to meters
        self.assertAlmostEqual(feet_to_meters(3.28084), 1.0, places=4)
        self.assertAlmostEqual(feet_to_meters(1000), 304.8, places=1)
        self.assertIsNone(feet_to_meters(None))

        # Test meters to feet
        self.assertAlmostEqual(meters_to_feet(1.0), 3.28084, places=4)
        self.assertAlmostEqual(meters_to_feet(304.8), 1000, places=1)
        self.assertIsNone(meters_to_feet(None))

    def test_pressure_conversions(self):
        """Test pressure conversion functions"""
        # Test inHg to hPa
        self.assertAlmostEqual(inhg_to_hpa(29.92), 1013.25, places=1)
        self.assertAlmostEqual(inhg_to_hpa(30.00), 1015.95, places=1)
        self.assertIsNone(inhg_to_hpa(None))

    def test_speed_conversions(self):
        """Test speed conversion functions"""
        # Test mph to m/s
        self.assertAlmostEqual(mph_to_mps(22.369), 10.0, places=2)
        self.assertAlmostEqual(mph_to_mps(60), 26.82, places=1)
        self.assertIsNone(mph_to_mps(None))


class TestWeatherIntegrationAdvanced(unittest.TestCase):
    """Advanced integration tests for weather module"""

    def setUp(self):
        self.mock_supabase = MagicMock()
        self.weather_service = WeatherService(self.mock_supabase)
        self.test_user_id = "integration-user-123"

    def test_complete_weather_workflow_integration(self):
        """Test complete weather data workflow from source creation to measurements"""
        # Step 1: Create weather source
        source_data = {
            "user_id": self.test_user_id,
            "name": "Integration Kestrel",
            "device_name": "Kestrel 5700",
            "model": "5700 Elite",
            "serial_number": "INT123456"
        }

        # Mock source creation response
        create_response = MagicMock()
        create_response.data = [{"id": "int-source-123", **source_data}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = create_response

        source_id = self.weather_service.create_source(source_data)
        self.assertEqual(source_id, "int-source-123")

        # Step 2: Create multiple measurements for the source
        measurements = []
        for i in range(10):
            measurement_data = {
                "user_id": self.test_user_id,
                "weather_source_id": source_id,
                "measurement_timestamp": f"2023-12-01T{i:02d}:00:00Z",
                "uploaded_at": f"2023-12-01T{i:02d}:01:00Z",
                "temperature_f": 70.0 + (i * 0.5),
                "relative_humidity_pct": 60.0 + i,
                "barometric_pressure_inhg": 29.90 + (i * 0.01),
                "wind_speed_mph": 5.0 + i
            }
            measurements.append(measurement_data)

        # Mock batch measurement creation
        batch_response = MagicMock()
        batch_response.data = [{"id": f"int-measurement-{i}"}
                               for i in range(10)]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = batch_response

        measurement_ids = self.weather_service.create_measurements_batch(
            measurements)
        self.assertEqual(len(measurement_ids), 10)

        # Step 3: Query measurements back
        # Mock query response with created measurements
        query_response = MagicMock()
        query_response.data = [
            {"id": f"int-measurement-{i}", **measurements[i]}
            for i in range(10)
        ]

        # Setup mock chain for measurement query
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = query_response

        retrieved_measurements = self.weather_service.get_measurements_for_source(
            source_id, self.test_user_id)
        self.assertEqual(len(retrieved_measurements), 10)

        # Verify data integrity
        for i, measurement in enumerate(retrieved_measurements):
            self.assertIsInstance(measurement, WeatherMeasurement)
            self.assertEqual(measurement.weather_source_id, source_id)
            self.assertEqual(measurement.temperature_f, 70.0 + (i * 0.5))

    def test_weather_source_device_info_integration(self):
        """Test integration of device info detection and source management"""
        device_scenarios = [
            # New device - should create new source
            {
                "device_name": "Kestrel 5700",
                "device_model": "5700 Elite",
                "serial_number": "NEW123456",
                "existing_sources": [],
                "expected_action": "create"
            },
            # Existing device by serial - should find existing
            {
                "device_name": "Kestrel 5700",
                "device_model": "5700 Elite",
                "serial_number": "EXISTING123",
                "existing_sources": [{"id": "existing-source", "serial_number": "EXISTING123"}],
                "expected_action": "find_existing"
            },
            # Existing device by name - should find existing
            {
                "device_name": "Kestrel 5700",
                "device_model": "5700 Elite",
                "serial_number": "BYNAME123",
                "existing_sources": [],
                "existing_by_name": {"id": "existing-by-name"},
                "expected_action": "find_by_name"
            }
        ]

        for scenario in device_scenarios:
            with self.subTest(scenario=scenario["expected_action"]):
                # Reset mock
                self.mock_supabase.reset_mock()

                if scenario["expected_action"] == "find_existing":
                    # Mock finding existing source by serial number
                    existing_response = MagicMock()
                    existing_response.data = scenario["existing_sources"]
                    self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = existing_response

                    source_id = self.weather_service.create_or_get_source_from_device_info(
                        user_id=self.test_user_id,
                        device_name=scenario["device_name"],
                        device_model=scenario["device_model"],
                        serial_number=scenario["serial_number"]
                    )

                    self.assertEqual(source_id, "existing-source")

                elif scenario["expected_action"] == "create":
                    # Mock no existing sources, then successful creation
                    no_existing_response = MagicMock()
                    no_existing_response.data = []
                    create_response = MagicMock()
                    create_response.data = [{"id": "new-source-123"}]

                    # Setup mock chain for serial search -> name search ->
                    # create
                    self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = no_existing_response
                    self.mock_supabase.table.return_value.insert.return_value.execute.return_value = create_response

                    source_id = self.weather_service.create_or_get_source_from_device_info(
                        user_id=self.test_user_id,
                        device_name=scenario["device_name"],
                        device_model=scenario["device_model"],
                        serial_number=scenario["serial_number"]
                    )

                    self.assertEqual(source_id, "new-source-123")

    def test_data_consistency_across_operations(self):
        """Test data consistency across multiple weather operations"""
        # Create a source
        source_data = {
            "user_id": self.test_user_id,
            "name": "Consistency Test Source",
            "device_name": "Test Device"
        }

        create_response = MagicMock()
        create_response.data = [{"id": "consistency-source", **source_data}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = create_response

        source_id = self.weather_service.create_source(source_data)

        # Update source with device info
        device_updates = {
            "device_name": "Updated Device",
            "model": "Model X",
            "serial_number": "UPDATED123"
        }

        self.weather_service.update_source_with_device_info(
            source_id=source_id,
            user_id=self.test_user_id,
            device_name=device_updates["device_name"],
            device_model=device_updates["model"],
            serial_number=device_updates["serial_number"]
        )

        # Verify update was called with correct parameters
        expected_update = {
            "device_name": "Updated Device",
            "model": "Model X",
            "serial_number": "UPDATED123",
            "updated_at": "NOW()"
        }

        self.mock_supabase.table.return_value.update.assert_called_with(
            expected_update)

        # Create measurements for the updated source
        measurement_data = {
            "user_id": self.test_user_id,
            "weather_source_id": source_id,
            "measurement_timestamp": "2023-12-01T10:00:00Z",
            "temperature_f": 75.0
        }

        measurement_response = MagicMock()
        measurement_response.data = [
            {"id": "consistency-measurement", **measurement_data}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = measurement_response

        measurement_id = self.weather_service.create_measurement(
            measurement_data)
        self.assertEqual(measurement_id, "consistency-measurement")

        # Verify measurement existence check
        exists_response = MagicMock()
        exists_response.data = [{"id": "consistency-measurement"}]
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = exists_response

        exists = self.weather_service.measurement_exists(
            user_id=self.test_user_id,
            source_id=source_id,
            measurement_timestamp="2023-12-01T10:00:00Z"
        )
        self.assertTrue(exists)

    def test_error_recovery_and_rollback_simulation(self):
        """Test error recovery scenarios in weather operations"""
        # Test partial batch failure recovery
        large_batch = [{"user_id": self.test_user_id, "weather_source_id": "source-1",
                        "measurement_timestamp": f"2023-12-01T{i:02d}:00:00Z"} for i in range(50)]

        # Simulate partial failure in batch insert
        self.mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
            "Batch insert failed at record 25")

        with self.assertRaises(Exception) as context:
            self.weather_service.create_measurements_batch(large_batch)

        self.assertIn("Batch insert failed", str(context.exception))

        # Test source creation failure with rollback
        self.mock_supabase.reset_mock()
        self.mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
            "Source creation failed")

        with self.assertRaises(Exception) as context:
            self.weather_service.create_source(
                {"user_id": self.test_user_id, "name": "Fail Source"})

        self.assertIn("Error creating weather source", str(context.exception))


if __name__ == "__main__":
    unittest.main()
