"""
Integration tests for bullets UI to API layer.

These tests verify that UI code correctly uses API methods.
They catch issues like:
- Calling non-existent API methods
- Wrong number of arguments
- Wrong method names

These are NOT full UI tests - they just verify API method calls work.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bullets.models import BulletModel
from bullets.api import BulletsAPI


class TestBulletsUIIntegration(unittest.TestCase):
    """Test UI to API integration for bullets"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.bullets_api = BulletsAPI(self.mock_supabase)

    def test_view_tab_can_get_all_bullets(self):
        """Test that view_tab can call get_all_bullets() correctly"""
        # This is the call made in view_tab.py line 18
        try:
            # Mock the response
            self.mock_supabase.table.return_value.select.return_value.execute.return_value.data = []

            result = self.bullets_api.get_all_bullets()

            # Should return a list
            self.assertIsInstance(result, list)
        except AttributeError as e:
            self.fail(f"API method call failed: {e}")

    def test_view_tab_can_filter_bullets(self):
        """Test that view_tab can call filter_bullets() correctly"""
        # This is the call made in view_tab.py line 61
        try:
            # Mock the response
            self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value.data = []

            result = self.bullets_api.filter_bullets(
                manufacturer="Sierra",
                bore_diameter_mm=7.62,
                weight_grains=168
            )

            # Should return a list
            self.assertIsInstance(result, list)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_view_tab_can_update_bullet(self):
        """Test that view_tab can call update_bullet() correctly"""
        # This is the call made in view_tab.py line 433
        bullet_id = "test-bullet-123"
        updated_data = {
            "ballistic_coefficient_g1": 0.450,
            "ballistic_coefficient_g7": 0.225,
        }

        try:
            # Mock the response
            mock_record = {
                "id": bullet_id,
                "user_id": "admin",
                "manufacturer": "Sierra",
                "model": "MatchKing",
                "weight_grains": 168,
                "bullet_diameter_groove_mm": 7.82,
                "bore_diameter_land_mm": 7.62,
                "ballistic_coefficient_g1": 0.450,
                "ballistic_coefficient_g7": 0.225,
            }
            self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [mock_record]

            result = self.bullets_api.update_bullet(bullet_id, updated_data)

            # Should return a BulletModel
            self.assertIsInstance(result, BulletModel)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_create_tab_can_create_bullet(self):
        """Test that create_tab can call create_bullet() correctly"""
        # This is the call made in create_tab.py line 230
        bullet_data = {
            "user_id": "admin",
            "manufacturer": "Sierra",
            "model": "MatchKing",
            "weight_grains": 168.0,
            "bullet_diameter_groove_mm": 7.82,
            "bore_diameter_land_mm": 7.62,
        }

        try:
            # Mock the response
            mock_record = {
                "id": "new-bullet-123",
                **bullet_data,
            }
            self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [mock_record]

            result = self.bullets_api.create_bullet(bullet_data)

            # Should return a BulletModel
            self.assertIsInstance(result, BulletModel)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_bullet_model_has_display_name_property(self):
        """Test that BulletModel has display_name property (used throughout UI)"""
        # This is used in view_tab and create_tab
        bullet = BulletModel(
            id="test-123",
            user_id="admin",
            manufacturer="Sierra",
            model="MatchKing",
            weight_grains=168.0,
            bullet_diameter_groove_mm=7.82,
            bore_diameter_land_mm=7.62,
        )

        try:
            display_name = bullet.display_name

            # Should return a string with manufacturer, model, weight, and diameters
            self.assertIsInstance(display_name, str)
            self.assertIn("Sierra", display_name)
            self.assertIn("MatchKing", display_name)
            self.assertIn("168", display_name)
            self.assertIn("7.62mm", display_name)  # bore diameter
            self.assertIn("7.82mm", display_name)  # groove diameter
        except AttributeError as e:
            self.fail(f"BulletModel missing display_name property: {e}")

    def test_filter_bullets_handles_none_parameters(self):
        """Test that filter_bullets can handle None parameters"""
        # The UI might call filter_bullets with None values when filters aren't set
        try:
            # Mock the response
            self.mock_supabase.table.return_value.select.return_value.execute.return_value.data = []

            # Should not raise TypeError for None parameters
            result = self.bullets_api.filter_bullets(
                manufacturer=None,
                bore_diameter_mm=None,
                weight_grains=None
            )

            self.assertIsInstance(result, list)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed with None parameters: {e}")

    def test_update_bullet_returns_correct_type(self):
        """Test that update_bullet returns BulletModel not dict"""
        # Ensures UI gets a model instance with properties, not raw dict
        bullet_id = "test-123"
        update_data = {"notes": "Updated notes"}

        try:
            # Mock the response
            mock_record = {
                "id": bullet_id,
                "user_id": "admin",
                "manufacturer": "Sierra",
                "model": "MatchKing",
                "weight_grains": 168,
                "bullet_diameter_groove_mm": 7.82,
                "bore_diameter_land_mm": 7.62,
            }
            self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [mock_record]

            result = self.bullets_api.update_bullet(bullet_id, update_data)

            # UI expects to access properties like result.manufacturer
            self.assertIsInstance(result, BulletModel)
            self.assertEqual(result.manufacturer, "Sierra")
            self.assertEqual(result.model, "MatchKing")

        except (AttributeError, TypeError) as e:
            self.fail(f"API method return type incorrect: {e}")


if __name__ == "__main__":
    unittest.main()
