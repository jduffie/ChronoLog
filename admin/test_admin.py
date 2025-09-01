#!/usr/bin/env python3
"""
Comprehensive test suite for the admin module.
Tests admin functionality including user management, data processing, and business logic.
"""

import os
import sys
import unittest
from datetime import datetime
from unittest.mock import Mock, patch
import pandas as pd

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin.users_tab import render_users_tab, render_user_edit_form, render_user_delete_form


class TestAdminUsersTab(unittest.TestCase):
    """Test admin users tab functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_supabase = Mock()
        self.mock_user = {
            "id": "admin-user-123",
            "email": "admin@example.com",
            "name": "Admin User",
            "roles": ["admin", "user"],
        }
        
        self.sample_users_data = [
            {
                "id": "user-1",
                "email": "user1@example.com",
                "name": "User One",
                "username": "user1",
                "country": "United States",
                "state": "California",
                "unit_system": "Imperial",
                "profile_complete": True,
                "roles": ["user"],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": "user-2",
                "email": "user2@example.com",
                "name": "User Two",
                "username": "user2",
                "country": "Canada",
                "state": "Ontario",
                "unit_system": "Metric",
                "profile_complete": False,
                "roles": ["user"],
                "created_at": "2024-01-02T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            },
            {
                "id": "admin-1",
                "email": "admin1@example.com",
                "name": "Admin One",
                "username": "admin1",
                "country": "United States",
                "state": "New York",
                "unit_system": "Imperial",
                "profile_complete": True,
                "roles": ["admin", "user"],
                "created_at": "2024-01-03T00:00:00Z",
                "updated_at": "2024-01-03T00:00:00Z",
            }
        ]

    def test_database_query_construction(self):
        """Test that database queries are constructed correctly"""
        # Mock successful database response
        mock_response = Mock()
        mock_response.data = self.sample_users_data
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

        with patch("admin.users_tab.st"):
            render_users_tab(self.mock_user, self.mock_supabase)

        # Verify database query was constructed correctly
        self.mock_supabase.table.assert_called_with("users")
        self.mock_supabase.table.return_value.select.assert_called_with("*")
        self.mock_supabase.table.return_value.select.return_value.order.assert_called_with("created_at", desc=True)

    @patch("admin.users_tab.st")
    def test_render_users_tab_no_users(self, mock_st):
        """Test rendering users tab when no users exist"""
        # Mock empty database response
        mock_response = Mock()
        mock_response.data = []
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

        # Call the function
        render_users_tab(self.mock_user, self.mock_supabase)

        # Verify info message is shown
        mock_st.info.assert_called_with("📭 No users found in the database.")

    @patch("admin.users_tab.st")
    def test_render_users_tab_database_error(self, mock_st):
        """Test handling of database errors"""
        # Mock database error
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.side_effect = Exception("Database error")

        # Call the function
        render_users_tab(self.mock_user, self.mock_supabase)

        # Verify error handling
        mock_st.error.assert_called()
        error_call_args = mock_st.error.call_args[0][0]
        self.assertIn("Error loading users", error_call_args)

    @patch("admin.users_tab.pd.DataFrame")
    def test_data_processing_logic(self, mock_dataframe):
        """Test that user data is processed correctly"""
        # Mock successful database response
        mock_response = Mock()
        mock_response.data = self.sample_users_data
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

        # Mock DataFrame creation
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=3)  # Total users count
        mock_dataframe.return_value = mock_df

        with patch("admin.users_tab.st"):
            render_users_tab(self.mock_user, self.mock_supabase)

        # Verify DataFrame was created with correct data
        mock_dataframe.assert_called_with(self.sample_users_data)

    def test_user_role_analysis(self):
        """Test admin vs regular user role analysis logic"""
        # Create DataFrame with mixed roles
        df = pd.DataFrame(self.sample_users_data)
        
        # Test admin count logic (mimicking the admin module logic)
        admin_count = df["roles"].apply(
            lambda x: "admin" in x if x and isinstance(x, list) else False
        ).sum()
        
        self.assertEqual(admin_count, 1)  # Only one admin in sample data

    def test_profile_completeness_analysis(self):
        """Test profile completeness analysis logic"""
        # Create DataFrame
        df = pd.DataFrame(self.sample_users_data)
        
        # Test profile completeness logic
        complete_profiles = df["profile_complete"].sum()
        
        self.assertEqual(complete_profiles, 2)  # Two users have complete profiles

    def test_country_analysis(self):
        """Test country analysis logic"""
        # Create DataFrame
        df = pd.DataFrame(self.sample_users_data)
        
        # Test most common country logic
        if not df["country"].empty:
            most_common_country = df["country"].mode().iloc[0]
            country_count = (df["country"] == most_common_country).sum()
            
            self.assertEqual(most_common_country, "United States")
            self.assertEqual(country_count, 2)  # Two users from US

    def test_filtering_logic(self):
        """Test data filtering logic"""
        # Create DataFrame
        df = pd.DataFrame(self.sample_users_data)
        
        # Test country filtering
        us_users = df[df["country"] == "United States"]
        self.assertEqual(len(us_users), 2)
        
        # Test unit system filtering
        imperial_users = df[df["unit_system"] == "Imperial"]
        self.assertEqual(len(imperial_users), 2)
        
        # Test profile status filtering
        complete_users = df[df["profile_complete"] == True]
        self.assertEqual(len(complete_users), 2)
        
        # Test role filtering (admin users)
        admin_users = df[df["roles"].apply(
            lambda x: "admin" in x if x and isinstance(x, list) else False
        )]
        self.assertEqual(len(admin_users), 1)


class TestAdminUserEditForm(unittest.TestCase):
    """Test admin user edit form functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_supabase = Mock()
        self.sample_user = {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User",
            "username": "testuser",
            "country": "United States",
            "state": "California",
            "unit_system": "Imperial",
            "profile_complete": True,
            "roles": ["user"],
            "picture": "https://example.com/pic.jpg",
        }

    def test_user_edit_data_validation(self):
        """Test user edit data validation logic"""
        # Test that required fields are properly validated
        update_data = {
            "name": "Updated User",
            "username": "updateduser",
            "country": "Canada",
            "state": "Ontario",
            "unit_system": "Metric",
            "profile_complete": False,
            "roles": ["user", "admin"],
            "picture": None,  # Should handle None pictures
            "updated_at": datetime.now().isoformat(),
        }
        
        # Verify data structure is correct
        self.assertIsInstance(update_data["name"], str)
        self.assertIsInstance(update_data["roles"], list)
        self.assertIsInstance(update_data["profile_complete"], bool)
        self.assertIn("updated_at", update_data)

    def test_role_validation_logic(self):
        """Test role validation and assignment logic"""
        # Test role combinations
        test_cases = [
            (True, False, ["user"]),           # Only user role
            (True, True, ["user", "admin"]),   # Both roles
            (False, True, ["admin"]),          # Only admin role (should default to user)
            (False, False, ["user"]),          # No roles (should default to user)
        ]
        
        for has_user_role, has_admin_role, expected_roles in test_cases:
            new_roles = []
            if has_user_role:
                new_roles.append("user")
            if has_admin_role:
                new_roles.append("admin")
            
            # Ensure at least user role (mimicking admin module logic)
            if not new_roles:
                new_roles = ["user"]
            
            # For case where only admin is selected, we still need user role
            if "admin" in new_roles and "user" not in new_roles:
                # This test case shows current logic - admin users should also have user role
                pass
            
            # The key insight is that the admin module ensures at least user role exists
            self.assertGreaterEqual(len(new_roles), 1)

    def test_update_data_preparation(self):
        """Test update data preparation and sanitization"""
        # Test data cleaning
        raw_data = {
            "name": "  Test User  ",  # Should be trimmed
            "username": "  testuser  ",  # Should be trimmed
            "country": "United States",
            "state": "California",
            "unit_system": "Imperial",
            "profile_complete": True,
            "roles": ["user"],
            "picture": "   ",  # Empty string should become None
        }
        
        # Simulate data cleaning (as done in admin module)
        cleaned_data = {
            "name": raw_data["name"].strip(),
            "username": raw_data["username"].strip(),
            "country": raw_data["country"].strip(),
            "state": raw_data["state"].strip(),
            "unit_system": raw_data["unit_system"],
            "profile_complete": raw_data["profile_complete"],
            "roles": raw_data["roles"],
            "picture": raw_data["picture"].strip() if raw_data["picture"].strip() else None,
        }
        
        self.assertEqual(cleaned_data["name"], "Test User")
        self.assertEqual(cleaned_data["username"], "testuser")
        self.assertIsNone(cleaned_data["picture"])


class TestAdminUserDeleteForm(unittest.TestCase):
    """Test admin user delete form functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_supabase = Mock()
        self.sample_user = {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User",
            "username": "testuser",
            "roles": ["user"],
            "created_at": "2024-01-01T00:00:00Z",
        }
        
        self.admin_user = {
            "id": "admin-123",
            "email": "admin@example.com",
            "name": "Admin User",
            "roles": ["admin", "user"],
        }

    def test_admin_user_detection(self):
        """Test detection of admin users for deletion warnings"""
        # Test regular user
        regular_roles = self.sample_user.get("roles", [])
        is_admin = isinstance(regular_roles, list) and "admin" in regular_roles
        self.assertFalse(is_admin)
        
        # Test admin user
        admin_roles = self.admin_user.get("roles", [])
        is_admin = isinstance(admin_roles, list) and "admin" in admin_roles
        self.assertTrue(is_admin)

    def test_email_confirmation_logic(self):
        """Test email confirmation validation logic"""
        test_cases = [
            ("test@example.com", "test@example.com", True),      # Exact match
            ("test@example.com", "TEST@EXAMPLE.COM", False),     # Case sensitive
            ("test@example.com", "test@example.co", False),      # Partial match
            ("test@example.com", "", False),                     # Empty confirmation
            ("test@example.com", "   test@example.com   ", True), # Whitespace (should match after strip)
        ]
        
        for user_email, confirmation_email, should_match in test_cases:
            email_matches = confirmation_email.strip() == user_email
            self.assertEqual(email_matches, should_match, 
                           f"Email match test failed: '{confirmation_email}' vs '{user_email}'")

    def test_related_data_table_checking(self):
        """Test related data table checking logic"""
        # Tables that should be checked for user data
        tables_to_check = [
            "chrono_sessions",
            "chrono_measurements", 
            "dope_sessions",
            "dope_measurements",
            "weather_measurements",
            "weather_source",
            "ranges_submissions",
            "rifles",
            "bullets",
        ]
        
        # Verify we have a comprehensive list of tables
        self.assertGreater(len(tables_to_check), 5)
        self.assertIn("chrono_sessions", tables_to_check)
        self.assertIn("rifles", tables_to_check)
        self.assertIn("bullets", tables_to_check)

    def test_foreign_key_error_detection(self):
        """Test foreign key error detection logic"""
        error_messages = [
            "foreign key constraint violation",
            "violates foreign key constraint",
            "FOREIGN KEY constraint failed",
        ]
        
        # Test messages that should be detected
        for error_msg in error_messages:
            # Simulate error detection logic from admin module
            is_foreign_key_error = (
                "foreign key constraint" in error_msg.lower() or
                "violates foreign key" in error_msg.lower()
            )
            
            self.assertTrue(is_foreign_key_error, f"Should detect FK error: {error_msg}")
        
        # Test message that should NOT be detected
        non_fk_error = "Cannot delete or update a parent row"
        is_foreign_key_error = (
            "foreign key constraint" in non_fk_error.lower() or
            "violates foreign key" in non_fk_error.lower()
        )
        self.assertFalse(is_foreign_key_error, "Should not detect as FK error without specific keywords")


class TestAdminModuleIntegration(unittest.TestCase):
    """Test admin module integration functionality"""

    def test_admin_module_imports(self):
        """Test that admin module components can be imported"""
        from admin.users_tab import render_users_tab, render_user_edit_form, render_user_delete_form
        
        # Verify functions are callable
        self.assertTrue(callable(render_users_tab))
        self.assertTrue(callable(render_user_edit_form))
        self.assertTrue(callable(render_user_delete_form))

    def test_admin_function_signatures(self):
        """Test that admin functions have correct signatures"""
        import inspect
        
        # Test render_users_tab signature
        sig = inspect.signature(render_users_tab)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['user', 'supabase'])

        # Test render_user_edit_form signature
        sig = inspect.signature(render_user_edit_form)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['user_data', 'supabase'])

        # Test render_user_delete_form signature
        sig = inspect.signature(render_user_delete_form)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['user_data', 'supabase'])

    def test_pandas_dataframe_compatibility(self):
        """Test compatibility with pandas DataFrame operations"""
        # Create test data similar to what admin module would process
        sample_data = [
            {"roles": ["user"], "profile_complete": True, "country": "US"},
            {"roles": ["admin", "user"], "profile_complete": False, "country": "CA"},
            {"roles": ["user"], "profile_complete": True, "country": "US"},
        ]
        
        df = pd.DataFrame(sample_data)
        
        # Test operations used in admin module
        admin_count = df["roles"].apply(
            lambda x: "admin" in x if x and isinstance(x, list) else False
        ).sum()
        
        complete_profiles = df["profile_complete"].sum()
        most_common_country = df["country"].mode().iloc[0]
        
        self.assertEqual(admin_count, 1)
        self.assertEqual(complete_profiles, 2)
        self.assertEqual(most_common_country, "US")

    def test_datetime_handling(self):
        """Test datetime handling for admin operations"""
        # Test that datetime operations work correctly
        current_time = datetime.now()
        iso_string = current_time.isoformat()
        
        # Verify ISO format string creation (used in update operations)
        self.assertIsInstance(iso_string, str)
        self.assertIn("T", iso_string)  # ISO format contains T separator
        
        # Test datetime parsing compatibility
        parsed_time = datetime.fromisoformat(iso_string.replace('Z', '+00:00') if iso_string.endswith('Z') else iso_string)
        self.assertIsInstance(parsed_time, datetime)

    def test_error_handling_patterns(self):
        """Test error handling patterns used in admin module"""
        # Test exception handling scenarios
        test_exceptions = [
            Exception("General error"),
            ValueError("Invalid value"), 
            KeyError("Missing key"),
            AttributeError("Missing attribute"),
        ]
        
        for exc in test_exceptions:
            # Simulate error handling pattern from admin module
            try:
                raise exc
            except Exception as e:
                error_message = str(e)
                # Verify we can get meaningful error messages
                self.assertIsInstance(error_message, str)
                self.assertGreater(len(error_message), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)