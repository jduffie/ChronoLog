"""
Integration tests for rifles UI to API layer.

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
from unittest.mock import MagicMock

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rifles.api import RiflesAPI
from rifles.models import RifleModel


class TestRiflesUIIntegration(unittest.TestCase):
    """Test UI to API integration for rifles"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.rifles_api = RiflesAPI(self.mock_supabase)
        self.test_user_id = "test-user-123"

    def test_view_tab_can_get_rifles_for_user(self):
        """Test that view_tab can call get_all_rifles() correctly"""
        # view_tab.py line 27 calls: rifle_service.get_rifles_for_user(user["id"])
        # API has: get_all_rifles(user_id)
        try:
            # Mock the response
            self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

            result = self.rifles_api.get_all_rifles(self.test_user_id)

            # Should return a list
            self.assertIsInstance(result, list)
        except AttributeError as e:
            self.fail(f"API method call failed: {e}")

    def test_view_tab_can_update_rifle(self):
        """Test that view_tab can call update_rifle() correctly"""
        # view_tab.py line 348 calls: rifle_service.update_rifle()
        rifle_id = "test-rifle-123"
        updated_data = {
            "name": "Updated Rifle Name",
            "barrel_length": "24 inches",
        }

        try:
            # Mock the response
            mock_record = {
                "id": rifle_id,
                "user_id": self.test_user_id,
                "name": "Updated Rifle Name",
                "cartridge_type": "6.5 Creedmoor",
                "barrel_length": "24 inches",
            }
            self.mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = [mock_record]

            result = self.rifles_api.update_rifle(rifle_id, updated_data, self.test_user_id)

            # Should return a RifleModel
            self.assertIsInstance(result, RifleModel)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_view_tab_can_delete_rifle(self):
        """Test that view_tab can call delete_rifle() correctly"""
        # view_tab.py line 421 calls: rifle_service.delete_rifle()
        rifle_id = "test-rifle-123"

        try:
            # Mock the response
            self.mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{"id": rifle_id}]

            result = self.rifles_api.delete_rifle(rifle_id, self.test_user_id)

            # Should return a boolean
            self.assertIsInstance(result, bool)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_create_tab_can_create_rifle(self):
        """Test that create_tab can call create_rifle() correctly"""
        # create_tab.py line 128 calls: rifle_service.create_rifle(rifle_data)
        rifle_data = {
            "name": "Remington 700",
            "cartridge_type": "6.5 Creedmoor",
            "barrel_twist_ratio": "1:8",
            "barrel_length": "24 inches",
        }

        try:
            # Mock the response
            mock_record = {
                "id": "new-rifle-123",
                "user_id": self.test_user_id,
                **rifle_data,
            }
            self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [mock_record]

            result = self.rifles_api.create_rifle(rifle_data, self.test_user_id)

            # Should return a RifleModel
            self.assertIsInstance(result, RifleModel)
        except (AttributeError, TypeError) as e:
            self.fail(f"API method call failed: {e}")

    def test_rifle_model_has_required_fields(self):
        """Test that RifleModel has all fields the UI expects"""
        # Verify the model structure matches what UI accesses
        rifle = RifleModel(
            id="test-123",
            user_id=self.test_user_id,
            name="Test Rifle",
            cartridge_type="6.5 Creedmoor",
            barrel_twist_ratio="1:8",
            barrel_length="24 inches",
        )

        try:
            # UI accesses these fields directly
            self.assertEqual(rifle.id, "test-123")
            self.assertEqual(rifle.name, "Test Rifle")
            self.assertEqual(rifle.cartridge_type, "6.5 Creedmoor")
            self.assertEqual(rifle.barrel_twist_ratio, "1:8")
            self.assertEqual(rifle.barrel_length, "24 inches")
            self.assertEqual(rifle.user_id, self.test_user_id)

        except AttributeError as e:
            self.fail(f"RifleModel missing required field: {e}")

    def test_get_all_rifles_returns_rifle_models(self):
        """Test that get_all_rifles returns RifleModel instances not dicts"""
        # Ensures UI gets model instances with properties, not raw dicts
        try:
            # Mock the response
            mock_record = {
                "id": "rifle-123",
                "user_id": self.test_user_id,
                "name": "Test Rifle",
                "cartridge_type": "6.5 Creedmoor",
            }
            self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_record]

            result = self.rifles_api.get_all_rifles(self.test_user_id)

            # Should return list of RifleModel instances
            self.assertIsInstance(result, list)
            if len(result) > 0:
                self.assertIsInstance(result[0], RifleModel)
                # UI expects to access properties
                self.assertEqual(result[0].name, "Test Rifle")
                self.assertEqual(result[0].cartridge_type, "6.5 Creedmoor")

        except (AttributeError, TypeError) as e:
            self.fail(f"API method return type incorrect: {e}")

    def test_rifle_model_is_flat_structure(self):
        """Test that RifleModel is a flat structure (no nested objects)"""
        # Unlike CartridgeModel which has nested bullet fields,
        # RifleModel should be flat
        rifle = RifleModel(
            id="test-123",
            user_id=self.test_user_id,
            name="Test Rifle",
            cartridge_type="6.5 Creedmoor",
        )

        # Should NOT have nested objects like rifle.cartridge or rifle.barrel
        # Everything should be at the top level
        self.assertFalse(hasattr(rifle, "cartridge"),
                        "RifleModel should NOT have nested cartridge object")
        self.assertFalse(hasattr(rifle, "barrel"),
                        "RifleModel should NOT have nested barrel object")


if __name__ == "__main__":
    unittest.main()
