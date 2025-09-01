import os
import sys
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

import pandas as pd

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chronograph.import_tab import render_chronograph_import_tab
from chronograph.models import ChronographMeasurement, ChronographSession
from chronograph.service import ChronographService


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


class TestChronographModels(unittest.TestCase):



    def test_chronograph_measurement_from_supabase_record(self):
        record = {
            "id": "measurement-1",
            "user_id": "google-oauth2|111273793361054745867",
            "chrono_session_id": "session-1",
            "shot_number": 1,
            "speed_fps": 1200.5,
            "datetime_local": "2023-12-01T10:01:00",
            "delta_avg_fps": 5.2,
            "ke_ft_lb": 368.5,
            "power_factor": 138.1,
            "clean_bore": True,
            "cold_bore": False,
            "shot_notes": "Test note",
        }

        measurement = ChronographMeasurement.from_supabase_record(record)

        self.assertEqual(measurement.id, "measurement-1")
        self.assertEqual(measurement.shot_number, 1)
        self.assertAlmostEqual(measurement.speed_fps, 1200.5)
        self.assertAlmostEqual(measurement.delta_avg_fps, 5.2)
        self.assertTrue(measurement.clean_bore)
        self.assertFalse(measurement.cold_bore)
        self.assertEqual(measurement.shot_notes, "Test note")




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
