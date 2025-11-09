"""
Integration tests for Rifles module.

These tests verify end-to-end operations with real Supabase database:
- Loading rifle data from CSV
- Writing to remote database
- Reading back data
- Testing CRUD operations
- Cleaning up test data

Run with: python -m pytest rifles/test_rifles_integration.py -v -m integration
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

from rifles import RifleModel, RiflesAPI


class BaseRiflesIntegrationTest(unittest.TestCase):
    """Base class for rifles integration tests with common setup"""

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

        # Initialize API
        cls.rifles_api = RiflesAPI(cls.supabase)

    def setUp(self):
        """Set up each test with clean state"""
        self.test_rifle_ids: List[str] = []  # Track created rifles for cleanup

    def tearDown(self):
        """Clean up test data after each test"""
        if not self.mock_mode:
            # Clean up test rifles
            for rifle_id in reversed(self.test_rifle_ids):
                try:
                    self.rifles_api.delete_rifle(rifle_id, self.test_user_id)
                except Exception as e:
                    print(f"Cleanup warning: Could not delete rifle {rifle_id}: {e}")


@pytest.mark.integration
@pytest.mark.database
class TestRiflesCSVIntegration(BaseRiflesIntegrationTest):
    """Test loading rifles from CSV, writing to DB, reading back, and cleanup"""

    def load_rifles_from_csv(self, csv_path: str) -> List[dict]:
        """
        Load rifle data from CSV file.

        Args:
            csv_path: Path to CSV file

        Returns:
            List of rifle data dictionaries
        """
        rifles_data = []

        with open(csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rifle_data = {
                    "name": row["name"],
                    "cartridge_type": row["cartridge_type"],
                }

                # Add optional fields if present
                if row.get("barrel_twist_ratio"):
                    rifle_data["barrel_twist_ratio"] = row["barrel_twist_ratio"]
                if row.get("barrel_length"):
                    rifle_data["barrel_length"] = row["barrel_length"]
                if row.get("scope"):
                    rifle_data["scope"] = row["scope"]
                if row.get("trigger"):
                    rifle_data["trigger"] = row["trigger"]
                if row.get("sight_offset"):
                    rifle_data["sight_offset"] = row["sight_offset"]

                rifles_data.append(rifle_data)

        return rifles_data

    def test_csv_load_write_read_delete_workflow(self):
        """
        Complete integration test:
        1. Load rifles from CSV
        2. Create rifles in Supabase
        3. Read back and verify
        4. Test filter operations
        5. Test update operation
        6. Delete and verify cleanup
        """
        if self.mock_mode:
            # Mock mode: Skip actual database operations
            print("Running in mock mode - skipping real database operations")
            return

        # Path to test CSV
        csv_path = os.path.join(
            os.path.dirname(__file__), "test_data", "test_rifles.csv"
        )

        # Step 1: Load rifles from CSV
        print("Loading rifles from CSV...")
        rifles_data = self.load_rifles_from_csv(csv_path)
        self.assertEqual(len(rifles_data), 3, "Should load 3 test rifles from CSV")

        created_rifles: List[RifleModel] = []

        try:
            # Step 2: Create rifles
            print("Creating rifles...")
            for rifle_data in rifles_data:
                created_rifle = self.rifles_api.create_rifle(
                    rifle_data, self.test_user_id
                )
                created_rifles.append(created_rifle)
                self.test_rifle_ids.append(created_rifle.id)

            self.assertEqual(
                len(created_rifles), 3, "Should create 3 rifles in database"
            )

            # Verify created rifles
            for rifle in created_rifles:
                self.assertIsNotNone(rifle.id, "Created rifle should have an ID")
                self.assertEqual(
                    rifle.user_id,
                    self.test_user_id,
                    "Rifle should have user_id set",
                )
                self.assertTrue(
                    rifle.name.startswith("TEST_"),
                    "Test rifle should have TEST_ prefix",
                )

            # Step 3: Read back rifles and verify
            print("Reading back rifles...")
            for i, created_rifle in enumerate(created_rifles):
                # Read by ID
                read_rifle = self.rifles_api.get_rifle_by_id(
                    created_rifle.id, self.test_user_id
                )

                self.assertIsNotNone(
                    read_rifle, f"Should find rifle {created_rifle.id}"
                )
                self.assertEqual(
                    read_rifle.id, created_rifle.id, "IDs should match"
                )
                self.assertEqual(
                    read_rifle.name,
                    rifles_data[i]["name"],
                    "Name should match original CSV data",
                )
                self.assertEqual(
                    read_rifle.cartridge_type,
                    rifles_data[i]["cartridge_type"],
                    "Cartridge type should match original CSV data",
                )

                # Verify optional fields
                if rifles_data[i].get("barrel_twist_ratio"):
                    self.assertEqual(
                        read_rifle.barrel_twist_ratio,
                        rifles_data[i]["barrel_twist_ratio"],
                        "Twist ratio should match",
                    )

                # Verify display_name works
                self.assertIn(read_rifle.name, read_rifle.display_name())
                self.assertIn(
                    read_rifle.cartridge_type, read_rifle.display_name()
                )

                # Verify display helpers
                barrel_display = read_rifle.barrel_display()
                self.assertIsInstance(barrel_display, str)
                self.assertTrue(len(barrel_display) > 0)

            # Test get all rifles
            print("Testing get_all_rifles...")
            all_test_rifles = self.rifles_api.get_all_rifles(self.test_user_id)
            test_rifle_ids_set = set(r.id for r in created_rifles)
            found_ids = set(
                r.id for r in all_test_rifles if r.id in test_rifle_ids_set
            )
            self.assertEqual(
                len(found_ids),
                3,
                "get_all_rifles should include all our test rifles",
            )

            # Test filter by cartridge type
            print("Testing filter operations...")
            creedmoor_rifles = self.rifles_api.filter_rifles(
                self.test_user_id, cartridge_type="6.5mm Creedmoor"
            )
            test_creedmoor = [
                r for r in creedmoor_rifles if r.id in test_rifle_ids_set
            ]
            self.assertGreaterEqual(
                len(test_creedmoor),
                2,
                "Should find at least 2 6.5mm Creedmoor test rifles",
            )

            # Test get_rifle_by_name
            print("Testing get_rifle_by_name...")
            rifle_by_name = self.rifles_api.get_rifle_by_name(
                self.test_user_id, "TEST_Remington_700"
            )
            self.assertIsNotNone(rifle_by_name)
            self.assertEqual(rifle_by_name.name, "TEST_Remington_700")

            # Step 4: Test metadata operations
            print("Testing metadata operations...")
            cartridge_types = self.rifles_api.get_unique_cartridge_types(
                self.test_user_id
            )
            self.assertIsInstance(cartridge_types, list)
            # Should include our test types
            self.assertTrue(
                "6.5mm Creedmoor" in cartridge_types
                or "308 Winchester" in cartridge_types
            )

            twist_ratios = self.rifles_api.get_unique_twist_ratios(
                self.test_user_id
            )
            self.assertIsInstance(twist_ratios, list)

            # Step 5: Test update operation
            print("Testing update operation...")
            update_data = {"barrel_length": "28 inches"}
            updated = self.rifles_api.update_rifle(
                created_rifles[0].id, update_data, self.test_user_id
            )
            self.assertEqual(updated.barrel_length, "28 inches")

            # Verify update timestamp changed
            self.assertIsNotNone(updated.updated_at)

            # Step 6: Delete rifles and verify cleanup
            print("Deleting rifles...")
            for rifle in created_rifles:
                deleted = self.rifles_api.delete_rifle(
                    rifle.id, self.test_user_id
                )
                self.assertTrue(
                    deleted, f"Should successfully delete rifle {rifle.id}"
                )

                # Verify rifle is gone
                read_after_delete = self.rifles_api.get_rifle_by_id(
                    rifle.id, self.test_user_id
                )
                self.assertIsNone(
                    read_after_delete,
                    f"Rifle {rifle.id} should not exist after deletion",
                )

            # Clear the test_rifle_ids since we manually deleted them
            self.test_rifle_ids.clear()

            print("Integration test completed successfully!")

        except Exception as e:
            # If test fails, ensure cleanup still happens in tearDown
            self.fail(f"Integration test failed: {str(e)}")


@pytest.mark.integration
@pytest.mark.database
class TestRiflesAPIIntegration(BaseRiflesIntegrationTest):
    """Test RiflesAPI operations against real database"""

    def test_get_all_rifles_returns_data(self):
        """Test that get_all_rifles returns data from real database"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Should return rifles from the database
        rifles = self.rifles_api.get_all_rifles(self.test_user_id)

        # Should return a list
        self.assertIsInstance(rifles, list, "Should return a list of rifles")

        # If there are rifles, verify they are RifleModel instances
        if rifles:
            self.assertIsInstance(
                rifles[0], RifleModel, "Should return RifleModel instances"
            )

    def test_create_and_delete_rifle(self):
        """Test creating and deleting a single rifle"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create a rifle
        rifle_data = {
            "name": "TEST_Integration_Rifle",
            "cartridge_type": "6.5mm Creedmoor",
            "barrel_twist_ratio": "1:8",
            "barrel_length": "24 inches",
        }

        rifle = self.rifles_api.create_rifle(rifle_data, self.test_user_id)
        self.test_rifle_ids.append(rifle.id)

        # Verify creation
        self.assertIsNotNone(rifle.id)
        self.assertEqual(rifle.name, "TEST_Integration_Rifle")
        self.assertEqual(rifle.user_id, self.test_user_id)

        # Read it back
        read_rifle = self.rifles_api.get_rifle_by_id(
            rifle.id, self.test_user_id
        )
        self.assertIsNotNone(read_rifle)
        self.assertEqual(read_rifle.id, rifle.id)

        # Delete it
        deleted = self.rifles_api.delete_rifle(rifle.id, self.test_user_id)
        self.assertTrue(deleted)

        # Verify deletion
        read_after_delete = self.rifles_api.get_rifle_by_id(
            rifle.id, self.test_user_id
        )
        self.assertIsNone(read_after_delete)

        # Clear tracking
        self.test_rifle_ids.clear()

    def test_filter_operations(self):
        """Test filtering rifles by various criteria"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Create test rifles with different specs
        rifles_data = [
            {
                "name": "TEST_Filter_1",
                "cartridge_type": "6.5mm Creedmoor",
                "barrel_twist_ratio": "1:8",
            },
            {
                "name": "TEST_Filter_2",
                "cartridge_type": "308 Winchester",
                "barrel_twist_ratio": "1:10",
            },
            {
                "name": "TEST_Filter_3",
                "cartridge_type": "6.5mm Creedmoor",
                "barrel_twist_ratio": "1:7",
            },
        ]

        created_rifles = []
        for data in rifles_data:
            rifle = self.rifles_api.create_rifle(data, self.test_user_id)
            created_rifles.append(rifle)
            self.test_rifle_ids.append(rifle.id)

        try:
            # Filter by cartridge type
            creedmoor = self.rifles_api.filter_rifles(
                self.test_user_id, cartridge_type="6.5mm Creedmoor"
            )
            test_creedmoor = [
                r
                for r in creedmoor
                if r.id in [r.id for r in created_rifles]
            ]
            self.assertGreaterEqual(len(test_creedmoor), 2)

            # Filter by twist ratio
            one_eight = self.rifles_api.filter_rifles(
                self.test_user_id, twist_ratio="1:8"
            )
            test_one_eight = [
                r for r in one_eight if r.id in [r.id for r in created_rifles]
            ]
            self.assertGreaterEqual(len(test_one_eight), 1)

            # Filter by both
            specific = self.rifles_api.filter_rifles(
                self.test_user_id,
                cartridge_type="6.5mm Creedmoor",
                twist_ratio="1:8",
            )
            test_specific = [
                r for r in specific if r.id in [r.id for r in created_rifles]
            ]
            self.assertEqual(len(test_specific), 1)

        finally:
            # Clean up
            for rifle in created_rifles:
                self.rifles_api.delete_rifle(rifle.id, self.test_user_id)
            self.test_rifle_ids.clear()


if __name__ == "__main__":
    # Set up test environment
    # If environment variables are not set, will use mock mode
    if not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        print("Warning: SUPABASE_SERVICE_ROLE_KEY not set - running in mock mode")
        print("To run real integration tests, set environment variables:")
        print("  export SUPABASE_SERVICE_ROLE_KEY=your-key")

    # Run the tests
    unittest.main(verbosity=2)
