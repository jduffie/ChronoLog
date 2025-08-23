#!/usr/bin/env python3
"""
Comprehensive test suite for the cartridges module.
Tests models, data validation, and UI components.
"""

import os
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cartridges.models import CartridgeModel, CartridgeTypeModel


class TestCartridgeModel(unittest.TestCase):
    """Test CartridgeModel functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.sample_record = {
            "id": "test-id-123",
            "owner_id": "user-123",
            "make": "Federal",
            "model": "Premium",
            "bullet_id": "bullet-456",
            "cartridge_type": "6mm Creedmoor",
            "data_source_name": "Manufacturer Data",
            "data_source_link": "https://example.com",
            "cartridge_key": "federal-premium-6mm",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "bullet_manufacturer": "Hornady",
            "bullet_model": "ELD Match",
            "bullet_weight_grains": 108,
            "bullet_diameter_groove_mm": 6.17,
            "bore_diameter_land_mm": 6.05,
            "bullet_length_mm": 32.5,
            "ballistic_coefficient_g1": 0.536,
            "ballistic_coefficient_g7": 0.274,
            "sectional_density": 0.262,
            "min_req_twist_rate_in_per_rev": 8.0,
            "pref_twist_rate_in_per_rev": 7.0,
        }

    def test_from_supabase_record(self):
        """Test creating CartridgeModel from Supabase record"""
        cartridge = CartridgeModel.from_supabase_record(self.sample_record)

        self.assertEqual(cartridge.id, "test-id-123")
        self.assertEqual(cartridge.owner_id, "user-123")
        self.assertEqual(cartridge.make, "Federal")
        self.assertEqual(cartridge.model, "Premium")
        self.assertEqual(cartridge.bullet_id, "bullet-456")
        self.assertEqual(cartridge.cartridge_type, "6mm Creedmoor")
        self.assertEqual(cartridge.bullet_manufacturer, "Hornady")
        self.assertEqual(cartridge.bullet_weight_grains, 108)
        self.assertEqual(cartridge.ballistic_coefficient_g1, 0.536)

    def test_from_supabase_records_list(self):
        """Test creating multiple CartridgeModels from records"""
        records = [self.sample_record, {**self.sample_record, "id": "test-id-456"}]
        cartridges = CartridgeModel.from_supabase_records(records)

        self.assertEqual(len(cartridges), 2)
        self.assertEqual(cartridges[0].id, "test-id-123")
        self.assertEqual(cartridges[1].id, "test-id-456")

    def test_to_dict_conversion(self):
        """Test converting CartridgeModel to dictionary"""
        cartridge = CartridgeModel.from_supabase_record(self.sample_record)
        result = cartridge.to_dict()

        expected_keys = [
            "owner_id",
            "make",
            "model",
            "bullet_id",
            "cartridge_type",
            "data_source_name",
            "data_source_link",
        ]

        for key in expected_keys:
            self.assertIn(key, result)

        self.assertEqual(result["make"], "Federal")
        self.assertEqual(result["model"], "Premium")
        self.assertEqual(result["cartridge_type"], "6mm Creedmoor")

    def test_display_name_property(self):
        """Test display_name property"""
        cartridge = CartridgeModel.from_supabase_record(self.sample_record)
        expected = "Federal Premium (6mm Creedmoor)"
        self.assertEqual(cartridge.display_name, expected)

    def test_display_name_property_minimal(self):
        """Test display_name with minimal data"""
        minimal_record = {"make": "Test", "model": "", "cartridge_type": ""}
        cartridge = CartridgeModel.from_supabase_record(minimal_record)
        self.assertEqual(cartridge.display_name, "Test")

    def test_display_name_property_empty(self):
        """Test display_name with no data"""
        empty_record = {"make": "", "model": "", "cartridge_type": ""}
        cartridge = CartridgeModel.from_supabase_record(empty_record)
        self.assertEqual(cartridge.display_name, "Unknown Cartridge")

    def test_bullet_display_property(self):
        """Test bullet_display property"""
        cartridge = CartridgeModel.from_supabase_record(self.sample_record)
        expected = "Hornady ELD Match 108gr"
        self.assertEqual(cartridge.bullet_display, expected)

    def test_bullet_display_property_no_data(self):
        """Test bullet_display with no bullet data"""
        cartridge = CartridgeModel()
        self.assertEqual(cartridge.bullet_display, "Unknown Bullet")

    def test_is_global_property(self):
        """Test is_global property"""
        # User-owned cartridge
        cartridge = CartridgeModel.from_supabase_record(self.sample_record)
        self.assertFalse(cartridge.is_global)

        # Global cartridge
        global_record = {**self.sample_record, "owner_id": None}
        global_cartridge = CartridgeModel.from_supabase_record(global_record)
        self.assertTrue(global_cartridge.is_global)

    def test_is_user_owned_property(self):
        """Test is_user_owned property"""
        # User-owned cartridge
        cartridge = CartridgeModel.from_supabase_record(self.sample_record)
        self.assertTrue(cartridge.is_user_owned)

        # Global cartridge
        global_record = {**self.sample_record, "owner_id": None}
        global_cartridge = CartridgeModel.from_supabase_record(global_record)
        self.assertFalse(global_cartridge.is_user_owned)

    def test_ballistic_data_summary(self):
        """Test ballistic_data_summary property"""
        cartridge = CartridgeModel.from_supabase_record(self.sample_record)
        expected = "G1 BC: 0.536, G7 BC: 0.274, SD: 0.262"
        self.assertEqual(cartridge.ballistic_data_summary, expected)

    def test_ballistic_data_summary_no_data(self):
        """Test ballistic_data_summary with no data"""
        cartridge = CartridgeModel()
        self.assertEqual(cartridge.ballistic_data_summary, "No ballistic data")

    def test_twist_rate_recommendation(self):
        """Test twist_rate_recommendation property"""
        cartridge = CartridgeModel.from_supabase_record(self.sample_record)
        expected = 'Min: 1:8.0", Pref: 1:7.0"'
        self.assertEqual(cartridge.twist_rate_recommendation, expected)

    def test_twist_rate_recommendation_min_only(self):
        """Test twist_rate_recommendation with only min rate"""
        record = {**self.sample_record, "pref_twist_rate_in_per_rev": None}
        cartridge = CartridgeModel.from_supabase_record(record)
        expected = 'Min: 1:8.0"'
        self.assertEqual(cartridge.twist_rate_recommendation, expected)

    def test_twist_rate_recommendation_no_data(self):
        """Test twist_rate_recommendation with no data"""
        cartridge = CartridgeModel()
        self.assertEqual(cartridge.twist_rate_recommendation, "No twist rate data")

    def test_is_complete_true(self):
        """Test is_complete method returns True for complete cartridge"""
        cartridge = CartridgeModel.from_supabase_record(self.sample_record)
        self.assertTrue(cartridge.is_complete())

    def test_is_complete_false_missing_make(self):
        """Test is_complete method returns False when make is missing"""
        record = {**self.sample_record, "make": ""}
        cartridge = CartridgeModel.from_supabase_record(record)
        self.assertFalse(cartridge.is_complete())

    def test_is_complete_false_missing_bullet_id(self):
        """Test is_complete method returns False when bullet_id is missing"""
        record = {**self.sample_record, "bullet_id": None}
        cartridge = CartridgeModel.from_supabase_record(record)
        self.assertFalse(cartridge.is_complete())

    def test_get_missing_mandatory_fields(self):
        """Test get_missing_mandatory_fields method"""
        # Complete cartridge
        cartridge = CartridgeModel.from_supabase_record(self.sample_record)
        missing = cartridge.get_missing_mandatory_fields()
        self.assertEqual(missing, [])

    def test_get_missing_mandatory_fields_with_missing(self):
        """Test get_missing_mandatory_fields with missing fields"""
        incomplete_record = {
            "make": "",
            "model": "Test Model",
            "bullet_id": None,
            "cartridge_type": "6mm Creedmoor",
        }
        cartridge = CartridgeModel.from_supabase_record(incomplete_record)
        missing = cartridge.get_missing_mandatory_fields()

        self.assertIn("Make", missing)
        self.assertIn("Bullet Id", missing)
        self.assertNotIn("Model", missing)
        self.assertNotIn("Cartridge Type", missing)


class TestCartridgeTypeModel(unittest.TestCase):
    """Test CartridgeTypeModel functionality"""

    def test_from_supabase_record(self):
        """Test creating CartridgeTypeModel from Supabase record"""
        record = {"name": "6mm Creedmoor"}
        cartridge_type = CartridgeTypeModel.from_supabase_record(record)

        self.assertEqual(cartridge_type.name, "6mm Creedmoor")

    def test_from_supabase_records_list(self):
        """Test creating multiple CartridgeTypeModels from records"""
        records = [{"name": "6mm Creedmoor"}, {"name": ".308 Winchester"}]
        cartridge_types = CartridgeTypeModel.from_supabase_records(records)

        self.assertEqual(len(cartridge_types), 2)
        self.assertEqual(cartridge_types[0].name, "6mm Creedmoor")
        self.assertEqual(cartridge_types[1].name, ".308 Winchester")

    def test_to_dict_conversion(self):
        """Test converting CartridgeTypeModel to dictionary"""
        cartridge_type = CartridgeTypeModel(name="6mm Creedmoor")
        result = cartridge_type.to_dict()

        self.assertEqual(result, {"name": "6mm Creedmoor"})

    def test_display_name_property(self):
        """Test display_name property"""
        cartridge_type = CartridgeTypeModel(name="6mm Creedmoor")
        self.assertEqual(cartridge_type.display_name, "6mm Creedmoor")

    def test_display_name_property_empty(self):
        """Test display_name property with empty name"""
        cartridge_type = CartridgeTypeModel(name="")
        self.assertEqual(cartridge_type.display_name, "Unknown Type")


class TestCartridgeDataValidation(unittest.TestCase):
    """Test cartridge data validation"""

    def test_common_cartridge_types(self):
        """Test that common cartridge types are recognized"""
        common_types = [
            "6mm Creedmoor",
            ".308 Winchester",
            ".300 Winchester Magnum",
            "6.5 Creedmoor",
            ".223 Remington",
            "5.56x45mm NATO",
            ".22 Long Rifle",
            ".17 HMR",
        ]

        for cartridge_type in common_types:
            cartridge = CartridgeModel(cartridge_type=cartridge_type)
            self.assertIsNotNone(cartridge.cartridge_type)
            self.assertTrue(len(cartridge.cartridge_type) > 0)

    def test_ballistic_coefficient_ranges(self):
        """Test that ballistic coefficients are in reasonable ranges"""
        # G1 BC typically ranges from 0.1 to 1.0
        cartridge = CartridgeModel(ballistic_coefficient_g1=0.536)
        self.assertGreater(cartridge.ballistic_coefficient_g1, 0.0)
        self.assertLess(cartridge.ballistic_coefficient_g1, 1.5)

        # G7 BC typically ranges from 0.1 to 0.6
        cartridge = CartridgeModel(ballistic_coefficient_g7=0.274)
        self.assertGreater(cartridge.ballistic_coefficient_g7, 0.0)
        self.assertLess(cartridge.ballistic_coefficient_g7, 1.0)

    def test_bullet_weight_ranges(self):
        """Test that bullet weights are in reasonable ranges"""
        # Test various bullet weights
        weights = [55, 77, 108, 140, 168, 175, 208]

        for weight in weights:
            cartridge = CartridgeModel(bullet_weight_grains=weight)
            self.assertGreater(cartridge.bullet_weight_grains, 10)
            self.assertLess(cartridge.bullet_weight_grains, 1000)

    def test_twist_rate_ranges(self):
        """Test that twist rates are in reasonable ranges"""
        # Common twist rates
        twist_rates = [7.0, 8.0, 9.0, 10.0, 12.0, 16.0]

        for rate in twist_rates:
            cartridge = CartridgeModel(
                min_req_twist_rate_in_per_rev=rate,
                pref_twist_rate_in_per_rev=rate - 1.0,
            )
            self.assertGreater(cartridge.min_req_twist_rate_in_per_rev, 5.0)
            self.assertLess(cartridge.min_req_twist_rate_in_per_rev, 20.0)


class TestCartridgeManufacturers(unittest.TestCase):
    """Test cartridge manufacturer data"""

    def test_common_manufacturers(self):
        """Test that common cartridge manufacturers are handled"""
        manufacturers = [
            "Federal",
            "Hornady",
            "Remington",
            "Winchester",
            "Norma",
            "Lapua",
            "Sierra",
            "Nosler",
            "Berger",
        ]

        for make in manufacturers:
            cartridge = CartridgeModel(make=make)
            self.assertIsNotNone(cartridge.make)
            self.assertTrue(len(cartridge.make) > 0)

    def test_model_format(self):
        """Test cartridge model format"""
        models = ["Premium", "Match", "Gold Medal", "Black Hills", "Custom Competition"]

        for model in models:
            cartridge = CartridgeModel(model=model)
            self.assertIsNotNone(cartridge.model)
            self.assertTrue(len(cartridge.model) > 0)


if __name__ == "__main__":
    unittest.main()
