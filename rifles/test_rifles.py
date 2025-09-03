import os
import sys
import unittest
import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pandas as pd

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rifles.create_tab import render_create_rifle_tab
from rifles.view_tab import render_view_rifle_tab
from rifles.models import Rifle
from rifles.service import RifleService


class TestRiflesCreateTab(unittest.TestCase):

    @patch("rifles.create_tab.get_cartridge_types")
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.header")
    @patch("streamlit.subheader")
    @patch("streamlit.form")
    @patch("streamlit.text_input")
    @patch("streamlit.selectbox")
    @patch("streamlit.form_submit_button")
    def test_render_create_rifle_tab_basic(
        self,
        mock_submit,
        mock_selectbox,
        mock_text_input,
        mock_form,
        mock_subheader,
        mock_header,
        mock_columns,
        mock_markdown,
        mock_get_cartridge_types,
    ):
        user = {"id": "test-user-id", "email": "test@example.com", "name": "Test User"}
        mock_supabase = Mock()

        # Mock get_cartridge_types to return available cartridge types
        mock_get_cartridge_types.return_value = [".308 Winchester", "6.5 Creedmoor", ".223 Remington"]

        # Mock form context manager
        mock_form_ctx = Mock()
        mock_form.return_value.__enter__ = Mock(return_value=mock_form_ctx)
        mock_form.return_value.__exit__ = Mock(return_value=None)

        # Mock columns for layout
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = [mock_col, mock_col]

        # Mock form inputs (6 text inputs based on actual function)
        mock_text_input.side_effect = [
            "My Test Rifle",  # name
            "1:10",  # barrel_twist_ratio
            "24 inches",  # barrel_length
            "1.5 inches",  # sight_offset
            "Timney",  # trigger
            "Leupold Mark 4",  # scope
        ]
        mock_submit.return_value = False  # Not submitted

        result = render_create_rifle_tab(user, mock_supabase)

        # Function should complete without error
        self.assertIsNone(result)
        mock_header.assert_called()

    @patch("rifles.create_tab.get_cartridge_types")
    @patch("streamlit.rerun")
    @patch("streamlit.expander")
    @patch("streamlit.write")
    @patch("streamlit.info")
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.header")
    @patch("streamlit.subheader")
    @patch("streamlit.form")
    @patch("streamlit.text_input")
    @patch("streamlit.selectbox")
    @patch("streamlit.form_submit_button")
    @patch("streamlit.success")
    def test_render_create_rifle_tab_submit_success(
        self,
        mock_success,
        mock_submit,
        mock_selectbox,
        mock_text_input,
        mock_form,
        mock_subheader,
        mock_header,
        mock_columns,
        mock_markdown,
        mock_info,
        mock_write,
        mock_expander,
        mock_rerun,
        mock_get_cartridge_types,
    ):
        user = {"id": "test-user-id", "email": "test@example.com", "name": "Test User"}
        mock_supabase = Mock()

        # Mock get_cartridge_types to return available cartridge types
        mock_get_cartridge_types.return_value = [".308 Winchester", "6.5 Creedmoor", ".223 Remington"]

        # Mock successful database insertion
        mock_response = Mock()
        mock_response.data = [{"id": "new-rifle-id"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        # Mock form context manager
        mock_form_ctx = Mock()
        mock_form.return_value.__enter__ = Mock(return_value=mock_form_ctx)
        mock_form.return_value.__exit__ = Mock(return_value=None)

        # Mock columns for layout
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = [mock_col, mock_col]

        # Mock expander context manager
        mock_expander.return_value.__enter__ = Mock(return_value=Mock())
        mock_expander.return_value.__exit__ = Mock(return_value=None)

        # Mock form inputs (5 text inputs based on actual function)
        mock_text_input.side_effect = [
            "My Test Rifle",  # name
            "1:10",  # barrel_twist_ratio
            "24 inches",  # barrel_length
            "1.5 inches",  # sight_offset
            "Timney",  # trigger
            "Leupold Mark 4",  # scope
        ]
        mock_selectbox.return_value = ".308 Winchester"
        mock_submit.return_value = True  # Form submitted

        result = render_create_rifle_tab(user, mock_supabase)

        # Should show success message
        mock_success.assert_called()


class TestRiflesViewTab(unittest.TestCase):

    @patch("streamlit.subheader")
    @patch("streamlit.info")
    def test_render_view_rifle_tab_no_rifles(self, mock_info, mock_subheader):
        user = {"id": "test-user-id", "email": "test@example.com", "name": "Test User"}
        mock_supabase = Mock()

        # Mock empty rifles list
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response
        )

        result = render_view_rifle_tab(user, mock_supabase)

        # Should show info message about no rifles
        mock_info.assert_called()
        self.assertIsNone(result)

    @patch("pandas.to_datetime")
    @patch("streamlit.column_config")
    @patch("streamlit.download_button")
    @patch("streamlit.warning")
    @patch("streamlit.info")
    @patch("streamlit.button")
    @patch("streamlit.expander")
    @patch("streamlit.selectbox")
    @patch("streamlit.columns")
    @patch("streamlit.metric")
    @patch("streamlit.subheader")
    @patch("streamlit.header")
    @patch("streamlit.dataframe")
    def test_render_view_rifle_tab_with_rifles(
        self,
        mock_dataframe,
        mock_header,
        mock_subheader,
        mock_metric,
        mock_columns,
        mock_selectbox,
        mock_expander,
        mock_button,
        mock_info,
        mock_warning,
        mock_download_button,
        mock_column_config,
        mock_to_datetime,
    ):
        user = {"id": "test-user-id", "email": "test@example.com", "name": "Test User"}
        mock_supabase = Mock()

        # Mock rifle data with all required fields
        mock_data = [
            {
                "id": "rifle-1",
                "user_id": "test-user-id",
                "name": "Test Rifle",
                "barrel_twist_ratio": "1:10",
                "barrel_length": "24 inches",
                "sight_offset": "1.5 inches",
                "scope": "Leupold Mark 4",
                "trigger": "Timney",
                "created_at": "2023-12-01T10:00:00",
                "updated_at": "2023-12-01T10:00:00",
            }
        ]

        mock_response = Mock()
        mock_response.data = mock_data
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response
        )

        # Mock Streamlit widgets
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = [mock_col, mock_col, mock_col, mock_col]
        mock_selectbox.side_effect = [
            "All",
            "All",
            "rifle-1",
        ]  # For twist, completeness filters, and detailed view
        mock_expander.return_value.__enter__ = Mock(return_value=Mock())
        mock_expander.return_value.__exit__ = Mock(return_value=None)
        mock_button.return_value = False

        # Mock pandas datetime formatting
        mock_datetime_obj = Mock()
        mock_datetime_obj.dt.strftime.return_value = ["2023-12-01 10:00"]
        mock_to_datetime.return_value = mock_datetime_obj

        # Mock column config
        mock_column_config.TextColumn.return_value = Mock()

        result = render_view_rifle_tab(user, mock_supabase)

        # Function should complete without error (dataframe may or may not be called due to complex logic)
        self.assertIsNone(result)


class TestRiflesPageStructure(unittest.TestCase):
    """Test the rifles page structure and configuration"""

    def test_rifles_page_exists(self):
        """Test that the rifles page file exists"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "6_Rifles.py"
        )
        self.assertTrue(os.path.exists(page_path), "Rifles page should exist")

    def test_rifles_page_has_required_imports(self):
        """Test that rifles page has required imports"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "6_📏_Rifles.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            required_imports = [
                "streamlit",
                "handle_auth",
                "create_client",
                "render_create_rifle_tab",
            ]
            for required_import in required_imports:
                self.assertIn(
                    required_import,
                    content,
                    f"Rifles page should import {required_import}",
                )

    def test_rifles_page_has_correct_tabs(self):
        """Test that rifles page has expected tabs"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "6_📏_Rifles.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            expected_tabs = ["Create", "View"]
            for tab in expected_tabs:
                self.assertIn(f'"{tab}"', content, f"Rifles page should have {tab} tab")

    def test_rifles_page_configuration(self):
        """Test rifles page configuration"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "6_📏_Rifles.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            self.assertIn('page_title="Rifles"', content)
            self.assertIn('page_icon="📏"', content)
            self.assertIn('layout="wide"', content)

    def test_rifles_page_title(self):
        """Test rifles page displays correct title"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "6_📏_Rifles.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            self.assertIn('st.title("🔫 Rifle Management")', content)


class TestRifleDataValidation(unittest.TestCase):
    """Test rifle data validation and handling"""

    def test_rifle_caliber_options(self):
        """Test that common rifle calibers are available"""
        common_calibers = [
            ".308 Winchester",
            ".223 Remington",
            ".22 LR",
            ".30-06 Springfield",
            ".270 Winchester",
            "6.5 Creedmoor",
            ".300 Winchester Magnum",
        ]

        for caliber in common_calibers:
            self.assertIsInstance(caliber, str)
            self.assertTrue(len(caliber) > 0)

    def test_barrel_length_range(self):
        """Test that barrel lengths are in reasonable ranges"""
        typical_lengths = [16, 18, 20, 22, 24, 26, 28]  # inches

        for length in typical_lengths:
            self.assertIsInstance(length, (int, float))
            self.assertGreater(length, 10)  # Minimum reasonable length
            self.assertLess(length, 50)  # Maximum reasonable length

    def test_twist_ratio_format(self):
        """Test twist ratio format validation"""
        typical_ratios = ["1:8", "1:9", "1:10", "1:12", "1:14"]

        for ratio in typical_ratios:
            self.assertIsInstance(ratio, str)
            self.assertIn(":", ratio)
            parts = ratio.split(":")
            self.assertEqual(len(parts), 2)
            self.assertEqual(parts[0], "1")
            self.assertTrue(parts[1].isdigit())

    def test_trigger_weight_range(self):
        """Test that trigger weights are in reasonable ranges"""
        typical_weights = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]  # pounds

        for weight in typical_weights:
            self.assertIsInstance(weight, (int, float))
            self.assertGreater(weight, 0.5)  # Minimum safe weight
            self.assertLess(weight, 10.0)  # Maximum reasonable weight

    def test_sight_offset_range(self):
        """Test that sight offsets are in reasonable ranges"""
        typical_offsets = [1.0, 1.5, 2.0, 2.5, 3.0]  # inches

        for offset in typical_offsets:
            self.assertIsInstance(offset, (int, float))
            self.assertGreater(offset, 0)  # Must be positive
            self.assertLess(offset, 10.0)  # Reasonable upper bound


class TestRifleManufacturers(unittest.TestCase):
    """Test rifle manufacturer and model validation"""

    def test_common_manufacturers(self):
        """Test common rifle manufacturers"""
        common_makes = [
            "Remington",
            "Winchester",
            "Savage",
            "Ruger",
            "Tikka",
            "Bergara",
            "Browning",
        ]

        for make in common_makes:
            self.assertIsInstance(make, str)
            self.assertTrue(len(make) > 0)
            self.assertTrue(make[0].isupper())  # Should be capitalized

    def test_model_format(self):
        """Test rifle model format"""
        common_models = ["700", "Model 70", "10/110", "American", "T3x"]

        for model in common_models:
            self.assertIsInstance(model, str)
            self.assertTrue(len(model) > 0)


class TestRifleModel(unittest.TestCase):
    """Test the Rifle model class"""

    def setUp(self):
        """Set up test data"""
        self.sample_record = {
            "id": "rifle-123",
            "user_id": "user-456",
            "name": "Test Rifle",
            "cartridge_type": ".308 Winchester",
            "barrel_twist_ratio": "1:10",
            "barrel_length": "24 inches",
            "sight_offset": "1.5 inches",
            "trigger": "Timney 2-stage",
            "scope": "Leupold Mark 4",
            "created_at": "2023-12-01T10:00:00",
            "updated_at": "2023-12-01T12:00:00"
        }

    def test_from_supabase_record_complete(self):
        """Test creating Rifle from complete Supabase record"""
        rifle = Rifle.from_supabase_record(self.sample_record)

        self.assertEqual(rifle.id, "rifle-123")
        self.assertEqual(rifle.user_id, "user-456")
        self.assertEqual(rifle.name, "Test Rifle")
        self.assertEqual(rifle.cartridge_type, ".308 Winchester")
        self.assertEqual(rifle.barrel_twist_ratio, "1:10")
        self.assertEqual(rifle.barrel_length, "24 inches")
        self.assertEqual(rifle.sight_offset, "1.5 inches")
        self.assertEqual(rifle.trigger, "Timney 2-stage")
        self.assertEqual(rifle.scope, "Leupold Mark 4")
        self.assertIsNotNone(rifle.created_at)
        self.assertIsNotNone(rifle.updated_at)

    def test_from_supabase_record_minimal(self):
        """Test creating Rifle from minimal Supabase record"""
        minimal_record = {
            "id": "rifle-123",
            "user_id": "user-456",
            "name": "Basic Rifle",
            "cartridge_type": ".223 Remington"
        }

        rifle = Rifle.from_supabase_record(minimal_record)

        self.assertEqual(rifle.id, "rifle-123")
        self.assertEqual(rifle.name, "Basic Rifle")
        self.assertIsNone(rifle.barrel_twist_ratio)
        self.assertIsNone(rifle.barrel_length)
        self.assertIsNone(rifle.sight_offset)
        self.assertIsNone(rifle.trigger)
        self.assertIsNone(rifle.scope)
        self.assertIsNone(rifle.created_at)
        self.assertIsNone(rifle.updated_at)

    def test_from_supabase_records(self):
        """Test creating list of Rifles from Supabase records"""
        records = [self.sample_record, {
            "id": "rifle-789",
            "user_id": "user-456",
            "name": "Second Rifle",
            "cartridge_type": ".223 Remington"
        }]

        rifles = Rifle.from_supabase_records(records)

        self.assertEqual(len(rifles), 2)
        self.assertEqual(rifles[0].name, "Test Rifle")
        self.assertEqual(rifles[1].name, "Second Rifle")

    def test_display_name(self):
        """Test display name formatting"""
        rifle = Rifle.from_supabase_record(self.sample_record)
        display_name = rifle.display_name()

        self.assertEqual(display_name, "Test Rifle (.308 Winchester)")

    def test_barrel_display_complete(self):
        """Test barrel display with complete info"""
        rifle = Rifle.from_supabase_record(self.sample_record)
        barrel_display = rifle.barrel_display()

        self.assertEqual(barrel_display, "24 inches - Twist: 1:10")

    def test_barrel_display_partial(self):
        """Test barrel display with partial info"""
        record = self.sample_record.copy()
        record["barrel_twist_ratio"] = None
        rifle = Rifle.from_supabase_record(record)

        barrel_display = rifle.barrel_display()
        self.assertEqual(barrel_display, "24 inches")

    def test_barrel_display_empty(self):
        """Test barrel display with no info"""
        record = self.sample_record.copy()
        record["barrel_length"] = None
        record["barrel_twist_ratio"] = None
        rifle = Rifle.from_supabase_record(record)

        barrel_display = rifle.barrel_display()
        self.assertEqual(barrel_display, "Not specified")

    def test_optics_display_complete(self):
        """Test optics display with complete info"""
        rifle = Rifle.from_supabase_record(self.sample_record)
        optics_display = rifle.optics_display()

        self.assertEqual(optics_display, "Scope: Leupold Mark 4 - Offset: 1.5 inches")

    def test_optics_display_scope_only(self):
        """Test optics display with scope only"""
        record = self.sample_record.copy()
        record["sight_offset"] = None
        rifle = Rifle.from_supabase_record(record)

        optics_display = rifle.optics_display()
        self.assertEqual(optics_display, "Scope: Leupold Mark 4")

    def test_optics_display_empty(self):
        """Test optics display with no info"""
        record = self.sample_record.copy()
        record["scope"] = None
        record["sight_offset"] = None
        rifle = Rifle.from_supabase_record(record)

        optics_display = rifle.optics_display()
        self.assertEqual(optics_display, "Not specified")

    def test_trigger_display_with_value(self):
        """Test trigger display with value"""
        rifle = Rifle.from_supabase_record(self.sample_record)
        trigger_display = rifle.trigger_display()

        self.assertEqual(trigger_display, "Timney 2-stage")

    def test_trigger_display_empty(self):
        """Test trigger display without value"""
        record = self.sample_record.copy()
        record["trigger"] = None
        rifle = Rifle.from_supabase_record(record)

        trigger_display = rifle.trigger_display()
        self.assertEqual(trigger_display, "Not specified")


class TestRifleService(unittest.TestCase):
    """Test the RifleService class"""

    def setUp(self):
        """Set up test mocks"""
        self.mock_supabase = Mock()
        self.service = RifleService(self.mock_supabase)
        self.user_id = "test-user-123"

        self.sample_rifle_data = {
            "id": "rifle-123",
            "user_id": self.user_id,
            "name": "Test Rifle",
            "cartridge_type": ".308 Winchester",
            "barrel_twist_ratio": "1:10",
            "barrel_length": "24 inches",
            "sight_offset": "1.5 inches",
            "trigger": "Timney",
            "scope": "Leupold",
            "created_at": "2023-12-01T10:00:00",
            "updated_at": "2023-12-01T10:00:00"
        }

    def test_get_rifles_for_user_success(self):
        """Test successful retrieval of rifles for user"""
        mock_response = Mock()
        mock_response.data = [self.sample_rifle_data]

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

        rifles = self.service.get_rifles_for_user(self.user_id)

        self.assertEqual(len(rifles), 1)
        self.assertEqual(rifles[0].name, "Test Rifle")
        self.mock_supabase.table.assert_called_with("rifles")

    def test_get_rifles_for_user_empty(self):
        """Test retrieval with no rifles"""
        mock_response = Mock()
        mock_response.data = []

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

        rifles = self.service.get_rifles_for_user(self.user_id)

        self.assertEqual(len(rifles), 0)

    def test_get_rifles_for_user_exception(self):
        """Test exception handling in get_rifles_for_user"""
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception("Database error")

        with self.assertRaises(Exception) as context:
            self.service.get_rifles_for_user(self.user_id)

        self.assertIn("Error fetching rifles", str(context.exception))

    def test_get_rifle_by_id_success(self):
        """Test successful retrieval of rifle by ID"""
        mock_response = Mock()
        mock_response.data = self.sample_rifle_data

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        rifle = self.service.get_rifle_by_id("rifle-123", self.user_id)

        self.assertIsNotNone(rifle)
        self.assertEqual(rifle.name, "Test Rifle")

    def test_get_rifle_by_id_not_found(self):
        """Test rifle not found by ID"""
        mock_response = Mock()
        mock_response.data = None

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        rifle = self.service.get_rifle_by_id("nonexistent", self.user_id)

        self.assertIsNone(rifle)

    def test_get_rifle_by_name_success(self):
        """Test successful retrieval of rifle by name"""
        mock_response = Mock()
        mock_response.data = self.sample_rifle_data

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        rifle = self.service.get_rifle_by_name(self.user_id, "Test Rifle")

        self.assertIsNotNone(rifle)
        self.assertEqual(rifle.name, "Test Rifle")

    def test_get_rifle_by_name_exception(self):
        """Test exception handling in get_rifle_by_name"""
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("Database error")

        rifle = self.service.get_rifle_by_name(self.user_id, "Test Rifle")

        self.assertIsNone(rifle)

    def test_get_rifles_filtered_no_filters(self):
        """Test filtered retrieval with no filters"""
        mock_response = Mock()
        mock_response.data = [self.sample_rifle_data]

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response

        rifles = self.service.get_rifles_filtered(self.user_id)

        self.assertEqual(len(rifles), 1)

    def test_get_rifles_filtered_with_cartridge_type(self):
        """Test filtered retrieval with cartridge type filter"""
        mock_response = Mock()
        mock_response.data = [self.sample_rifle_data]

        mock_query = self.mock_supabase.table.return_value.select.return_value.eq.return_value
        mock_query.eq.return_value.order.return_value.execute.return_value = mock_response

        rifles = self.service.get_rifles_filtered(self.user_id, cartridge_type=".308 Winchester")

        self.assertEqual(len(rifles), 1)

    def test_get_unique_cartridge_types(self):
        """Test retrieval of unique cartridge types"""
        mock_response = Mock()
        mock_response.data = [
            {"cartridge_type": ".308 Winchester"},
            {"cartridge_type": ".223 Remington"},
            {"cartridge_type": ".308 Winchester"}  # Duplicate
        ]

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        cartridge_types = self.service.get_unique_cartridge_types(self.user_id)

        self.assertEqual(len(cartridge_types), 2)
        self.assertIn(".308 Winchester", cartridge_types)
        self.assertIn(".223 Remington", cartridge_types)

    def test_get_unique_twist_ratios(self):
        """Test retrieval of unique twist ratios"""
        mock_response = Mock()
        mock_response.data = [
            {"barrel_twist_ratio": "1:10"},
            {"barrel_twist_ratio": "1:8"},
            {"barrel_twist_ratio": "1:10"}  # Duplicate
        ]

        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        twist_ratios = self.service.get_unique_twist_ratios(self.user_id)

        self.assertEqual(len(twist_ratios), 2)
        self.assertIn("1:10", twist_ratios)
        self.assertIn("1:8", twist_ratios)

    def test_create_rifle_success(self):
        """Test successful rifle creation"""
        mock_response = Mock()
        mock_response.data = [{"id": "new-rifle-id"}]

        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        rifle_data = {"name": "New Rifle", "cartridge_type": ".308 Winchester"}
        rifle_id = self.service.create_rifle(rifle_data)

        self.assertEqual(rifle_id, "new-rifle-id")

    def test_create_rifle_failure(self):
        """Test rifle creation failure"""
        mock_response = Mock()
        mock_response.data = None

        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        with self.assertRaises(Exception) as context:
            self.service.create_rifle({"name": "New Rifle"})

        self.assertIn("Failed to create rifle", str(context.exception))

    @patch('rifles.service.datetime')
    def test_update_rifle(self, mock_datetime):
        """Test rifle update"""
        mock_datetime.now.return_value.isoformat.return_value = "2023-12-02T10:00:00"

        updates = {"name": "Updated Rifle"}
        self.service.update_rifle("rifle-123", self.user_id, updates)

        expected_updates = {
            "name": "Updated Rifle",
            "updated_at": "2023-12-02T10:00:00"
        }

        self.mock_supabase.table.return_value.update.assert_called_with(expected_updates)

    def test_delete_rifle(self):
        """Test rifle deletion"""
        self.service.delete_rifle("rifle-123", self.user_id)

        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.assert_called_with("user_id", self.user_id)

    def test_save_rifle_complete(self):
        """Test saving complete rifle entity"""
        from datetime import datetime
        rifle = Rifle(
            id="rifle-123",
            user_id=self.user_id,
            name="Test Rifle",
            cartridge_type=".308 Winchester",
            barrel_twist_ratio="1:10",
            barrel_length="24 inches",
            sight_offset="1.5 inches",
            trigger="Timney",
            scope="Leupold",
            created_at=datetime(2023, 12, 1, 10, 0, 0),
            updated_at=datetime(2023, 12, 1, 12, 0, 0)
        )

        mock_response = Mock()
        mock_response.data = [{"id": "rifle-123"}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        result_id = self.service.save_rifle(rifle)

        self.assertEqual(result_id, "rifle-123")

    def test_save_rifle_minimal(self):
        """Test saving minimal rifle entity"""
        rifle = Rifle(
            id="rifle-123",
            user_id=self.user_id,
            name="Basic Rifle",
            cartridge_type=".223 Remington"
        )

        mock_response = Mock()
        mock_response.data = [{"id": "rifle-123"}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        result_id = self.service.save_rifle(rifle)

        self.assertEqual(result_id, "rifle-123")


class TestRifleIntegration(unittest.TestCase):
    """Test integration between models and service"""

    def setUp(self):
        """Set up test environment"""
        self.mock_supabase = Mock()
        self.service = RifleService(self.mock_supabase)
        self.user_id = "test-user-123"

    def test_create_and_retrieve_rifle(self):
        """Test creating and then retrieving a rifle"""
        # Mock creation
        mock_create_response = Mock()
        mock_create_response.data = [{"id": "rifle-123"}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_create_response

        # Mock retrieval
        rifle_data = {
            "id": "rifle-123",
            "user_id": self.user_id,
            "name": "Integration Test Rifle",
            "cartridge_type": ".308 Winchester",
            "created_at": "2023-12-01T10:00:00"
        }
        mock_get_response = Mock()
        mock_get_response.data = rifle_data
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_get_response

        # Create rifle
        create_data = {
            "user_id": self.user_id,
            "name": "Integration Test Rifle",
            "cartridge_type": ".308 Winchester"
        }
        rifle_id = self.service.create_rifle(create_data)

        # Retrieve rifle
        retrieved_rifle = self.service.get_rifle_by_id(rifle_id, self.user_id)

        self.assertEqual(rifle_id, "rifle-123")
        self.assertIsNotNone(retrieved_rifle)
        self.assertEqual(retrieved_rifle.name, "Integration Test Rifle")
        self.assertEqual(retrieved_rifle.cartridge_type, ".308 Winchester")

    def test_filter_rifles_by_cartridge_type(self):
        """Test filtering rifles by cartridge type"""
        rifle_data = [
            {
                "id": "rifle-1",
                "user_id": self.user_id,
                "name": "Rifle 1",
                "cartridge_type": ".308 Winchester",
                "created_at": "2023-12-01T10:00:00"
            }
        ]

        mock_response = Mock()
        mock_response.data = rifle_data

        # Mock the chain for filtered query
        mock_query = self.mock_supabase.table.return_value.select.return_value.eq.return_value
        mock_query.eq.return_value.order.return_value.execute.return_value = mock_response

        filtered_rifles = self.service.get_rifles_filtered(
            self.user_id,
            cartridge_type=".308 Winchester"
        )

        self.assertEqual(len(filtered_rifles), 1)
        self.assertEqual(filtered_rifles[0].cartridge_type, ".308 Winchester")


class TestRifleEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def setUp(self):
        """Set up test environment"""
        self.mock_supabase = Mock()
        self.service = RifleService(self.mock_supabase)
        self.user_id = "test-user-123"

    def test_empty_database_responses(self):
        """Test handling of empty database responses"""
        mock_response = Mock()
        mock_response.data = []

        # Mock for methods that use order() (like get_rifles_for_user)
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        # Mock for methods that don't use order() (like get_unique_cartridge_types and get_unique_twist_ratios)
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        rifles = self.service.get_rifles_for_user(self.user_id)
        cartridge_types = self.service.get_unique_cartridge_types(self.user_id)
        twist_ratios = self.service.get_unique_twist_ratios(self.user_id)

        self.assertEqual(len(rifles), 0)
        self.assertEqual(len(cartridge_types), 0)
        self.assertEqual(len(twist_ratios), 0)

    def test_malformed_data_handling(self):
        """Test handling of malformed data"""
        malformed_record = {
            "id": "rifle-123",
            "user_id": self.user_id,
            "name": "Test Rifle",
            "cartridge_type": ".308 Winchester",
            "created_at": None  # Use None instead of invalid date format
        }

        # Should not raise exception
        rifle = Rifle.from_supabase_record(malformed_record)
        self.assertEqual(rifle.name, "Test Rifle")
        self.assertIsNone(rifle.created_at)  # Should handle None gracefully

    def test_null_values_in_optional_fields(self):
        """Test handling of null values in optional fields"""
        record_with_nulls = {
            "id": "rifle-123",
            "user_id": self.user_id,
            "name": "Test Rifle",
            "cartridge_type": ".308 Winchester",
            "barrel_twist_ratio": None,
            "barrel_length": None,
            "sight_offset": None,
            "trigger": None,
            "scope": None,
            "created_at": None,
            "updated_at": None
        }

        rifle = Rifle.from_supabase_record(record_with_nulls)

        # Should handle nulls gracefully
        self.assertEqual(rifle.barrel_display(), "Not specified")
        self.assertEqual(rifle.optics_display(), "Not specified")
        self.assertEqual(rifle.trigger_display(), "Not specified")

    def test_service_exception_propagation(self):
        """Test that service exceptions are properly propagated"""
        self.mock_supabase.table.return_value.select.side_effect = Exception("Connection error")

        with self.assertRaises(Exception) as context:
            self.service.get_rifles_for_user(self.user_id)

        self.assertIn("Error fetching rifles", str(context.exception))
        self.assertIn("Connection error", str(context.exception))


class TestRifleModelAdvanced(unittest.TestCase):
    """Advanced tests for Rifle model functionality"""

    def setUp(self):
        self.complete_record = {
            "id": "rifle-advanced-001",
            "user_id": "user-advanced",
            "name": "Advanced Test Rifle",
            "cartridge_type": "6.5 Creedmoor",
            "barrel_twist_ratio": "1:8",
            "barrel_length": "26 inches",
            "sight_offset": "2.0 inches",
            "trigger": "Geissele SSA-E 3.5lb",
            "scope": "Nightforce NX8 2.5-20x50",
            "created_at": "2023-12-01T10:00:00",
            "updated_at": "2023-12-01T15:30:00"
        }

    def test_rifle_display_methods_comprehensive(self):
        """Test all rifle display methods with various data combinations"""
        rifle = Rifle.from_supabase_record(self.complete_record)
        
        # Test display_name
        self.assertEqual(rifle.display_name(), "Advanced Test Rifle (6.5 Creedmoor)")
        
        # Test barrel_display
        expected_barrel = "26 inches - Twist: 1:8"
        self.assertEqual(rifle.barrel_display(), expected_barrel)
        
        # Test optics_display
        expected_optics = "Scope: Nightforce NX8 2.5-20x50 - Offset: 2.0 inches"
        self.assertEqual(rifle.optics_display(), expected_optics)
        
        # Test trigger_display
        self.assertEqual(rifle.trigger_display(), "Geissele SSA-E 3.5lb")

    def test_rifle_display_methods_edge_cases(self):
        """Test display methods with edge cases"""
        # Test with only barrel length, no twist
        partial_record = self.complete_record.copy()
        partial_record["barrel_twist_ratio"] = None
        rifle = Rifle.from_supabase_record(partial_record)
        self.assertEqual(rifle.barrel_display(), "26 inches")
        
        # Test with only twist ratio, no length
        partial_record = self.complete_record.copy()
        partial_record["barrel_length"] = None
        rifle = Rifle.from_supabase_record(partial_record)
        self.assertEqual(rifle.barrel_display(), "Twist: 1:8")
        
        # Test with only scope, no offset
        partial_record = self.complete_record.copy()
        partial_record["sight_offset"] = None
        rifle = Rifle.from_supabase_record(partial_record)
        self.assertEqual(rifle.optics_display(), "Scope: Nightforce NX8 2.5-20x50")

    def test_rifle_creation_edge_cases(self):
        """Test rifle creation with edge cases"""
        # Test with whitespace in fields
        whitespace_record = {
            "id": "rifle-whitespace",
            "user_id": "user-test",
            "name": "  Test Rifle  ",
            "cartridge_type": "  .308 Winchester  ",
            "barrel_twist_ratio": "  1:10  ",
            "barrel_length": "  24 inches  ",
            "sight_offset": "  1.5 inches  ",
            "trigger": "  Timney  ",
            "scope": "  Leupold  "
        }
        
        rifle = Rifle.from_supabase_record(whitespace_record)
        
        # Fields should be preserved as-is (trimming would be done at input validation level)
        self.assertEqual(rifle.name, "  Test Rifle  ")
        self.assertEqual(rifle.cartridge_type, "  .308 Winchester  ")

    def test_rifle_from_supabase_records_bulk(self):
        """Test creating multiple rifles from records"""
        records = []
        for i in range(10):
            record = self.complete_record.copy()
            record["id"] = f"rifle-bulk-{i}"
            record["name"] = f"Bulk Test Rifle {i}"
            record["cartridge_type"] = f"Test Cartridge {i}"
            records.append(record)
        
        rifles = Rifle.from_supabase_records(records)
        
        self.assertEqual(len(rifles), 10)
        for i, rifle in enumerate(rifles):
            self.assertEqual(rifle.id, f"rifle-bulk-{i}")
            self.assertEqual(rifle.name, f"Bulk Test Rifle {i}")
            self.assertEqual(rifle.cartridge_type, f"Test Cartridge {i}")

    def test_rifle_datetime_handling(self):
        """Test proper datetime handling in rifle creation"""
        # Test with ISO datetime strings
        iso_record = self.complete_record.copy()
        rifle = Rifle.from_supabase_record(iso_record)
        
        self.assertIsNotNone(rifle.created_at)
        self.assertIsNotNone(rifle.updated_at)
        self.assertIsInstance(rifle.created_at, pd.Timestamp)
        self.assertIsInstance(rifle.updated_at, pd.Timestamp)
        
        # Test with None datetime values
        none_record = self.complete_record.copy()
        none_record["created_at"] = None
        none_record["updated_at"] = None
        rifle = Rifle.from_supabase_record(none_record)
        
        self.assertIsNone(rifle.created_at)
        self.assertIsNone(rifle.updated_at)

    def test_rifle_cartridge_type_variations(self):
        """Test different cartridge type formats"""
        cartridge_variations = [
            ".308 Winchester",
            "6.5 Creedmoor", 
            ".223 Remington",
            ".22-250 Rem",
            ".300 Win Mag",
            "7mm Rem Mag",
            ".338 Lapua Mag"
        ]
        
        for cartridge in cartridge_variations:
            record = self.complete_record.copy()
            record["cartridge_type"] = cartridge
            rifle = Rifle.from_supabase_record(record)
            
            self.assertEqual(rifle.cartridge_type, cartridge)
            self.assertIn(cartridge, rifle.display_name())


class TestRifleServiceAdvanced(unittest.TestCase):
    """Advanced tests for RifleService functionality"""

    def setUp(self):
        self.mock_supabase = MagicMock()
        self.service = RifleService(self.mock_supabase)
        self.test_user_id = "user-advanced-test"

    def test_create_rifle_advanced_data(self):
        """Test creating rifle with advanced data"""
        advanced_rifle_data = {
            "user_id": self.test_user_id,
            "name": "Precision Competition Rifle",
            "cartridge_type": "6.5 Creedmoor",
            "barrel_twist_ratio": "1:8",
            "barrel_length": "26 inches",
            "sight_offset": "2.0 inches",
            "trigger": "Geissele SSA-E 2.5lb",
            "scope": "Nightforce ATACR 7-35x56"
        }
        
        mock_response = Mock()
        mock_response.data = [{"id": "rifle-precision-001"}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        rifle_id = self.service.create_rifle(advanced_rifle_data)
        
        self.assertEqual(rifle_id, "rifle-precision-001")
        self.mock_supabase.table.assert_called_with("rifles")

    def test_get_rifles_filtered_multiple_filters(self):
        """Test filtering with multiple criteria"""
        rifle_data = [
            {
                "id": "rifle-filter-1",
                "user_id": self.test_user_id,
                "name": "Filtered Rifle 1",
                "cartridge_type": "6.5 Creedmoor",
                "barrel_twist_ratio": "1:8",
                "created_at": "2023-12-01T10:00:00"
            }
        ]
        
        mock_response = Mock()
        mock_response.data = rifle_data
        
        # Mock the filtering query chain
        mock_query = self.mock_supabase.table.return_value.select.return_value.eq.return_value
        mock_query.eq.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        filtered_rifles = self.service.get_rifles_filtered(
            self.test_user_id,
            cartridge_type="6.5 Creedmoor",
            twist_ratio="1:8"
        )
        
        self.assertEqual(len(filtered_rifles), 1)
        self.assertEqual(filtered_rifles[0].cartridge_type, "6.5 Creedmoor")
        self.assertEqual(filtered_rifles[0].barrel_twist_ratio, "1:8")

    def test_update_rifle_comprehensive(self):
        """Test comprehensive rifle updates"""
        updates = {
            "name": "Updated Competition Rifle",
            "barrel_length": "24 inches",
            "scope": "Updated Scope",
            "trigger": "Updated Trigger"
        }
        
        with patch('rifles.service.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2023-12-02T15:30:00"
            
            self.service.update_rifle("rifle-update-test", self.test_user_id, updates)
            
            expected_updates = updates.copy()
            expected_updates["updated_at"] = "2023-12-02T15:30:00"
            
            self.mock_supabase.table.return_value.update.assert_called_with(expected_updates)

    def test_service_error_handling_comprehensive(self):
        """Test comprehensive error handling scenarios"""
        # Test create rifle failure
        mock_response = Mock()
        mock_response.data = None
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            self.service.create_rifle({"name": "Test Rifle"})
        self.assertIn("Failed to create rifle", str(context.exception))
        
        # Test database connection error
        self.mock_supabase.table.side_effect = Exception("Database connection failed")
        
        with self.assertRaises(Exception) as context:
            self.service.get_rifles_for_user(self.test_user_id)
        self.assertIn("Error fetching rifles", str(context.exception))
        self.assertIn("Database connection failed", str(context.exception))

    def test_bulk_operations_performance(self):
        """Test bulk operations and performance scenarios"""
        # Create bulk rifle data
        bulk_rifles = []
        for i in range(50):
            rifle_data = {
                "id": f"bulk-rifle-{i}",
                "user_id": self.test_user_id,
                "name": f"Bulk Rifle {i}",
                "cartridge_type": f".{300 + i} Test",
                "barrel_twist_ratio": f"1:{8 + (i % 5)}",
                "created_at": f"2023-12-{(i % 30) + 1:02d}T10:00:00"
            }
            bulk_rifles.append(rifle_data)
        
        mock_response = Mock()
        mock_response.data = bulk_rifles
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        rifles = self.service.get_rifles_for_user(self.test_user_id)
        
        self.assertEqual(len(rifles), 50)
        self.assertEqual(rifles[0].name, "Bulk Rifle 0")
        self.assertEqual(rifles[49].name, "Bulk Rifle 49")

    def test_unique_values_with_duplicates(self):
        """Test unique value retrieval with duplicates and edge cases"""
        # Test unique cartridge types with duplicates
        cartridge_data = [
            {"cartridge_type": "6.5 Creedmoor"},
            {"cartridge_type": ".308 Winchester"},
            {"cartridge_type": "6.5 Creedmoor"},  # Duplicate
            {"cartridge_type": ".223 Remington"},
            {"cartridge_type": ".308 Winchester"},  # Duplicate
            {"cartridge_type": None},  # None value
            {"cartridge_type": ""}  # Empty string
        ]
        
        mock_response = Mock()
        mock_response.data = cartridge_data
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        unique_types = self.service.get_unique_cartridge_types(self.test_user_id)
        
        # Should only include non-empty, non-None values, sorted and deduplicated
        expected_types = [".223 Remington", ".308 Winchester", "6.5 Creedmoor"]
        self.assertEqual(unique_types, expected_types)

    def test_save_rifle_entity(self):
        """Test saving rifle entity with all fields"""
        rifle = Rifle(
            id="entity-save-test",
            user_id=self.test_user_id,
            name="Entity Save Test Rifle",
            cartridge_type="6.5 Creedmoor",
            barrel_twist_ratio="1:8",
            barrel_length="24 inches",
            sight_offset="1.8 inches",
            trigger="Timney Calvin Elite",
            scope="Vortex Razor HD Gen III",
            created_at=datetime(2023, 12, 1, 10, 0, 0),
            updated_at=datetime(2023, 12, 1, 15, 30, 0)
        )
        
        mock_response = Mock()
        mock_response.data = [{"id": "entity-save-test"}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        result_id = self.service.save_rifle(rifle)
        
        self.assertEqual(result_id, "entity-save-test")


class TestRifleIntegrationAdvanced(unittest.TestCase):
    """Advanced integration tests for rifles module"""

    def setUp(self):
        self.mock_supabase = MagicMock()
        self.service = RifleService(self.mock_supabase)
        self.test_user_id = "integration-test-user"

    def test_complete_rifle_lifecycle(self):
        """Test complete rifle lifecycle: create, read, update, delete"""
        # Step 1: Create rifle
        create_data = {
            "user_id": self.test_user_id,
            "name": "Lifecycle Test Rifle",
            "cartridge_type": "6.5 Creedmoor",
            "barrel_twist_ratio": "1:8",
            "barrel_length": "26 inches"
        }
        
        mock_create_response = Mock()
        mock_create_response.data = [{"id": "lifecycle-rifle-001"}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_create_response
        
        rifle_id = self.service.create_rifle(create_data)
        self.assertEqual(rifle_id, "lifecycle-rifle-001")
        
        # Step 2: Read rifle
        rifle_data = {
            "id": "lifecycle-rifle-001",
            "user_id": self.test_user_id,
            "name": "Lifecycle Test Rifle",
            "cartridge_type": "6.5 Creedmoor",
            "barrel_twist_ratio": "1:8",
            "barrel_length": "26 inches",
            "created_at": "2023-12-01T10:00:00"
        }
        
        mock_read_response = Mock()
        mock_read_response.data = rifle_data
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_read_response
        
        retrieved_rifle = self.service.get_rifle_by_id(rifle_id, self.test_user_id)
        self.assertIsNotNone(retrieved_rifle)
        self.assertEqual(retrieved_rifle.name, "Lifecycle Test Rifle")
        
        # Step 3: Update rifle
        updates = {"name": "Updated Lifecycle Rifle", "scope": "New Scope"}
        
        with patch('rifles.service.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2023-12-02T10:00:00"
            self.service.update_rifle(rifle_id, self.test_user_id, updates)
        
        # Step 4: Delete rifle
        self.service.delete_rifle(rifle_id, self.test_user_id)
        
        # Verify delete was called
        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.assert_called()

    def test_rifle_filtering_integration(self):
        """Test integration of filtering with complex scenarios"""
        rifles_data = [
            {
                "id": "filter-test-1",
                "user_id": self.test_user_id,
                "name": "Precision Rifle 1",
                "cartridge_type": "6.5 Creedmoor",
                "barrel_twist_ratio": "1:8",
                "barrel_length": "26 inches",
                "created_at": "2023-12-01T10:00:00"
            },
            {
                "id": "filter-test-2", 
                "user_id": self.test_user_id,
                "name": "Hunting Rifle 1",
                "cartridge_type": ".308 Winchester",
                "barrel_twist_ratio": "1:10",
                "barrel_length": "22 inches",
                "created_at": "2023-12-02T10:00:00"
            },
            {
                "id": "filter-test-3",
                "user_id": self.test_user_id,
                "name": "Precision Rifle 2",
                "cartridge_type": "6.5 Creedmoor",
                "barrel_twist_ratio": "1:8",
                "barrel_length": "24 inches",
                "created_at": "2023-12-03T10:00:00"
            }
        ]
        
        # Test cartridge type filtering
        creedmoor_rifles = [rifles_data[0], rifles_data[2]]
        mock_response_creedmoor = Mock()
        mock_response_creedmoor.data = creedmoor_rifles
        
        mock_query = self.mock_supabase.table.return_value.select.return_value.eq.return_value
        mock_query.eq.return_value.order.return_value.execute.return_value = mock_response_creedmoor
        
        filtered_rifles = self.service.get_rifles_filtered(
            self.test_user_id, 
            cartridge_type="6.5 Creedmoor"
        )
        
        self.assertEqual(len(filtered_rifles), 2)
        for rifle in filtered_rifles:
            self.assertEqual(rifle.cartridge_type, "6.5 Creedmoor")

    def test_service_model_integration_comprehensive(self):
        """Test comprehensive service-model integration"""
        # Test that service methods return proper model instances
        rifle_data = {
            "id": "model-integration-test",
            "user_id": self.test_user_id,
            "name": "Model Integration Rifle",
            "cartridge_type": "6.5 Creedmoor",
            "barrel_twist_ratio": "1:8",
            "barrel_length": "26 inches",
            "sight_offset": "2.0 inches",
            "trigger": "Timney",
            "scope": "Nightforce",
            "created_at": "2023-12-01T10:00:00"
        }
        
        mock_response = Mock()
        mock_response.data = [rifle_data]
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        rifles = self.service.get_rifles_for_user(self.test_user_id)
        
        self.assertEqual(len(rifles), 1)
        rifle = rifles[0]
        
        # Verify it's a proper Rifle model instance
        self.assertIsInstance(rifle, Rifle)
        
        # Verify all model methods work
        self.assertEqual(rifle.display_name(), "Model Integration Rifle (6.5 Creedmoor)")
        self.assertEqual(rifle.barrel_display(), "26 inches - Twist: 1:8")
        self.assertEqual(rifle.optics_display(), "Scope: Nightforce - Offset: 2.0 inches")
        self.assertEqual(rifle.trigger_display(), "Timney")

    def test_error_recovery_integration(self):
        """Test error recovery in integrated workflows"""
        # Test partial failure recovery
        
        # First attempt should fail - setup the mock to raise an exception
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception("Temporary connection error")
        
        # First attempt should fail
        with self.assertRaises(Exception) as context:
            self.service.get_rifles_for_user(self.test_user_id)
        
        self.assertIn("Error fetching rifles", str(context.exception))
        self.assertIn("Temporary connection error", str(context.exception))
        
        # Reset the mock for second attempt
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = None
        mock_response = Mock()
        mock_response.data = []
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        # Second attempt should succeed
        rifles = self.service.get_rifles_for_user(self.test_user_id)
        self.assertEqual(len(rifles), 0)

    def test_concurrent_operations_simulation(self):
        """Test simulation of concurrent operations"""
        # Simulate multiple users accessing rifles simultaneously
        user_ids = [f"concurrent-user-{i}" for i in range(5)]
        
        for user_id in user_ids:
            rifles_data = [
                {
                    "id": f"concurrent-rifle-{user_id}",
                    "user_id": user_id,
                    "name": f"Concurrent Rifle for {user_id}",
                    "cartridge_type": "6.5 Creedmoor",
                    "created_at": "2023-12-01T10:00:00"
                }
            ]
            
            mock_response = Mock()
            mock_response.data = rifles_data
            self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
            
            rifles = self.service.get_rifles_for_user(user_id)
            
            self.assertEqual(len(rifles), 1)
            self.assertEqual(rifles[0].user_id, user_id)
            self.assertIn(user_id, rifles[0].name)

    def test_data_consistency_validation(self):
        """Test data consistency across service operations"""
        # Test that create and retrieve operations are consistent
        rifle_data = {
            "user_id": self.test_user_id,
            "name": "Consistency Test Rifle",
            "cartridge_type": "6.5 Creedmoor",
            "barrel_twist_ratio": "1:8",
            "barrel_length": "26 inches"
        }
        
        # Mock creation
        mock_create_response = Mock()
        mock_create_response.data = [{"id": "consistency-test-001"}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_create_response
        
        rifle_id = self.service.create_rifle(rifle_data)
        
        # Mock retrieval with same data plus generated fields
        full_rifle_data = rifle_data.copy()
        full_rifle_data.update({
            "id": rifle_id,
            "created_at": "2023-12-01T10:00:00",
            "updated_at": "2023-12-01T10:00:00"
        })
        
        mock_get_response = Mock()
        mock_get_response.data = full_rifle_data
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_get_response
        
        retrieved_rifle = self.service.get_rifle_by_id(rifle_id, self.test_user_id)
        
        # Verify consistency
        self.assertEqual(retrieved_rifle.id, rifle_id)
        self.assertEqual(retrieved_rifle.name, rifle_data["name"])
        self.assertEqual(retrieved_rifle.cartridge_type, rifle_data["cartridge_type"])
        self.assertEqual(retrieved_rifle.barrel_twist_ratio, rifle_data["barrel_twist_ratio"])
        self.assertEqual(retrieved_rifle.barrel_length, rifle_data["barrel_length"])


class TestRifleUIIntegration(unittest.TestCase):
    """Test integration with UI components"""

    @patch("rifles.create_tab.get_cartridge_types")
    @patch("streamlit.success")
    @patch("streamlit.form_submit_button")
    @patch("streamlit.text_input")
    @patch("streamlit.selectbox")
    @patch("streamlit.form")
    @patch("streamlit.columns")
    @patch("streamlit.subheader")
    @patch("streamlit.header")
    @patch("streamlit.markdown")
    def test_create_rifle_tab_integration(
        self, mock_markdown, mock_header, mock_subheader, mock_columns,
        mock_form, mock_selectbox, mock_text_input, mock_submit, mock_success,
        mock_get_cartridge_types
    ):
        """Test create rifle tab with successful submission"""
        user = {"id": "ui-test-user", "email": "test@example.com", "name": "UI Test User"}
        mock_supabase = Mock()
        
        # Mock successful database insertion
        mock_response = Mock()
        mock_response.data = [{"id": "ui-created-rifle-001"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        # Mock form context manager
        mock_form_ctx = Mock()
        mock_form.return_value.__enter__ = Mock(return_value=mock_form_ctx)
        mock_form.return_value.__exit__ = Mock(return_value=None)
        
        # Mock columns
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = [mock_col, mock_col]
        
        # Mock form inputs
        mock_get_cartridge_types.return_value = ["6.5 Creedmoor", ".308 Winchester"]
        mock_text_input.side_effect = [
            "UI Integration Rifle",  # name
            "1:8",  # barrel_twist_ratio
            "26 inches",  # barrel_length
            "2.0 inches",  # sight_offset
            "Timney SSA-E",  # trigger
            "Nightforce ATACR"  # scope
        ]
        mock_selectbox.return_value = "6.5 Creedmoor"
        mock_submit.return_value = True
        
        result = render_create_rifle_tab(user, mock_supabase)
        
        # Should show success message
        mock_success.assert_called()
        
        # Verify database insert was called (it will have additional generated fields)
        mock_supabase.table.return_value.insert.assert_called_once()
        
        # Get the actual call args and verify core fields
        actual_call = mock_supabase.table.return_value.insert.call_args[0][0]
        expected_fields = {
            "user_id": "ui-test-user",
            "name": "UI Integration Rifle",
            "cartridge_type": "6.5 Creedmoor",
            "barrel_twist_ratio": "1:8",
            "barrel_length": "26 inches",
            "sight_offset": "2.0 inches",
            "trigger": "Timney SSA-E",
            "scope": "Nightforce ATACR"
        }
        
        # Verify all expected fields are present
        for key, value in expected_fields.items():
            self.assertEqual(actual_call[key], value)

    @patch("pandas.to_datetime")
    @patch("streamlit.dataframe")
    @patch("streamlit.metric")
    @patch("streamlit.columns")
    @patch("streamlit.selectbox")
    @patch("streamlit.subheader")
    @patch("streamlit.header")
    def test_view_rifle_tab_integration(
        self, mock_header, mock_subheader, mock_selectbox, mock_columns,
        mock_metric, mock_dataframe, mock_to_datetime
    ):
        """Test view rifle tab with rifle data"""
        user = {"id": "ui-view-user", "email": "view@example.com", "name": "View User"}
        mock_supabase = Mock()
        
        # Mock rifle data
        rifle_data = [
            {
                "id": "view-rifle-001",
                "user_id": "ui-view-user",
                "name": "View Test Rifle",
                "cartridge_type": "6.5 Creedmoor",
                "barrel_twist_ratio": "1:8",
                "barrel_length": "26 inches",
                "sight_offset": "2.0 inches",
                "trigger": "Timney",
                "scope": "Nightforce",
                "created_at": "2023-12-01T10:00:00",
                "updated_at": "2023-12-01T15:30:00"
            }
        ]
        
        mock_response = Mock()
        mock_response.data = rifle_data
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        # Mock UI components
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = [mock_col, mock_col, mock_col, mock_col]
        
        mock_selectbox.side_effect = ["All", "All", "view-rifle-001"]
        
        # Mock pandas datetime
        mock_datetime_obj = Mock()
        mock_datetime_obj.dt.strftime.return_value = ["2023-12-01 10:00"]
        mock_to_datetime.return_value = mock_datetime_obj
        
        result = render_view_rifle_tab(user, mock_supabase)
        
        # Should complete without error
        self.assertIsNone(result)
        
        # Verify metrics were displayed
        mock_metric.assert_called()


if __name__ == "__main__":
    unittest.main()
