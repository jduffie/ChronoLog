"""
Integration tests for cartridges UI to API layer.

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
from unittest.mock import Mock, MagicMock, patch

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cartridges.models import CartridgeModel
from cartridges.api import CartridgesAPI
from bullets.models import BulletModel
from bullets.api import BulletsAPI


class TestCartridgesUIIntegration(unittest.TestCase):
    """Test UI to API integration for cartridges"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.cartridges_api = CartridgesAPI(self.mock_supabase)
        self.bullets_api = BulletsAPI(self.mock_supabase)
        self.test_user_id = "test-user-123"

    def test_view_tab_can_get_all_cartridges(self):
        """Test that view_tab can call get_all_cartridges() correctly"""
        # This is the call made in view_tab.py line 20
        try:
            # Mock the response
            self.mock_supabase.table.return_value.select.return_value.or_.return_value.execute.return_value.data = []

            result = self.cartridges_api.get_all_cartridges(self.test_user_id)

            # Should return a list
            self.assertIsInstance(result, list)
        except AttributeError as e:
            self.fail(f"API method call failed: {e}")

    def test_view_tab_can_delete_user_cartridge(self):
        """Test that view_tab can call delete_user_cartridge() correctly"""
        # This is the call made in view_tab.py line 401-403
        cartridge_id = "test-cartridge-123"

        try:
            # Mock the response
            self.mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{"id": cartridge_id}]

            result = self.cartridges_api.delete_user_cartridge(
                cartridge_id,
                self.test_user_id
            )

            # Should return a boolean
            self.assertIsInstance(result, bool)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_edit_tab_can_get_all_bullets(self):
        """Test that edit_tab can call get_all_bullets() correctly"""
        # This is the call made in edit_tab.py line 35
        try:
            # Mock the response
            self.mock_supabase.table.return_value.select.return_value.execute.return_value.data = []

            result = self.bullets_api.get_all_bullets()

            # Should return a list
            self.assertIsInstance(result, list)
        except AttributeError as e:
            self.fail(f"API method call failed: {e}")

    def test_edit_tab_can_create_user_cartridge(self):
        """Test that edit_tab can call create_user_cartridge() correctly"""
        # This is the call made in edit_tab.py line 178
        cartridge_data = {
            "make": "Federal",
            "model": "Gold Medal Match",
            "cartridge_type": ".308 Winchester",
            "bullet_id": "bullet-123",
        }

        try:
            # Mock the response
            mock_record = {
                "id": "test-123",
                "owner_id": self.test_user_id,
                **cartridge_data,
                "bullets": {
                    "id": "bullet-123",
                    "manufacturer": "Sierra",
                    "model": "MatchKing",
                    "weight_grains": 168,
                    "bullet_diameter_groove_mm": 7.82,
                    "bore_diameter_land_mm": 7.62,
                },
            }
            self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [mock_record]

            result = self.cartridges_api.create_user_cartridge(
                cartridge_data,
                self.test_user_id
            )

            # Should return a CartridgeModel
            self.assertIsInstance(result, CartridgeModel)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_edit_tab_can_filter_user_cartridges(self):
        """Test that edit_tab can filter user-owned cartridges from get_all_cartridges()"""
        # This is the logic in edit_tab.py lines 194-196
        try:
            # Mock the response with mixed cartridges
            mock_user_record = {
                "id": "cart-1",
                "owner_id": self.test_user_id,
                "make": "Federal",
                "model": "Gold Medal",
                "cartridge_type": ".308 Winchester",
                "bullet_id": "bullet-1",
                "bullets": {
                    "id": "bullet-1",
                    "manufacturer": "Sierra",
                    "model": "MatchKing",
                    "weight_grains": 168,
                    "bullet_diameter_groove_mm": 7.82,
                    "bore_diameter_land_mm": 7.62,
                },
            }
            mock_global_record = {
                "id": "cart-2",
                "owner_id": None,  # Global cartridge
                "make": "Hornady",
                "model": "Match",
                "cartridge_type": "6.5 Creedmoor",
                "bullet_id": "bullet-2",
                "bullets": {
                    "id": "bullet-2",
                    "manufacturer": "Hornady",
                    "model": "ELD-M",
                    "weight_grains": 147,
                    "bullet_diameter_groove_mm": 6.5,
                    "bore_diameter_land_mm": 6.35,
                },
            }

            self.mock_supabase.table.return_value.select.return_value.or_.return_value.execute.return_value.data = [
                mock_user_record,
                mock_global_record,
            ]

            all_cartridges = self.cartridges_api.get_all_cartridges(self.test_user_id)

            # Filter for user-owned only (this is what edit_tab does)
            user_cartridges = [c for c in all_cartridges if c.owner_id == self.test_user_id]

            # Should have filtered out the global cartridge
            self.assertEqual(len(user_cartridges), 1)
            self.assertEqual(user_cartridges[0].owner_id, self.test_user_id)

        except (AttributeError, TypeError) as e:
            self.fail(f"API filtering failed: {e}")

    def test_bullet_model_has_display_name_property(self):
        """Test that BulletModel has display_name property (used in edit_tab)"""
        # This is used in edit_tab.py line 48
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

            # Should return a string
            self.assertIsInstance(display_name, str)
            self.assertIn("Sierra", display_name)
            self.assertIn("MatchKing", display_name)
        except AttributeError as e:
            self.fail(f"BulletModel missing display_name property: {e}")

    def test_cartridge_model_has_flattened_bullet_fields(self):
        """Test that CartridgeModel has flattened bullet fields (not a bullet property)"""
        # CartridgeModel should have bullet_manufacturer, bullet_model, etc. NOT cartridge.bullet
        # This is used in view_tab.py and edit_tab.py
        from cartridges.models import CartridgeModel

        cartridge = CartridgeModel(
            id="cart-123",
            owner_id="user-123",
            make="Federal",
            model="Gold Medal",
            cartridge_type=".308 Winchester",
            bullet_id="bullet-123",
            bullet_manufacturer="Sierra",
            bullet_model="MatchKing",
            bullet_weight_grains=168.0,
            bullet_diameter_groove_mm=7.82,
            bore_diameter_land_mm=7.62,
        )

        try:
            # Should have flattened fields
            self.assertEqual(cartridge.bullet_manufacturer, "Sierra")
            self.assertEqual(cartridge.bullet_model, "MatchKing")
            self.assertEqual(cartridge.bullet_weight_grains, 168.0)

            # Should NOT have a bullet property
            self.assertFalse(hasattr(cartridge, "bullet"),
                           "CartridgeModel should NOT have a 'bullet' property - fields are flattened")

        except AttributeError as e:
            self.fail(f"CartridgeModel missing flattened bullet fields: {e}")


if __name__ == "__main__":
    unittest.main()