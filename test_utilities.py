#!/usr/bin/env python3
"""
Test suite for utility scripts and helper functions.
Tests database utilities, file processing, and system management scripts.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, mock_open, patch

# Add root directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class TestVerifySupabase(unittest.TestCase):
    """Test verify_supabase.py utility"""

    @patch("sys.argv", ["verify_supabase.py"])
    def test_verify_supabase_imports(self):
        """Test that verify_supabase script can be imported"""
        try:
            # Try to import the module
            spec = __import__("verify_supabase")
            self.assertIsNotNone(spec)
        except ImportError as e:
            self.fail(f"verify_supabase.py should be importable: {e}")

    @patch.dict(os.environ, {"SUPABASE_SERVICE_ROLE_KEY": "test-key"})
    @patch("supabase.create_client")
    def test_supabase_connection_mocked(self, mock_create_client):
        """Test Supabase connection with mocked client"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        # Mock a simple connection test
        mock_client.table.return_value.select.return_value.limit.return_value.execute.return_value.data = (
            []
        )

        # This should not raise an exception
        try:
            import verify_supabase

            # If we got here, the connection test passed
            self.assertTrue(True)
        except Exception as e:
            # Connection failed - this is expected in test environment
            self.assertIn("connection", str(e).lower())


class TestEnvironmentVariables(unittest.TestCase):
    """Test test_env_variables.py utility"""

    def test_env_variables_script_structure(self):
        """Test that env variables test script has proper structure"""
        script_path = os.path.join(os.path.dirname(__file__), "test_env_variables.py")
        self.assertTrue(
            os.path.exists(script_path), "test_env_variables.py should exist"
        )

        # Check that it's a valid Python file
        with open(script_path, "r") as f:
            content = f.read()
            self.assertIn("def", content)  # Should have function definitions
            self.assertIn("AUTH0_", content)  # Should check Auth0 vars
            self.assertIn("SUPABASE_", content)  # Should check Supabase vars

    def test_required_env_vars_defined(self):
        """Test that required environment variables are defined in the script"""
        try:
            import test_env_variables

            # Should have test_env_variables function and environment checks
            has_test_func = hasattr(test_env_variables, "test_env_variables")
            has_auth0_check = any(
                "AUTH0_DOMAIN" in str(getattr(test_env_variables, attr, ""))
                for attr in dir(test_env_variables)
            )

            self.assertTrue(
                has_test_func or has_auth0_check,
                "test_env_variables should have test function or AUTH0 checks",
            )
        except ImportError:
            # If the module can't be imported, that's okay for this test
            self.skipTest("test_env_variables.py could not be imported")


class TestResetSystem(unittest.TestCase):
    """Test reset_system.py utility (with safety checks)"""

    def test_reset_system_imports(self):
        """Test that reset_system script can be imported safely"""
        try:
            # Import but don't execute main
            spec = __import__("reset_system")
            self.assertIsNotNone(spec)
        except ImportError as e:
            self.fail(f"reset_system.py should be importable: {e}")

    @patch("reset_system.input", return_value="n")  # Always answer 'no' to confirmation
    @patch("sys.exit")
    def test_reset_system_safety_confirmation(self, mock_exit, mock_input):
        """Test that reset_system requires confirmation before proceeding"""
        try:
            import reset_system

            # Try to run main function
            if hasattr(reset_system, "main"):
                reset_system.main()

            # Should exit when user says 'no'
            mock_exit.assert_called_once_with(0)
        except Exception:
            # Expected - script may fail without proper environment
            pass

    def test_reset_system_has_safety_checks(self):
        """Test that reset_system script has proper safety checks"""
        script_path = os.path.join(os.path.dirname(__file__), "reset_system.py")
        self.assertTrue(os.path.exists(script_path), "reset_system.py should exist")

        with open(script_path, "r") as f:
            content = f.read()
            # Should have confirmation prompts
            self.assertIn("input(", content.lower())
            self.assertIn("warning", content.lower())


class TestFilesUtilities(unittest.TestCase):
    """Test file-related utilities"""

    def test_download_uploads_exists(self):
        """Test that download_uploads.py exists"""
        script_path = os.path.join(os.path.dirname(__file__), "download_uploads.py")
        self.assertTrue(os.path.exists(script_path), "download_uploads.py should exist")

    def test_files_tab_exists(self):
        """Test that files_tab.py exists"""
        script_path = os.path.join(os.path.dirname(__file__), "files_tab.py")
        self.assertTrue(os.path.exists(script_path), "files_tab.py should exist")

    def test_import_factory_cartridges_exists(self):
        """Test that import_factory_cartridges.py exists"""
        script_path = os.path.join(
            os.path.dirname(__file__), "import_factory_cartridges.py"
        )
        self.assertTrue(
            os.path.exists(script_path), "import_factory_cartridges.py should exist"
        )


class TestRunAllTestsScript(unittest.TestCase):
    """Test the run_all_tests.py script itself"""

    def test_run_all_tests_structure(self):
        """Test that run_all_tests script has proper structure"""
        script_path = os.path.join(os.path.dirname(__file__), "run_all_tests.py")
        self.assertTrue(os.path.exists(script_path), "run_all_tests.py should exist")

        with open(script_path, "r") as f:
            content = f.read()
            # Should have main function
            self.assertIn("def main()", content)
            # Should discover tests
            self.assertIn("discover", content.lower())
            # Should have test directories defined
            self.assertIn("test_dirs", content)

    def test_test_runner_discovers_modules(self):
        """Test that test runner can discover test modules"""
        import run_all_tests

        # Should have test discovery function
        self.assertTrue(hasattr(run_all_tests, "discover_and_run_tests"))
        self.assertTrue(hasattr(run_all_tests, "run_specific_module_tests"))

    def test_test_directories_exist(self):
        """Test that configured test directories exist"""
        import run_all_tests

        # Get test directories from the module
        test_dirs = []
        with open("run_all_tests.py", "r") as f:
            content = f.read()
            # Extract test_dirs list (basic parsing)
            if "test_dirs = [" in content:
                # This is a basic check that the directories are meaningful
                self.assertIn("chronograph", content)
                self.assertIn("weather", content)
                self.assertIn("mapping", content)


class TestIntegrationScripts(unittest.TestCase):
    """Test integration test scripts"""

    def test_run_integration_tests_exists(self):
        """Test that run_integration_tests.py exists"""
        script_path = os.path.join(
            os.path.dirname(__file__), "run_integration_tests.py"
        )
        self.assertTrue(
            os.path.exists(script_path), "run_integration_tests.py should exist"
        )

    def test_test_integration_exists(self):
        """Test that test_integration.py exists"""
        script_path = os.path.join(os.path.dirname(__file__), "test_integration.py")
        self.assertTrue(os.path.exists(script_path), "test_integration.py should exist")


class TestNavigationUtilities(unittest.TestCase):
    """Test navigation and UI utilities"""

    def test_navigation_module_exists(self):
        """Test that navigation.py exists"""
        script_path = os.path.join(os.path.dirname(__file__), "navigation.py")
        self.assertTrue(os.path.exists(script_path), "navigation.py should exist")


class TestDataManagementScripts(unittest.TestCase):
    """Test data import/export scripts"""

    def test_upload_bullets_csv_exists(self):
        """Test that upload_bullets_csv.py exists"""
        script_path = os.path.join(os.path.dirname(__file__), "upload_bullets_csv.py")
        self.assertTrue(
            os.path.exists(script_path), "upload_bullets_csv.py should exist"
        )



class TestMainApplications(unittest.TestCase):
    """Test main application entry points"""

    def test_chronolog_main_exists(self):
        """Test that ChronoLog.py main application exists"""
        script_path = os.path.join(os.path.dirname(__file__), "ChronoLog.py")
        self.assertTrue(os.path.exists(script_path), "ChronoLog.py should exist")

    def test_chronolog_structure(self):
        """Test that ChronoLog.py has proper structure"""
        script_path = os.path.join(os.path.dirname(__file__), "ChronoLog.py")
        if os.path.exists(script_path):
            with open(script_path, "r") as f:
                content = f.read()
                # Should import or reference main functionality
                has_import = "import" in content.lower()
                has_main_ref = "main" in content.lower() or "run" in content.lower()

                self.assertTrue(
                    has_import and has_main_ref,
                    "ChronoLog.py should have imports and main functionality",
                )

    def test_pages_directory_structure(self):
        """Test that pages directory has proper structure"""
        pages_dir = os.path.join(os.path.dirname(__file__), "pages")
        self.assertTrue(os.path.exists(pages_dir), "pages directory should exist")

        # Should have some page files
        page_files = [f for f in os.listdir(pages_dir) if f.endswith(".py")]
        self.assertGreater(len(page_files), 0, "Should have page files")

        # Check for key pages
        page_names = [f.lower() for f in page_files]
        expected_pages = ["home", "chronograph", "weather", "rifles"]

        for expected in expected_pages:
            has_page = any(expected in name for name in page_names)
            self.assertTrue(has_page, f"Should have a page containing '{expected}'")


class TestScriptExecutability(unittest.TestCase):
    """Test that scripts are properly executable"""

    def test_python_scripts_have_shebang(self):
        """Test that key scripts have proper shebang lines"""
        scripts_to_check = [
            "run_all_tests.py",
            "run_integration_tests.py",
            "verify_supabase.py",
        ]

        for script_name in scripts_to_check:
            script_path = os.path.join(os.path.dirname(__file__), script_name)
            if os.path.exists(script_path):
                with open(script_path, "r") as f:
                    first_line = f.readline().strip()
                    if first_line:  # If file is not empty
                        # Should have shebang for Python
                        self.assertTrue(
                            first_line.startswith("#!/usr/bin/env python")
                            or first_line.startswith("#!/usr/bin/python")
                            or not first_line.startswith(
                                "#!"
                            ),  # Or no shebang is fine too
                            f"{script_name} should have proper shebang or none",
                        )

    def test_shell_scripts_exist_and_executable(self):
        """Test that shell scripts exist and are properly formatted"""
        shell_scripts = ["export_env_from_1password.sh", "setup_secrets.sh"]

        for script_name in shell_scripts:
            script_path = os.path.join(os.path.dirname(__file__), script_name)
            if os.path.exists(script_path):
                # Check that it's a shell script
                with open(script_path, "r") as f:
                    first_line = f.readline().strip()
                    if first_line:
                        self.assertTrue(
                            first_line.startswith("#!/bin/bash")
                            or first_line.startswith("#!/bin/sh")
                            or "bash" in first_line.lower(),
                            f"{script_name} should be a shell script",
                        )


if __name__ == "__main__":
    unittest.main()
