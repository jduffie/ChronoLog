"""
Tests for DOPE page modules in the new directory structure.

This module tests the new DOPE page modules located in:
- dope/create/create_page.py
- dope/view/view_page.py  
- dope/analytics/analytics_page.py
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDopeModuleStructure(unittest.TestCase):
    """Test the new DOPE module directory structure"""

    def test_dope_subdirectories_exist(self):
        """Test that all DOPE subdirectories exist"""
        base_dir = os.path.dirname(__file__)
        
        expected_subdirs = ["create", "view", "analytics"]
        for subdir in expected_subdirs:
            subdir_path = os.path.join(base_dir, subdir)
            self.assertTrue(
                os.path.exists(subdir_path),
                f"DOPE subdirectory {subdir} should exist at {subdir_path}"
            )
            self.assertTrue(
                os.path.isdir(subdir_path),
                f"{subdir_path} should be a directory"
            )

    def test_dope_page_modules_exist(self):
        """Test that all DOPE page module files exist"""
        base_dir = os.path.dirname(__file__)
        
        expected_modules = [
            "create/create_page.py",
            "view/view_page.py",
            "analytics/analytics_page.py"
        ]
        
        for module_path in expected_modules:
            full_path = os.path.join(base_dir, module_path)
            self.assertTrue(
                os.path.exists(full_path),
                f"DOPE module {module_path} should exist at {full_path}"
            )

    def test_dope_modules_can_be_imported(self):
        """Test that all DOPE modules can be imported successfully"""
        try:
            from dope.create.create_page import render_create_page
            self.assertTrue(callable(render_create_page))
        except ImportError as e:
            self.fail(f"Failed to import dope.create.create_page: {e}")

        try:
            from dope.view.view_page import render_view_page
            self.assertTrue(callable(render_view_page))
        except ImportError as e:
            self.fail(f"Failed to import dope.view.view_page: {e}")

        try:
            from dope.analytics.analytics_page import render_analytics_page
            self.assertTrue(callable(render_analytics_page))
        except ImportError as e:
            self.fail(f"Failed to import dope.analytics.analytics_page: {e}")


class TestDopeCreatePage(unittest.TestCase):
    """Test the DOPE create page module"""

    @patch('streamlit.title')
    @patch('streamlit.info')
    @patch('streamlit.write')
    def test_render_create_page_basic(self, mock_write, mock_info, mock_title):
        """Test that render_create_page runs without errors"""
        from dope.create.create_page import render_create_page
        
        # Should not raise any exceptions
        result = render_create_page()
        
        # Verify Streamlit functions were called
        mock_title.assert_called_once_with("Create DOPE Session")
        mock_info.assert_called_once_with("🚧 This page is under development - TBD")
        mock_write.assert_called_once()
        
        # Function should return None by default
        self.assertIsNone(result)

    def test_create_page_has_docstring(self):
        """Test that create_page module has proper documentation"""
        from dope.create import create_page
        
        self.assertIsNotNone(create_page.__doc__)
        self.assertIn("DOPE Create Page", create_page.__doc__)

    def test_create_page_function_has_docstring(self):
        """Test that render_create_page function has documentation"""
        from dope.create.create_page import render_create_page
        
        self.assertIsNotNone(render_create_page.__doc__)
        self.assertIn("TODO", render_create_page.__doc__)


class TestDopeViewPage(unittest.TestCase):
    """Test the DOPE view page module"""

    @patch('streamlit.title')
    @patch('streamlit.info')
    @patch('streamlit.write')
    def test_render_view_page_basic(self, mock_write, mock_info, mock_title):
        """Test that render_view_page runs without errors"""
        from dope.view.view_page import render_view_page
        
        # Should not raise any exceptions
        result = render_view_page()
        
        # Verify Streamlit functions were called
        mock_title.assert_called_once_with("View DOPE Sessions")
        mock_info.assert_called_once_with("🚧 This page is under development - TBD")
        mock_write.assert_called_once()
        
        # Function should return None by default
        self.assertIsNone(result)

    def test_view_page_has_docstring(self):
        """Test that view_page module has proper documentation"""
        from dope.view import view_page
        
        self.assertIsNotNone(view_page.__doc__)
        self.assertIn("DOPE View Page", view_page.__doc__)

    def test_view_page_function_has_docstring(self):
        """Test that render_view_page function has documentation"""
        from dope.view.view_page import render_view_page
        
        self.assertIsNotNone(render_view_page.__doc__)
        self.assertIn("TODO", render_view_page.__doc__)


class TestDopeAnalyticsPage(unittest.TestCase):
    """Test the DOPE analytics page module"""

    @patch('streamlit.title')
    @patch('streamlit.info')
    @patch('streamlit.write')
    def test_render_analytics_page_basic(self, mock_write, mock_info, mock_title):
        """Test that render_analytics_page runs without errors"""
        from dope.analytics.analytics_page import render_analytics_page
        
        # Should not raise any exceptions
        result = render_analytics_page()
        
        # Verify Streamlit functions were called
        mock_title.assert_called_once_with("DOPE Analytics")
        mock_info.assert_called_once_with("🚧 This page is under development - TBD")
        mock_write.assert_called_once()
        
        # Function should return None by default
        self.assertIsNone(result)

    def test_analytics_page_has_docstring(self):
        """Test that analytics_page module has proper documentation"""
        from dope.analytics import analytics_page
        
        self.assertIsNotNone(analytics_page.__doc__)
        self.assertIn("DOPE Analytics Page", analytics_page.__doc__)

    def test_analytics_page_function_has_docstring(self):
        """Test that render_analytics_page function has documentation"""
        from dope.analytics.analytics_page import render_analytics_page
        
        self.assertIsNotNone(render_analytics_page.__doc__)
        self.assertIn("TODO", render_analytics_page.__doc__)


class TestDopePageIntegration(unittest.TestCase):
    """Test integration between DOPE pages and the main application"""

    def test_all_dope_pages_exist(self):
        """Test that all DOPE page files exist in the pages directory"""
        pages_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages")
        
        expected_pages = [
            "2a_📊_DOPE_Overview.py",
            "2b_📊_DOPE_Create.py", 
            "2c_📊_DOPE_View.py",
            "2d_📊_DOPE_Analytics.py"
        ]
        
        for page_file in expected_pages:
            page_path = os.path.join(pages_dir, page_file)
            self.assertTrue(
                os.path.exists(page_path),
                f"DOPE page {page_file} should exist at {page_path}"
            )

    def test_dope_pages_import_correct_modules(self):
        """Test that DOPE pages import the correct modules"""
        pages_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages")
        
        # Test Create page imports
        create_page_path = os.path.join(pages_dir, "2b_📊_DOPE_Create.py")
        if os.path.exists(create_page_path):
            with open(create_page_path, 'r') as f:
                content = f.read()
            self.assertIn("from dope.create.create_page import render_create_page", content)

        # Test View page imports  
        view_page_path = os.path.join(pages_dir, "2c_📊_DOPE_View.py")
        if os.path.exists(view_page_path):
            with open(view_page_path, 'r') as f:
                content = f.read()
            self.assertIn("from dope.view.view_page import render_view_page", content)

        # Test Analytics page imports
        analytics_page_path = os.path.join(pages_dir, "2d_📊_DOPE_Analytics.py")
        if os.path.exists(analytics_page_path):
            with open(analytics_page_path, 'r') as f:
                content = f.read()
            self.assertIn("from dope.analytics.analytics_page import render_analytics_page", content)

    def test_dope_pages_have_proper_configuration(self):
        """Test that DOPE pages have proper Streamlit configuration"""
        pages_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages")
        
        dope_pages = [
            ("2b_📊_DOPE_Create.py", "DOPE Create", "📊"),
            ("2c_📊_DOPE_View.py", "DOPE View", "📊"), 
            ("2d_📊_DOPE_Analytics.py", "DOPE Analytics", "📊")
        ]
        
        for page_file, expected_title, expected_icon in dope_pages:
            page_path = os.path.join(pages_dir, page_file)
            if os.path.exists(page_path):
                with open(page_path, 'r') as f:
                    content = f.read()
                
                # Check for Streamlit page configuration
                self.assertIn("st.set_page_config", content)
                self.assertIn(f'page_title="{expected_title}"', content)
                self.assertIn(f'page_icon="{expected_icon}"', content)
                self.assertIn('layout="wide"', content)
                
                # Check for authentication handling
                self.assertIn("handle_auth()", content)
                self.assertIn("if not user:", content)


class TestDopeModuleCompatibility(unittest.TestCase):
    """Test compatibility and integration of DOPE modules"""

    def test_dope_model_still_exists(self):
        """Test that the existing dope_model.py is still available"""
        dope_dir = os.path.dirname(__file__)
        model_path = os.path.join(dope_dir, "dope_model.py")
        
        self.assertTrue(
            os.path.exists(model_path),
            "dope_model.py should still exist for compatibility"
        )

    def test_dope_model_can_be_imported(self):
        """Test that DopeModel can still be imported"""
        try:
            from dope.dope_model import DopeModel
            model = DopeModel()
            self.assertIsNotNone(model)
        except ImportError as e:
            self.fail(f"Failed to import DopeModel: {e}")

    def test_no_old_tab_modules_exist(self):
        """Test that old tab modules have been properly removed"""
        dope_dir = os.path.dirname(__file__)
        
        old_modules = [
            "sessions_tab.py",
            "view_session_tab.py", 
            "create_session_tab.py",
            "test_dope.py"
        ]
        
        for old_module in old_modules:
            old_path = os.path.join(dope_dir, old_module)
            self.assertFalse(
                os.path.exists(old_path),
                f"Old module {old_module} should not exist anymore"
            )


if __name__ == "__main__":
    unittest.main()