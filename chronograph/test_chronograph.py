import os
import sys
import unittest
import tempfile
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch
from decimal import Decimal

import pandas as pd

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chronograph.import_tab import render_chronograph_import_tab
from chronograph.chronograph_session_models import ChronographMeasurement, ChronographSession
from chronograph.service import ChronographService
from chronograph.chronograph_source_models import ChronographSource


class TestChronographService(unittest.TestCase):

    def setUp(self):
        self.mock_supabase = Mock()
        self.service = ChronographService(self.mock_supabase)
        self.user_id = "test@example.com"
        self.user_id = "google-oauth2|111273793361054745867"


    def test_get_sessions_for_user_empty(self):
        mock_response = Mock()
        mock_response.data = []

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response
        )

        sessions = self.service.get_sessions_for_user(self.user_id)

        self.assertEqual(len(sessions), 0)


    def test_get_measurements_for_session(self):
        session_id = "session-1"
        mock_data = [
            {
                "id": "measurement-1",
                "user_id": self.user_id,
                "chrono_session_id": session_id,
                "shot_number": 1,
                "speed_fps": 1200.5,
                "datetime_local": "2023-12-01T10:01:00",
                "delta_avg_fps": 5.2,
                "ke_ft_lb": 368.5,
                "power_factor": 138.1,
            }
        ]

        mock_response = Mock()
        mock_response.data = mock_data

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response
        )

        measurements = self.service.get_measurements_for_session(
            self.user_id, session_id
        )

        self.assertEqual(len(measurements), 1)
        self.assertIsInstance(measurements[0], ChronographMeasurement)
        self.assertEqual(measurements[0].shot_number, 1)
        self.assertEqual(measurements[0].speed_fps, 1200.5)

    def test_session_exists_true(self):
        mock_response = Mock()
        mock_response.data = [{"id": "session-1"}]

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        exists = self.service.session_exists(
            self.user_id, "Sheet1", "2023-12-01T10:00:00"
        )

        self.assertTrue(exists)

    def test_session_exists_false(self):
        mock_response = Mock()
        mock_response.data = []

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        exists = self.service.session_exists(
            self.user_id, "Sheet1", "2023-12-01T10:00:00"
        )

        self.assertFalse(exists)


    def test_get_unique_bullet_types(self):
        mock_data = [
            {"bullet_type": "9mm FMJ"},
            {"bullet_type": ".45 ACP"},
            {"bullet_type": "9mm FMJ"},
            {"bullet_type": ".380 Auto"},
        ]

        mock_response = Mock()
        mock_response.data = mock_data

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        bullet_types = self.service.get_unique_bullet_types(self.user_id)

        expected_types = [".380 Auto", ".45 ACP", "9mm FMJ"]
        self.assertEqual(bullet_types, expected_types)

    def test_get_sessions_for_user_with_data(self):
        """Test getting sessions with actual data"""
        mock_data = [
            {
                "id": "session-1",
                "user_id": self.user_id,
                "tab_name": "Sheet1",
                "session_name": "9mm FMJ Test",
                "datetime_local": "2023-12-01T10:00:00",
                "uploaded_at": "2023-12-01T10:05:00",
                "file_path": "/uploads/test.xlsx",
                "shot_count": 5,
                "avg_speed_fps": 1150.0,
                "std_dev_fps": 12.5
            }
        ]

        mock_response = Mock()
        mock_response.data = mock_data

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response
        )

        sessions = self.service.get_sessions_for_user(self.user_id)

        self.assertEqual(len(sessions), 1)
        self.assertIsInstance(sessions[0], ChronographSession)
        self.assertEqual(sessions[0].session_name, "9mm FMJ Test")
        self.assertEqual(sessions[0].shot_count, 5)

    def test_get_sessions_for_user_database_error(self):
        """Test database error handling in get_sessions_for_user"""
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception(
            "Database connection failed"
        )
        
        with self.assertRaises(Exception) as context:
            self.service.get_sessions_for_user(self.user_id)
        
        self.assertIn("Error fetching sessions", str(context.exception))
        self.assertIn("Database connection failed", str(context.exception))

    def test_get_measurements_for_session_empty(self):
        """Test getting measurements for session with no data"""
        mock_response = Mock()
        mock_response.data = []

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response
        )

        measurements = self.service.get_measurements_for_session(self.user_id, "session-1")

        self.assertEqual(len(measurements), 0)

    def test_get_measurements_for_session_database_error(self):
        """Test database error handling in get_measurements_for_session"""
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.side_effect = Exception(
            "Query failed"
        )
        
        with self.assertRaises(Exception) as context:
            self.service.get_measurements_for_session(self.user_id, "session-1")
        
        self.assertIn("Error fetching measurements", str(context.exception))

    def test_session_exists_database_error(self):
        """Test database error handling in session_exists"""
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.side_effect = Exception(
            "Query failed"
        )
        
        with self.assertRaises(Exception) as context:
            self.service.session_exists(self.user_id, "Sheet1", "2023-12-01T10:00:00")
        
        self.assertIn("Error checking session existence", str(context.exception))

    def test_get_unique_bullet_types_empty(self):
        """Test getting unique bullet types with no data"""
        mock_response = Mock()
        mock_response.data = []

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        bullet_types = self.service.get_unique_bullet_types(self.user_id)

        self.assertEqual(bullet_types, [])

    def test_get_unique_bullet_types_database_error(self):
        """Test database error handling in get_unique_bullet_types"""
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception(
            "Query failed"
        )
        
        with self.assertRaises(Exception) as context:
            self.service.get_unique_bullet_types(self.user_id)
        
        self.assertIn("Error fetching bullet types", str(context.exception))


class TestChronographModels(unittest.TestCase):

    def setUp(self):
        self.sample_session_record = {
            "id": "session-123",
            "user_id": "user-456",
            "tab_name": "Sheet1",
            "session_name": "9mm Test Session",
            "datetime_local": "2023-12-01T10:00:00",
            "uploaded_at": "2023-12-01T10:05:00",
            "file_path": "/uploads/garmin_data.xlsx",
            "chronograph_source_id": "source-789",
            "shot_count": 10,
            "avg_speed_fps": 1150.5,
            "std_dev_fps": 15.3,
            "min_speed_fps": 1120.2,
            "max_speed_fps": 1175.8,
            "created_at": "2023-12-01T10:05:30"
        }

        self.sample_measurement_record = {
            "id": "measurement-1",
            "user_id": "google-oauth2|111273793361054745867",
            "chrono_session_id": "session-1",
            "shot_number": 1,
            "speed_fps": 1200.5,
            "speed_mps": 365.8,
            "datetime_local": "2023-12-01T10:01:00",
            "delta_avg_fps": 5.2,
            "delta_avg_mps": 1.6,
            "ke_ft_lb": 368.5,
            "ke_j": 499.2,
            "power_factor": 138.1,
            "power_factor_kgms": 62.7,
            "clean_bore": True,
            "cold_bore": False,
            "shot_notes": "Test note",
        }

    def test_chronograph_session_from_supabase_record(self):
        """Test creating ChronographSession from Supabase record"""
        session = ChronographSession.from_supabase_record(self.sample_session_record)
        
        self.assertEqual(session.id, "session-123")
        self.assertEqual(session.user_id, "user-456")
        self.assertEqual(session.tab_name, "Sheet1")
        self.assertEqual(session.session_name, "9mm Test Session")
        self.assertEqual(session.chronograph_source_id, "source-789")
        self.assertEqual(session.shot_count, 10)
        self.assertEqual(session.avg_speed_fps, 1150.5)
        self.assertEqual(session.std_dev_fps, 15.3)
        self.assertIsInstance(session.datetime_local, pd.Timestamp)
        self.assertIsInstance(session.uploaded_at, pd.Timestamp)

    def test_chronograph_session_from_supabase_records(self):
        """Test creating multiple ChronographSession objects from records"""
        records = [
            self.sample_session_record,
            {**self.sample_session_record, "id": "session-456", "session_name": "45 ACP Test"}
        ]
        
        sessions = ChronographSession.from_supabase_records(records)
        
        self.assertEqual(len(sessions), 2)
        self.assertEqual(sessions[0].id, "session-123")
        self.assertEqual(sessions[1].id, "session-456")
        self.assertEqual(sessions[1].session_name, "45 ACP Test")

    def test_chronograph_session_display_methods(self):
        """Test ChronographSession display methods"""
        session = ChronographSession.from_supabase_record(self.sample_session_record)
        
        # Test display_name
        expected_display = "Sheet1 - 2023-12-01 10:00"
        self.assertEqual(session.display_name(), expected_display)
        
        # Test bullet_display
        self.assertEqual(session.bullet_display(), "9mm Test Session")
        
        # Test muzzle_vel_speed_units
        self.assertEqual(session.muzzle_vel_speed_units(), "fps")
        
        # Test avg_speed_display
        self.assertEqual(session.avg_speed_display(), "1150")
        
        # Test std_dev_display
        self.assertEqual(session.std_dev_display(), "15.3 fps")
        
        # Test velocity_range_display
        expected_range = f"{1175.8 - 1120.2:.0f} fps"
        self.assertEqual(session.velocity_range_display(), expected_range)
        
        # Test file_name
        self.assertEqual(session.file_name(), "garmin_data.xlsx")
        
        # Test has_measurements
        self.assertTrue(session.has_measurements())

    def test_chronograph_session_display_methods_with_none_values(self):
        """Test ChronographSession display methods with None values"""
        minimal_record = {
            "id": "session-minimal",
            "user_id": "user-123",
            "tab_name": "Test",
            "session_name": "",
            "datetime_local": "2023-12-01T10:00:00",
            "uploaded_at": "2023-12-01T10:05:00",
            "file_path": None,
            "shot_count": 0,
            "avg_speed_fps": None,
            "std_dev_fps": None,
            "min_speed_fps": None,
            "max_speed_fps": None,
        }
        
        session = ChronographSession.from_supabase_record(minimal_record)
        
        # Test with None/empty values
        self.assertEqual(session.bullet_display(), "Unknown Session")
        self.assertEqual(session.avg_speed_display(), "N/A")
        self.assertEqual(session.std_dev_display(), "N/A")
        self.assertEqual(session.velocity_range_display(), "N/A")
        self.assertEqual(session.file_name(), "N/A")
        self.assertFalse(session.has_measurements())

    def test_chronograph_measurement_from_supabase_record(self):
        """Test creating ChronographMeasurement from Supabase record"""
        measurement = ChronographMeasurement.from_supabase_record(self.sample_measurement_record)

        self.assertEqual(measurement.id, "measurement-1")
        self.assertEqual(measurement.shot_number, 1)
        self.assertAlmostEqual(measurement.speed_fps, 1200.5)
        self.assertAlmostEqual(measurement.speed_mps, 365.8)
        self.assertAlmostEqual(measurement.delta_avg_fps, 5.2)
        self.assertAlmostEqual(measurement.delta_avg_mps, 1.6)
        self.assertAlmostEqual(measurement.ke_ft_lb, 368.5)
        self.assertAlmostEqual(measurement.ke_j, 499.2)
        self.assertAlmostEqual(measurement.power_factor, 138.1)
        self.assertAlmostEqual(measurement.power_factor_kgms, 62.7)
        self.assertTrue(measurement.clean_bore)
        self.assertFalse(measurement.cold_bore)
        self.assertEqual(measurement.shot_notes, "Test note")

    def test_chronograph_measurement_from_supabase_records(self):
        """Test creating multiple ChronographMeasurement objects from records"""
        records = [
            self.sample_measurement_record,
            {**self.sample_measurement_record, "id": "measurement-2", "shot_number": 2, "speed_fps": 1195.3}
        ]
        
        measurements = ChronographMeasurement.from_supabase_records(records)
        
        self.assertEqual(len(measurements), 2)
        self.assertEqual(measurements[0].id, "measurement-1")
        self.assertEqual(measurements[1].id, "measurement-2")
        self.assertEqual(measurements[1].shot_number, 2)
        self.assertEqual(measurements[1].speed_fps, 1195.3)

    def test_chronograph_measurement_minimal_data(self):
        """Test ChronographMeasurement with minimal required data"""
        minimal_record = {
            "id": "measurement-minimal",
            "user_id": "user-123",
            "chrono_session_id": "session-123",
            "shot_number": 1,
            "speed_fps": 1200.0,
            "datetime_local": "2023-12-01T10:01:00",
        }
        
        measurement = ChronographMeasurement.from_supabase_record(minimal_record)
        
        self.assertEqual(measurement.id, "measurement-minimal")
        self.assertEqual(measurement.speed_fps, 1200.0)
        self.assertEqual(measurement.speed_mps, 0)  # Default value
        self.assertIsNone(measurement.delta_avg_fps)
        self.assertIsNone(measurement.ke_ft_lb)
        self.assertIsNone(measurement.power_factor)
        self.assertIsNone(measurement.clean_bore)
        self.assertIsNone(measurement.cold_bore)
        self.assertIsNone(measurement.shot_notes)

    def test_chronograph_measurement_field_types(self):
        """Test ChronographMeasurement field types"""
        measurement = ChronographMeasurement.from_supabase_record(self.sample_measurement_record)
        
        # Test numeric fields
        self.assertIsInstance(measurement.shot_number, int)
        self.assertIsInstance(measurement.speed_fps, float)
        self.assertIsInstance(measurement.speed_mps, (int, float))
        
        # Test optional numeric fields
        if measurement.delta_avg_fps is not None:
            self.assertIsInstance(measurement.delta_avg_fps, (int, float))
        if measurement.ke_ft_lb is not None:
            self.assertIsInstance(measurement.ke_ft_lb, (int, float))
        if measurement.power_factor is not None:
            self.assertIsInstance(measurement.power_factor, (int, float))
        
        # Test boolean fields
        if measurement.clean_bore is not None:
            self.assertIsInstance(measurement.clean_bore, bool)
        if measurement.cold_bore is not None:
            self.assertIsInstance(measurement.cold_bore, bool)
        
        # Test string fields
        if measurement.shot_notes is not None:
            self.assertIsInstance(measurement.shot_notes, str)
        
        # Test datetime field
        self.assertIsInstance(measurement.datetime_local, pd.Timestamp)


class TestChronographSourceModels(unittest.TestCase):
    """Test ChronographSource model"""

    def setUp(self):
        self.sample_source_record = {
            "id": "source-123",
            "user_id": "user-456",
            "name": "Garmin Xero C1 Pro",
            "source_type": "chronograph",
            "device_name": "Garmin Xero C1 Pro",
            "make": "Garmin",
            "model": "Xero C1 Pro",
            "serial_number": "ABC123456",
            "created_at": "2023-12-01T10:00:00",
            "updated_at": "2023-12-01T10:05:00"
        }

    def test_chronograph_source_from_supabase_record(self):
        """Test creating ChronographSource from Supabase record"""
        source = ChronographSource.from_supabase_record(self.sample_source_record)
        
        self.assertEqual(source.id, "source-123")
        self.assertEqual(source.user_id, "user-456")
        self.assertEqual(source.name, "Garmin Xero C1 Pro")
        self.assertEqual(source.source_type, "chronograph")
        self.assertEqual(source.device_name, "Garmin Xero C1 Pro")
        self.assertEqual(source.make, "Garmin")
        self.assertEqual(source.model, "Xero C1 Pro")
        self.assertEqual(source.serial_number, "ABC123456")
        self.assertIsInstance(source.created_at, pd.Timestamp)
        self.assertIsInstance(source.updated_at, pd.Timestamp)

    def test_chronograph_source_from_supabase_records(self):
        """Test creating multiple ChronographSource objects from records"""
        records = [
            self.sample_source_record,
            {**self.sample_source_record, "id": "source-456", "name": "LabRadar", "make": "LabRadar"}
        ]
        
        sources = ChronographSource.from_supabase_records(records)
        
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0].id, "source-123")
        self.assertEqual(sources[1].id, "source-456")
        self.assertEqual(sources[1].name, "LabRadar")
        self.assertEqual(sources[1].make, "LabRadar")

    def test_chronograph_source_display_methods(self):
        """Test ChronographSource display methods"""
        source = ChronographSource.from_supabase_record(self.sample_source_record)
        
        # Test display_name
        self.assertEqual(source.display_name(), "Garmin Xero C1 Pro")
        
        # Test device_display with make and model
        expected_device = "Garmin Xero C1 Pro (S/N: ABC123456)"
        self.assertEqual(source.device_display(), expected_device)
        
        # Test short_display
        expected_short = "Garmin Xero C1 Pro - Garmin Xero C1 Pro (S/N: ABC123456)"
        self.assertEqual(source.short_display(), expected_short)

    def test_chronograph_source_device_display_variations(self):
        """Test device_display with different data combinations"""
        # Test with only device_name
        record_device_only = {**self.sample_source_record, "make": None, "model": None, "serial_number": None}
        source = ChronographSource.from_supabase_record(record_device_only)
        self.assertEqual(source.device_display(), "Garmin Xero C1 Pro")
        
        # Test with only model
        record_model_only = {**self.sample_source_record, "make": None, "device_name": None, "serial_number": None}
        source = ChronographSource.from_supabase_record(record_model_only)
        self.assertEqual(source.device_display(), "Xero C1 Pro")
        
        # Test with unknown device
        record_unknown = {**self.sample_source_record, "make": None, "model": None, "device_name": None, "serial_number": None}
        source = ChronographSource.from_supabase_record(record_unknown)
        self.assertEqual(source.device_display(), "Unknown Device")

    def test_chronograph_source_minimal_data(self):
        """Test ChronographSource with minimal required data"""
        minimal_record = {
            "id": "source-minimal",
            "user_id": "user-123",
            "name": "Test Source"
        }
        
        source = ChronographSource.from_supabase_record(minimal_record)
        
        self.assertEqual(source.id, "source-minimal")
        self.assertEqual(source.name, "Test Source")
        self.assertEqual(source.source_type, "chronograph")  # Default value
        self.assertIsNone(source.device_name)
        self.assertIsNone(source.make)
        self.assertIsNone(source.model)
        self.assertIsNone(source.serial_number)


class TestChronographIntegration(unittest.TestCase):
    """Integration tests for chronograph module components"""

    def setUp(self):
        self.mock_supabase = Mock()
        self.service = ChronographService(self.mock_supabase)
        self.user_id = "google-oauth2|111273793361054745867"

    def test_real_world_session_processing_workflow(self):
        """Test a complete session processing workflow"""
        # Step 1: Create session
        session_data = {
            "id": str(uuid.uuid4()),
            "user_id": self.user_id,
            "tab_name": "9mm_test_2024",
            "session_name": "9mm Federal HST 124gr",
            "bullet_type": "9mm HST",
            "bullet_grain": 124.0,
            "datetime_local": datetime.now(timezone.utc).isoformat(),
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "file_path": "/uploads/garmin_9mm_test.xlsx",
            "shot_count": 0,
        }

        # Mock session creation
        mock_response = Mock()
        mock_response.data = [session_data]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        result_id = self.service.create_measurement(session_data)
        
        self.assertEqual(result_id, session_data["id"])

    def test_measurement_stats_calculation_workflow(self):
        """Test measurement statistics calculation workflow"""
        session_id = "session-123"
        
        # Mock speed data for stats calculation
        speed_data = [
            {"speed_fps": 1150.0},
            {"speed_fps": 1155.0},
            {"speed_fps": 1148.0},
            {"speed_fps": 1152.0},
            {"speed_fps": 1149.0}
        ]
        
        mock_response = Mock()
        mock_response.data = speed_data
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        # Mock stats update
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()
        
        speeds = self.service.get_measurements_for_stats(self.user_id, session_id)
        expected_speeds = [1150.0, 1155.0, 1148.0, 1152.0, 1149.0]
        
        self.assertEqual(speeds, expected_speeds)

    def test_session_with_measurements_integration(self):
        """Test session and measurements integration"""
        session_id = "integration-session-123"
        
        # Mock session data
        session_data = {
            "id": session_id,
            "user_id": self.user_id,
            "tab_name": "Integration Test",
            "session_name": "Integration Test Session",
            "datetime_local": "2023-12-01T10:00:00",
            "uploaded_at": "2023-12-01T10:05:00",
            "file_path": "/uploads/test.xlsx",
            "shot_count": 3,
            "avg_speed_fps": 1150.0
        }
        
        # Mock measurement data
        measurements_data = [
            {
                "id": "measurement-1",
                "user_id": self.user_id,
                "chrono_session_id": session_id,
                "shot_number": 1,
                "speed_fps": 1145.0,
                "datetime_local": "2023-12-01T10:01:00"
            },
            {
                "id": "measurement-2",
                "user_id": self.user_id,
                "chrono_session_id": session_id,
                "shot_number": 2,
                "speed_fps": 1150.0,
                "datetime_local": "2023-12-01T10:02:00"
            },
            {
                "id": "measurement-3",
                "user_id": self.user_id,
                "chrono_session_id": session_id,
                "shot_number": 3,
                "speed_fps": 1155.0,
                "datetime_local": "2023-12-01T10:03:00"
            }
        ]
        
        # Mock session retrieval
        mock_session_response = Mock()
        mock_session_response.data = session_data
        
        # Mock measurements retrieval
        mock_measurements_response = Mock()
        mock_measurements_response.data = measurements_data
        
        # Setup mock chain for session
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_session_response
        
        # Setup mock chain for measurements
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = mock_measurements_response
        
        # Get session
        session = self.service.get_session_by_id(session_id, self.user_id)
        self.assertIsNotNone(session)
        self.assertEqual(session.shot_count, 3)
        self.assertTrue(session.has_measurements())
        
        # Get measurements
        measurements = self.service.get_measurements_for_session(self.user_id, session_id)
        self.assertEqual(len(measurements), 3)
        self.assertEqual(measurements[0].shot_number, 1)
        self.assertEqual(measurements[2].speed_fps, 1155.0)

    def test_chronograph_source_integration(self):
        """Test chronograph source integration with service"""
        # Mock source data
        source_data = {
            "id": "source-123",
            "user_id": self.user_id,
            "name": "Test Chronograph",
            "source_type": "chronograph",
            "make": "Test Make",
            "model": "Test Model",
            "serial_number": "TEST123"
        }
        
        # Mock source retrieval
        mock_response = Mock()
        mock_response.data = source_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        
        source = self.service.get_source_by_id("source-123", self.user_id)
        
        self.assertIsNotNone(source)
        self.assertEqual(source.name, "Test Chronograph")
        self.assertEqual(source.make, "Test Make")
        self.assertEqual(source.model, "Test Model")
        self.assertEqual(source.serial_number, "TEST123")

    def test_error_propagation_integration(self):
        """Test error propagation through service layers"""
        # Test database connection error
        self.mock_supabase.table.side_effect = Exception("Database connection failed")
        
        with self.assertRaises(Exception) as context:
            self.service.get_sessions_for_user(self.user_id)
        
        self.assertIn("Error fetching sessions", str(context.exception))
        self.assertIn("Database connection failed", str(context.exception))

    def test_bulk_data_processing(self):
        """Test processing bulk chronograph data"""
        # Simulate bulk session data
        bulk_sessions = []
        for i in range(5):
            session_data = {
                "id": f"session-{i}",
                "user_id": self.user_id,
                "tab_name": f"Test_{i}",
                "session_name": f"Test Session {i}",
                "datetime_local": f"2023-12-0{i+1}T10:00:00",
                "uploaded_at": f"2023-12-0{i+1}T10:05:00",
                "file_path": f"/uploads/test_{i}.xlsx",
                "shot_count": (i+1) * 5,
                "avg_speed_fps": 1150.0 + (i * 10)
            }
            bulk_sessions.append(session_data)
        
        # Mock bulk session retrieval
        mock_response = Mock()
        mock_response.data = bulk_sessions
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        sessions = self.service.get_sessions_for_user(self.user_id)
        
        self.assertEqual(len(sessions), 5)
        self.assertEqual(sessions[0].session_name, "Test Session 0")
        self.assertEqual(sessions[4].avg_speed_fps, 1190.0)
        self.assertEqual(sessions[2].shot_count, 15)

    def test_filtered_sessions_integration(self):
        """Test filtered session retrieval integration"""
        filtered_data = [
            {
                "id": "filtered-session-1",
                "user_id": self.user_id,
                "tab_name": "9mm Filter Test",
                "session_name": "9mm Filtered Session",
                "datetime_local": "2023-12-01T10:00:00",
                "uploaded_at": "2023-12-01T10:05:00",
                "file_path": "/uploads/filtered.xlsx",
                "shot_count": 10,
                "bullet_type": "9mm FMJ"
            }
        ]
        
        # Mock filtered query response
        mock_response = Mock()
        mock_response.data = filtered_data
        
        # Setup complex mock chain for filtered query
        mock_table = Mock()
        mock_select = Mock()
        mock_eq1 = Mock()
        mock_eq2 = Mock()
        mock_gte = Mock()
        mock_lte = Mock()
        mock_order = Mock()
        
        self.mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq1
        mock_eq1.eq.return_value = mock_eq2
        mock_eq2.gte.return_value = mock_gte
        mock_gte.lte.return_value = mock_lte
        mock_lte.order.return_value = mock_order
        mock_order.execute.return_value = mock_response
        
        sessions = self.service.get_sessions_filtered(
            user_id=self.user_id,
            bullet_type="9mm FMJ",
            start_date="2023-12-01",
            end_date="2023-12-31"
        )
        
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].session_name, "9mm Filtered Session")


class TestChronographPageStructure(unittest.TestCase):
    """Test the chronograph page structure and configuration"""

    def test_chronograph_page_exists(self):
        """Test that the chronograph page file exists"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "3_Chronograph.py"
        )
        self.assertTrue(os.path.exists(page_path), "Chronograph page should exist")

    def test_chronograph_page_has_required_imports(self):
        """Test that chronograph page has required imports"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "3_⏱️_Chronograph.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            required_imports = [
                "streamlit",
                "handle_auth",
                "create_client",
                "render_chronograph_import_tab",
            ]
            for required_import in required_imports:
                self.assertIn(
                    required_import,
                    content,
                    f"Chronograph page should import {required_import}",
                )

    def test_chronograph_page_has_correct_tabs(self):
        """Test that chronograph page has expected tabs"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "3_⏱️_Chronograph.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            expected_tabs = ["Import", "View", "Edit", "My Files"]
            for tab in expected_tabs:
                self.assertIn(
                    f'"{tab}"', content, f"Chronograph page should have {tab} tab"
                )

    def test_chronograph_page_configuration(self):
        """Test chronograph page configuration"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "3_⏱️_Chronograph.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            self.assertIn('page_title="Chronograph"', content)
            self.assertIn('page_icon="📁"', content)
            self.assertIn('layout="wide"', content)


if __name__ == "__main__":
    unittest.main()
