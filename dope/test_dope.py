import os
import sys
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

import pandas as pd

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dope.create_session_tab import render_create_session_tab
from dope.dope_model import DopeModel


class TestDopeModel(unittest.TestCase):

    def setUp(self):
        self.model = DopeModel()
        self.test_tab = "test_tab"

    def test_get_all_tabs(self):
        # Initially should be empty
        tabs = self.model.get_all_tabs()
        self.assertEqual(len(tabs), 0)

        # Add some data to a tab (this should create the tab)
        test_data = [{"session_id": "test-session", "velocity": 2800}]
        self.model.set_tab_measurements(self.test_tab, test_data)

        tabs = self.model.get_all_tabs()
        self.assertEqual(len(tabs), 1)
        self.assertIn(self.test_tab, tabs)

    def test_set_and_get_chronograph_data(self):
        test_data = [
            {
                "session_id": "test-session",
                "bullet_type": "9mm FMJ",
                "avg_speed": 1200.5,
            }
        ]

        # Set data
        self.model.set_tab_measurements(self.test_tab, test_data)

        # Get data
        retrieved_df = self.model.get_tab_measurements_df(self.test_tab)
        self.assertIsNotNone(retrieved_df)
        self.assertEqual(len(retrieved_df), 1)
        self.assertEqual(retrieved_df.iloc[0]["session_id"], "test-session")

    def test_set_and_get_session_details(self):
        test_data = {"log_id": "weather-log-1", "temperature": 72.5, "humidity": 65}

        # Set data
        self.model.set_tab_session_details(self.test_tab, test_data)

        # Get data
        retrieved_data = self.model.get_tab_session_details(self.test_tab)
        self.assertEqual(retrieved_data, test_data)

    def test_update_tab_measurements(self):
        # First set initial data
        initial_data = [
            {"shot": 1, "velocity": 2800},
            {"shot": 2, "velocity": 2810},
        ]
        self.model.set_tab_measurements(self.test_tab, initial_data)

        # Create edited DataFrame
        edited_df = pd.DataFrame([
            {"shot": 1, "velocity": 2805},
            {"shot": 2, "velocity": 2815},
            {"shot": 3, "velocity": 2820},
        ])

        # Update measurements
        self.model.update_tab_measurements(self.test_tab, edited_df)

        # Get updated data
        retrieved_df = self.model.get_tab_measurements_df(self.test_tab)
        self.assertIsNotNone(retrieved_df)
        self.assertEqual(len(retrieved_df), 3)
        self.assertEqual(retrieved_df.iloc[2]["velocity"], 2820)

    def test_is_tab_created(self):
        # Initially should be False
        self.assertFalse(self.model.is_tab_created(self.test_tab))

        # After setting measurements, should be True
        test_data = [{"shot": 1, "velocity": 2800}]
        self.model.set_tab_measurements(self.test_tab, test_data)
        self.assertTrue(self.model.is_tab_created(self.test_tab))

    def test_clear_tab_data(self):
        # Add data to tab
        test_data = [{"shot": 1, "velocity": 2800}]
        self.model.set_tab_measurements(self.test_tab, test_data)
        self.model.set_tab_session_details(self.test_tab, {"range_id": "test"})

        # Verify tab exists
        self.assertIn(self.test_tab, self.model.get_all_tabs())
        self.assertIsNotNone(self.model.get_tab_measurements_df(self.test_tab))

        # Clear tab data
        self.model.clear_tab_data(self.test_tab)

        # Verify data is cleared
        self.assertNotIn(self.test_tab, self.model.get_all_tabs())
        self.assertIsNone(self.model.get_tab_measurements_df(self.test_tab))

    def test_tab_data_structure(self):
        # Test the internal tab data structure
        tab_data = self.model.get_tab_data(self.test_tab)
        
        # Should have the expected keys
        expected_keys = {"measurements_data", "edited_measurements", "session_details", "is_created"}
        self.assertEqual(set(tab_data.keys()), expected_keys)
        
        # Initial values should be correct
        self.assertEqual(tab_data["measurements_data"], [])
        self.assertIsNone(tab_data["edited_measurements"])
        self.assertEqual(tab_data["session_details"], {})
        self.assertFalse(tab_data["is_created"])

    def test_empty_measurements_df(self):
        # When no measurements are set, should return None
        df = self.model.get_tab_measurements_df(self.test_tab)
        self.assertIsNone(df)


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

        # Set different measurements for each tab
        data1 = [{"session_id": "chrono-1", "velocity": 2800}]
        data2 = [{"session_id": "chrono-2", "velocity": 2900}]
        
        model.set_tab_measurements(tab1, data1)
        model.set_tab_measurements(tab2, data2)

        # Set different session details
        model.set_tab_session_details(tab1, {"range_id": "range-1"})
        model.set_tab_session_details(tab2, {"range_id": "range-2"})

        # Verify data isolation
        df1 = model.get_tab_measurements_df(tab1)
        df2 = model.get_tab_measurements_df(tab2)
        
        self.assertEqual(df1.iloc[0]["session_id"], "chrono-1")
        self.assertEqual(df2.iloc[0]["session_id"], "chrono-2")

        details1 = model.get_tab_session_details(tab1)
        details2 = model.get_tab_session_details(tab2)
        
        self.assertEqual(details1["range_id"], "range-1")
        self.assertEqual(details2["range_id"], "range-2")

        # Clear one tab shouldn't affect the other
        model.clear_tab_data(tab1)

        self.assertIsNone(model.get_tab_measurements_df(tab1))
        self.assertIsNotNone(model.get_tab_measurements_df(tab2))


if __name__ == "__main__":
    unittest.main()
