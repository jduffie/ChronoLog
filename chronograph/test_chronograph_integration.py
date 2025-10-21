"""
Integration tests for Chronograph module.

These tests verify end-to-end operations with real Supabase database:
- Creating chronograph sources
- Creating sessions with statistics
- Creating measurements (single and batch)
- Session statistics calculation
- Filtering sessions
- Device info-based source creation
- Cleaning up test data

Run with: python -m pytest chronograph/test_chronograph_integration.py -v -m integration
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

from chronograph import (
    ChronographAPI,
    ChronographMeasurement,
    ChronographSession,
    ChronographSource,
)


class BaseChronographIntegrationTest(unittest.TestCase):
    """Base class for chronograph integration tests with common setup"""

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
        cls.chrono_api = ChronographAPI(cls.supabase)

    def setUp(self):
        """Set up each test with clean state"""
        self.test_source_ids: List[str] = []  # Track created sources for cleanup
        self.test_session_ids: List[str] = []  # Track created sessions for cleanup

    def tearDown(self):
        """Clean up test data after each test"""
        if not self.mock_mode:
            # Clean up test sessions (measurements will cascade delete)
            for session_id in reversed(self.test_session_ids):
                try:
                    # Delete session by deleting directly from database
                    # (ChronographAPI doesn't have delete_session method yet)
                    self.supabase.table("chrono_sessions").delete().eq(
                        "id", session_id
                    ).execute()
                except Exception as e:
                    print(
                        f"Cleanup warning: Could not delete session {session_id}: {e}"
                    )

            # Clean up test sources
            for source_id in reversed(self.test_source_ids):
                try:
                    self.chrono_api.delete_source(source_id, self.test_user_id)
                except Exception as e:
                    print(f"Cleanup warning: Could not delete source {source_id}: {e}")


@pytest.mark.integration
@pytest.mark.database
class TestChronographAPIIntegration(BaseChronographIntegrationTest):
    """Test ChronographAPI operations against real database"""

    def test_create_and_delete_source(self):
        """Test creating and deleting a single chronograph source"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create a source
        source_data = {
            "name": "TEST_Integration_Garmin",
            "device_name": "Garmin Xero",
            "make": "Garmin",
            "model": "Xero C1",
            "serial_number": "TEST_INT_G123456",
        }

        source = self.chrono_api.create_source(source_data, self.test_user_id)
        self.test_source_ids.append(source.id)

        # Verify creation
        self.assertIsNotNone(source.id)
        self.assertEqual(source.name, "TEST_Integration_Garmin")
        self.assertEqual(source.user_id, self.test_user_id)
        self.assertEqual(source.model, "Xero C1")

        # Read it back
        read_source = self.chrono_api.get_source_by_id(source.id, self.test_user_id)
        self.assertIsNotNone(read_source)
        self.assertEqual(read_source.id, source.id)
        self.assertEqual(read_source.serial_number, "TEST_INT_G123456")

        # Delete it
        deleted = self.chrono_api.delete_source(source.id, self.test_user_id)
        self.assertTrue(deleted)

        # Verify deletion
        read_after_delete = self.chrono_api.get_source_by_id(
            source.id, self.test_user_id
        )
        self.assertIsNone(read_after_delete)

        # Clear tracking
        self.test_source_ids.clear()

    def test_session_crud_operations(self):
        """Test creating, reading, and verifying sessions"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create a test source
        source = self.chrono_api.create_source(
            {"name": "TEST_Session_Source", "model": "Test Model"},
            self.test_user_id,
        )
        self.test_source_ids.append(source.id)

        # Create a session
        now = datetime.now()
        session_data = {
            "tab_name": "168gr HPBT TEST",
            "session_name": "Integration Test Session",
            "datetime_local": now.isoformat(),
            "chronograph_source_id": source.id,
        }

        session = self.chrono_api.create_session(session_data, self.test_user_id)
        self.test_session_ids.append(session.id)

        # Verify creation
        self.assertIsNotNone(session.id)
        self.assertEqual(session.tab_name, "168gr HPBT TEST")
        self.assertEqual(session.session_name, "Integration Test Session")
        self.assertEqual(session.chronograph_source_id, source.id)

        # Read it back
        read_session = self.chrono_api.get_session_by_id(
            session.id, self.test_user_id
        )
        self.assertIsNotNone(read_session)
        self.assertEqual(read_session.id, session.id)
        self.assertEqual(read_session.tab_name, "168gr HPBT TEST")

        # Verify in all sessions
        all_sessions = self.chrono_api.get_all_sessions(self.test_user_id)
        test_sessions = [s for s in all_sessions if s.id == session.id]
        self.assertEqual(len(test_sessions), 1)

        # Clean up
        self.supabase.table("chrono_sessions").delete().eq(
            "id", session.id
        ).execute()
        self.test_session_ids.clear()
        self.chrono_api.delete_source(source.id, self.test_user_id)
        self.test_source_ids.clear()

    def test_measurement_crud_operations(self):
        """Test creating and reading measurements"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create source and session
        source = self.chrono_api.create_source(
            {"name": "TEST_Measurement_Source"},
            self.test_user_id,
        )
        self.test_source_ids.append(source.id)

        session = self.chrono_api.create_session(
            {
                "tab_name": "175gr SMK TEST",
                "session_name": "Measurement Test",
                "datetime_local": datetime.now().isoformat(),
            },
            self.test_user_id,
        )
        self.test_session_ids.append(session.id)

        # Create single measurement
        measurement_data = {
            "chrono_session_id": session.id,
            "shot_number": 1,
            "speed_mps": 792.5,
            "datetime_local": datetime.now().isoformat(),
            "ke_j": 3500.0,
            "power_factor_kgms": 42.5,
        }

        measurement = self.chrono_api.create_measurement(
            measurement_data, self.test_user_id
        )

        # Verify creation
        self.assertIsNotNone(measurement.id)
        self.assertEqual(measurement.chrono_session_id, session.id)
        self.assertEqual(measurement.shot_number, 1)
        self.assertEqual(measurement.speed_mps, 792.5)
        self.assertEqual(measurement.ke_j, 3500.0)

        # Query measurements for session
        measurements = self.chrono_api.get_measurements_for_session(
            session.id, self.test_user_id
        )
        self.assertGreaterEqual(len(measurements), 1)
        self.assertEqual(measurements[0].id, measurement.id)

        # Clean up
        self.supabase.table("chrono_sessions").delete().eq(
            "id", session.id
        ).execute()
        self.test_session_ids.clear()
        self.chrono_api.delete_source(source.id, self.test_user_id)
        self.test_source_ids.clear()

    def test_batch_measurement_creation_with_statistics(self):
        """Test creating multiple measurements and verifying statistics calculation"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create source and session
        source = self.chrono_api.create_source(
            {"name": "TEST_Batch_Source"},
            self.test_user_id,
        )
        self.test_source_ids.append(source.id)

        session = self.chrono_api.create_session(
            {
                "tab_name": "140gr ELD-M TEST",
                "session_name": "Batch Test",
                "datetime_local": datetime.now().isoformat(),
            },
            self.test_user_id,
        )
        self.test_session_ids.append(session.id)

        # Create batch measurements with known statistics
        base_time = datetime.now()
        batch_data = []
        velocities = [792.0, 794.0, 793.0, 795.0, 791.0, 796.0, 792.5, 793.5, 794.5, 795.5]

        for i, velocity in enumerate(velocities):
            timestamp = (base_time + timedelta(seconds=i * 5)).isoformat()
            batch_data.append(
                {
                    "chrono_session_id": session.id,
                    "shot_number": i + 1,
                    "speed_mps": velocity,
                    "datetime_local": timestamp,
                }
            )

        measurements = self.chrono_api.create_measurements_batch(
            batch_data, self.test_user_id
        )

        # Verify measurements created
        self.assertEqual(len(measurements), 10)
        for i, measurement in enumerate(measurements):
            self.assertEqual(measurement.chrono_session_id, session.id)
            self.assertEqual(measurement.shot_number, i + 1)

        # Get updated session with statistics
        updated_session = self.chrono_api.get_session_by_id(
            session.id, self.test_user_id
        )

        # Verify statistics were calculated
        self.assertEqual(updated_session.shot_count, 10)
        self.assertIsNotNone(updated_session.avg_speed_mps)
        self.assertIsNotNone(updated_session.std_dev_mps)
        self.assertIsNotNone(updated_session.min_speed_mps)
        self.assertIsNotNone(updated_session.max_speed_mps)
        self.assertIsNotNone(updated_session.extreme_spread_mps)

        # Verify statistics values are reasonable
        self.assertGreater(updated_session.avg_speed_mps, 790.0)
        self.assertLess(updated_session.avg_speed_mps, 800.0)
        self.assertEqual(updated_session.min_speed_mps, 791.0)
        self.assertEqual(updated_session.max_speed_mps, 796.0)
        self.assertEqual(updated_session.extreme_spread_mps, 5.0)  # 796 - 791

        # Clean up
        self.supabase.table("chrono_sessions").delete().eq(
            "id", session.id
        ).execute()
        self.test_session_ids.clear()
        self.chrono_api.delete_source(source.id, self.test_user_id)
        self.test_source_ids.clear()

    def test_session_statistics_calculation(self):
        """Test manual statistics calculation"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create source and session
        source = self.chrono_api.create_source(
            {"name": "TEST_Stats_Source"},
            self.test_user_id,
        )
        self.test_source_ids.append(source.id)

        session = self.chrono_api.create_session(
            {
                "tab_name": "155gr SCENAR TEST",
                "session_name": "Stats Test",
                "datetime_local": datetime.now().isoformat(),
            },
            self.test_user_id,
        )
        self.test_session_ids.append(session.id)

        # Create measurements
        batch_data = [
            {
                "chrono_session_id": session.id,
                "shot_number": i + 1,
                "speed_mps": 800.0 + i,
                "datetime_local": datetime.now().isoformat(),
            }
            for i in range(5)
        ]

        self.chrono_api.create_measurements_batch(batch_data, self.test_user_id)

        # Calculate statistics
        stats = self.chrono_api.calculate_session_statistics(
            session.id, self.test_user_id
        )

        # Verify statistics
        self.assertEqual(stats["shot_count"], 5)
        self.assertEqual(stats["avg_speed_mps"], 802.0)  # (800+801+802+803+804)/5
        self.assertEqual(stats["min_speed_mps"], 800.0)
        self.assertEqual(stats["max_speed_mps"], 804.0)
        self.assertEqual(stats["extreme_spread_mps"], 4.0)
        self.assertIsNotNone(stats["std_dev_mps"])
        self.assertIsNotNone(stats["coefficient_of_variation"])

        # Clean up
        self.supabase.table("chrono_sessions").delete().eq(
            "id", session.id
        ).execute()
        self.test_session_ids.clear()
        self.chrono_api.delete_source(source.id, self.test_user_id)
        self.test_source_ids.clear()

    def test_session_filtering(self):
        """Test filtering sessions by bullet type and date range"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create source
        source = self.chrono_api.create_source(
            {"name": "TEST_Filter_Source"},
            self.test_user_id,
        )
        self.test_source_ids.append(source.id)

        # Create sessions across different times and bullet types
        base_time = datetime.now()
        sessions_data = [
            {
                "tab_name": "168gr HPBT TEST",
                "session_name": "Session 1",
                "datetime_local": base_time.isoformat(),
            },
            {
                "tab_name": "175gr SMK TEST",
                "session_name": "Session 2",
                "datetime_local": (base_time + timedelta(hours=1)).isoformat(),
            },
            {
                "tab_name": "168gr HPBT TEST",
                "session_name": "Session 3",
                "datetime_local": (base_time + timedelta(hours=2)).isoformat(),
            },
        ]

        created_sessions = []
        for session_data in sessions_data:
            session = self.chrono_api.create_session(session_data, self.test_user_id)
            self.test_session_ids.append(session.id)
            created_sessions.append(session)

        # Filter by bullet type
        filtered_168 = self.chrono_api.filter_sessions(
            self.test_user_id, bullet_type="168gr HPBT TEST"
        )
        test_filtered_168 = [s for s in filtered_168 if s.id in self.test_session_ids]
        self.assertEqual(len(test_filtered_168), 2)

        # Filter by date range
        start_date = (base_time + timedelta(minutes=30)).isoformat()
        end_date = (base_time + timedelta(hours=1, minutes=30)).isoformat()
        filtered_date = self.chrono_api.filter_sessions(
            self.test_user_id, start_date=start_date, end_date=end_date
        )
        test_filtered_date = [s for s in filtered_date if s.id in self.test_session_ids]
        self.assertGreaterEqual(len(test_filtered_date), 1)

        # Clean up
        for session_id in self.test_session_ids:
            self.supabase.table("chrono_sessions").delete().eq(
                "id", session_id
            ).execute()
        self.test_session_ids.clear()
        self.chrono_api.delete_source(source.id, self.test_user_id)
        self.test_source_ids.clear()

    def test_session_existence_check(self):
        """Test checking if a session already exists"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create source
        source = self.chrono_api.create_source(
            {"name": "TEST_Existence_Source"},
            self.test_user_id,
        )
        self.test_source_ids.append(source.id)

        # Create a session
        timestamp = datetime.now().isoformat()
        session = self.chrono_api.create_session(
            {
                "tab_name": "140gr ELD-M TEST",
                "session_name": "Existence Test",
                "datetime_local": timestamp,
            },
            self.test_user_id,
        )
        self.test_session_ids.append(session.id)

        # Check existence
        exists = self.chrono_api.session_exists(
            self.test_user_id, "140gr ELD-M TEST", timestamp
        )
        self.assertTrue(exists)

        # Check non-existent session
        future_timestamp = (datetime.now() + timedelta(days=1)).isoformat()
        not_exists = self.chrono_api.session_exists(
            self.test_user_id, "140gr ELD-M TEST", future_timestamp
        )
        self.assertFalse(not_exists)

        # Clean up
        self.supabase.table("chrono_sessions").delete().eq(
            "id", session.id
        ).execute()
        self.test_session_ids.clear()
        self.chrono_api.delete_source(source.id, self.test_user_id)
        self.test_source_ids.clear()

    def test_complete_chronograph_workflow(self):
        """Test complete workflow: source creation, session, batch measurements, stats verification"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Step 1: Create source from device info (like CSV import)
        source_id = self.chrono_api.create_or_get_source_from_device_info(
            self.test_user_id,
            "Garmin Xero",
            "Xero C1",
            "TEST_WORKFLOW_G789",
        )

        # Get the source object
        source = self.chrono_api.get_source_by_id(source_id, self.test_user_id)
        self.test_source_ids.append(source.id)
        self.assertEqual(source.serial_number, "TEST_WORKFLOW_G789")

        # Step 2: Create session
        session = self.chrono_api.create_session(
            {
                "tab_name": "168gr HPBT WORKFLOW TEST",
                "session_name": "Complete Workflow Test",
                "datetime_local": datetime.now().isoformat(),
                "chronograph_source_id": source.id,
            },
            self.test_user_id,
        )
        self.test_session_ids.append(session.id)

        # Step 3: Create batch measurements (20 shots)
        base_time = datetime.now()
        batch_data = []
        for i in range(20):
            timestamp = (base_time + timedelta(seconds=i * 5)).isoformat()
            # Simulate realistic velocity data with small variations
            velocity = 792.0 + (i % 5) * 0.5 - 1.0
            batch_data.append(
                {
                    "chrono_session_id": session.id,
                    "shot_number": i + 1,
                    "speed_mps": velocity,
                    "datetime_local": timestamp,
                    "ke_j": 3500.0 + i,
                    "power_factor_kgms": 42.0 + (i * 0.1),
                }
            )

        measurements = self.chrono_api.create_measurements_batch(
            batch_data, self.test_user_id
        )
        self.assertEqual(len(measurements), 20)

        # Step 4: Verify session statistics
        updated_session = self.chrono_api.get_session_by_id(
            session.id, self.test_user_id
        )

        self.assertEqual(updated_session.shot_count, 20)
        self.assertIsNotNone(updated_session.avg_speed_mps)
        self.assertIsNotNone(updated_session.std_dev_mps)
        self.assertIsNotNone(updated_session.extreme_spread_mps)
        self.assertIsNotNone(updated_session.coefficient_of_variation)

        # Step 5: Get all measurements for session
        all_measurements = self.chrono_api.get_measurements_for_session(
            session.id, self.test_user_id
        )
        self.assertEqual(len(all_measurements), 20)

        # Step 6: Verify data integrity
        for measurement in measurements:
            self.assertEqual(measurement.chrono_session_id, session.id)
            self.assertEqual(measurement.user_id, self.test_user_id)
            self.assertIsNotNone(measurement.id)
            self.assertIsNotNone(measurement.uploaded_at)

        # Step 7: Get unique bullet types
        bullet_types = self.chrono_api.get_unique_bullet_types(self.test_user_id)
        self.assertIn("168gr HPBT WORKFLOW TEST", bullet_types)

        # Step 8: Clean up (delete session, then source)
        self.supabase.table("chrono_sessions").delete().eq(
            "id", session.id
        ).execute()

        # Verify session is gone
        session_after_delete = self.chrono_api.get_session_by_id(
            session.id, self.test_user_id
        )
        self.assertIsNone(session_after_delete)

        # Verify measurements are gone (cascade delete)
        measurements_after_delete = self.chrono_api.get_measurements_for_session(
            session.id, self.test_user_id
        )
        self.assertEqual(len(measurements_after_delete), 0)

        # Delete source
        deleted = self.chrono_api.delete_source(source.id, self.test_user_id)
        self.assertTrue(deleted)

        # Clear tracking
        self.test_session_ids.clear()
        self.test_source_ids.clear()

        print("Complete chronograph workflow test completed successfully!")


if __name__ == "__main__":
    # Set up test environment
    if not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        print("Warning: SUPABASE_SERVICE_ROLE_KEY not set - running in mock mode")
        print("To run real integration tests, set environment variables:")
        print("  export SUPABASE_SERVICE_ROLE_KEY=your-key")

    # Run the tests
    unittest.main(verbosity=2)
