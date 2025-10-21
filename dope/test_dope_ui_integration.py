"""
Integration tests for DOPE UI to API layer.

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

from dope.api import DopeAPI
from dope.filters import DopeSessionFilter
from dope.models import DopeMeasurementModel, DopeSessionModel


class TestDopeUIIntegration(unittest.TestCase):
    """Test UI to API integration for DOPE module"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.dope_api = DopeAPI(self.mock_supabase)
        self.test_user_id = "test-user-123"

    # -------------------------------------------------------------------------
    # Session Management - View Page Uses These
    # -------------------------------------------------------------------------

    def test_view_page_can_get_sessions_for_user(self):
        """Test that view_page can call get_sessions_for_user() correctly"""
        # view_page.py line 563: sessions = service.get_sessions_for_user(user_id)
        try:
            # Mock the service method
            self.dope_api._service.get_sessions_for_user = MagicMock(return_value=[])

            result = self.dope_api.get_sessions_for_user(self.test_user_id)

            # Should return a list
            self.assertIsInstance(result, list)
        except AttributeError as e:
            self.fail(f"API method call failed: {e}")

    def test_view_page_can_search_sessions(self):
        """Test that view_page can call search_sessions() correctly"""
        # view_page.py line 561: sessions = service.search_sessions(user_id, filters["search"])
        try:
            # Mock the service method
            self.dope_api._service.search_sessions = MagicMock(return_value=[])

            result = self.dope_api.search_sessions(
                user_id=self.test_user_id, search_term="308 Winchester"
            )

            # Should return a list
            self.assertIsInstance(result, list)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_view_page_can_filter_sessions(self):
        """Test that view_page can call filter_sessions() correctly"""
        # view_page.py line 566: sessions = service.filter_sessions(user_id, filters)
        try:
            # Mock the service method
            self.dope_api._service.filter_sessions = MagicMock(return_value=[])

            # DopeSessionFilter actually takes a dict, not keyword arguments
            filters = {"cartridge_type": "308 Winchester", "rifle_name": "Test Rifle"}
            result = self.dope_api.filter_sessions(
                user_id=self.test_user_id, filters=filters
            )

            # Should return a list
            self.assertIsInstance(result, list)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_view_page_can_get_unique_values(self):
        """Test that view_page can call get_unique_values() correctly"""
        # view_page.py lines 204-210: Multiple calls to get_unique_values
        try:
            # Mock the service method
            self.dope_api._service.get_unique_values = MagicMock(return_value=[])

            # Test each field that view_page requests
            fields = [
                "rifle_name",
                "cartridge_type",
                "cartridge_make",
                "bullet_make",
                "range_name",
            ]
            for field_name in fields:
                result = self.dope_api.get_unique_values(
                    user_id=self.test_user_id, field_name=field_name
                )
                self.assertIsInstance(result, list)

        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_view_page_can_get_edit_dropdown_options(self):
        """Test that view_page can call get_edit_dropdown_options() correctly"""
        # view_page.py line 831: dropdown_options = service.get_edit_dropdown_options(user_id)
        try:
            # Mock the service method
            self.dope_api._service.get_edit_dropdown_options = MagicMock(
                return_value={}
            )

            result = self.dope_api.get_edit_dropdown_options(self.test_user_id)

            # Should return a dict
            self.assertIsInstance(result, dict)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_view_page_can_update_session(self):
        """Test that view_page can call update_session() correctly"""
        # view_page.py line 999: updated_session = service.update_session(session.id, update_data, user_id)
        try:
            # Mock the service method
            mock_session = DopeSessionModel(
                id="session-123",
                user_id=self.test_user_id,
                session_name="Test Session",
                cartridge_type="308 Winchester",
                rifle_name="Test Rifle",
            )
            self.dope_api._service.update_session = MagicMock(return_value=mock_session)

            update_data = {"notes": "Updated notes"}
            result = self.dope_api.update_session(
                session_id="session-123",
                session_data=update_data,
                user_id=self.test_user_id,
            )

            # Should return a DopeSessionModel or None
            self.assertTrue(result is None or isinstance(result, DopeSessionModel))
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_view_page_can_delete_session(self):
        """Test that view_page can call delete_session() correctly"""
        # view_page.py line 1064, 1133: success = service.delete_session(session.id, user_id)
        try:
            # Mock the service method
            self.dope_api._service.delete_session = MagicMock(return_value=True)

            result = self.dope_api.delete_session(
                session_id="session-123", user_id=self.test_user_id
            )

            # Should return a boolean
            self.assertIsInstance(result, bool)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_view_page_can_get_measurements_for_session(self):
        """Test that view_page can call get_measurements_for_dope_session() correctly"""
        # view_page.py lines 1040, 1164, 1532: measurements = service.get_measurements_for_dope_session(session.id, user_id)
        try:
            # Mock the service method
            self.dope_api._service.get_measurements_for_dope_session = MagicMock(
                return_value=[]
            )

            result = self.dope_api.get_measurements_for_dope_session(
                dope_session_id="session-123", user_id=self.test_user_id
            )

            # Should return a list
            self.assertIsInstance(result, list)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_view_page_can_update_measurement(self):
        """Test that view_page can call update_measurement() correctly"""
        # view_page.py lines 1882, 1947: service.update_measurement(measurement.id, update_data, user_id)
        try:
            # Mock the service method
            mock_measurement = DopeMeasurementModel(
                id="meas-123",
                user_id=self.test_user_id,
                dope_session_id="session-123",
                shot_number=1,
                speed_mps=792.5,
            )
            self.dope_api._service.update_measurement = MagicMock(
                return_value=mock_measurement
            )

            update_data = {"shot_notes": "Test note"}
            result = self.dope_api.update_measurement(
                measurement_id="meas-123",
                measurement_data=update_data,
                user_id=self.test_user_id,
            )

            # Should return a DopeMeasurementModel or None
            self.assertTrue(result is None or isinstance(result, DopeMeasurementModel))
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    # -------------------------------------------------------------------------
    # Session Management - Business Layer Uses These
    # -------------------------------------------------------------------------

    def test_business_can_create_session(self):
        """Test that business layer can call create_session() correctly"""
        # business.py line 165: return self.dope_service.create_session(session_data, user_id)
        try:
            # Mock the service method
            mock_session = DopeSessionModel(
                id="session-123",
                user_id=self.test_user_id,
                session_name="Test Session",
                cartridge_type="308 Winchester",
                rifle_name="Test Rifle",
            )
            self.dope_api._service.create_session = MagicMock(return_value=mock_session)

            session_data = {
                "session_name": "Test Session",
                "cartridge_id": "cart-123",
                "rifle_id": "rifle-123",
                "chrono_session_id": "chrono-123",
                "range_submission_id": "range-123",
            }
            result = self.dope_api.create_session(
                session_data=session_data, user_id=self.test_user_id
            )

            # Should return a DopeSessionModel
            self.assertIsInstance(result, DopeSessionModel)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    # -------------------------------------------------------------------------
    # Model Field Tests
    # -------------------------------------------------------------------------

    def test_dope_session_model_has_required_fields(self):
        """Test that DopeSessionModel has all fields the UI expects"""
        session = DopeSessionModel(
            id="session-123",
            user_id=self.test_user_id,
            session_name="Test Session",
            cartridge_type="308 Winchester",
            rifle_name="Test Rifle",
            chrono_session_id="chrono-123",
            cartridge_id="cart-123",
            rifle_id="rifle-123",
            bullet_id="bullet-123",
            range_submission_id="range-123",
        )

        try:
            # UI accesses these fields directly
            self.assertEqual(session.id, "session-123")
            self.assertEqual(session.session_name, "Test Session")
            self.assertEqual(session.cartridge_type, "308 Winchester")
            self.assertEqual(session.rifle_name, "Test Rifle")

            # Check optional fields exist (may be None)
            _ = session.notes
            _ = session.range_name
            _ = session.range_distance_m
            _ = session.temperature_c_median
            _ = session.barometric_pressure_hpa_median
            _ = session.wind_speed_mps_median

        except AttributeError as e:
            self.fail(f"DopeSessionModel missing required field: {e}")

    def test_dope_measurement_model_has_required_fields(self):
        """Test that DopeMeasurementModel has all fields the UI expects"""
        measurement = DopeMeasurementModel(
            id="meas-123",
            user_id=self.test_user_id,
            dope_session_id="session-123",
            shot_number=1,
            speed_mps=792.5,
        )

        try:
            # UI accesses these fields directly
            self.assertEqual(measurement.id, "meas-123")
            self.assertEqual(measurement.shot_number, 1)
            self.assertEqual(measurement.speed_mps, 792.5)

            # Check optional fields exist (may be None)
            _ = measurement.ke_j
            _ = measurement.power_factor_kgms  # Correct field name
            _ = measurement.temperature_c
            _ = measurement.shot_notes

        except AttributeError as e:
            self.fail(f"DopeMeasurementModel missing required field: {e}")

    # -------------------------------------------------------------------------
    # Additional API Method Tests
    # -------------------------------------------------------------------------

    def test_api_has_get_session_by_id(self):
        """Test that API has get_session_by_id method (not currently used but may be needed)"""
        try:
            # Mock the service method
            self.dope_api._service.get_session_by_id = MagicMock(return_value=None)

            result = self.dope_api.get_session_by_id(
                session_id="session-123", user_id=self.test_user_id
            )

            # Should return DopeSessionModel or None
            self.assertTrue(result is None or isinstance(result, DopeSessionModel))
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_api_has_get_session_statistics(self):
        """Test that API has get_session_statistics method (for analytics page)"""
        try:
            # Mock the service method
            self.dope_api._service.get_session_statistics = MagicMock(return_value={})

            result = self.dope_api.get_session_statistics(self.test_user_id)

            # Should return a dict
            self.assertIsInstance(result, dict)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_api_has_delete_sessions_bulk(self):
        """Test that API has delete_sessions_bulk method (for future bulk operations)"""
        try:
            # Mock the service method
            self.dope_api._service.delete_sessions_bulk = MagicMock(
                return_value={"deleted_count": 2, "failed_ids": []}
            )

            result = self.dope_api.delete_sessions_bulk(
                session_ids=["id1", "id2"], user_id=self.test_user_id
            )

            # Should return a dict
            self.assertIsInstance(result, dict)
            self.assertIn("deleted_count", result)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_api_has_create_measurement(self):
        """Test that API has create_measurement method (for manual measurement entry)"""
        try:
            # Mock the service method
            mock_measurement = DopeMeasurementModel(
                id="meas-123",
                user_id=self.test_user_id,
                dope_session_id="session-123",
                shot_number=1,
                speed_mps=792.5,
            )
            self.dope_api._service.create_measurement = MagicMock(
                return_value=mock_measurement
            )

            measurement_data = {
                "dope_session_id": "session-123",
                "shot_number": 1,
                "speed_mps": 792.5,
            }
            result = self.dope_api.create_measurement(
                measurement_data=measurement_data, user_id=self.test_user_id
            )

            # Should return a DopeMeasurementModel
            self.assertIsInstance(result, DopeMeasurementModel)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_api_has_delete_measurement(self):
        """Test that API has delete_measurement method (for measurement deletion)"""
        try:
            # Mock the service method
            self.dope_api._service.delete_measurement = MagicMock(return_value=True)

            result = self.dope_api.delete_measurement(
                measurement_id="meas-123", user_id=self.test_user_id
            )

            # Should return a boolean
            self.assertIsInstance(result, bool)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    # -------------------------------------------------------------------------
    # Return Type Tests
    # -------------------------------------------------------------------------

    def test_get_sessions_for_user_returns_dope_session_models(self):
        """Test that get_sessions_for_user returns DopeSessionModel instances not dicts"""
        # Ensures UI gets model instances with properties, not raw dicts
        try:
            # Mock the service method
            mock_session = DopeSessionModel(
                id="session-123",
                user_id=self.test_user_id,
                session_name="Test Session",
                cartridge_type="308 Winchester",
                rifle_name="Test Rifle",
            )
            self.dope_api._service.get_sessions_for_user = MagicMock(
                return_value=[mock_session]
            )

            result = self.dope_api.get_sessions_for_user(self.test_user_id)

            # Should return list of DopeSessionModel instances
            self.assertIsInstance(result, list)
            if len(result) > 0:
                self.assertIsInstance(result[0], DopeSessionModel)
                # UI expects to access properties
                self.assertEqual(result[0].session_name, "Test Session")

        except (AttributeError, TypeError) as e:
            self.fail(f"API method return type incorrect: {e}")

    def test_get_measurements_returns_dope_measurement_models(self):
        """Test that get_measurements_for_dope_session returns DopeMeasurementModel instances"""
        try:
            # Mock the service method
            mock_measurement = DopeMeasurementModel(
                id="meas-123",
                user_id=self.test_user_id,
                dope_session_id="session-123",
                shot_number=1,
                speed_mps=792.5,
            )
            self.dope_api._service.get_measurements_for_dope_session = MagicMock(
                return_value=[mock_measurement]
            )

            result = self.dope_api.get_measurements_for_dope_session(
                dope_session_id="session-123", user_id=self.test_user_id
            )

            # Should return list of DopeMeasurementModel instances
            self.assertIsInstance(result, list)
            if len(result) > 0:
                self.assertIsInstance(result[0], DopeMeasurementModel)
                # UI expects to access properties
                self.assertEqual(result[0].speed_mps, 792.5)

        except (AttributeError, TypeError) as e:
            self.fail(f"API method return type incorrect: {e}")


if __name__ == "__main__":
    unittest.main()
