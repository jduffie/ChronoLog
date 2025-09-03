#!/usr/bin/env python3
"""
Comprehensive test suite for the cartridges module.
Tests models, data validation, and UI components.
"""

import csv
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from decimal import Decimal
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


class TestCartridgeModelEnhancements(unittest.TestCase):
    """Enhanced tests for CartridgeModel functionality"""

    def setUp(self):
        self.complete_record = {
            "id": "cartridge-uuid-123",
            "owner_id": "user-456",
            "make": "Hornady",
            "model": "Precision Hunter",
            "bullet_id": "bullet-uuid-789",
            "cartridge_type": "6.5 Creedmoor",
            "data_source_name": "Hornady Official",
            "data_source_link": "https://hornady.com/precision-hunter",
            "cartridge_key": "hornady|precision-hunter|6.5-creedmoor|bullet-uuid-789",
            "created_at": "2023-06-01T12:00:00Z",
            "updated_at": "2023-06-15T14:30:00Z",
            "bullet_manufacturer": "Hornady",
            "bullet_model": "ELD-X",
            "bullet_weight_grains": 143,
            "bullet_diameter_groove_mm": 6.71,
            "bore_diameter_land_mm": 6.50,
            "bullet_length_mm": 34.2,
            "ballistic_coefficient_g1": 0.625,
            "ballistic_coefficient_g7": 0.315,
            "sectional_density": 0.293,
            "min_req_twist_rate_in_per_rev": 8.0,
            "pref_twist_rate_in_per_rev": 7.5,
        }

    def test_cartridge_model_field_types_validation(self):
        """Test that CartridgeModel handles different field types correctly"""
        cartridge = CartridgeModel.from_supabase_record(self.complete_record)
        
        # Test string fields
        self.assertIsInstance(cartridge.make, str)
        self.assertIsInstance(cartridge.model, str)
        self.assertIsInstance(cartridge.cartridge_type, str)
        
        # Test numeric fields
        if cartridge.bullet_weight_grains is not None:
            self.assertIsInstance(cartridge.bullet_weight_grains, (int, float))
        if cartridge.ballistic_coefficient_g1 is not None:
            self.assertIsInstance(cartridge.ballistic_coefficient_g1, (int, float))
        if cartridge.sectional_density is not None:
            self.assertIsInstance(cartridge.sectional_density, (int, float))

    def test_cartridge_model_with_decimal_values(self):
        """Test CartridgeModel with decimal precision values"""
        record = self.complete_record.copy()
        record["bullet_weight_grains"] = 143.5
        record["ballistic_coefficient_g1"] = 0.6247
        record["sectional_density"] = 0.2935
        
        cartridge = CartridgeModel.from_supabase_record(record)
        
        self.assertEqual(cartridge.bullet_weight_grains, 143.5)
        self.assertEqual(cartridge.ballistic_coefficient_g1, 0.6247)
        self.assertEqual(cartridge.sectional_density, 0.2935)

    def test_cartridge_model_edge_case_values(self):
        """Test CartridgeModel with edge case values"""
        # Test with zero values
        record = self.complete_record.copy()
        record["bullet_weight_grains"] = 0
        record["ballistic_coefficient_g1"] = 0.0
        
        cartridge = CartridgeModel.from_supabase_record(record)
        self.assertEqual(cartridge.bullet_weight_grains, 0)
        self.assertEqual(cartridge.ballistic_coefficient_g1, 0.0)

    def test_display_name_complex_scenarios(self):
        """Test display_name property with complex scenarios"""
        # Test with special characters
        record = self.complete_record.copy()
        record["make"] = "Winchester"
        record["model"] = "Super-X"
        record["cartridge_type"] = ".300 Winchester Magnum"
        
        cartridge = CartridgeModel.from_supabase_record(record)
        expected = "Winchester Super-X (.300 Winchester Magnum)"
        self.assertEqual(cartridge.display_name, expected)
        
        # Test with only make
        record = {"make": "Federal", "model": "", "cartridge_type": ""}
        cartridge = CartridgeModel.from_supabase_record(record)
        self.assertEqual(cartridge.display_name, "Federal")

    def test_bullet_display_complex_scenarios(self):
        """Test bullet_display property with complex scenarios"""
        # Test with decimal weight
        record = self.complete_record.copy()
        record["bullet_weight_grains"] = 147.5
        
        cartridge = CartridgeModel.from_supabase_record(record)
        expected = "Hornady ELD-X 147.5gr"
        self.assertEqual(cartridge.bullet_display, expected)
        
        # Test with missing manufacturer but has model
        record = self.complete_record.copy()
        record["bullet_manufacturer"] = ""
        record["bullet_model"] = "MatchKing"
        record["bullet_weight_grains"] = 168
        
        cartridge = CartridgeModel.from_supabase_record(record)
        expected = "MatchKing 168gr"
        self.assertEqual(cartridge.bullet_display, expected)

    def test_ballistic_data_summary_variations(self):
        """Test ballistic_data_summary with different data combinations"""
        # Test with only G1 BC
        record = self.complete_record.copy()
        record["ballistic_coefficient_g1"] = 0.625
        record["ballistic_coefficient_g7"] = None
        record["sectional_density"] = None
        
        cartridge = CartridgeModel.from_supabase_record(record)
        self.assertEqual(cartridge.ballistic_data_summary, "G1 BC: 0.625")
        
        # Test with only sectional density
        record = self.complete_record.copy()
        record["ballistic_coefficient_g1"] = None
        record["ballistic_coefficient_g7"] = None
        record["sectional_density"] = 0.293
        
        cartridge = CartridgeModel.from_supabase_record(record)
        self.assertEqual(cartridge.ballistic_data_summary, "SD: 0.293")

    def test_twist_rate_recommendation_edge_cases(self):
        """Test twist_rate_recommendation with edge cases"""
        # Test with only preferred twist rate
        record = self.complete_record.copy()
        record["min_req_twist_rate_in_per_rev"] = None
        record["pref_twist_rate_in_per_rev"] = 7.5
        
        cartridge = CartridgeModel.from_supabase_record(record)
        expected = 'Pref: 1:7.5"'
        self.assertEqual(cartridge.twist_rate_recommendation, expected)
        
        # Test with same values for min and preferred
        record = self.complete_record.copy()
        record["min_req_twist_rate_in_per_rev"] = 8.0
        record["pref_twist_rate_in_per_rev"] = 8.0
        
        cartridge = CartridgeModel.from_supabase_record(record)
        expected = 'Min: 1:8.0", Pref: 1:8.0"'
        self.assertEqual(cartridge.twist_rate_recommendation, expected)

    def test_is_complete_edge_cases(self):
        """Test is_complete method with edge cases"""
        # Test with whitespace-only values
        record = self.complete_record.copy()
        record["make"] = "   "  # Only whitespace
        
        cartridge = CartridgeModel.from_supabase_record(record)
        self.assertFalse(cartridge.is_complete())
        
        # Test with None bullet_id
        record = self.complete_record.copy()
        record["bullet_id"] = None
        
        cartridge = CartridgeModel.from_supabase_record(record)
        self.assertFalse(cartridge.is_complete())

    def test_get_missing_mandatory_fields_comprehensive(self):
        """Test get_missing_mandatory_fields with various missing combinations"""
        # Test multiple missing fields
        record = {
            "make": "",
            "model": "",
            "bullet_id": None,
            "cartridge_type": "6.5 Creedmoor",
        }
        
        cartridge = CartridgeModel.from_supabase_record(record)
        missing = cartridge.get_missing_mandatory_fields()
        
        self.assertIn("Make", missing)
        self.assertIn("Model", missing)
        self.assertIn("Bullet Id", missing)
        self.assertNotIn("Cartridge Type", missing)
        self.assertEqual(len(missing), 3)

    def test_datetime_handling(self):
        """Test datetime field handling"""
        record = self.complete_record.copy()
        
        cartridge = CartridgeModel.from_supabase_record(record)
        
        # Test that datetime strings are preserved
        self.assertEqual(cartridge.created_at, "2023-06-01T12:00:00Z")
        self.assertEqual(cartridge.updated_at, "2023-06-15T14:30:00Z")


class TestCartridgeTypeModelEnhancements(unittest.TestCase):
    """Enhanced tests for CartridgeTypeModel functionality"""

    def test_cartridge_type_with_special_characters(self):
        """Test CartridgeTypeModel with special characters"""
        special_names = [
            ".300 Winchester Magnum",
            "5.56x45mm NATO",
            ".22-250 Remington",
            "7mm Remington Magnum",
        ]
        
        for name in special_names:
            record = {"name": name}
            cartridge_type = CartridgeTypeModel.from_supabase_record(record)
            self.assertEqual(cartridge_type.name, name)
            self.assertEqual(cartridge_type.display_name, name)

    def test_cartridge_type_whitespace_handling(self):
        """Test CartridgeTypeModel whitespace handling"""
        record = {"name": "  6mm Creedmoor  "}
        cartridge_type = CartridgeTypeModel.from_supabase_record(record)
        self.assertEqual(cartridge_type.name, "  6mm Creedmoor  ")  # Preserves original
        
    def test_cartridge_type_none_values(self):
        """Test CartridgeTypeModel with None values"""
        record = {"name": None}
        cartridge_type = CartridgeTypeModel.from_supabase_record(record)
        # When record has key with None value, .get() returns None (not the default)
        self.assertIsNone(cartridge_type.name)  # None value is preserved
        self.assertEqual(cartridge_type.display_name, "Unknown Type")  # display_name handles None


class TestCartridgeDataValidationEnhancements(unittest.TestCase):
    """Enhanced cartridge data validation tests"""

    def test_extreme_ballistic_coefficient_values(self):
        """Test extreme ballistic coefficient values"""
        # Test very low BC values (like .22 LR)
        cartridge = CartridgeModel(
            ballistic_coefficient_g1=0.125,
            ballistic_coefficient_g7=0.063
        )
        
        self.assertGreater(cartridge.ballistic_coefficient_g1, 0.0)
        self.assertGreater(cartridge.ballistic_coefficient_g7, 0.0)
        
        # Test high BC values (like long-range match bullets)
        cartridge = CartridgeModel(
            ballistic_coefficient_g1=0.850,
            ballistic_coefficient_g7=0.435
        )
        
        self.assertLess(cartridge.ballistic_coefficient_g1, 1.0)
        self.assertLess(cartridge.ballistic_coefficient_g7, 0.6)

    def test_extreme_bullet_weights(self):
        """Test extreme bullet weight values"""
        # Very light bullets (like .17 caliber)
        light_weights = [17, 20, 25]
        for weight in light_weights:
            cartridge = CartridgeModel(bullet_weight_grains=weight)
            self.assertGreater(cartridge.bullet_weight_grains, 10)
            
        # Very heavy bullets (like .50 caliber)
        heavy_weights = [500, 650, 750]
        for weight in heavy_weights:
            cartridge = CartridgeModel(bullet_weight_grains=weight)
            self.assertLess(cartridge.bullet_weight_grains, 1000)

    def test_uncommon_twist_rates(self):
        """Test uncommon twist rate values"""
        # Fast twist rates for heavy bullets
        fast_rates = [6.0, 6.5, 7.0]
        for rate in fast_rates:
            cartridge = CartridgeModel(min_req_twist_rate_in_per_rev=rate)
            self.assertGreater(cartridge.min_req_twist_rate_in_per_rev, 5.0)
            
        # Slow twist rates for light bullets
        slow_rates = [14.0, 16.0, 18.0]
        for rate in slow_rates:
            cartridge = CartridgeModel(min_req_twist_rate_in_per_rev=rate)
            self.assertLess(cartridge.min_req_twist_rate_in_per_rev, 20.0)

    def test_cartridge_type_format_validation(self):
        """Test cartridge type format validation"""
        valid_formats = [
            "6mm Creedmoor",
            ".308 Winchester",
            "5.56x45mm NATO",
            ".300 Winchester Magnum",
            ".22-250 Remington",
            "7mm Remington Magnum",
            ".17 Remington Fireball",
        ]
        
        for cartridge_type in valid_formats:
            cartridge = CartridgeModel(cartridge_type=cartridge_type)
            self.assertTrue(len(cartridge.cartridge_type) > 0)
            # Basic format validation - should contain either caliber or cartridge designation
            self.assertTrue(
                any(char.isdigit() for char in cartridge_type) or 
                "mm" in cartridge_type.lower() or
                "magnum" in cartridge_type.lower() or
                "remington" in cartridge_type.lower()
            )

    def test_manufacturer_name_variations(self):
        """Test manufacturer name variations"""
        variations = [
            "Federal Premium",  # With space
            "Hornady Manufacturing",  # Full company name
            "Remington Arms",
            "Winchester Ammunition",
            "Nosler, Inc.",  # With punctuation
        ]
        
        for make in variations:
            cartridge = CartridgeModel(make=make)
            self.assertTrue(len(cartridge.make) > 0)
            self.assertIsInstance(cartridge.make, str)


class TestCartridgeIntegration(unittest.TestCase):
    """Integration tests for cartridge module components"""
    
    def setUp(self):
        # Sample data that mimics real cartridge database records
        self.cartridge_records = [
            {
                "id": "cart-6mm-creedmoor-1",
                "owner_id": None,  # Global record
                "make": "Hornady",
                "model": "Precision Hunter",
                "bullet_id": "bullet-hornady-eldx-143",
                "cartridge_type": "6mm Creedmoor",
                "data_source_name": "Hornady Official",
                "data_source_link": "https://hornady.com/precision-hunter",
                "cartridge_key": "hornady|precision-hunter|6mm-creedmoor|bullet-hornady-eldx-143",
                "created_at": "2023-06-01T12:00:00Z",
                "updated_at": "2023-06-01T12:00:00Z",
                "bullet_manufacturer": "Hornady",
                "bullet_model": "ELD-X",
                "bullet_weight_grains": 143,
                "bullet_diameter_groove_mm": 6.17,
                "bore_diameter_land_mm": 6.05,
                "bullet_length_mm": 34.2,
                "ballistic_coefficient_g1": 0.625,
                "ballistic_coefficient_g7": 0.315,
                "sectional_density": 0.293,
                "min_req_twist_rate_in_per_rev": 8.0,
                "pref_twist_rate_in_per_rev": 7.5,
            },
            {
                "id": "cart-308-win-1",
                "owner_id": "user-123",  # User-owned record
                "make": "Federal",
                "model": "Gold Medal",
                "bullet_id": "bullet-sierra-matchking-168",
                "cartridge_type": ".308 Winchester",
                "data_source_name": "User Input",
                "data_source_link": None,
                "cartridge_key": "federal|gold-medal|.308-winchester|bullet-sierra-matchking-168",
                "created_at": "2023-06-15T14:30:00Z",
                "updated_at": "2023-06-15T14:30:00Z",
                "bullet_manufacturer": "Sierra",
                "bullet_model": "MatchKing",
                "bullet_weight_grains": 168,
                "bullet_diameter_groove_mm": 7.82,
                "bore_diameter_land_mm": 7.62,
                "bullet_length_mm": 31.8,
                "ballistic_coefficient_g1": 0.462,
                "ballistic_coefficient_g7": 0.236,
                "sectional_density": 0.253,
                "min_req_twist_rate_in_per_rev": 12.0,
                "pref_twist_rate_in_per_rev": 10.0,
            }
        ]

    def test_cartridge_model_integration_with_bullet_data(self):
        """Test CartridgeModel integration with complete bullet data"""
        # Test global cartridge
        global_cartridge = CartridgeModel.from_supabase_record(self.cartridge_records[0])
        
        self.assertTrue(global_cartridge.is_global)
        self.assertFalse(global_cartridge.is_user_owned)
        self.assertEqual(global_cartridge.display_name, "Hornady Precision Hunter (6mm Creedmoor)")
        self.assertEqual(global_cartridge.bullet_display, "Hornady ELD-X 143gr")
        self.assertEqual(global_cartridge.ballistic_data_summary, "G1 BC: 0.625, G7 BC: 0.315, SD: 0.293")
        self.assertEqual(global_cartridge.twist_rate_recommendation, 'Min: 1:8.0", Pref: 1:7.5"')
        self.assertTrue(global_cartridge.is_complete())
        
        # Test user-owned cartridge
        user_cartridge = CartridgeModel.from_supabase_record(self.cartridge_records[1])
        
        self.assertFalse(user_cartridge.is_global)
        self.assertTrue(user_cartridge.is_user_owned)
        self.assertEqual(user_cartridge.display_name, "Federal Gold Medal (.308 Winchester)")
        self.assertEqual(user_cartridge.bullet_display, "Sierra MatchKing 168gr")

    def test_multiple_cartridge_processing(self):
        """Test processing multiple cartridge records"""
        cartridges = CartridgeModel.from_supabase_records(self.cartridge_records)
        
        self.assertEqual(len(cartridges), 2)
        
        # Verify first cartridge
        self.assertEqual(cartridges[0].cartridge_type, "6mm Creedmoor")
        self.assertTrue(cartridges[0].is_global)
        
        # Verify second cartridge
        self.assertEqual(cartridges[1].cartridge_type, ".308 Winchester")
        self.assertTrue(cartridges[1].is_user_owned)

    def test_cartridge_filtering_scenarios(self):
        """Test various cartridge filtering scenarios"""
        cartridges = CartridgeModel.from_supabase_records(self.cartridge_records)
        
        # Filter by ownership type
        global_cartridges = [c for c in cartridges if c.is_global]
        user_cartridges = [c for c in cartridges if c.is_user_owned]
        
        self.assertEqual(len(global_cartridges), 1)
        self.assertEqual(len(user_cartridges), 1)
        
        # Filter by cartridge type
        creedmoor_cartridges = [c for c in cartridges if "Creedmoor" in c.cartridge_type]
        winchester_cartridges = [c for c in cartridges if "Winchester" in c.cartridge_type]
        
        self.assertEqual(len(creedmoor_cartridges), 1)
        self.assertEqual(len(winchester_cartridges), 1)
        
        # Filter by manufacturer
        hornady_cartridges = [c for c in cartridges if c.make == "Hornady"]
        federal_cartridges = [c for c in cartridges if c.make == "Federal"]
        
        self.assertEqual(len(hornady_cartridges), 1)
        self.assertEqual(len(federal_cartridges), 1)

    def test_cartridge_data_consistency(self):
        """Test data consistency across cartridge records"""
        cartridges = CartridgeModel.from_supabase_records(self.cartridge_records)
        
        for cartridge in cartridges:
            # Test that all complete cartridges have valid data
            if cartridge.is_complete():
                self.assertTrue(len(cartridge.make.strip()) > 0)
                self.assertTrue(len(cartridge.model.strip()) > 0)
                self.assertIsNotNone(cartridge.bullet_id)
                self.assertTrue(len(cartridge.cartridge_type.strip()) > 0)
                
            # Test bullet data consistency
            if cartridge.bullet_weight_grains:
                self.assertGreater(cartridge.bullet_weight_grains, 0)
                self.assertLess(cartridge.bullet_weight_grains, 1000)
                
            # Test ballistic coefficient consistency
            if cartridge.ballistic_coefficient_g1 and cartridge.ballistic_coefficient_g7:
                # G1 BC should typically be higher than G7 BC
                self.assertGreater(cartridge.ballistic_coefficient_g1, cartridge.ballistic_coefficient_g7)

    def test_cartridge_to_dict_conversion_workflow(self):
        """Test cartridge to dictionary conversion workflow"""
        cartridge = CartridgeModel.from_supabase_record(self.cartridge_records[0])
        
        # Convert to dict for database operations
        cartridge_dict = cartridge.to_dict()
        
        # Verify essential fields are present
        self.assertEqual(cartridge_dict["make"], "Hornady")
        self.assertEqual(cartridge_dict["model"], "Precision Hunter")
        self.assertEqual(cartridge_dict["cartridge_type"], "6mm Creedmoor")
        self.assertEqual(cartridge_dict["bullet_id"], "bullet-hornady-eldx-143")
        
        # Verify id is not included (for database insert operations)
        self.assertNotIn("id", cartridge_dict)
        
        # Verify bullet data is not included (separate table)
        self.assertNotIn("bullet_manufacturer", cartridge_dict)
        self.assertNotIn("bullet_weight_grains", cartridge_dict)

    def test_cartridge_type_model_integration(self):
        """Test CartridgeTypeModel integration"""
        cartridge_type_records = [
            {"name": "6mm Creedmoor"},
            {"name": ".308 Winchester"},
            {"name": ".300 Winchester Magnum"},
            {"name": "5.56x45mm NATO"},
        ]
        
        cartridge_types = CartridgeTypeModel.from_supabase_records(cartridge_type_records)
        
        self.assertEqual(len(cartridge_types), 4)
        
        # Test that all types have valid names
        for cartridge_type in cartridge_types:
            self.assertTrue(len(cartridge_type.name) > 0)
            self.assertEqual(cartridge_type.display_name, cartridge_type.name)
            
        # Test to_dict conversion
        type_dict = cartridge_types[0].to_dict()
        self.assertEqual(type_dict["name"], "6mm Creedmoor")

    def test_real_world_data_processing(self):
        """Test processing data that matches real-world structure"""
        # Simulate data that might come from CSV import or API
        csv_style_record = {
            "id": "csv-import-1",
            "owner_id": None,
            "make": "Lapua",
            "model": "Naturalis",
            "bullet_id": "bullet-lapua-naturalis-170",
            "cartridge_type": ".300 Winchester Magnum",
            "data_source_name": "Lapua Catalog 2023",
            "data_source_link": "https://lapua.com/product/300-win-mag-naturalis",
            "bullet_manufacturer": "Lapua",
            "bullet_model": "Naturalis",
            "bullet_weight_grains": 170,
            "bullet_diameter_groove_mm": 7.82,
            "bore_diameter_land_mm": 7.62,
            "ballistic_coefficient_g1": 0.485,
            "ballistic_coefficient_g7": None,  # Not always available
            "sectional_density": 0.256,
            "min_req_twist_rate_in_per_rev": 11.0,
            "pref_twist_rate_in_per_rev": None,  # Not always specified
        }
        
        cartridge = CartridgeModel.from_supabase_record(csv_style_record)
        
        # Test that model handles missing optional data gracefully
        self.assertEqual(cartridge.display_name, "Lapua Naturalis (.300 Winchester Magnum)")
        self.assertEqual(cartridge.bullet_display, "Lapua Naturalis 170gr")
        self.assertEqual(cartridge.ballistic_data_summary, "G1 BC: 0.485, SD: 0.256")
        self.assertEqual(cartridge.twist_rate_recommendation, 'Min: 1:11.0"')
        self.assertTrue(cartridge.is_complete())
        self.assertTrue(cartridge.is_global)


class TestCartridgeViewTabIntegration(unittest.TestCase):
    """Integration tests for cartridge view tab functionality"""
    
    def setUp(self):
        self.mock_supabase = Mock()
        self.mock_user = {"id": "user-123", "email": "test@example.com"}

    @patch('cartridges.view_tab.st')
    def test_view_tab_session_state_cleanup(self, mock_st):
        """Test that view tab properly cleans up session state"""
        from cartridges.view_tab import render_view_cartridges_tab

        # Create a mock session state that behaves like a dictionary but allows mocking
        mock_session_state = Mock()
        mock_session_state.__contains__ = Mock(return_value=True)
        mock_session_state.__delitem__ = Mock()
        
        mock_st.session_state = mock_session_state
        
        # Mock successful database response
        mock_response = Mock()
        mock_response.data = []
        
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
        
        # Call the function
        render_view_cartridges_tab(self.mock_user, self.mock_supabase)
        
        # Verify session state cleanup was attempted
        mock_session_state.__contains__.assert_called_with('cartridges')

    @patch('cartridges.view_tab.st')
    def test_view_tab_database_integration(self, mock_st):
        """Test view tab database query integration"""
        from cartridges.view_tab import render_view_cartridges_tab

        # Mock successful database response with cartridge data
        mock_response = Mock()
        mock_response.data = [
            {
                "id": "cart-1",
                "make": "Hornady",
                "model": "Precision Hunter",
                "cartridge_type": "6mm Creedmoor",
                "bullets": {
                    "manufacturer": "Hornady",
                    "model": "ELD-X",
                    "weight_grains": 143,
                }
            }
        ]
        
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
        
        # Create a mock session state that behaves correctly
        mock_session_state = Mock()
        mock_session_state.__contains__ = Mock(return_value=False)
        mock_st.session_state = mock_session_state
        
        # Call the function
        render_view_cartridges_tab(self.mock_user, self.mock_supabase)
        
        # Verify database query was made with correct parameters
        self.mock_supabase.table.assert_called_with("cartridges")


if __name__ == "__main__":
    unittest.main()
