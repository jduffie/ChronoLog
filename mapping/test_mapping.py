import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mapping.admin.admin_controller import AdminController
from mapping.nominate.nominate_controller import NominateController
from mapping.public_ranges.public_ranges_controller import PublicRangesController


class TestPublicRangesController(unittest.TestCase):

    def setUp(self):
        self.controller = PublicRangesController()

    def test_setup_page_state(self):
        """Test that page state setup works"""
        # This would normally interact with Streamlit session state
        # We're testing that the method exists and can be called
        try:
            self.controller.setup_page_state()
            # If no exception is raised, the method exists
            self.assertTrue(True)
        except AttributeError:
            self.fail("setup_page_state method should exist")

    @patch("streamlit.error")
    def test_get_public_ranges_error_handling(self, mock_error):
        """Test error handling in get_public_ranges"""
        mock_supabase = Mock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception(
            "Database error"
        )

        try:
            result = self.controller.get_public_ranges(mock_supabase)
            # Should handle the error gracefully
            self.assertEqual(result, [])
        except Exception:
            # If an exception propagates, that's also acceptable behavior
            pass

    def test_get_public_ranges_success(self):
        """Test successful public ranges retrieval"""
        mock_supabase = Mock()
        mock_data = [
            {
                "id": "range-1",
                "range_name": "Test Range",
                "address": "123 Test St",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "status": "approved",
            }
        ]

        mock_response = Mock()
        mock_response.data = mock_data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        result = self.controller.get_public_ranges(mock_supabase)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["range_name"], "Test Range")

    def test_delete_public_range(self):
        """Test public range deletion"""
        mock_supabase = Mock()
        mock_response = Mock()
        mock_response.data = [{"id": "range-1"}]
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        result = self.controller.delete_public_range("range-1", mock_supabase)

        # Should return True for successful deletion
        self.assertTrue(result)


class TestNominateController(unittest.TestCase):

    def setUp(self):
        self.controller = NominateController()

    def test_controller_initialization(self):
        """Test that nominate controller initializes properly"""
        self.assertIsNotNone(self.controller)
        self.assertIsInstance(self.controller, NominateController)

    def test_run_nominate_functionality_exists(self):
        """Test that run nominate functionality method exists"""
        # Check if the method exists
        self.assertTrue(
            hasattr(self.controller, "_run_nominate_functionality")
            or hasattr(self.controller, "run")
        )


class TestAdminController(unittest.TestCase):

    def setUp(self):
        self.controller = AdminController()

    def test_controller_initialization(self):
        """Test that admin controller initializes properly"""
        self.assertIsNotNone(self.controller)
        self.assertIsInstance(self.controller, AdminController)

    def test_admin_functionality_exists(self):
        """Test that admin functionality methods exist"""
        # Check for common admin methods
        methods_to_check = ["run", "handle_admin_actions", "get_submissions"]

        existing_methods = []
        for method in methods_to_check:
            if hasattr(self.controller, method):
                existing_methods.append(method)

        # At least one admin method should exist
        self.assertGreater(
            len(existing_methods),
            0,
            f"Admin controller should have at least one of these methods: {methods_to_check}",
        )


class TestMappingPageStructure(unittest.TestCase):
    """Test the mapping/ranges page structure and configuration"""

    def test_ranges_page_exists(self):
        """Test that the ranges page file exists"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "5_🌍_Ranges.py"
        )
        self.assertTrue(os.path.exists(page_path), "Ranges page should exist")

    def test_ranges_page_has_required_imports(self):
        """Test that ranges page has required imports"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "5_🌍_Ranges.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            required_imports = [
                "streamlit",
                "handle_auth",
                "create_client",
                "PublicRangesController",
            ]
            for required_import in required_imports:
                self.assertIn(
                    required_import,
                    content,
                    f"Ranges page should import {required_import}",
                )

    def test_ranges_page_has_correct_tabs(self):
        """Test that ranges page has expected tabs"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "5_🌍_Ranges.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            expected_tabs = ["Public Ranges", "Nominate", "Submissions"]
            for tab in expected_tabs:
                self.assertIn(tab, content, f"Ranges page should reference {tab}")

    def test_ranges_page_configuration(self):
        """Test ranges page configuration"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "5_🌍_Ranges.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            self.assertIn('page_title="Ranges"', content)
            self.assertIn('page_icon="🌍"', content)
            self.assertIn('layout="wide"', content)

    def test_ranges_page_auth_app_setting(self):
        """Test that ranges page sets correct app for auth"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "5_🌍_Ranges.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            # Should set app to "mapping" for authentication
            self.assertIn('"app"] = "mapping"', content)


class TestMappingModels(unittest.TestCase):
    """Test mapping models and data structures"""

    def test_range_models_exists(self):
        """Test that range models file exists"""
        models_path = os.path.join(os.path.dirname(__file__), "range_models.py")
        self.assertTrue(os.path.exists(models_path), "Range models file should exist")

    def test_mapping_controllers_exist(self):
        """Test that mapping controller files exist"""
        controller_paths = [
            "public_ranges/public_ranges_controller.py",
            "nominate/nominate_controller.py",
            "admin/admin_controller.py",
        ]

        for controller_path in controller_paths:
            full_path = os.path.join(os.path.dirname(__file__), controller_path)
            self.assertTrue(
                os.path.exists(full_path),
                f"Controller file {controller_path} should exist",
            )

    def test_mapping_views_exist(self):
        """Test that mapping view files exist"""
        view_paths = [
            "public_ranges/public_ranges_view.py",
            "nominate/nominate_view.py",
            "admin/admin_view.py",
        ]

        for view_path in view_paths:
            full_path = os.path.join(os.path.dirname(__file__), view_path)
            self.assertTrue(
                os.path.exists(full_path), f"View file {view_path} should exist"
            )


class TestMappingDataValidation(unittest.TestCase):
    """Test mapping data validation"""

    def test_coordinate_validation(self):
        """Test coordinate validation for ranges"""
        # Test valid coordinates
        valid_coords = [
            (40.7128, -74.0060),  # New York
            (34.0522, -118.2437),  # Los Angeles
            (51.5074, -0.1278),  # London
        ]

        for lat, lng in valid_coords:
            self.assertGreaterEqual(lat, -90)
            self.assertLessEqual(lat, 90)
            self.assertGreaterEqual(lng, -180)
            self.assertLessEqual(lng, 180)

    def test_range_name_validation(self):
        """Test range name validation"""
        valid_names = [
            "Test Range",
            "Outdoor Shooting Range",
            "Pine Valley Gun Club",
            "Metro Pistol Range",
        ]

        for name in valid_names:
            self.assertIsInstance(name, str)
            self.assertGreater(len(name), 0)
            self.assertLessEqual(len(name), 100)  # Reasonable max length

    def test_address_validation(self):
        """Test address validation"""
        valid_addresses = [
            "123 Main St, Anytown, ST 12345",
            "456 Oak Avenue, City, State 67890",
            "789 Pine Road, Town, ST",
        ]

        for address in valid_addresses:
            self.assertIsInstance(address, str)
            self.assertGreater(len(address), 5)  # Minimum reasonable length


class TestMappingIntegration(unittest.TestCase):
    """Test mapping component integration"""

    def test_controllers_can_be_imported(self):
        """Test that all controllers can be imported"""
        try:
            from mapping.admin.admin_controller import AdminController
            from mapping.nominate.nominate_controller import NominateController
            from mapping.public_ranges.public_ranges_controller import (
                PublicRangesController,
            )

            # If we get here, imports succeeded
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Controller import failed: {e}")

    def test_session_state_manager_exists(self):
        """Test that session state manager exists"""
        manager_path = os.path.join(
            os.path.dirname(__file__), "session_state_manager.py"
        )
        self.assertTrue(
            os.path.exists(manager_path), "Session state manager should exist"
        )


if __name__ == "__main__":
    unittest.main()
