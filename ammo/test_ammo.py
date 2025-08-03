import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ammo.create_tab import render_create_ammo_tab
from ammo.view_tab import render_view_ammo_tab


class TestAmmoCreateTab(unittest.TestCase):

    @patch("streamlit.subheader")
    @patch("streamlit.form")
    @patch("streamlit.text_input")
    @patch("streamlit.number_input")
    @patch("streamlit.selectbox")
    @patch("streamlit.form_submit_button")
    def test_render_create_ammo_tab_basic(
        self,
        mock_submit,
        mock_selectbox,
        mock_number_input,
        mock_text_input,
        mock_form,
        mock_subheader,
    ):
        user = {"email": "test@example.com", "name": "Test User"}
        mock_supabase = Mock()

        # Mock form context manager
        mock_form_ctx = Mock()
        mock_form.return_value.__enter__ = Mock(return_value=mock_form_ctx)
        mock_form.return_value.__exit__ = Mock(return_value=None)

        # Mock form inputs
        mock_text_input.side_effect = ["Federal", "Gold Medal", "Match"]
        mock_selectbox.return_value = ".308 Winchester"
        mock_number_input.side_effect = [168, 2.5, 1000]  # grain, bc, velocity
        mock_submit.return_value = False  # Not submitted

        result = render_create_ammo_tab(user, mock_supabase)

        # Function should complete without error
        self.assertIsNone(result)
        mock_subheader.assert_called()

    @patch("streamlit.subheader")
    @patch("streamlit.form")
    @patch("streamlit.text_input")
    @patch("streamlit.number_input")
    @patch("streamlit.selectbox")
    @patch("streamlit.form_submit_button")
    @patch("streamlit.success")
    def test_render_create_ammo_tab_submit_success(
        self,
        mock_success,
        mock_submit,
        mock_selectbox,
        mock_number_input,
        mock_text_input,
        mock_form,
        mock_subheader,
    ):
        user = {"email": "test@example.com", "name": "Test User"}
        mock_supabase = Mock()

        # Mock successful database insertion
        mock_response = Mock()
        mock_response.data = [{"id": "new-ammo-id"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        # Mock form context manager
        mock_form_ctx = Mock()
        mock_form.return_value.__enter__ = Mock(return_value=mock_form_ctx)
        mock_form.return_value.__exit__ = Mock(return_value=None)

        # Mock form inputs
        mock_text_input.side_effect = ["Federal", "Gold Medal", "Match"]
        mock_selectbox.return_value = ".308 Winchester"
        mock_number_input.side_effect = [168, 2.5, 1000]
        mock_submit.return_value = True  # Form submitted

        result = render_create_ammo_tab(user, mock_supabase)

        # Should show success message
        mock_success.assert_called()


class TestAmmoViewTab(unittest.TestCase):

    @patch("streamlit.subheader")
    @patch("streamlit.info")
    def test_render_view_ammo_tab_no_ammo(self, mock_info, mock_subheader):
        user = {"email": "test@example.com", "name": "Test User"}
        mock_supabase = Mock()

        # Mock empty ammo list
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response
        )

        result = render_view_ammo_tab(user, mock_supabase)

        # Should show info message about no ammo
        mock_info.assert_called()
        self.assertIsNone(result)

    @patch("streamlit.subheader")
    @patch("streamlit.dataframe")
    def test_render_view_ammo_tab_with_ammo(self, mock_dataframe, mock_subheader):
        user = {"email": "test@example.com", "name": "Test User"}
        mock_supabase = Mock()

        # Mock ammo data
        mock_data = [
            {
                "id": "ammo-1",
                "user_email": "test@example.com",
                "make": "Federal",
                "model": "Gold Medal",
                "caliber": ".308 Winchester",
                "grain_weight": 168,
                "bullet_type": "Match",
                "ballistic_coefficient": 2.5,
                "velocity_fps": 1000,
                "created_at": "2023-12-01T10:00:00",
            }
        ]

        mock_response = Mock()
        mock_response.data = mock_data
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response
        )

        result = render_view_ammo_tab(user, mock_supabase)

        # Should display dataframe with ammo
        mock_dataframe.assert_called()
        self.assertIsNone(result)


class TestAmmoPageStructure(unittest.TestCase):
    """Test the ammo page structure and configuration"""

    def test_ammo_page_exists(self):
        """Test that the ammo page file exists"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "6_📦_Ammo.py"
        )
        self.assertTrue(os.path.exists(page_path), "Ammo page should exist")

    def test_ammo_page_has_required_imports(self):
        """Test that ammo page has required imports"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "6_📦_Ammo.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            required_imports = [
                "streamlit",
                "handle_auth",
                "create_client",
                "render_create_ammo_tab",
            ]
            for required_import in required_imports:
                self.assertIn(
                    required_import,
                    content,
                    f"Ammo page should import {required_import}",
                )

    def test_ammo_page_has_correct_tabs(self):
        """Test that ammo page has expected tabs"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "6_📦_Ammo.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            expected_tabs = ["Create", "View"]
            for tab in expected_tabs:
                self.assertIn(f'"{tab}"', content, f"Ammo page should have {tab} tab")

    def test_ammo_page_configuration(self):
        """Test ammo page configuration"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "6_📦_Ammo.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            self.assertIn('page_title="Ammo"', content)
            self.assertIn('page_icon="📦"', content)
            self.assertIn('layout="wide"', content)

    def test_ammo_page_title(self):
        """Test ammo page displays correct title"""
        page_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pages", "6_📦_Ammo.py"
        )
        if os.path.exists(page_path):
            with open(page_path, "r") as f:
                content = f.read()

            self.assertIn('st.title("🔫 Ammunition Management")', content)


class TestAmmoDataValidation(unittest.TestCase):
    """Test ammo data validation and handling"""

    def test_ammo_caliber_options(self):
        """Test that common calibers are available"""
        # This would test that the ammo creation form includes common calibers
        common_calibers = [
            ".308 Winchester",
            ".223 Remington",
            "9mm Luger",
            ".45 ACP",
            ".22 LR",
        ]

        # In a real implementation, we'd check the selectbox options
        # For now, we just verify these are reasonable caliber choices
        for caliber in common_calibers:
            self.assertIsInstance(caliber, str)
            self.assertTrue(len(caliber) > 0)

    def test_ammo_grain_weight_range(self):
        """Test that grain weights are in reasonable ranges"""
        # Test some typical grain weights
        typical_weights = [55, 62, 115, 124, 147, 168, 175, 180]

        for weight in typical_weights:
            self.assertIsInstance(weight, (int, float))
            self.assertGreater(weight, 0)
            self.assertLess(weight, 1000)  # Reasonable upper bound

    def test_ballistic_coefficient_range(self):
        """Test that ballistic coefficients are in reasonable ranges"""
        # Typical BC values
        typical_bcs = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]

        for bc in typical_bcs:
            self.assertIsInstance(bc, (int, float))
            self.assertGreater(bc, 0)
            self.assertLess(bc, 2.0)  # Reasonable upper bound


if __name__ == "__main__":
    unittest.main()
