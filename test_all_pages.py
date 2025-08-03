import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modular tests from subdirectories
from chronograph.test_chronograph import (
    TestChronographService,
    TestChronographModels,
    TestChronographImportTab,
    TestChronographPageStructure,
)

# from weather.test_weather import TestWeatherSource, TestWeatherMeasurement, TestWeatherImportTab, TestWeatherPageStructure  # Temporarily disabled
from dope.test_dope import (
    TestDopeModel,
    TestDopeCreateSessionTab,
    TestDopePageStructure,
    TestDopeSessionManagement,
)
from ammo.test_ammo import (
    TestAmmoCreateTab,
    TestAmmoViewTab,
    TestAmmoPageStructure,
    TestAmmoDataValidation,
)
from rifles.test_rifles import (
    TestRiflesCreateTab,
    TestRiflesViewTab,
    TestRiflesPageStructure,
    TestRifleDataValidation,
)
from mapping.test_mapping import (
    TestPublicRangesController,
    TestMappingPageStructure,
    TestMappingModels,
)


class TestPageStructure(unittest.TestCase):
    """Test the structural aspects of pages without running full functionality"""

    def test_all_pages_exist(self):
        """Test that all expected page files exist"""
        expected_pages = [
            "pages/1_🏠_Home.py",
            "pages/2_📊_DOPE.py",
            "pages/3_⏱️_Chronograph.py",
            "pages/4_🌤️_Weather.py",
            "pages/5_🌍_Ranges.py",
            "pages/6_📦_Ammo.py",
            "pages/7_📏_Rifles.py",
        ]

        for page_file in expected_pages:
            with self.subTest(page=page_file):
                self.assertTrue(
                    os.path.exists(page_file), f"Page file {page_file} should exist"
                )

    def test_pages_have_required_imports(self):
        """Test that pages have required imports"""
        page_imports = {
            "pages/1_🏠_Home.py": ["streamlit", "handle_auth"],
            "pages/2_📊_DOPE.py": ["streamlit", "handle_auth", "create_client"],
            "pages/3_⏱️_Chronograph.py": ["streamlit", "handle_auth", "create_client"],
            "pages/4_🌤️_Weather.py": ["streamlit", "handle_auth", "create_client"],
            "pages/5_🌍_Ranges.py": ["streamlit", "handle_auth", "create_client"],
            "pages/6_📦_Ammo.py": ["streamlit", "handle_auth", "create_client"],
            "pages/7_📏_Rifles.py": ["streamlit", "handle_auth", "create_client"],
        }

        for page_file, required_imports in page_imports.items():
            with self.subTest(page=page_file):
                if os.path.exists(page_file):
                    with open(page_file, "r") as f:
                        content = f.read()

                    for required_import in required_imports:
                        self.assertIn(
                            required_import,
                            content,
                            f"Page {page_file} should import {required_import}",
                        )

    def test_pages_have_main_or_run_function(self):
        """Test that pages have either main() or run() function"""
        page_files = [
            "pages/1_🏠_Home.py",
            "pages/2_📊_DOPE.py",
            "pages/3_⏱️_Chronograph.py",
            "pages/4_🌤️_Weather.py",
            "pages/5_🌍_Ranges.py",
            "pages/6_📦_Ammo.py",
            "pages/7_📏_Rifles.py",
        ]

        for page_file in page_files:
            with self.subTest(page=page_file):
                if os.path.exists(page_file):
                    with open(page_file, "r") as f:
                        content = f.read()

                    has_main = "def main(" in content
                    has_run = "def run(" in content

                    self.assertTrue(
                        has_main or has_run,
                        f"Page {page_file} should have either main() or run() function",
                    )

    def test_pages_set_page_config(self):
        """Test that pages call st.set_page_config"""
        page_files = [
            "pages/1_🏠_Home.py",
            "pages/2_📊_DOPE.py",
            "pages/3_⏱️_Chronograph.py",
            "pages/4_🌤️_Weather.py",
            "pages/5_🌍_Ranges.py",
            "pages/6_📦_Ammo.py",
            "pages/7_📏_Rifles.py",
        ]

        for page_file in page_files:
            with self.subTest(page=page_file):
                if os.path.exists(page_file):
                    with open(page_file, "r") as f:
                        content = f.read()

                    self.assertIn(
                        "st.set_page_config",
                        content,
                        f"Page {page_file} should call st.set_page_config",
                    )

    def test_pages_handle_authentication(self):
        """Test that pages handle authentication"""
        page_files = [
            "pages/1_🏠_Home.py",
            "pages/2_📊_DOPE.py",
            "pages/3_⏱️_Chronograph.py",
            "pages/4_🌤️_Weather.py",
            "pages/5_🌍_Ranges.py",
            "pages/6_📦_Ammo.py",
            "pages/7_📏_Rifles.py",
        ]

        for page_file in page_files:
            with self.subTest(page=page_file):
                if os.path.exists(page_file):
                    with open(page_file, "r") as f:
                        content = f.read()

                    self.assertIn(
                        "handle_auth()",
                        content,
                        f"Page {page_file} should call handle_auth()",
                    )

                    # Should also check if user is None and return early
                    self.assertIn(
                        "if not user:",
                        content,
                        f"Page {page_file} should check if user is authenticated",
                    )


class TestPageConfiguration(unittest.TestCase):
    """Test page configuration details"""

    def test_page_titles_and_icons(self):
        """Test that pages have appropriate titles and icons"""
        expected_configs = {
            "pages/1_🏠_Home.py": ("ChronoLog - Home", "🏠"),
            "pages/2_📊_DOPE.py": ("DOPE", "📊"),
            "pages/3_⏱️_Chronograph.py": ("Chronograph", "📁"),
            "pages/4_🌤️_Weather.py": ("Weather - ChronoLog", "🌤️"),
            "pages/5_🌍_Ranges.py": ("Ranges", "🌍"),
            "pages/6_📦_Ammo.py": ("Ammo", "📦"),
            "pages/7_📏_Rifles.py": ("Rifles", "📏"),
        }

        for page_file, (expected_title, expected_icon) in expected_configs.items():
            with self.subTest(page=page_file):
                if os.path.exists(page_file):
                    with open(page_file, "r") as f:
                        content = f.read()

                    self.assertIn(
                        f'page_title="{expected_title}"',
                        content,
                        f"Page {page_file} should have title '{expected_title}'",
                    )
                    self.assertIn(
                        f'page_icon="{expected_icon}"',
                        content,
                        f"Page {page_file} should have icon '{expected_icon}'",
                    )

    def test_pages_use_wide_layout(self):
        """Test that pages use wide layout"""
        page_files = [
            "pages/1_🏠_Home.py",
            "pages/2_📊_DOPE.py",
            "pages/3_⏱️_Chronograph.py",
            "pages/4_🌤️_Weather.py",
            "pages/5_🌍_Ranges.py",
            "pages/6_📦_Ammo.py",
            "pages/7_📏_Rifles.py",
        ]

        for page_file in page_files:
            with self.subTest(page=page_file):
                if os.path.exists(page_file):
                    with open(page_file, "r") as f:
                        content = f.read()

                    self.assertIn(
                        'layout="wide"',
                        content,
                        f"Page {page_file} should use wide layout",
                    )


class TestMainAppStructure(unittest.TestCase):
    """Test the main ChronoLog.py application structure"""

    def test_chronolog_main_exists(self):
        """Test that ChronoLog.py exists"""
        self.assertTrue(os.path.exists("ChronoLog.py"), "ChronoLog.py should exist")

    def test_chronolog_imports_home_page(self):
        """Test that ChronoLog.py imports the home page"""
        if os.path.exists("ChronoLog.py"):
            with open("ChronoLog.py", "r") as f:
                content = f.read()

            self.assertIn(
                "pages/1_🏠_Home.py",
                content,
                "ChronoLog.py should import the home page",
            )
            self.assertIn(
                "importlib.util",
                content,
                "ChronoLog.py should use importlib to load the home page",
            )


class TestPageTabStructure(unittest.TestCase):
    """Test that pages have appropriate tab structures"""

    def test_chronograph_has_correct_tabs(self):
        """Test that chronograph page has expected tabs"""
        if os.path.exists("pages/3_⏱️_Chronograph.py"):
            with open("pages/3_⏱️_Chronograph.py", "r") as f:
                content = f.read()

            expected_tabs = ["Import", "View", "Edit", "My Files"]
            for tab in expected_tabs:
                self.assertIn(
                    f'"{tab}"', content, f"Chronograph page should have {tab} tab"
                )

    def test_weather_has_correct_tabs(self):
        """Test that weather page has expected tabs"""
        if os.path.exists("pages/4_🌤️_Weather.py"):
            with open("pages/4_🌤️_Weather.py", "r") as f:
                content = f.read()

            expected_tabs = ["Sources", "Import", "Logs", "View Log", "My Files"]
            for tab in expected_tabs:
                self.assertIn(
                    f'"{tab}"', content, f"Weather page should have {tab} tab"
                )

    def test_dope_has_correct_tabs(self):
        """Test that DOPE page has expected tabs"""
        if os.path.exists("pages/2_📊_DOPE.py"):
            with open("pages/2_📊_DOPE.py", "r") as f:
                content = f.read()

            expected_tabs = ["Create", "View", "Analytics"]
            for tab in expected_tabs:
                self.assertIn(f'"{tab}"', content, f"DOPE page should have {tab} tab")

    def test_ranges_has_correct_tabs(self):
        """Test that ranges page has expected tabs"""
        if os.path.exists("pages/5_🌍_Ranges.py"):
            with open("pages/5_🌍_Ranges.py", "r") as f:
                content = f.read()

            expected_tabs = ["Public Ranges", "Nominate Range", "My Submissions"]
            # Check for partial matches since the full tab names include emojis
            tab_patterns = ["Public Ranges", "Nominate", "Submissions"]
            for pattern in tab_patterns:
                self.assertIn(
                    pattern, content, f"Ranges page should reference {pattern}"
                )


class TestDatabaseConnections(unittest.TestCase):
    """Test that pages properly handle database connections"""

    def test_pages_handle_supabase_errors(self):
        """Test that pages handle Supabase connection errors"""
        pages_with_db = [
            "pages/2_📊_DOPE.py",
            "pages/3_⏱️_Chronograph.py",
            "pages/4_🌤️_Weather.py",
            "pages/5_🌍_Ranges.py",
            "pages/6_📦_Ammo.py",
            "pages/7_📏_Rifles.py",
        ]

        for page_file in pages_with_db:
            with self.subTest(page=page_file):
                if os.path.exists(page_file):
                    with open(page_file, "r") as f:
                        content = f.read()

                    self.assertIn(
                        "try:",
                        content,
                        f"Page {page_file} should have try/except for database connection",
                    )
                    self.assertIn(
                        "st.error",
                        content,
                        f"Page {page_file} should display error on database connection failure",
                    )

    def test_pages_use_secrets_for_db_config(self):
        """Test that pages use Streamlit secrets for database configuration"""
        pages_with_db = [
            "pages/2_📊_DOPE.py",
            "pages/3_⏱️_Chronograph.py",
            "pages/4_🌤️_Weather.py",
            "pages/5_🌍_Ranges.py",
            "pages/6_📦_Ammo.py",
            "pages/7_📏_Rifles.py",
        ]

        for page_file in pages_with_db:
            with self.subTest(page=page_file):
                if os.path.exists(page_file):
                    with open(page_file, "r") as f:
                        content = f.read()

                    self.assertIn(
                        'st.secrets["supabase"]',
                        content,
                        f"Page {page_file} should use Streamlit secrets for Supabase config",
                    )


if __name__ == "__main__":
    unittest.main()
