"""
Integration tests for chronograph UI to API layer.

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

from chronograph.chronograph_session_models import (
    ChronographMeasurement,
    ChronographSession,
)
from chronograph.chronograph_source_models import ChronographSource
from chronograph.client_api import ChronographAPI


class TestChronographUIIntegration(unittest.TestCase):
    """Test UI to API integration for chronograph"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.chrono_api = ChronographAPI(self.mock_supabase)
        self.test_user_id = "test-user-123"

    def test_import_tab_can_get_all_sources(self):
        """Test that import_tab can call get_all_sources() correctly"""
        # import_tab.py calls: chrono_service.get_sources_for_user(user["id"])
        # API has: get_all_sources(user_id)
        try:
            # Mock the service method
            self.chrono_api._service.get_sources_for_user = MagicMock(return_value=[])

            result = self.chrono_api.get_all_sources(self.test_user_id)

            # Should return a list
            self.assertIsInstance(result, list)
        except AttributeError as e:
            self.fail(f"API method call failed: {e}")

    def test_import_tab_can_get_source_by_name(self):
        """Test that import_tab can call get_source_by_name() correctly"""
        # import_tab.py calls: chrono_service.get_source_by_name()
        # API has: get_source_by_name(user_id, name)
        try:
            # Mock the service method
            self.chrono_api._service.get_source_by_name = MagicMock(return_value=None)

            result = self.chrono_api.get_source_by_name(
                user_id=self.test_user_id,
                name="Test Chronograph"
            )

            # Should return None (or a ChronographSource)
            self.assertTrue(result is None or isinstance(result, ChronographSource))
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_import_tab_can_create_source(self):
        """Test that import_tab can call create_source() correctly"""
        # import_tab.py calls: chrono_service.create_source()
        # API has: create_source(source_data, user_id)
        source_data = {
            "name": "Test Garmin Xero",
            "device_name": "Garmin Xero C1 Pro",
            "model": "C1 Pro"
        }

        try:
            # Mock the service method to return a ChronographSource
            mock_source = ChronographSource(
                id="source-123",
                user_id=self.test_user_id,
                name="Test Garmin Xero",
                source_type="chronograph"
            )
            self.chrono_api._service.create_source = MagicMock(return_value="source-123")
            self.chrono_api._service.get_source_by_id = MagicMock(return_value=mock_source)

            result = self.chrono_api.create_source(source_data, self.test_user_id)

            # Should return a ChronographSource
            self.assertIsInstance(result, ChronographSource)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_import_tab_can_get_source_by_id(self):
        """Test that import_tab can call get_source_by_id() correctly"""
        # import_tab.py calls: chrono_service.get_source_by_id()
        # API has: get_source_by_id(source_id, user_id)
        try:
            # Mock the service method
            self.chrono_api._service.get_source_by_id = MagicMock(return_value=None)

            result = self.chrono_api.get_source_by_id("source-123", self.test_user_id)

            # Should return None (or a ChronographSource)
            self.assertTrue(result is None or isinstance(result, ChronographSource))
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_chronograph_source_model_has_required_fields(self):
        """Test that ChronographSource has all fields the UI expects"""
        source = ChronographSource(
            id="source-123",
            user_id=self.test_user_id,
            name="Test Garmin Xero",
            source_type="chronograph",
            device_name="Garmin Xero C1 Pro",
            make="Garmin",
            model="C1 Pro"
        )

        try:
            # UI accesses these fields directly
            self.assertEqual(source.id, "source-123")
            self.assertEqual(source.name, "Test Garmin Xero")
            self.assertEqual(source.device_name, "Garmin Xero C1 Pro")
            self.assertEqual(source.model, "C1 Pro")

        except AttributeError as e:
            self.fail(f"ChronographSource missing required field: {e}")

    def test_chronograph_session_model_has_required_fields(self):
        """Test that ChronographSession has all fields the UI expects"""
        session = ChronographSession(
            id="session-123",
            user_id=self.test_user_id,
            chronograph_source_id="source-123",
            tab_name="168gr HPBT",
            session_name="Range Day 1",
            datetime_local=datetime.now(),
            uploaded_at=datetime.now(),
            file_path="/path/to/file.csv"
        )

        try:
            # UI accesses these fields directly
            self.assertEqual(session.id, "session-123")
            self.assertEqual(session.tab_name, "168gr HPBT")
            self.assertEqual(session.session_name, "Range Day 1")

        except AttributeError as e:
            self.fail(f"ChronographSession missing required field: {e}")

    def test_chronograph_measurement_model_has_required_fields(self):
        """Test that ChronographMeasurement has all fields the UI expects"""
        measurement = ChronographMeasurement(
            id="measurement-123",
            user_id=self.test_user_id,
            chrono_session_id="session-123",
            shot_number=1,
            speed_mps=792.5,
            datetime_local="2024-01-15T10:00:00"
        )

        try:
            # UI accesses these fields directly
            self.assertEqual(measurement.id, "measurement-123")
            self.assertEqual(measurement.shot_number, 1)
            self.assertEqual(measurement.speed_mps, 792.5)

        except AttributeError as e:
            self.fail(f"ChronographMeasurement missing required field: {e}")

    def test_get_all_sources_returns_chronograph_source_models(self):
        """Test that get_all_sources returns ChronographSource instances not dicts"""
        # Ensures UI gets model instances with properties, not raw dicts
        try:
            # Mock the service method
            mock_source = ChronographSource(
                id="source-123",
                user_id=self.test_user_id,
                name="Test Garmin Xero",
                source_type="chronograph"
            )
            self.chrono_api._service.get_sources_for_user = MagicMock(return_value=[mock_source])

            result = self.chrono_api.get_all_sources(self.test_user_id)

            # Should return list of ChronographSource instances
            self.assertIsInstance(result, list)
            if len(result) > 0:
                self.assertIsInstance(result[0], ChronographSource)
                # UI expects to access properties
                self.assertEqual(result[0].name, "Test Garmin Xero")

        except (AttributeError, TypeError) as e:
            self.fail(f"API method return type incorrect: {e}")


if __name__ == "__main__":
    unittest.main()