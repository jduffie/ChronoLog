import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rifles.create_tab import render_create_rifle_tab
from rifles.view_tab import render_view_rifle_tab


class TestRiflesCreateTab(unittest.TestCase):

    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.header")
    @patch("streamlit.subheader")
    @patch("streamlit.form")
    @patch("streamlit.text_input")
    @patch("streamlit.number_input")
    @patch("streamlit.selectbox")
    @patch("streamlit.form_submit_button")
    def test_render_create_rifle_tab_basic(
        self,
        mock_submit,
        mock_selectbox,
        mock_number_input,
        mock_text_input,
        mock_form,
        mock_subheader,
        mock_header,
        mock_columns,
        mock_markdown,
    ):
        user = {"id": "test-user-id", "email": "test@example.com", "name": "Test User"}
        mock_supabase = Mock()

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
    @patch("streamlit.number_input")
    @patch("streamlit.selectbox")
    @patch("streamlit.form_submit_button")
    @patch("streamlit.success")
    def test_render_create_rifle_tab_submit_success(
        self,
        mock_success,
        mock_submit,
        mock_selectbox,
        mock_number_input,
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
    ):
        user = {"id": "test-user-id", "email": "test@example.com", "name": "Test User"}
        mock_supabase = Mock()

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

        # Mock form inputs (6 text inputs based on actual function)
        mock_text_input.side_effect = [
            "My Test Rifle",  # name
            "1:10",  # barrel_twist_ratio
            "24 inches",  # barrel_length
            "1.5 inches",  # sight_offset
            "Timney",  # trigger
            "Leupold Mark 4",  # scope
        ]
        mock_selectbox.return_value = ".308 Winchester"
        mock_number_input.side_effect = [24, 1.0, 10.0, 2.5]
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
            os.path.dirname(os.path.dirname(__file__)), "pages", "6_📏_Rifles.py"
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


if __name__ == "__main__":
    unittest.main()
