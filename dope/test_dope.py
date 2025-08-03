import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timezone
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dope.dope_model import DopeModel
from dope.create_session_tab import render_create_session_tab


class TestDopeModel(unittest.TestCase):

    def setUp(self):
        self.model = DopeModel()
        self.test_tab = "test_tab"

    def test_get_all_tabs(self):
        # Initially should be empty
        tabs = self.model.get_all_tabs()
        self.assertEqual(len(tabs), 0)

        # Add some data to a tab
        self.model.set_chronograph_data(self.test_tab, {"session_id": "test-session"})

        tabs = self.model.get_all_tabs()
        self.assertEqual(len(tabs), 1)
        self.assertIn(self.test_tab, tabs)

    def test_set_and_get_chronograph_data(self):
        test_data = {
            "session_id": "test-session",
            "bullet_type": "9mm FMJ",
            "avg_speed": 1200.5,
        }

        # Set data
        self.model.set_chronograph_data(self.test_tab, test_data)

        # Get data
        retrieved_data = self.model.get_chronograph_data(self.test_tab)
        self.assertEqual(retrieved_data, test_data)

    def test_set_and_get_weather_data(self):
        test_data = {"log_id": "weather-log-1", "temperature": 72.5, "humidity": 65}

        # Set data
        self.model.set_weather_data(self.test_tab, test_data)

        # Get data
        retrieved_data = self.model.get_weather_data(self.test_tab)
        self.assertEqual(retrieved_data, test_data)

    def test_set_and_get_range_data(self):
        test_data = {
            "range_id": "range-1",
            "distance_yards": 100,
            "elevation_angle": 2.5,
        }

        # Set data
        self.model.set_range_data(self.test_tab, test_data)

        # Get data
        retrieved_data = self.model.get_range_data(self.test_tab)
        self.assertEqual(retrieved_data, test_data)

    def test_set_and_get_rifle_data(self):
        test_data = {
            "rifle_id": "rifle-1",
            "make": "Remington",
            "model": "700",
            "caliber": ".308 Winchester",
        }

        # Set data
        self.model.set_rifle_data(self.test_tab, test_data)

        # Get data
        retrieved_data = self.model.get_rifle_data(self.test_tab)
        self.assertEqual(retrieved_data, test_data)

    def test_set_and_get_ammo_data(self):
        test_data = {
            "ammo_id": "ammo-1",
            "make": "Federal",
            "model": "Gold Medal",
            "grain": 168,
        }

        # Set data
        self.model.set_ammo_data(self.test_tab, test_data)

        # Get data
        retrieved_data = self.model.get_ammo_data(self.test_tab)
        self.assertEqual(retrieved_data, test_data)

    def test_clear_tab_data(self):
        # Add data to multiple categories
        self.model.set_chronograph_data(self.test_tab, {"session_id": "test"})
        self.model.set_weather_data(self.test_tab, {"log_id": "test"})
        self.model.set_range_data(self.test_tab, {"range_id": "test"})

        # Verify data exists
        self.assertIsNotNone(self.model.get_chronograph_data(self.test_tab))
        self.assertIsNotNone(self.model.get_weather_data(self.test_tab))
        self.assertIsNotNone(self.model.get_range_data(self.test_tab))

        # Clear tab data
        self.model.clear_tab_data(self.test_tab)

        # Verify data is cleared
        self.assertIsNone(self.model.get_chronograph_data(self.test_tab))
        self.assertIsNone(self.model.get_weather_data(self.test_tab))
        self.assertIsNone(self.model.get_range_data(self.test_tab))

    def test_is_tab_complete(self):
        # Initially incomplete
        self.assertFalse(self.model.is_tab_complete(self.test_tab))

        # Add required data
        self.model.set_chronograph_data(self.test_tab, {"session_id": "test"})
        self.model.set_range_data(self.test_tab, {"range_id": "test"})
        self.model.set_rifle_data(self.test_tab, {"rifle_id": "test"})
        self.model.set_ammo_data(self.test_tab, {"ammo_id": "test"})

        # Should be complete now
        self.assertTrue(self.model.is_tab_complete(self.test_tab))

    def test_get_tab_summary(self):
        # Set some data
        self.model.set_chronograph_data(self.test_tab, {"bullet_type": "9mm FMJ"})
        self.model.set_range_data(self.test_tab, {"distance_yards": 25})

        summary = self.model.get_tab_summary(self.test_tab)

        self.assertIsInstance(summary, dict)
        self.assertIn("chronograph", summary)
        self.assertIn("range", summary)
        self.assertEqual(summary["chronograph"]["bullet_type"], "9mm FMJ")
        self.assertEqual(summary["range"]["distance_yards"], 25)


class TestDopeCreateSessionTab(unittest.TestCase):

    @patch("streamlit.subheader")
    @patch("streamlit.info")
    def test_render_create_session_tab_basic(self, mock_info, mock_subheader):
        user = {"email": "test@example.com", "name": "Test User"}
        mock_supabase = Mock()

        # Mock the various service calls that might be made
        with patch(
            "chronograph.service.ChronographService"
        ) as mock_chrono_service, patch(
            "weather.service.WeatherService"
        ) as mock_weather_service:

            mock_chrono_instance = Mock()
            mock_chrono_service.return_value = mock_chrono_instance
            mock_chrono_instance.get_sessions_for_user.return_value = []

            mock_weather_instance = Mock()
            mock_weather_service.return_value = mock_weather_instance
            mock_weather_instance.get_logs_for_user.return_value = []

            # This would normally render the tab content
            # We're just testing that it doesn't crash
            result = render_create_session_tab(user, mock_supabase)

            # The function doesn't return anything by default
            self.assertIsNone(result)


class TestDopePageStructure(unittest.TestCase):
    """Test the DOPE page structure and configuration"""

    def test_dope_page_exists(self):
        """Test that the DOPE page file exists"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "2_📊_DOPE.py"
        )
        self.assertTrue(os.path.exists(page_path), "DOPE page should exist")

    def test_dope_page_has_required_imports(self):
        """Test that DOPE page has required imports"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "2_📊_DOPE.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            required_imports = [
                "streamlit",
                "handle_auth",
                "create_client",
                "render_create_session_tab",
            ]
            for required_import in required_imports:
                self.assertIn(
                    required_import,
                    content,
                    f"DOPE page should import {required_import}",
                )

    def test_dope_page_has_correct_tabs(self):
        """Test that DOPE page has expected tabs"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "2_📊_DOPE.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            expected_tabs = ["Create", "View", "Analytics"]
            for tab in expected_tabs:
                self.assertIn(f'"{tab}"', content, f"DOPE page should have {tab} tab")

    def test_dope_page_configuration(self):
        """Test DOPE page configuration"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "2_📊_DOPE.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            self.assertIn('page_title="DOPE"', content)
            self.assertIn('page_icon="📊"', content)
            self.assertIn('layout="wide"', content)

    def test_dope_page_handles_session_state(self):
        """Test that DOPE page properly handles session state management"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "2_📊_DOPE.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            # Should handle tab state management
            self.assertIn("dope_tab_create_visited", content)
            self.assertIn("dope_tab_view_visited", content)
            self.assertIn("dope_tab_sessions_visited", content)

            # Should clear DOPE model data on tab switches
            self.assertIn("dope_model", content)
            self.assertIn("clear_tab_data", content)


class TestDopeSessionManagement(unittest.TestCase):
    """Test DOPE session management functionality"""

    def test_dope_model_session_isolation(self):
        """Test that different tabs maintain separate data"""
        model = DopeModel()

        tab1 = "session_1"
        tab2 = "session_2"

        # Set different data for each tab
        model.set_chronograph_data(tab1, {"session_id": "chrono-1"})
        model.set_chronograph_data(tab2, {"session_id": "chrono-2"})

        model.set_range_data(tab1, {"range_id": "range-1"})
        model.set_range_data(tab2, {"range_id": "range-2"})

        # Verify data isolation
        self.assertEqual(model.get_chronograph_data(tab1)["session_id"], "chrono-1")
        self.assertEqual(model.get_chronograph_data(tab2)["session_id"], "chrono-2")

        self.assertEqual(model.get_range_data(tab1)["range_id"], "range-1")
        self.assertEqual(model.get_range_data(tab2)["range_id"], "range-2")

        # Clear one tab shouldn't affect the other
        model.clear_tab_data(tab1)

        self.assertIsNone(model.get_chronograph_data(tab1))
        self.assertIsNotNone(model.get_chronograph_data(tab2))


if __name__ == "__main__":
    unittest.main()
