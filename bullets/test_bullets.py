import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bullets.models import BulletModel
from bullets.service import BulletsService


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
            "data_source_url": "https://hornady.com"
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
        expected = "Hornady ELD-M - 147gr - 6.5mm"
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
            "data_source_url": None
        }
        
        bullet = BulletModel.from_supabase_record(minimal_record)
        self.assertIsNone(bullet.bullet_length_mm)
        self.assertIsNone(bullet.ballistic_coefficient_g1)
        self.assertEqual(bullet.display_name, "Federal Gold Medal - 168gr - 7.82mm")


class TestBulletsService(unittest.TestCase):
    """Test the BulletsService class"""

    def setUp(self):
        self.mock_supabase = Mock()
        self.service = BulletsService(self.mock_supabase)
        
        self.sample_data = [{
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
            "data_source_url": "https://hornady.com"
        }]

    def test_get_all_bullets_success(self):
        """Test successful retrieval of all bullets"""
        mock_response = Mock()
        mock_response.data = self.sample_data
        
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
        
        bullets = self.service.get_all_bullets()
        
        self.assertEqual(len(bullets), 1)
        self.assertIsInstance(bullets[0], BulletModel)
        self.assertEqual(bullets[0].manufacturer, "Hornady")

    def test_get_all_bullets_empty(self):
        """Test retrieval when no bullets exist"""
        mock_response = Mock()
        mock_response.data = []
        
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
        
        bullets = self.service.get_all_bullets()
        
        self.assertEqual(len(bullets), 0)

    def test_get_bullet_by_id_success(self):
        """Test successful retrieval of bullet by ID"""
        mock_response = Mock()
        mock_response.data = self.sample_data[0]
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        
        bullet = self.service.get_bullet_by_id("test-id-123")
        
        self.assertIsInstance(bullet, BulletModel)
        self.assertEqual(bullet.manufacturer, "Hornady")

    def test_get_bullet_by_id_not_found(self):
        """Test retrieval when bullet ID not found"""
        mock_response = Mock()
        mock_response.data = None
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        
        bullet = self.service.get_bullet_by_id("nonexistent-id")
        
        self.assertIsNone(bullet)

    def test_create_bullet_success(self):
        """Test successful bullet creation"""
        mock_response = Mock()
        mock_response.data = self.sample_data
        
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        bullet_data = {
            "user_id": "user-123",
            "manufacturer": "Hornady",
            "model": "ELD-M",
            "weight_grains": 147,
            "bullet_diameter_groove_mm": 6.5,
            "bore_diameter_land_mm": 6.35
        }
        
        bullet = self.service.create_bullet(bullet_data)
        
        self.assertIsInstance(bullet, BulletModel)
        self.assertEqual(bullet.manufacturer, "Hornady")

    def test_create_bullet_generates_uuid(self):
        """Test that create_bullet generates a UUID for the 'id' field"""
        mock_response = Mock()
        mock_response.data = self.sample_data
        
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        bullet_data = {
            "user_id": "user-123",
            "manufacturer": "Hornady",
            "model": "ELD-M",
            "weight_grains": 147,
            "bullet_diameter_groove_mm": 6.5,
            "bore_diameter_land_mm": 6.35
        }
        
        bullet = self.service.create_bullet(bullet_data)
        
        # Verify that insert was called with a generated UUID
        insert_call_args = self.mock_supabase.table.return_value.insert.call_args[0][0]
        self.assertIn("id", insert_call_args)
        self.assertEqual(len(insert_call_args["id"]), 36)  # UUID4 length with hyphens
        self.assertEqual(insert_call_args["manufacturer"], "Hornady")
        
        self.assertIsInstance(bullet, BulletModel)
        self.assertEqual(bullet.manufacturer, "Hornady")

    def test_create_bullet_duplicate_error(self):
        """Test bullet creation with duplicate constraint error"""
        mock_response = Mock()
        mock_response.data = None
        
        self.mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
            "duplicate key value violates unique constraint"
        )
        
        bullet_data = {"manufacturer": "Test"}
        
        with self.assertRaises(Exception) as context:
            self.service.create_bullet(bullet_data)
        
        self.assertIn("already exists", str(context.exception))

    def test_update_bullet_success(self):
        """Test successful bullet update"""
        mock_response = Mock()
        mock_response.data = self.sample_data
        
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        
        update_data = {"manufacturer": "Updated Hornady"}
        
        bullet = self.service.update_bullet("test-id-123", update_data)
        
        self.assertIsInstance(bullet, BulletModel)

    def test_delete_bullet_success(self):
        """Test successful bullet deletion"""
        mock_response = Mock()
        mock_response.data = [{"id": "test-id-123"}]
        
        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_response
        
        result = self.service.delete_bullet("test-id-123")
        
        self.assertTrue(result)

    def test_delete_bullet_not_found(self):
        """Test bullet deletion when bullet not found"""
        mock_response = Mock()
        mock_response.data = []
        
        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_response
        
        result = self.service.delete_bullet("nonexistent-id")
        
        self.assertFalse(result)

    def test_filter_bullets_with_filters(self):
        """Test filtering bullets with various criteria"""
        mock_response = Mock()
        mock_response.data = self.sample_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        bullets = self.service.filter_bullets(
            manufacturer="Hornady",
            bore_diameter_mm=6.35,
            weight_grains=147
        )
        
        self.assertEqual(len(bullets), 1)
        self.assertIsInstance(bullets[0], BulletModel)

    def test_get_unique_manufacturers(self):
        """Test getting unique manufacturers"""
        with patch.object(self.service, 'get_all_bullets') as mock_get_all:
            mock_bullets = [
                Mock(manufacturer="Hornady"),
                Mock(manufacturer="Federal"),
                Mock(manufacturer="Hornady")  # Duplicate
            ]
            mock_get_all.return_value = mock_bullets
            
            manufacturers = self.service.get_unique_manufacturers()
            
            self.assertEqual(set(manufacturers), {"Federal", "Hornady"})
            self.assertEqual(manufacturers, ["Federal", "Hornady"])  # Should be sorted

    def test_get_unique_bore_diameters(self):
        """Test getting unique bore diameters"""
        with patch.object(self.service, 'get_all_bullets') as mock_get_all:
            mock_bullets = [
                Mock(bore_diameter_land_mm=6.35),
                Mock(bore_diameter_land_mm=7.62),
                Mock(bore_diameter_land_mm=6.35)  # Duplicate
            ]
            mock_get_all.return_value = mock_bullets
            
            diameters = self.service.get_unique_bore_diameters()
            
            self.assertEqual(set(diameters), {6.35, 7.62})
            self.assertEqual(diameters, [6.35, 7.62])  # Should be sorted

    def test_get_unique_weights(self):
        """Test getting unique weights"""
        with patch.object(self.service, 'get_all_bullets') as mock_get_all:
            mock_bullets = [
                Mock(weight_grains=147),
                Mock(weight_grains=168),
                Mock(weight_grains=147)  # Duplicate
            ]
            mock_get_all.return_value = mock_bullets
            
            weights = self.service.get_unique_weights()
            
            self.assertEqual(set(weights), {147, 168})
            self.assertEqual(weights, [147, 168])  # Should be sorted


class TestBulletsPageStructure(unittest.TestCase):
    """Test bullets page structure and imports"""

    def test_bullets_page_exists(self):
        """Test that the bullets page file exists"""
        page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages", "9_📦_Bullets.py")
        self.assertTrue(os.path.exists(page_path), f"Bullets page not found at {page_path}")

    def test_bullets_page_has_required_imports(self):
        """Test that bullets page has required imports"""
        page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages", "9_📦_Bullets.py")
        
        with open(page_path, 'r') as f:
            content = f.read()
        
        # Check for required imports
        self.assertIn("import streamlit as st", content)
        self.assertIn("from bullets.create_tab import render_create_bullets_tab", content)
        self.assertIn("from bullets.view_tab import render_view_bullets_tab", content)
        self.assertIn("from auth import handle_auth", content)

    def test_bullets_models_has_service_import(self):
        """Test that bullets create_tab imports the service"""
        create_tab_path = os.path.join(os.path.dirname(__file__), "create_tab.py")
        
        with open(create_tab_path, 'r') as f:
            content = f.read()
        
        self.assertIn("from .service import BulletsService", content)

    def test_bullets_view_tab_has_service_import(self):
        """Test that bullets view_tab imports the service and models"""
        view_tab_path = os.path.join(os.path.dirname(__file__), "view_tab.py")
        
        with open(view_tab_path, 'r') as f:
            content = f.read()
        
        self.assertIn("from .service import BulletsService", content)
        self.assertIn("from .models import BulletModel", content)


if __name__ == '__main__':
    unittest.main()