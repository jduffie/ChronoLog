"""
Integration tests for Weather module.

These tests verify end-to-end operations with real Supabase database:
- Creating weather sources
- Creating measurements (single and batch)
- Filtering measurements
- Device info-based source creation
- Cleaning up test data

Run with: python -m pytest weather/test_weather_integration.py -v -m integration
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from typing import List
from unittest.mock import Mock

import pytest
from supabase import create_client

# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather import WeatherAPI, WeatherMeasurement, WeatherSource


class BaseWeatherIntegrationTest(unittest.TestCase):
    """Base class for weather integration tests with common setup"""

    @classmethod
    def setUpClass(cls):
        """Set up test database connection"""
        # Use environment variables for Supabase connection
        cls.supabase_url = os.getenv(
            "SUPABASE_URL", "https://qnzioartedlrithdxszx.supabase.co"
        )
        cls.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "test-key")
        # Use existing test user ID that's in the users table
        cls.test_user_id = "google-oauth2|111273793361054745867"

        # Create Supabase client (or mock for CI)
        if cls.supabase_key == "test-key":
            # Mock client for CI/testing without credentials
            cls.supabase = Mock()
            cls.mock_mode = True
        else:
            # Real client for local integration testing
            cls.supabase = create_client(cls.supabase_url, cls.supabase_key)
            cls.mock_mode = False

        # Initialize API
        cls.weather_api = WeatherAPI(cls.supabase)

    def setUp(self):
        """Set up each test with clean state"""
        self.test_source_ids: List[str] = []  # Track created sources for cleanup

    def tearDown(self):
        """Clean up test data after each test"""
        if not self.mock_mode:
            # Clean up test sources (measurements will cascade delete)
            for source_id in reversed(self.test_source_ids):
                try:
                    self.weather_api.delete_source(source_id, self.test_user_id)
                except Exception as e:
                    print(f"Cleanup warning: Could not delete source {source_id}: {e}")


@pytest.mark.integration
@pytest.mark.database
class TestWeatherAPIIntegration(BaseWeatherIntegrationTest):
    """Test WeatherAPI operations against real database"""

    def test_create_and_delete_source(self):
        """Test creating and deleting a single weather source"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create a source
        source_data = {
            "name": "TEST_Integration_Kestrel",
            "device_name": "Kestrel 5700",
            "model": "5700 Elite",
            "serial_number": "TEST_INT_123456",
        }

        source = self.weather_api.create_source(source_data, self.test_user_id)
        self.test_source_ids.append(source.id)

        # Verify creation
        self.assertIsNotNone(source.id)
        self.assertEqual(source.name, "TEST_Integration_Kestrel")
        self.assertEqual(source.user_id, self.test_user_id)
        self.assertEqual(source.model, "5700 Elite")

        # Read it back
        read_source = self.weather_api.get_source_by_id(
            source.id, self.test_user_id
        )
        self.assertIsNotNone(read_source)
        self.assertEqual(read_source.id, source.id)
        self.assertEqual(read_source.serial_number, "TEST_INT_123456")

        # Delete it
        deleted = self.weather_api.delete_source(source.id, self.test_user_id)
        self.assertTrue(deleted)

        # Verify deletion
        read_after_delete = self.weather_api.get_source_by_id(
            source.id, self.test_user_id
        )
        self.assertIsNone(read_after_delete)

        # Clear tracking
        self.test_source_ids.clear()

    def test_source_device_info_workflow(self):
        """Test creating sources from device info (like CSV import)"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # First call should create new source
        source1 = self.weather_api.create_or_get_source_from_device_info(
            self.test_user_id,
            "Kestrel 5700",
            "5700 Elite",
            "TEST_DEVICE_123",
        )
        self.test_source_ids.append(source1.id)

        self.assertIsNotNone(source1.id)
        self.assertEqual(source1.serial_number, "TEST_DEVICE_123")

        # Second call with same serial should return same source
        source2 = self.weather_api.create_or_get_source_from_device_info(
            self.test_user_id,
            "Kestrel 5700",
            "5700 Elite",
            "TEST_DEVICE_123",
        )

        self.assertEqual(source1.id, source2.id, "Should return same source for same serial number")

        # Clean up
        self.weather_api.delete_source(source1.id, self.test_user_id)
        self.test_source_ids.clear()

    def test_measurement_crud_operations(self):
        """Test creating, reading, and filtering measurements"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create a test source
        source = self.weather_api.create_source(
            {
                "name": "TEST_Measurement_Source",
                "model": "Test Model",
            },
            self.test_user_id,
        )
        self.test_source_ids.append(source.id)

        # Create single measurement
        now = datetime.now()
        measurement_data = {
            "weather_source_id": source.id,
            "measurement_timestamp": now.isoformat(),
            "temperature_c": 22.5,
            "relative_humidity_pct": 65.0,
            "barometric_pressure_hpa": 1013.25,
            "wind_speed_mps": 3.5,
        }

        measurement = self.weather_api.create_measurement(
            measurement_data, self.test_user_id
        )

        self.assertIsNotNone(measurement.id)
        self.assertEqual(measurement.weather_source_id, source.id)
        self.assertEqual(measurement.temperature_c, 22.5)
        self.assertEqual(measurement.relative_humidity_pct, 65.0)

        # Query measurements for source
        measurements = self.weather_api.get_measurements_for_source(
            source.id, self.test_user_id
        )
        self.assertGreaterEqual(len(measurements), 1)
        self.assertEqual(measurements[0].id, measurement.id)

        # Clean up (source deletion will cascade delete measurements)
        self.weather_api.delete_source(source.id, self.test_user_id)
        self.test_source_ids.clear()

    def test_batch_measurement_creation(self):
        """Test creating multiple measurements in a batch"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create a test source
        source = self.weather_api.create_source(
            {"name": "TEST_Batch_Source"},
            self.test_user_id,
        )
        self.test_source_ids.append(source.id)

        # Create batch measurements
        base_time = datetime.now()
        batch_data = []
        for i in range(10):
            timestamp = (base_time + timedelta(minutes=i)).isoformat()
            batch_data.append({
                "weather_source_id": source.id,
                "measurement_timestamp": timestamp,
                "temperature_c": 20.0 + (i * 0.5),
                "relative_humidity_pct": 60.0 + i,
            })

        measurements = self.weather_api.create_measurements_batch(
            batch_data, self.test_user_id
        )

        self.assertEqual(len(measurements), 10)
        for i, measurement in enumerate(measurements):
            self.assertEqual(measurement.weather_source_id, source.id)
            self.assertEqual(measurement.temperature_c, 20.0 + (i * 0.5))

        # Verify all measurements are in database
        all_measurements = self.weather_api.get_measurements_for_source(
            source.id, self.test_user_id
        )
        self.assertEqual(len(all_measurements), 10)

        # Clean up
        self.weather_api.delete_source(source.id, self.test_user_id)
        self.test_source_ids.clear()

    def test_measurement_filtering(self):
        """Test filtering measurements by date range"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create a test source
        source = self.weather_api.create_source(
            {"name": "TEST_Filter_Source"},
            self.test_user_id,
        )
        self.test_source_ids.append(source.id)

        # Create measurements across different time periods
        base_time = datetime.now()
        batch_data = []
        for i in range(5):
            # Create measurements 1 hour apart
            timestamp = (base_time + timedelta(hours=i)).isoformat()
            batch_data.append({
                "weather_source_id": source.id,
                "measurement_timestamp": timestamp,
                "temperature_c": 20.0 + i,
            })

        self.weather_api.create_measurements_batch(batch_data, self.test_user_id)

        # Filter for middle 3 hours
        start_date = (base_time + timedelta(hours=1)).isoformat()
        end_date = (base_time + timedelta(hours=3)).isoformat()

        filtered = self.weather_api.filter_measurements(
            self.test_user_id,
            source_id=source.id,
            start_date=start_date,
            end_date=end_date,
        )

        # Should get measurements at hours 1, 2, 3
        self.assertGreaterEqual(len(filtered), 2)
        self.assertLessEqual(len(filtered), 3)

        # Clean up
        self.weather_api.delete_source(source.id, self.test_user_id)
        self.test_source_ids.clear()

    def test_measurement_existence_check(self):
        """Test checking if measurements exist"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create a test source
        source = self.weather_api.create_source(
            {"name": "TEST_Existence_Source"},
            self.test_user_id,
        )
        self.test_source_ids.append(source.id)

        # Create a measurement
        timestamp = datetime.now().isoformat()
        measurement_data = {
            "weather_source_id": source.id,
            "measurement_timestamp": timestamp,
            "temperature_c": 22.5,
        }

        self.weather_api.create_measurement(measurement_data, self.test_user_id)

        # Check existence
        exists = self.weather_api.measurement_exists(
            self.test_user_id, source.id, timestamp
        )
        self.assertTrue(exists)

        # Check non-existent measurement
        future_timestamp = (datetime.now() + timedelta(days=1)).isoformat()
        not_exists = self.weather_api.measurement_exists(
            self.test_user_id, source.id, future_timestamp
        )
        self.assertFalse(not_exists)

        # Clean up
        self.weather_api.delete_source(source.id, self.test_user_id)
        self.test_source_ids.clear()

    def test_complete_weather_workflow(self):
        """Test complete workflow: source creation, batch measurements, filtering, cleanup"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Step 1: Create source from device info (like CSV import)
        source = self.weather_api.create_or_get_source_from_device_info(
            self.test_user_id,
            "Kestrel 5700",
            "5700 Elite",
            "TEST_WORKFLOW_SN",
        )
        self.test_source_ids.append(source.id)

        # Step 2: Create batch measurements
        base_time = datetime.now()
        batch_data = []
        for i in range(20):
            timestamp = (base_time + timedelta(minutes=i * 5)).isoformat()
            batch_data.append({
                "weather_source_id": source.id,
                "measurement_timestamp": timestamp,
                "temperature_c": 20.0 + (i * 0.2),
                "relative_humidity_pct": 60.0 + (i * 0.5),
                "barometric_pressure_hpa": 1013.25 + (i * 0.1),
                "wind_speed_mps": 2.0 + (i * 0.1),
            })

        measurements = self.weather_api.create_measurements_batch(
            batch_data, self.test_user_id
        )
        self.assertEqual(len(measurements), 20)

        # Step 3: Filter measurements
        mid_start = (base_time + timedelta(minutes=25)).isoformat()
        mid_end = (base_time + timedelta(minutes=75)).isoformat()

        filtered = self.weather_api.filter_measurements(
            self.test_user_id,
            source_id=source.id,
            start_date=mid_start,
            end_date=mid_end,
        )
        self.assertGreater(len(filtered), 0)
        self.assertLess(len(filtered), 20)

        # Step 4: Get all measurements for user
        all_user_measurements = self.weather_api.get_all_measurements(
            self.test_user_id, limit=50
        )
        test_measurements = [
            m for m in all_user_measurements
            if m.weather_source_id == source.id
        ]
        self.assertEqual(len(test_measurements), 20)

        # Step 5: Verify data integrity
        for i, measurement in enumerate(measurements):
            self.assertEqual(measurement.weather_source_id, source.id)
            self.assertEqual(measurement.user_id, self.test_user_id)
            self.assertIsNotNone(measurement.id)
            self.assertIsNotNone(measurement.uploaded_at)

        # Step 6: Update source
        updated_source = self.weather_api.update_source(
            source.id,
            {"name": "TEST_UPDATED_Kestrel", "make": "Kestrel"},
            self.test_user_id,
        )
        self.assertEqual(updated_source.name, "TEST_UPDATED_Kestrel")
        self.assertEqual(updated_source.make, "Kestrel")

        # Step 7: Delete source (should cascade delete measurements)
        deleted = self.weather_api.delete_source(source.id, self.test_user_id)
        self.assertTrue(deleted)

        # Verify source is gone
        source_after_delete = self.weather_api.get_source_by_id(
            source.id, self.test_user_id
        )
        self.assertIsNone(source_after_delete)

        # Verify measurements are gone
        measurements_after_delete = self.weather_api.get_measurements_for_source(
            source.id, self.test_user_id
        )
        self.assertEqual(len(measurements_after_delete), 0)

        # Clear tracking
        self.test_source_ids.clear()

        print("Complete weather workflow test completed successfully!")


if __name__ == "__main__":
    # Set up test environment
    if not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        print("Warning: SUPABASE_SERVICE_ROLE_KEY not set - running in mock mode")
        print("To run real integration tests, set environment variables:")
        print("  export SUPABASE_SERVICE_ROLE_KEY=your-key")

    # Run the tests
    unittest.main(verbosity=2)