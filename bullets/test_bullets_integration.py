"""
Integration tests for Bullets module.

These tests verify end-to-end operations with real Supabase database:
- Loading bullet data from CSV
- Writing to remote database
- Reading back data
- Cleaning up test data

Run with: python -m pytest bullets/test_bullets_integration.py -v -m integration
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


class BaseBulletsIntegrationTest(unittest.TestCase):
    """Base class for bullets integration tests with common setup"""

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

        # Initialize BulletsAPI
        cls.api = BulletsAPI(cls.supabase)

    def setUp(self):
        """Set up each test with clean state"""
        self.test_bullet_ids: List[str] = []  # Track created bullets for cleanup

    def tearDown(self):
        """Clean up test data after each test"""
        if not self.mock_mode:
            # Clean up test bullets (delete in reverse order of creation)
            for bullet_id in reversed(self.test_bullet_ids):
                try:
                    self.api.delete_bullet(bullet_id)
                except Exception as e:
                    # Best effort cleanup - bullet may have already been deleted
                    print(f"Cleanup warning: Could not delete bullet {bullet_id}: {e}")


@pytest.mark.integration
@pytest.mark.database
class TestBulletsCSVIntegration(BaseBulletsIntegrationTest):
    """Test loading bullets from CSV, writing to DB, reading back, and cleanup"""

    def load_bullets_from_csv(self, csv_path: str) -> List[dict]:
        """
        Load bullet data from CSV file.

        Args:
            csv_path: Path to CSV file

        Returns:
            List of bullet data dictionaries
        """
        bullets_data = []

        with open(csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert numeric fields from strings
                bullet_data = {
                    "user_id": self.test_user_id,  # Admin user for test
                    "manufacturer": row["manufacturer"],
                    "model": row["model"],
                    "weight_grains": float(row["weight_grains"]),
                    "bullet_diameter_groove_mm": float(
                        row["bullet_diameter_groove_mm"]
                    ),
                    "bore_diameter_land_mm": float(row["bore_diameter_land_mm"]),
                }

                # Add optional fields if present and not empty
                if row.get("bullet_length_mm"):
                    bullet_data["bullet_length_mm"] = float(row["bullet_length_mm"])
                if row.get("ballistic_coefficient_g1"):
                    bullet_data["ballistic_coefficient_g1"] = float(
                        row["ballistic_coefficient_g1"]
                    )
                if row.get("ballistic_coefficient_g7"):
                    bullet_data["ballistic_coefficient_g7"] = float(
                        row["ballistic_coefficient_g7"]
                    )
                if row.get("sectional_density"):
                    bullet_data["sectional_density"] = float(row["sectional_density"])
                if row.get("min_req_twist_rate_in_per_rev"):
                    bullet_data["min_req_twist_rate_in_per_rev"] = float(
                        row["min_req_twist_rate_in_per_rev"]
                    )
                if row.get("pref_twist_rate_in_per_rev"):
                    bullet_data["pref_twist_rate_in_per_rev"] = float(
                        row["pref_twist_rate_in_per_rev"]
                    )
                if row.get("data_source_name"):
                    bullet_data["data_source_name"] = row["data_source_name"]
                if row.get("data_source_url"):
                    bullet_data["data_source_url"] = row["data_source_url"]

                bullets_data.append(bullet_data)

        return bullets_data

    def test_csv_load_write_read_delete_workflow(self):
        """
        Complete integration test:
        1. Load bullets from CSV
        2. Write to Supabase
        3. Read back and verify
        4. Delete and verify cleanup
        """
        # Path to test CSV
        csv_path = os.path.join(
            os.path.dirname(__file__), "test_data", "test_bullets.csv"
        )

        # Step 1: Load bullets from CSV
        bullets_data = self.load_bullets_from_csv(csv_path)
        self.assertEqual(len(bullets_data), 3, "Should load 3 test bullets from CSV")

        if self.mock_mode:
            # Mock mode: Skip actual database operations
            print("Running in mock mode - skipping real database operations")
            return

        created_bullets: List[BulletModel] = []

        try:
            # Step 2: Write bullets to database
            for bullet_data in bullets_data:
                created_bullet = self.api.create_bullet(bullet_data)
                created_bullets.append(created_bullet)
                self.test_bullet_ids.append(created_bullet.id)

            self.assertEqual(
                len(created_bullets), 3, "Should create 3 bullets in database"
            )

            # Verify created bullets have IDs
            for bullet in created_bullets:
                self.assertIsNotNone(bullet.id, "Created bullet should have an ID")
                self.assertTrue(
                    bullet.manufacturer.startswith("TEST_"),
                    "Test bullet should have TEST_ prefix",
                )

            # Step 3: Read back bullets and verify
            for i, created_bullet in enumerate(created_bullets):
                # Read by ID
                read_bullet = self.api.get_bullet_by_id(created_bullet.id)

                self.assertIsNotNone(
                    read_bullet, f"Should find bullet {created_bullet.id}"
                )
                self.assertEqual(
                    read_bullet.id,
                    created_bullet.id,
                    "IDs should match",
                )
                self.assertEqual(
                    read_bullet.manufacturer,
                    bullets_data[i]["manufacturer"],
                    "Manufacturer should match original CSV data",
                )
                self.assertEqual(
                    read_bullet.model,
                    bullets_data[i]["model"],
                    "Model should match original CSV data",
                )
                self.assertAlmostEqual(
                    read_bullet.weight_grains,
                    bullets_data[i]["weight_grains"],
                    places=1,
                    msg="Weight should match original CSV data",
                )
                self.assertAlmostEqual(
                    read_bullet.bore_diameter_land_mm,
                    bullets_data[i]["bore_diameter_land_mm"],
                    places=2,
                    msg="Bore diameter should match original CSV data",
                )

                # Verify display_name uses bore_diameter_land_mm (caliber)
                expected_display = f"{read_bullet.manufacturer} {read_bullet.model} - {read_bullet.weight_grains}gr - {read_bullet.bore_diameter_land_mm}mm"
                self.assertEqual(
                    read_bullet.display_name,
                    expected_display,
                    "Display name should use bore_diameter_land_mm for caliber",
                )

            # Test batch read
            all_test_ids = [b.id for b in created_bullets]
            batch_bullets = self.api.get_bullets_by_ids(all_test_ids)
            self.assertEqual(
                len(batch_bullets), 3, "Batch read should return all 3 bullets"
            )

            # Verify we can filter by manufacturer
            test_sierra_bullets = self.api.filter_bullets(manufacturer="TEST_Sierra")
            self.assertGreaterEqual(
                len(test_sierra_bullets),
                1,
                "Should find at least 1 TEST_Sierra bullet",
            )
            sierra_bullet = next(
                b for b in test_sierra_bullets if b.manufacturer == "TEST_Sierra"
            )
            self.assertEqual(sierra_bullet.model, "TEST_MatchKing")

            # Step 4: Delete bullets and verify cleanup
            for bullet in created_bullets:
                deleted = self.api.delete_bullet(bullet.id)
                self.assertTrue(deleted, f"Should successfully delete bullet {bullet.id}")

                # Verify bullet is gone
                read_after_delete = self.api.get_bullet_by_id(bullet.id)
                self.assertIsNone(
                    read_after_delete,
                    f"Bullet {bullet.id} should not exist after deletion",
                )

            # Clear the test_bullet_ids since we manually deleted them
            self.test_bullet_ids.clear()

        except Exception as e:
            # If test fails, ensure cleanup still happens in tearDown
            self.fail(f"Integration test failed: {str(e)}")


@pytest.mark.integration
@pytest.mark.database
class TestBulletsAPIIntegration(BaseBulletsIntegrationTest):
    """Test BulletsAPI operations against real database"""

    def test_get_all_bullets_returns_data(self):
        """Test that get_all_bullets returns data from real database"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # This should return existing bullets from the database
        # (including any pre-existing data, not just test data)
        bullets = self.api.get_all_bullets()

        # Should return a list (may be empty if database is empty)
        self.assertIsInstance(bullets, list, "Should return a list of bullets")

        # If there are bullets, verify they are BulletModel instances
        if bullets:
            self.assertIsInstance(
                bullets[0], BulletModel, "Should return BulletModel instances"
            )

    def test_filter_operations(self):
        """Test various filter operations"""
        if self.mock_mode:
            print("Running in mock mode - skipping test")
            return

        # Get unique manufacturers
        manufacturers = self.api.get_unique_manufacturers()
        self.assertIsInstance(manufacturers, list, "Should return list of manufacturers")

        # Get unique bore diameters
        bore_diameters = self.api.get_unique_bore_diameters()
        self.assertIsInstance(
            bore_diameters, list, "Should return list of bore diameters"
        )

        # Get unique weights
        weights = self.api.get_unique_weights()
        self.assertIsInstance(weights, list, "Should return list of weights")

        # All lists should contain unique values
        self.assertEqual(
            len(manufacturers),
            len(set(manufacturers)),
            "Manufacturers should be unique",
        )
        self.assertEqual(
            len(bore_diameters),
            len(set(bore_diameters)),
            "Bore diameters should be unique",
        )
        self.assertEqual(len(weights), len(set(weights)), "Weights should be unique")


if __name__ == "__main__":
    # Set up test environment
    # If environment variables are not set, will use mock mode
    if not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        print("Warning: SUPABASE_SERVICE_ROLE_KEY not set - running in mock mode")
        print("To run real integration tests, set environment variables:")
        print("  export SUPABASE_SERVICE_ROLE_KEY=your-key")

    # Run the tests
    unittest.main(verbosity=2)