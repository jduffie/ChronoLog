import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

from bullets.models import BulletModel
from bullets.service import BulletsService

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBulletModel(unittest.TestCase):
    """Test the BulletModel dataclass"""

    def setUp(self):
        self.sample_record = {
            "id": "test-id-123",
            "user_id": "user-123",
            "manufacturer": "Hornady",
            "model": "ELD-M",
            "weight_grains": 147,
            "bullet_diameter_groove_mm": 6.5,
            "bore_diameter_land_mm": 6.35,
            "bullet_length_mm": 37.3,
            "ballistic_coefficient_g1": 0.697,
            "ballistic_coefficient_g7": 0.351,
            "sectional_density": 0.301,
            "min_req_twist_rate_in_per_rev": 8.0,
            "pref_twist_rate_in_per_rev": 7.0,
            "data_source_name": "Hornady Website",
            "data_source_url": "https://hornady.com",
        }

    def test_bullet_model_from_supabase_record(self):
        """Test creating BulletModel from Supabase record"""
        bullet = BulletModel.from_supabase_record(self.sample_record)

        self.assertEqual(bullet.id, "test-id-123")
        self.assertEqual(bullet.manufacturer, "Hornady")
        self.assertEqual(bullet.model, "ELD-M")
        self.assertEqual(bullet.weight_grains, 147)
        self.assertEqual(bullet.bullet_diameter_groove_mm, 6.5)
        self.assertEqual(bullet.bore_diameter_land_mm, 6.35)
        self.assertEqual(bullet.ballistic_coefficient_g1, 0.697)

    def test_bullet_model_from_supabase_records(self):
        """Test creating list of BulletModel from Supabase records"""
        records = [self.sample_record, self.sample_record.copy()]
        bullets = BulletModel.from_supabase_records(records)

        self.assertEqual(len(bullets), 2)
        self.assertIsInstance(bullets[0], BulletModel)
        self.assertIsInstance(bullets[1], BulletModel)

    def test_bullet_model_to_dict(self):
        """Test converting BulletModel to dictionary"""
        bullet = BulletModel.from_supabase_record(self.sample_record)
        bullet_dict = bullet.to_dict()

        self.assertEqual(bullet_dict["manufacturer"], "Hornady")
        self.assertEqual(bullet_dict["model"], "ELD-M")
        self.assertEqual(bullet_dict["weight_grains"], 147)
        self.assertNotIn("id", bullet_dict)  # ID should not be in to_dict()

    def test_bullet_model_display_name(self):
        """Test display_name property"""
        bullet = BulletModel.from_supabase_record(self.sample_record)
        expected = "Hornady ELD-M 147.0gr 6.35mm/6.5mm"
        self.assertEqual(bullet.display_name, expected)

    def test_bullet_model_with_optional_none_values(self):
        """Test BulletModel with None values for optional fields"""
        minimal_record = {
            "id": "test-id-123",
            "user_id": "user-123",
            "manufacturer": "Federal",
            "model": "Gold Medal",
            "weight_grains": 168,
            "bullet_diameter_groove_mm": 7.82,
            "bore_diameter_land_mm": 7.62,
            "bullet_length_mm": None,
            "ballistic_coefficient_g1": None,
            "ballistic_coefficient_g7": None,
            "sectional_density": None,
            "min_req_twist_rate_in_per_rev": None,
            "pref_twist_rate_in_per_rev": None,
            "data_source_name": None,
            "data_source_url": None,
        }

        bullet = BulletModel.from_supabase_record(minimal_record)
        self.assertIsNone(bullet.bullet_length_mm)
        self.assertIsNone(bullet.ballistic_coefficient_g1)
        self.assertEqual(
            bullet.display_name,
            "Federal Gold Medal 168.0gr 7.62mm/7.82mm")

    def test_bullet_model_display_name_variations(self):
        """Test display name with various formats"""
        # Test with decimal weight
        record = self.sample_record.copy()
        record["weight_grains"] = 147.5
        bullet = BulletModel.from_supabase_record(record)
        self.assertEqual(
            bullet.display_name,
            "Hornady ELD-M 147.5gr 6.35mm/6.5mm")

        # Test with very long manufacturer name
        record["manufacturer"] = "Very Long Manufacturer Name"
        bullet = BulletModel.from_supabase_record(record)
        self.assertIn("Very Long Manufacturer Name", bullet.display_name)

    def test_bullet_model_required_fields_validation(self):
        """Test that required fields are properly handled"""
        record = self.sample_record.copy()

        # Test with missing required field should raise KeyError
        del record["manufacturer"]
        with self.assertRaises(KeyError):
            BulletModel.from_supabase_record(record)

    def test_bullet_model_field_types(self):
        """Test that field types are handled correctly"""
        bullet = BulletModel.from_supabase_record(self.sample_record)

        # Test numeric field types
        self.assertIsInstance(bullet.weight_grains, (int, float))
        self.assertIsInstance(bullet.bullet_diameter_groove_mm, (int, float))
        self.assertIsInstance(bullet.bore_diameter_land_mm, (int, float))

        # Test optional float fields
        if bullet.ballistic_coefficient_g1 is not None:
            self.assertIsInstance(
                bullet.ballistic_coefficient_g1, (int, float))
        if bullet.sectional_density is not None:
            self.assertIsInstance(bullet.sectional_density, (int, float))

    def test_bullet_model_to_dict_excludes_id(self):
        """Test that to_dict properly excludes ID field"""
        bullet = BulletModel.from_supabase_record(self.sample_record)
        bullet_dict = bullet.to_dict()

        # ID should not be in dictionary
        self.assertNotIn("id", bullet_dict)

        # All other fields should be present
        expected_fields = [
            "user_id",
            "manufacturer",
            "model",
            "weight_grains",
            "bullet_diameter_groove_mm",
            "bore_diameter_land_mm",
            "bullet_length_mm",
            "ballistic_coefficient_g1",
            "ballistic_coefficient_g7",
            "sectional_density",
            "min_req_twist_rate_in_per_rev",
            "pref_twist_rate_in_per_rev",
            "data_source_name",
            "data_source_url"]

        for field in expected_fields:
            self.assertIn(field, bullet_dict)


class TestBulletsService(unittest.TestCase):
    """Test the BulletsService class"""

    def setUp(self):
        self.mock_supabase = Mock()
        self.service = BulletsService(self.mock_supabase)

        self.sample_data = [
            {
                "id": "test-id-123",
                "user_id": "user-123",
                "manufacturer": "Hornady",
                "model": "ELD-M",
                "weight_grains": 147,
                "bullet_diameter_groove_mm": 6.5,
                "bore_diameter_land_mm": 6.35,
                "bullet_length_mm": 37.3,
                "ballistic_coefficient_g1": 0.697,
                "ballistic_coefficient_g7": 0.351,
                "sectional_density": 0.301,
                "min_req_twist_rate_in_per_rev": 8.0,
                "pref_twist_rate_in_per_rev": 7.0,
                "data_source_name": "Hornady Website",
                "data_source_url": "https://hornady.com",
            }
        ]

    def test_get_all_bullets_success(self):
        """Test successful retrieval of all bullets"""
        mock_response = Mock()
        mock_response.data = self.sample_data

        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = (
            mock_response)

        bullets = self.service.get_all_bullets()

        self.assertEqual(len(bullets), 1)
        self.assertIsInstance(bullets[0], BulletModel)
        self.assertEqual(bullets[0].manufacturer, "Hornady")

    def test_get_all_bullets_empty(self):
        """Test retrieval when no bullets exist"""
        mock_response = Mock()
        mock_response.data = []

        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = (
            mock_response)

        bullets = self.service.get_all_bullets()

        self.assertEqual(len(bullets), 0)

    def test_get_bullet_by_id_success(self):
        """Test successful retrieval of bullet by ID"""
        mock_response = Mock()
        mock_response.data = self.sample_data[0]

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = (
            mock_response)

        bullet = self.service.get_bullet_by_id("test-id-123")

        self.assertIsInstance(bullet, BulletModel)
        self.assertEqual(bullet.manufacturer, "Hornady")

    def test_get_bullet_by_id_not_found(self):
        """Test retrieval when bullet ID not found"""
        mock_response = Mock()
        mock_response.data = None

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = (
            mock_response)

        bullet = self.service.get_bullet_by_id("nonexistent-id")

        self.assertIsNone(bullet)

    def test_create_bullet_success(self):
        """Test successful bullet creation"""
        mock_response = Mock()
        mock_response.data = self.sample_data

        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_response)

        bullet_data = {
            "user_id": "user-123",
            "manufacturer": "Hornady",
            "model": "ELD-M",
            "weight_grains": 147,
            "bullet_diameter_groove_mm": 6.5,
            "bore_diameter_land_mm": 6.35,
        }

        bullet = self.service.create_bullet(bullet_data)

        self.assertIsInstance(bullet, BulletModel)
        self.assertEqual(bullet.manufacturer, "Hornady")

    def test_create_bullet_generates_uuid(self):
        """Test that create_bullet generates a UUID for the 'id' field"""
        mock_response = Mock()
        mock_response.data = self.sample_data

        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_response)

        bullet_data = {
            "user_id": "user-123",
            "manufacturer": "Hornady",
            "model": "ELD-M",
            "weight_grains": 147,
            "bullet_diameter_groove_mm": 6.5,
            "bore_diameter_land_mm": 6.35,
        }

        bullet = self.service.create_bullet(bullet_data)

        # Verify that insert was called with a generated UUID
        insert_call_args = self.mock_supabase.table.return_value.insert.call_args[0][0]
        self.assertIn("id", insert_call_args)
        # UUID4 length with hyphens
        self.assertEqual(len(insert_call_args["id"]), 36)
        self.assertEqual(insert_call_args["manufacturer"], "Hornady")

        self.assertIsInstance(bullet, BulletModel)
        self.assertEqual(bullet.manufacturer, "Hornady")

    def test_create_bullet_duplicate_error(self):
        """Test bullet creation with duplicate constraint error"""
        mock_response = Mock()
        mock_response.data = None

        self.mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
            "duplicate key value violates unique constraint")

        bullet_data = {"manufacturer": "Test"}

        with self.assertRaises(Exception) as context:
            self.service.create_bullet(bullet_data)

        self.assertIn("already exists", str(context.exception))

    def test_update_bullet_success(self):
        """Test successful bullet update"""
        mock_response = Mock()
        mock_response.data = self.sample_data

        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = (
            mock_response)

        update_data = {"manufacturer": "Updated Hornady"}

        bullet = self.service.update_bullet("test-id-123", update_data)

        self.assertIsInstance(bullet, BulletModel)

    def test_delete_bullet_success(self):
        """Test successful bullet deletion"""
        mock_response = Mock()
        mock_response.data = [{"id": "test-id-123"}]

        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = (
            mock_response)

        result = self.service.delete_bullet("test-id-123")

        self.assertTrue(result)

    def test_delete_bullet_not_found(self):
        """Test bullet deletion when bullet not found"""
        mock_response = Mock()
        mock_response.data = []

        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = (
            mock_response)

        result = self.service.delete_bullet("nonexistent-id")

        self.assertFalse(result)

    def test_filter_bullets_with_filters(self):
        """Test filtering bullets with various criteria"""
        mock_response = Mock()
        mock_response.data = self.sample_data

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response)

        bullets = self.service.filter_bullets(
            manufacturer="Hornady", bore_diameter_mm=6.35, weight_grains=147
        )

        self.assertEqual(len(bullets), 1)
        self.assertIsInstance(bullets[0], BulletModel)

    def test_get_unique_manufacturers(self):
        """Test getting unique manufacturers"""
        with patch.object(self.service, "get_all_bullets") as mock_get_all:
            mock_bullets = [
                Mock(manufacturer="Hornady"),
                Mock(manufacturer="Federal"),
                Mock(manufacturer="Hornady"),  # Duplicate
            ]
            mock_get_all.return_value = mock_bullets

            manufacturers = self.service.get_unique_manufacturers()

            self.assertEqual(set(manufacturers), {"Federal", "Hornady"})
            self.assertEqual(
                manufacturers, [
                    "Federal", "Hornady"])  # Should be sorted

    def test_get_unique_bore_diameters(self):
        """Test getting unique bore diameters"""
        with patch.object(self.service, "get_all_bullets") as mock_get_all:
            mock_bullets = [
                Mock(bore_diameter_land_mm=6.35),
                Mock(bore_diameter_land_mm=7.62),
                Mock(bore_diameter_land_mm=6.35),  # Duplicate
            ]
            mock_get_all.return_value = mock_bullets

            diameters = self.service.get_unique_bore_diameters()

            self.assertEqual(set(diameters), {6.35, 7.62})
            self.assertEqual(diameters, [6.35, 7.62])  # Should be sorted

    def test_get_unique_weights(self):
        """Test getting unique weights"""
        with patch.object(self.service, "get_all_bullets") as mock_get_all:
            mock_bullets = [
                Mock(weight_grains=147),
                Mock(weight_grains=168),
                Mock(weight_grains=147),  # Duplicate
            ]
            mock_get_all.return_value = mock_bullets

            weights = self.service.get_unique_weights()

            self.assertEqual(set(weights), {147, 168})
            self.assertEqual(weights, [147, 168])  # Should be sorted

    def test_get_all_bullets_database_error(self):
        """Test database error handling in get_all_bullets"""
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.side_effect = Exception(
            "Database connection failed")

        with self.assertRaises(Exception) as context:
            self.service.get_all_bullets()

        self.assertIn("Error fetching bullets", str(context.exception))
        self.assertIn("Database connection failed", str(context.exception))

    def test_get_bullet_by_id_database_error(self):
        """Test database error handling in get_bullet_by_id"""
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception(
            "Database error")

        with self.assertRaises(Exception) as context:
            self.service.get_bullet_by_id("test-id")

        self.assertIn("Error fetching bullet", str(context.exception))

    def test_create_bullet_database_failure(self):
        """Test create bullet when database insert fails"""
        mock_response = Mock()
        mock_response.data = None  # Empty response indicates failure

        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        with self.assertRaises(Exception) as context:
            self.service.create_bullet({"manufacturer": "Test"})

        self.assertIn("Failed to create bullet entry", str(context.exception))

    def test_update_bullet_database_failure(self):
        """Test update bullet when database update fails"""
        mock_response = Mock()
        mock_response.data = None  # Empty response indicates failure

        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response

        with self.assertRaises(Exception) as context:
            self.service.update_bullet("test-id", {"manufacturer": "Updated"})

        self.assertIn("Failed to update bullet entry", str(context.exception))

    def test_update_bullet_database_error(self):
        """Test update bullet with database error"""
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception(
            "Update failed")

        with self.assertRaises(Exception) as context:
            self.service.update_bullet("test-id", {"manufacturer": "Updated"})

        self.assertIn("Error updating bullet", str(context.exception))

    def test_delete_bullet_database_error(self):
        """Test delete bullet with database error"""
        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.side_effect = Exception(
            "Delete failed")

        with self.assertRaises(Exception) as context:
            self.service.delete_bullet("test-id")

        self.assertIn("Error deleting bullet", str(context.exception))

    def test_filter_bullets_no_filters(self):
        """Test filtering bullets with no filters applied"""
        mock_response = Mock()
        mock_response.data = self.sample_data

        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

        bullets = self.service.filter_bullets()

        self.assertEqual(len(bullets), 1)
        self.assertIsInstance(bullets[0], BulletModel)

    def test_filter_bullets_single_filter(self):
        """Test filtering bullets with single filter"""
        mock_response = Mock()
        mock_response.data = self.sample_data

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

        bullets = self.service.filter_bullets(manufacturer="Hornady")

        self.assertEqual(len(bullets), 1)
        self.assertIsInstance(bullets[0], BulletModel)

    def test_filter_bullets_database_error(self):
        """Test filter bullets with database error"""
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.side_effect = Exception(
            "Filter failed")

        with self.assertRaises(Exception) as context:
            self.service.filter_bullets(manufacturer="Test")

        self.assertIn("Error filtering bullets", str(context.exception))

    def test_get_unique_manufacturers_database_error(self):
        """Test get unique manufacturers with database error"""
        with patch.object(self.service, "get_all_bullets") as mock_get_all:
            mock_get_all.side_effect = Exception("Database error")

            with self.assertRaises(Exception) as context:
                self.service.get_unique_manufacturers()

            self.assertIn(
                "Error getting manufacturers", str(
                    context.exception))

    def test_get_unique_bore_diameters_database_error(self):
        """Test get unique bore diameters with database error"""
        with patch.object(self.service, "get_all_bullets") as mock_get_all:
            mock_get_all.side_effect = Exception("Database error")

            with self.assertRaises(Exception) as context:
                self.service.get_unique_bore_diameters()

            self.assertIn(
                "Error getting bore diameters", str(
                    context.exception))

    def test_get_unique_weights_database_error(self):
        """Test get unique weights with database error"""
        with patch.object(self.service, "get_all_bullets") as mock_get_all:
            mock_get_all.side_effect = Exception("Database error")

            with self.assertRaises(Exception) as context:
                self.service.get_unique_weights()

            self.assertIn("Error getting weights", str(context.exception))

    def test_service_initialization(self):
        """Test service initialization with supabase client"""
        service = BulletsService(self.mock_supabase)
        self.assertEqual(service.supabase, self.mock_supabase)

    def test_create_bullet_with_optional_fields(self):
        """Test creating bullet with optional fields populated"""
        mock_response = Mock()
        mock_response.data = self.sample_data

        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        bullet_data = {
            "user_id": "user-123",
            "manufacturer": "Hornady",
            "model": "ELD-M",
            "weight_grains": 147,
            "bullet_diameter_groove_mm": 6.5,
            "bore_diameter_land_mm": 6.35,
            "bullet_length_mm": 37.3,
            "ballistic_coefficient_g1": 0.697,
            "ballistic_coefficient_g7": 0.351,
            "sectional_density": 0.301,
            "min_req_twist_rate_in_per_rev": 8.0,
            "pref_twist_rate_in_per_rev": 7.0,
            "data_source_name": "Test Source",
            "data_source_url": "https://test.com",
        }

        bullet = self.service.create_bullet(bullet_data)

        # Verify UUID was generated
        insert_call_args = self.mock_supabase.table.return_value.insert.call_args[0][0]
        self.assertIn("id", insert_call_args)

        # Verify all fields were passed through
        for key, value in bullet_data.items():
            self.assertEqual(insert_call_args[key], value)

        self.assertIsInstance(bullet, BulletModel)


class TestBulletsPageStructure(unittest.TestCase):
    """Test bullets page structure and imports"""

    def test_bullets_page_exists(self):
        """Test that the bullets page file exists"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "9_Bullets.py"
        )
        self.assertTrue(
            os.path.exists(page_path), f"Bullets page not found at {page_path}"
        )

    def test_bullets_page_has_required_imports(self):
        """Test that bullets page has required imports"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "9_Bullets.py"
        )

        with open(page_path, "r") as f:
            content = f.read()

        # Check for required imports
        self.assertIn("import streamlit as st", content)
        self.assertIn(
            "from bullets.create_tab import render_create_bullets_tab", content
        )
        self.assertIn(
            "from bullets.view_tab import render_view_bullets_tab",
            content)
        self.assertIn("from auth import handle_auth", content)

    def test_bullets_models_has_service_import(self):
        """Test that bullets create_tab imports the service"""
        create_tab_path = os.path.join(
            os.path.dirname(__file__), "create_tab.py")

        with open(create_tab_path, "r") as f:
            content = f.read()

        self.assertIn("from .api import BulletsAPI", content)

    def test_bullets_view_tab_has_service_import(self):
        """Test that bullets view_tab imports the API"""
        view_tab_path = os.path.join(os.path.dirname(__file__), "view_tab.py")

        with open(view_tab_path, "r") as f:
            content = f.read()

        self.assertIn("from .api import BulletsAPI", content)


class TestBulletsIntegration(unittest.TestCase):
    """Integration tests for bullets module components"""

    def setUp(self):
        self.mock_supabase = Mock()
        self.service = BulletsService(self.mock_supabase)

        # Sample CSV data similar to what's in datasets
        self.csv_data = [
            {
                "user_id": "",
                "manufacturer": "Sierra",
                "model": "MatchKing",
                "weight_grains": "123",
                "bullet_diameter_groove_mm": "6.71",
                "bore_diameter_land_mm": "6.50",
                "bullet_length_mm": "29.21",
                "ballistic_coefficient_g1": "0.510",
                "ballistic_coefficient_g7": "0.257",
                "sectional_density": "0.252",
                "min_req_twist_rate_in_per_rev": "8.0",
                "pref_twist_rate_in_per_rev": "",
                "id": "4e0128b3-54c1-4f47-bb36-4e6315e37011",
                "data_source_name": "Sierra Official",
                "data_source_url": "https://www.sierrabullets.com/product/6-5mm-264-cal-123-gr-matchking-hpbt/"
            }
        ]

    def test_csv_data_to_model_conversion(self):
        """Test converting CSV dataset data to BulletModel objects"""
        # Convert string values from CSV to appropriate types
        processed_record = {
            "id": self.csv_data[0]["id"],
            "user_id": self.csv_data[0]["user_id"] or "admin",
            "manufacturer": self.csv_data[0]["manufacturer"],
            "model": self.csv_data[0]["model"],
            "weight_grains": float(self.csv_data[0]["weight_grains"]),
            "bullet_diameter_groove_mm": float(self.csv_data[0]["bullet_diameter_groove_mm"]),
            "bore_diameter_land_mm": float(self.csv_data[0]["bore_diameter_land_mm"]),
            "bullet_length_mm": float(self.csv_data[0]["bullet_length_mm"]),
            "ballistic_coefficient_g1": float(self.csv_data[0]["ballistic_coefficient_g1"]),
            "ballistic_coefficient_g7": float(self.csv_data[0]["ballistic_coefficient_g7"]),
            "sectional_density": float(self.csv_data[0]["sectional_density"]),
            "min_req_twist_rate_in_per_rev": float(self.csv_data[0]["min_req_twist_rate_in_per_rev"]),
            "pref_twist_rate_in_per_rev": None,  # Empty string should be None
            "data_source_name": self.csv_data[0]["data_source_name"],
            "data_source_url": self.csv_data[0]["data_source_url"]
        }

        bullet = BulletModel.from_supabase_record(processed_record)

        self.assertEqual(bullet.manufacturer, "Sierra")
        self.assertEqual(bullet.model, "MatchKing")
        self.assertEqual(bullet.weight_grains, 123)
        self.assertEqual(bullet.bullet_diameter_groove_mm, 6.71)
        self.assertIsNone(bullet.pref_twist_rate_in_per_rev)
        self.assertEqual(
            bullet.display_name,
            "Sierra MatchKing 123.0gr 6.5mm/6.71mm")

    def test_bulk_bullet_creation_workflow(self):
        """Test creating multiple bullets in a batch workflow"""
        mock_responses = []
        for i in range(3):
            mock_response = Mock()
            mock_response.data = [{
                "id": f"test-id-{i}",
                "user_id": "admin",
                "manufacturer": f"Manufacturer{i}",
                "model": f"Model{i}",
                "weight_grains": 100 + i,
                "bullet_diameter_groove_mm": 6.5,
                "bore_diameter_land_mm": 6.35,
                "bullet_length_mm": None,
                "ballistic_coefficient_g1": None,
                "ballistic_coefficient_g7": None,
                "sectional_density": None,
                "min_req_twist_rate_in_per_rev": None,
                "pref_twist_rate_in_per_rev": None,
                "data_source_name": None,
                "data_source_url": None,
            }]
            mock_responses.append(mock_response)

        self.mock_supabase.table.return_value.insert.return_value.execute.side_effect = mock_responses

        bullets = []
        for i in range(3):
            bullet_data = {
                "user_id": "admin",
                "manufacturer": f"Manufacturer{i}",
                "model": f"Model{i}",
                "weight_grains": 100 + i,
                "bullet_diameter_groove_mm": 6.5,
                "bore_diameter_land_mm": 6.35,
            }

            bullet = self.service.create_bullet(bullet_data)
            bullets.append(bullet)

        # Verify all bullets were created successfully
        self.assertEqual(len(bullets), 3)
        for i, bullet in enumerate(bullets):
            self.assertEqual(bullet.manufacturer, f"Manufacturer{i}")
            self.assertEqual(bullet.weight_grains, 100 + i)

    def test_service_model_integration(self):
        """Test integration between service and model classes"""
        # Mock database response
        mock_response = Mock()
        mock_response.data = [
            {
                "id": "test-id-123",
                "user_id": "user-123",
                "manufacturer": "Hornady",
                "model": "ELD-M",
                "weight_grains": 147,
                "bullet_diameter_groove_mm": 6.5,
                "bore_diameter_land_mm": 6.35,
                "bullet_length_mm": 37.3,
                "ballistic_coefficient_g1": 0.697,
                "ballistic_coefficient_g7": 0.351,
                "sectional_density": 0.301,
                "min_req_twist_rate_in_per_rev": 8.0,
                "pref_twist_rate_in_per_rev": 7.0,
                "data_source_name": "Hornady Website",
                "data_source_url": "https://hornady.com",
            },
            {
                "id": "test-id-456",
                "user_id": "user-456",
                "manufacturer": "Federal",
                "model": "Gold Medal",
                "weight_grains": 168,
                "bullet_diameter_groove_mm": 7.82,
                "bore_diameter_land_mm": 7.62,
                "bullet_length_mm": None,
                "ballistic_coefficient_g1": None,
                "ballistic_coefficient_g7": None,
                "sectional_density": None,
                "min_req_twist_rate_in_per_rev": None,
                "pref_twist_rate_in_per_rev": None,
                "data_source_name": None,
                "data_source_url": None,
            }
        ]

        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

        # Get all bullets and test model integration
        bullets = self.service.get_all_bullets()

        # Test service returns properly constructed models
        self.assertEqual(len(bullets), 2)

        # Test first bullet (complete data)
        hornady_bullet = bullets[0]
        self.assertIsInstance(hornady_bullet, BulletModel)
        self.assertEqual(hornady_bullet.manufacturer, "Hornady")
        self.assertEqual(
            hornady_bullet.display_name,
            "Hornady ELD-M 147.0gr 6.35mm/6.5mm")

        # Test bullet model to_dict works correctly
        hornady_dict = hornady_bullet.to_dict()
        self.assertEqual(hornady_dict["manufacturer"], "Hornady")
        self.assertNotIn("id", hornady_dict)

        # Test second bullet (minimal data)
        federal_bullet = bullets[1]
        self.assertEqual(federal_bullet.manufacturer, "Federal")
        self.assertIsNone(federal_bullet.ballistic_coefficient_g1)
        self.assertEqual(
            federal_bullet.display_name,
            "Federal Gold Medal 168.0gr 7.62mm/7.82mm")

    def test_filter_and_unique_values_integration(self):
        """Test integration of filtering and unique value extraction"""
        # Mock different bullets for filtering tests
        all_bullets_data = [{"id": "6mm-1",
                             "user_id": "admin",
                             "manufacturer": "Hornady",
                             "model": "ELD-M",
                             "weight_grains": 108,
                             "bullet_diameter_groove_mm": 6.5,
                             "bore_diameter_land_mm": 6.0,
                             "bullet_length_mm": None,
                             "ballistic_coefficient_g1": None,
                             "ballistic_coefficient_g7": None,
                             "sectional_density": None,
                             "min_req_twist_rate_in_per_rev": None,
                             "pref_twist_rate_in_per_rev": None,
                             "data_source_name": None,
                             "data_source_url": None,
                             },
                            {"id": "308-1",
                             "user_id": "admin",
                             "manufacturer": "Federal",
                             "model": "Gold Medal",
                             "weight_grains": 168,
                             "bullet_diameter_groove_mm": 7.82,
                             "bore_diameter_land_mm": 7.62,
                             "bullet_length_mm": None,
                             "ballistic_coefficient_g1": None,
                             "ballistic_coefficient_g7": None,
                             "sectional_density": None,
                             "min_req_twist_rate_in_per_rev": None,
                             "pref_twist_rate_in_per_rev": None,
                             "data_source_name": None,
                             "data_source_url": None,
                             },
                            {"id": "6mm-2",
                             "user_id": "admin",
                             "manufacturer": "Hornady",
                             "model": "ELD-X",
                             "weight_grains": 103,
                             "bullet_diameter_groove_mm": 6.5,
                             "bore_diameter_land_mm": 6.0,
                             "bullet_length_mm": None,
                             "ballistic_coefficient_g1": None,
                             "ballistic_coefficient_g7": None,
                             "sectional_density": None,
                             "min_req_twist_rate_in_per_rev": None,
                             "pref_twist_rate_in_per_rev": None,
                             "data_source_name": None,
                             "data_source_url": None,
                             }]

        # Mock get_all_bullets for unique value methods
        with patch.object(self.service, 'get_all_bullets') as mock_get_all:
            mock_bullets = BulletModel.from_supabase_records(all_bullets_data)
            mock_get_all.return_value = mock_bullets

            # Test unique manufacturers
            manufacturers = self.service.get_unique_manufacturers()
            self.assertEqual(set(manufacturers), {"Federal", "Hornady"})
            self.assertEqual(manufacturers, ["Federal", "Hornady"])  # Sorted

            # Test unique bore diameters
            bore_diameters = self.service.get_unique_bore_diameters()
            self.assertEqual(set(bore_diameters), {6.0, 7.62})
            self.assertEqual(bore_diameters, [6.0, 7.62])  # Sorted

            # Test unique weights
            weights = self.service.get_unique_weights()
            self.assertEqual(set(weights), {103, 108, 168})
            self.assertEqual(weights, [103, 108, 168])  # Sorted

        # Test filtering by manufacturer
        mock_filter_response = Mock()
        mock_filter_response.data = [
            all_bullets_data[0],
            all_bullets_data[2]]  # Only Hornady bullets
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_filter_response

        filtered_bullets = self.service.filter_bullets(manufacturer="Hornady")
        self.assertEqual(len(filtered_bullets), 2)
        for bullet in filtered_bullets:
            self.assertEqual(bullet.manufacturer, "Hornady")

    def test_error_recovery_and_data_consistency(self):
        """Test error handling doesn't corrupt data state"""
        # Test that failed operations don't leave the service in a bad state

        # First, simulate successful operation
        mock_success = Mock()
        mock_success.data = [{
            "id": "test-success",
            "user_id": "user-123",
            "manufacturer": "Test Manufacturer",
            "model": "Test Model",
            "weight_grains": 150,
            "bullet_diameter_groove_mm": 7.0,
            "bore_diameter_land_mm": 6.8,
            "bullet_length_mm": None,
            "ballistic_coefficient_g1": None,
            "ballistic_coefficient_g7": None,
            "sectional_density": None,
            "min_req_twist_rate_in_per_rev": None,
            "pref_twist_rate_in_per_rev": None,
            "data_source_name": None,
            "data_source_url": None,
        }]

        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_success

        # Successful operation
        success_bullet = self.service.create_bullet({
            "user_id": "user-123",
            "manufacturer": "Test Manufacturer",
            "model": "Test Model",
            "weight_grains": 150,
            "bullet_diameter_groove_mm": 7.0,
            "bore_diameter_land_mm": 6.8,
        })

        self.assertIsInstance(success_bullet, BulletModel)
        self.assertEqual(success_bullet.manufacturer, "Test Manufacturer")

        # Now simulate failure
        self.mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
            "Database error")

        # Failed operation should raise exception without corrupting state
        with self.assertRaises(Exception):
            self.service.create_bullet({
                "user_id": "user-456",
                "manufacturer": "Failed Manufacturer",
                "model": "Failed Model",
                "weight_grains": 160,
                "bullet_diameter_groove_mm": 7.2,
                "bore_diameter_land_mm": 7.0,
            })

        # Service should still be usable after failure
        self.assertIsInstance(self.service, BulletsService)
        self.assertEqual(self.service.supabase, self.mock_supabase)

    def test_real_world_dataset_processing(self):
        """Test processing data that matches real dataset structure"""
        # Test with actual data structure from berger_65mm_bullets.csv
        real_dataset_record = {
            "id": "4e0128b3-54c1-4f47-bb36-4e6315e37011",
            "user_id": "",  # Empty in CSV
            "manufacturer": "Sierra",
            "model": "MatchKing",
            "weight_grains": 123,
            "bullet_diameter_groove_mm": 6.71,
            "bore_diameter_land_mm": 6.50,
            "bullet_length_mm": 29.21,
            "ballistic_coefficient_g1": 0.510,
            "ballistic_coefficient_g7": 0.257,
            "sectional_density": 0.252,
            "min_req_twist_rate_in_per_rev": 8.0,
            "pref_twist_rate_in_per_rev": None,  # Empty in CSV
            "data_source_name": "Sierra Official",
            "data_source_url": "https://www.sierrabullets.com/product/6-5mm-264-cal-123-gr-matchking-hpbt/"
        }

        # Test model creation from real dataset
        bullet = BulletModel.from_supabase_record(real_dataset_record)

        # Verify all fields are correctly processed
        self.assertEqual(bullet.id, "4e0128b3-54c1-4f47-bb36-4e6315e37011")
        self.assertEqual(bullet.manufacturer, "Sierra")
        self.assertEqual(bullet.model, "MatchKing")
        self.assertEqual(bullet.weight_grains, 123)
        self.assertEqual(bullet.bullet_diameter_groove_mm, 6.71)
        self.assertEqual(bullet.bore_diameter_land_mm, 6.50)
        self.assertEqual(bullet.bullet_length_mm, 29.21)
        self.assertEqual(bullet.ballistic_coefficient_g1, 0.510)
        self.assertEqual(bullet.ballistic_coefficient_g7, 0.257)
        self.assertEqual(bullet.sectional_density, 0.252)
        self.assertEqual(bullet.min_req_twist_rate_in_per_rev, 8.0)
        self.assertIsNone(bullet.pref_twist_rate_in_per_rev)
        self.assertEqual(bullet.data_source_name, "Sierra Official")

        # Test display formatting
        expected_display = "Sierra MatchKing 123.0gr 6.5mm/6.71mm"
        self.assertEqual(bullet.display_name, expected_display)

        # Test to_dict doesn't include id but includes all other fields
        bullet_dict = bullet.to_dict()
        self.assertNotIn("id", bullet_dict)
        self.assertEqual(bullet_dict["manufacturer"], "Sierra")
        self.assertEqual(
            bullet_dict["data_source_url"],
            "https://www.sierrabullets.com/product/6-5mm-264-cal-123-gr-matchking-hpbt/")


class TestBulletsTabIntegration(unittest.TestCase):
    """Integration tests for bullets tab components"""

    def setUp(self):
        self.mock_supabase = Mock()
        self.mock_user = {
            "email": "test@example.com",
            "user_metadata": {"is_admin": True}
        }
        self.non_admin_user = {
            "email": "regular@example.com",
            "user_metadata": {"is_admin": False}
        }

    @patch('bullets.create_tab.BulletsAPI')
    @patch('streamlit.form')
    @patch('streamlit.header')
    def test_create_tab_admin_access_integration(
            self, mock_header, mock_form, mock_api_class):
        """Test that create tab properly integrates with admin access control"""
        from bullets.create_tab import render_create_bullets_tab

        mock_api = Mock()
        mock_api_class.return_value = mock_api

        # Mock form context manager
        mock_form_context = MagicMock()
        mock_form.return_value.__enter__ = Mock(return_value=mock_form_context)
        mock_form.return_value.__exit__ = Mock(return_value=None)

        # Should work for admin user
        with patch('streamlit.warning') as mock_warning, \
                patch('streamlit.info') as mock_info:

            render_create_bullets_tab(self.mock_user, self.mock_supabase)

            # Should not show warning/info for admin
            mock_warning.assert_not_called()
            # Info might be called for help text, but not for access denied

            # Should initialize API
            mock_api_class.assert_called_once_with(self.mock_supabase)

    @patch('bullets.create_tab.BulletsAPI')
    @patch('streamlit.warning')
    @patch('streamlit.info')
    @patch('streamlit.header')
    def test_create_tab_non_admin_access_integration(
            self, mock_header, mock_info, mock_warning, mock_api_class):
        """Test that create tab blocks non-admin users"""
        from bullets.create_tab import render_create_bullets_tab

        render_create_bullets_tab(self.non_admin_user, self.mock_supabase)

        # Should show access denied warning
        mock_warning.assert_called_with(
            "🔒 Access Denied: Only administrators can create bullet entries.")
        mock_info.assert_called_with(
            "This global bullet database is maintained by administrators to ensure data quality and consistency.")

        # Should not initialize API for non-admin
        mock_api_class.assert_not_called()


if __name__ == "__main__":
    unittest.main()
