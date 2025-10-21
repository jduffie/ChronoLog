"""
Integration tests for Cartridges module.

These tests verify end-to-end operations with real Supabase database:
- Creating test bullets first (dependency)
- Loading cartridge data from CSV
- Writing to remote database (both user-owned and global)
- Reading back data
- Testing dual ownership model
- Cleaning up test data

Run with: python -m pytest cartridges/test_cartridges_integration.py -v -m integration
"""

import csv
import os
import sys
import unittest
from typing import List
from unittest.mock import Mock

import pytest

from supabase import create_client

# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bullets import BulletModel, BulletsAPI
from cartridges import CartridgeModel, CartridgesAPI


class BaseCartridgesIntegrationTest(unittest.TestCase):
    """Base class for cartridges integration tests with common setup"""

    @classmethod
    def setUpClass(cls):
        """Set up test database connection"""
        # Use environment variables for Supabase connection
        cls.supabase_url = os.getenv(
            "SUPABASE_URL", "https://qnzioartedlrithdxszx.supabase.co"
        )
        cls.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "test-key")
        # Use existing test user ID that's in the users table
        cls.test_user_id = "google-oauth2|111273793361054745867"

        # Create Supabase client (or mock for CI)
        if cls.supabase_key == "test-key":
            # Mock client for CI/testing without credentials
            cls.supabase = Mock()
            cls.mock_mode = True
        else:
            # Real client for local integration testing
            cls.supabase = create_client(cls.supabase_url, cls.supabase_key)
            cls.mock_mode = False

        # Initialize APIs
        cls.bullets_api = BulletsAPI(cls.supabase)
        cls.cartridges_api = CartridgesAPI(cls.supabase)

    def setUp(self):
        """Set up each test with clean state"""
        self.test_bullet_ids: List[str] = []  # Track created bullets for cleanup
        self.test_cartridge_ids: List[str] = []  # Track created cartridges for cleanup

    def tearDown(self):
        """Clean up test data after each test"""
        if not self.mock_mode:
            # Clean up test cartridges first (foreign key dependency)
            for cartridge_id in reversed(self.test_cartridge_ids):
                try:
                    # Try user delete first, then global delete
                    if not self.cartridges_api.delete_user_cartridge(
                        cartridge_id, self.test_user_id
                    ):
                        self.cartridges_api.delete_global_cartridge(cartridge_id)
                except Exception as e:
                    print(
                        f"Cleanup warning: Could not delete cartridge {cartridge_id}: {e}"
                    )

            # Then clean up test bullets
            for bullet_id in reversed(self.test_bullet_ids):
                try:
                    self.bullets_api.delete_bullet(bullet_id)
                except Exception as e:
                    print(f"Cleanup warning: Could not delete bullet {bullet_id}: {e}")


@pytest.mark.integration
@pytest.mark.database
class TestCartridgesCSVIntegration(BaseCartridgesIntegrationTest):
    """Test loading cartridges from CSV, writing to DB, reading back, and cleanup"""

    def create_test_bullets(self) -> List[BulletModel]:
        """Create test bullets for cartridges to reference."""
        bullets_data = [
            {
                "user_id": self.test_user_id,
                "manufacturer": "TEST_Hornady",
                "model": "TEST_ELD_Match",
                "weight_grains": 147.0,
                "bullet_diameter_groove_mm": 6.71,
                "bore_diameter_land_mm": 6.5,
                "ballistic_coefficient_g7": 0.351,
            },
            {
                "user_id": self.test_user_id,
                "manufacturer": "TEST_Sierra",
                "model": "TEST_MatchKing",
                "weight_grains": 168.0,
                "bullet_diameter_groove_mm": 7.82,
                "bore_diameter_land_mm": 7.62,
                "ballistic_coefficient_g7": 0.243,
            },
            {
                "user_id": self.test_user_id,
                "manufacturer": "TEST_Berger",
                "model": "TEST_Hybrid",
                "weight_grains": 105.0,
                "bullet_diameter_groove_mm": 6.17,
                "bore_diameter_land_mm": 6.0,
                "ballistic_coefficient_g7": 0.275,
            },
        ]

        created_bullets = []
        for bullet_data in bullets_data:
            bullet = self.bullets_api.create_bullet(bullet_data)
            created_bullets.append(bullet)
            self.test_bullet_ids.append(bullet.id)

        return created_bullets

    def load_cartridges_from_csv(
        self, csv_path: str, bullet_ids: List[str]
    ) -> List[dict]:
        """
        Load cartridge data from CSV file and replace placeholder bullet IDs.

        Args:
            csv_path: Path to CSV file
            bullet_ids: List of actual bullet IDs to use

        Returns:
            List of cartridge data dictionaries
        """
        cartridges_data = []

        with open(csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                # Replace placeholder with actual bullet ID
                bullet_id = bullet_ids[i] if i < len(bullet_ids) else bullet_ids[0]

                cartridge_data = {
                    "make": row["make"],
                    "model": row["model"],
                    "bullet_id": bullet_id,
                    "cartridge_type": row["cartridge_type"],
                }

                # Add optional fields if present
                if row.get("data_source_name"):
                    cartridge_data["data_source_name"] = row["data_source_name"]
                if row.get("data_source_link"):
                    cartridge_data["data_source_link"] = row["data_source_link"]

                cartridges_data.append(cartridge_data)

        return cartridges_data

    def test_csv_load_write_read_delete_workflow(self):
        """
        Complete integration test:
        1. Create test bullets
        2. Load cartridges from CSV
        3. Create user-owned cartridges in Supabase
        4. Read back and verify
        5. Test dual ownership (user-owned vs global)
        6. Delete and verify cleanup
        """
        if self.mock_mode:
            # Mock mode: Skip actual database operations
            print("Running in mock mode - skipping real database operations")
            return

        # Step 1: Create test bullets
        print("Creating test bullets...")
        test_bullets = self.create_test_bullets()
        self.assertEqual(len(test_bullets), 3, "Should create 3 test bullets")

        bullet_ids = [b.id for b in test_bullets]

        # Path to test CSV
        csv_path = os.path.join(
            os.path.dirname(__file__), "test_data", "test_cartridges.csv"
        )

        # Step 2: Load cartridges from CSV
        print("Loading cartridges from CSV...")
        cartridges_data = self.load_cartridges_from_csv(csv_path, bullet_ids)
        self.assertEqual(len(cartridges_data), 3, "Should load 3 test cartridges from CSV")

        created_cartridges: List[CartridgeModel] = []

        try:
            # Step 3: Create user-owned cartridges
            print("Creating user-owned cartridges...")
            for cartridge_data in cartridges_data:
                created_cartridge = self.cartridges_api.create_user_cartridge(
                    cartridge_data, self.test_user_id
                )
                created_cartridges.append(created_cartridge)
                self.test_cartridge_ids.append(created_cartridge.id)

            self.assertEqual(
                len(created_cartridges), 3, "Should create 3 cartridges in database"
            )

            # Verify created cartridges
            for cartridge in created_cartridges:
                self.assertIsNotNone(cartridge.id, "Created cartridge should have an ID")
                self.assertEqual(
                    cartridge.owner_id,
                    self.test_user_id,
                    "User-owned cartridge should have owner_id set",
                )
                self.assertTrue(
                    cartridge.is_user_owned, "Should be user-owned cartridge"
                )
                self.assertFalse(cartridge.is_global, "Should not be global cartridge")
                self.assertTrue(
                    cartridge.make.startswith("TEST_"),
                    "Test cartridge should have TEST_ prefix",
                )

            # Step 4: Read back cartridges and verify
            print("Reading back cartridges...")
            for i, created_cartridge in enumerate(created_cartridges):
                # Read by ID
                read_cartridge = self.cartridges_api.get_cartridge_by_id(
                    created_cartridge.id, self.test_user_id
                )

                self.assertIsNotNone(
                    read_cartridge, f"Should find cartridge {created_cartridge.id}"
                )
                self.assertEqual(
                    read_cartridge.id, created_cartridge.id, "IDs should match"
                )
                self.assertEqual(
                    read_cartridge.make,
                    cartridges_data[i]["make"],
                    "Make should match original CSV data",
                )
                self.assertEqual(
                    read_cartridge.model,
                    cartridges_data[i]["model"],
                    "Model should match original CSV data",
                )
                self.assertEqual(
                    read_cartridge.cartridge_type,
                    cartridges_data[i]["cartridge_type"],
                    "Type should match original CSV data",
                )

                # Verify embedded bullet data
                self.assertIsNotNone(
                    read_cartridge.bullet_manufacturer,
                    "Should have embedded bullet data",
                )
                self.assertTrue(
                    read_cartridge.bullet_manufacturer.startswith("TEST_"),
                    "Bullet manufacturer should be test data",
                )

                # Verify display_name works
                self.assertIn(
                    read_cartridge.make, read_cartridge.display_name
                )
                self.assertIn(
                    read_cartridge.cartridge_type, read_cartridge.display_name
                )

            # Test batch read
            print("Testing batch read...")
            all_test_ids = [c.id for c in created_cartridges]
            batch_cartridges = self.cartridges_api.get_cartridges_by_ids(
                all_test_ids, self.test_user_id
            )
            self.assertEqual(
                len(batch_cartridges), 3, "Batch read should return all 3 cartridges"
            )

            # Test filter by make
            print("Testing filter operations...")
            test_federal = self.cartridges_api.filter_cartridges(
                self.test_user_id, make="TEST_Federal"
            )
            self.assertGreaterEqual(
                len(test_federal), 1, "Should find at least 1 TEST_Federal cartridge"
            )

            # Test get_all_cartridges includes our test cartridges
            print("Testing get_all_cartridges...")
            all_cartridges = self.cartridges_api.get_all_cartridges(self.test_user_id)
            test_cart_ids_set = set(c.id for c in created_cartridges)
            found_ids = set(c.id for c in all_cartridges if c.id in test_cart_ids_set)
            self.assertEqual(
                len(found_ids),
                3,
                "get_all_cartridges should include all our test cartridges",
            )

            # Step 5: Test update operation
            print("Testing update operation...")
            update_data = {"model": "TEST_Updated_Model"}
            updated = self.cartridges_api.update_user_cartridge(
                created_cartridges[0].id, update_data, self.test_user_id
            )
            self.assertEqual(updated.model, "TEST_Updated_Model")

            # Step 6: Delete cartridges and verify cleanup
            print("Deleting cartridges...")
            for cartridge in created_cartridges:
                deleted = self.cartridges_api.delete_user_cartridge(
                    cartridge.id, self.test_user_id
                )
                self.assertTrue(
                    deleted, f"Should successfully delete cartridge {cartridge.id}"
                )

                # Verify cartridge is gone
                read_after_delete = self.cartridges_api.get_cartridge_by_id(
                    cartridge.id, self.test_user_id
                )
                self.assertIsNone(
                    read_after_delete,
                    f"Cartridge {cartridge.id} should not exist after deletion",
                )

            # Clear the test_cartridge_ids since we manually deleted them
            self.test_cartridge_ids.clear()

            # Clean up bullets
            print("Deleting test bullets...")
            for bullet_id in self.test_bullet_ids:
                self.bullets_api.delete_bullet(bullet_id)
            self.test_bullet_ids.clear()

            print("Integration test completed successfully!")

        except Exception as e:
            # If test fails, ensure cleanup still happens in tearDown
            self.fail(f"Integration test failed: {str(e)}")


@pytest.mark.integration
@pytest.mark.database
class TestCartridgesDualOwnership(BaseCartridgesIntegrationTest):
    """Test dual ownership model (global vs user-owned cartridges)"""

    def test_global_vs_user_owned_cartridges(self):
        """Test that global and user-owned cartridges work correctly"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create test bullet
        bullet_data = {
            "user_id": self.test_user_id,
            "manufacturer": "TEST_Ownership",
            "model": "TEST_Bullet",
            "weight_grains": 150.0,
            "bullet_diameter_groove_mm": 7.82,
            "bore_diameter_land_mm": 7.62,
        }
        bullet = self.bullets_api.create_bullet(bullet_data)
        self.test_bullet_ids.append(bullet.id)

        # Create global cartridge (admin operation)
        global_cart_data = {
            "make": "TEST_Global",
            "model": "TEST_Admin_Load",
            "bullet_id": bullet.id,
            "cartridge_type": "308 Winchester",
        }
        global_cart = self.cartridges_api.create_global_cartridge(global_cart_data)
        self.test_cartridge_ids.append(global_cart.id)

        # Verify it's global
        self.assertIsNone(global_cart.owner_id, "Global cartridge should have NULL owner_id")
        self.assertTrue(global_cart.is_global, "Should be global cartridge")

        # Create user-owned cartridge
        user_cart_data = {
            "make": "TEST_UserOwned",
            "model": "TEST_Custom_Load",
            "bullet_id": bullet.id,
            "cartridge_type": "308 Winchester",
        }
        user_cart = self.cartridges_api.create_user_cartridge(
            user_cart_data, self.test_user_id
        )
        self.test_cartridge_ids.append(user_cart.id)

        # Verify it's user-owned
        self.assertEqual(
            user_cart.owner_id, self.test_user_id, "User cartridge should have owner_id"
        )
        self.assertTrue(user_cart.is_user_owned, "Should be user-owned cartridge")

        # Verify both are accessible to user
        all_carts = self.cartridges_api.get_all_cartridges(self.test_user_id)
        test_ids = {global_cart.id, user_cart.id}
        found_ids = {c.id for c in all_carts if c.id in test_ids}
        self.assertEqual(len(found_ids), 2, "User should see both global and own cartridges")

        # Cleanup
        self.cartridges_api.delete_global_cartridge(global_cart.id)
        self.cartridges_api.delete_user_cartridge(user_cart.id, self.test_user_id)
        self.test_cartridge_ids.clear()

        self.bullets_api.delete_bullet(bullet.id)
        self.test_bullet_ids.clear()


@pytest.mark.integration
@pytest.mark.database
class TestCartridgesAPIIntegration(BaseCartridgesIntegrationTest):
    """Test CartridgesAPI operations against real database"""

    def test_get_all_cartridges_returns_data(self):
        """Test that get_all_cartridges returns data from real database"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Should return existing cartridges from the database
        cartridges = self.cartridges_api.get_all_cartridges(self.test_user_id)

        # Should return a list
        self.assertIsInstance(cartridges, list, "Should return a list of cartridges")

        # If there are cartridges, verify they are CartridgeModel instances
        if cartridges:
            self.assertIsInstance(
                cartridges[0], CartridgeModel, "Should return CartridgeModel instances"
            )

    def test_get_cartridge_types(self):
        """Test that get_cartridge_types returns data"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        types = self.cartridges_api.get_cartridge_types()

        self.assertIsInstance(types, list, "Should return list of types")
        if types:
            self.assertIsInstance(types[0], str, "Types should be strings")


if __name__ == "__main__":
    # Set up test environment
    # If environment variables are not set, will use mock mode
    if not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        print("Warning: SUPABASE_SERVICE_ROLE_KEY not set - running in mock mode")
        print("To run real integration tests, set environment variables:")
        print("  export SUPABASE_SERVICE_ROLE_KEY=your-key")

    # Run the tests
    unittest.main(verbosity=2)