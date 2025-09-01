#!/usr/bin/env python3
"""
Comprehensive test suite for the admin module.
Tests admin functionality including user management, filtering, editing, and deletion.
"""

import os
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, Mock, call, patch
import pandas as pd
import pytest

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

    @patch("admin.users_tab.st")
    def test_render_users_tab_success(self, mock_st):
        """Test successful rendering of users tab"""
        # Mock database response
        mock_response = Mock()
        mock_response.data = self.sample_users_data
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

        # Mock Streamlit components
        mock_st.columns.return_value = [Mock(), Mock(), Mock(), Mock()]
        mock_st.selectbox.side_effect = ["All", "All", "All", "All"]  # Filter selections
        mock_st.dataframe.return_value = {"selection": {"rows": []}}  # No row selected

        # Call the function
        render_users_tab(self.mock_user, self.mock_supabase)

        # Verify database call
        self.mock_supabase.table.assert_called_with("users")
        self.mock_supabase.table.return_value.select.assert_called_with("*")
        self.mock_supabase.table.return_value.select.return_value.order.assert_called_with("created_at", desc=True)

        # Verify Streamlit calls
        mock_st.header.assert_called()
        mock_st.subheader.assert_called()
        mock_st.metric.assert_called()
        mock_st.dataframe.assert_called()

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

    @patch("admin.users_tab.st")
    @patch("admin.users_tab.pd.DataFrame")
    def test_render_users_tab_metrics_calculation(self, mock_dataframe, mock_st):
        """Test metrics calculation in users tab"""
        # Mock database response
        mock_response = Mock()
        mock_response.data = self.sample_users_data
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

        # Mock DataFrame
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=3)  # Total users
        mock_df.columns = ["profile_complete", "roles", "country"]
        
        # Mock profile_complete column
        mock_profile_complete_series = Mock()
        mock_profile_complete_series.sum.return_value = 2  # 2 complete profiles
        mock_df.__getitem__.side_effect = lambda key: {
            "profile_complete": mock_profile_complete_series,
            "roles": Mock(),
            "country": Mock()
        }[key]

        mock_dataframe.return_value = mock_df
        
        # Mock Streamlit components
        mock_st.columns.return_value = [Mock(), Mock(), Mock(), Mock()]
        mock_st.selectbox.side_effect = ["All", "All", "All", "All"]
        mock_st.dataframe.return_value = {"selection": {"rows": []}}

        # Call the function
        render_users_tab(self.mock_user, self.mock_supabase)

        # Verify metrics were calculated and displayed
        mock_st.metric.assert_called()
        metric_calls = mock_st.metric.call_args_list
        
        # Check that metrics were called with expected values
        metric_labels = [call[0][0] for call in metric_calls]
        self.assertIn("Total Users", metric_labels)
        self.assertIn("Complete Profiles", metric_labels)

    @patch("admin.users_tab.st")
    def test_render_users_tab_with_filters(self, mock_st):
        """Test users tab with various filters applied"""
        # Mock database response
        mock_response = Mock()
        mock_response.data = self.sample_users_data
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

        # Mock Streamlit components
        mock_st.columns.return_value = [Mock(), Mock(), Mock(), Mock()]
        mock_st.selectbox.side_effect = [
            "United States",  # Country filter
            "Imperial",       # Unit system filter
            "Complete",       # Profile status filter
            "Admin"          # Role filter
        ]
        mock_st.dataframe.return_value = {"selection": {"rows": []}}

        # Call the function
        render_users_tab(self.mock_user, self.mock_supabase)

        # Verify filter options were created
        selectbox_calls = mock_st.selectbox.call_args_list
        filter_labels = [call[0][0] for call in selectbox_calls]
        self.assertIn("Country:", filter_labels)
        self.assertIn("Unit System:", filter_labels)
        self.assertIn("Profile Status:", filter_labels)
        self.assertIn("Role:", filter_labels)

    @patch("admin.users_tab.st")
    @patch("admin.users_tab.render_user_edit_form")
    @patch("admin.users_tab.render_user_delete_form")
    def test_render_users_tab_with_user_selection(self, mock_render_delete, mock_render_edit, mock_st):
        """Test users tab when a user is selected"""
        # Mock database response
        mock_response = Mock()
        mock_response.data = self.sample_users_data
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

        # Mock Streamlit components
        mock_st.columns.return_value = [Mock(), Mock(), Mock(), Mock()]
        mock_st.selectbox.side_effect = ["All", "All", "All", "All"]
        mock_st.dataframe.return_value = {"selection": {"rows": [0]}}  # First row selected
        mock_st.tabs.return_value = [Mock(), Mock()]  # Edit and delete tabs

        # Call the function
        render_users_tab(self.mock_user, self.mock_supabase)

        # Verify tabs were created
        mock_st.tabs.assert_called_with(["✏️ Edit User", "🗑️ Delete User"])

        # Verify edit and delete forms were rendered
        mock_render_edit.assert_called_once()
        mock_render_delete.assert_called_once()


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

    @patch("admin.users_tab.st")
    def test_render_user_edit_form_display(self, mock_st):
        """Test user edit form display"""
        # Mock form context
        mock_form_context = Mock()
        mock_st.form.return_value.__enter__ = Mock(return_value=mock_form_context)
        mock_st.form.return_value.__exit__ = Mock(return_value=None)
        
        # Mock form inputs
        mock_st.text_input.side_effect = [
            "Test User",      # name
            "testuser",       # username
            "test@example.com", # email (disabled)
            "United States",  # country
            "California",     # state
            "https://example.com/pic.jpg"  # picture
        ]
        mock_st.selectbox.return_value = "Imperial"
        mock_st.checkbox.side_effect = [True, True, False]  # profile_complete, user_role, admin_role
        mock_st.form_submit_button.return_value = False
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]

        # Call the function
        render_user_edit_form(self.sample_user, self.mock_supabase)

        # Verify form was created
        mock_st.form.assert_called()
        
        # Verify form inputs were created
        self.assertGreater(mock_st.text_input.call_count, 0)
        mock_st.selectbox.assert_called()
        self.assertGreater(mock_st.checkbox.call_count, 0)
        mock_st.form_submit_button.assert_called()

    @patch("admin.users_tab.st")
    @patch("admin.users_tab.datetime")
    def test_render_user_edit_form_submission_success(self, mock_datetime, mock_st):
        """Test successful user edit form submission"""
        # Mock current time
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
        
        # Mock form context
        mock_form_context = Mock()
        mock_st.form.return_value.__enter__ = Mock(return_value=mock_form_context)
        mock_st.form.return_value.__exit__ = Mock(return_value=None)
        
        # Mock form inputs
        mock_st.text_input.side_effect = [
            "Updated User",    # name
            "updateduser",     # username
            "test@example.com", # email (disabled)
            "Canada",          # country
            "Ontario",         # state
            "https://example.com/new-pic.jpg"  # picture
        ]
        mock_st.selectbox.return_value = "Metric"
        mock_st.checkbox.side_effect = [False, True, True]  # profile_complete, user_role, admin_role
        mock_st.form_submit_button.return_value = True  # Form submitted
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]

        # Mock successful database update
        mock_response = Mock()
        mock_response.data = [{"id": "user-123"}]
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response

        # Call the function
        render_user_edit_form(self.sample_user, self.mock_supabase)

        # Verify database update was called
        self.mock_supabase.table.assert_called_with("users")
        update_call = self.mock_supabase.table.return_value.update.call_args[0][0]
        
        # Verify update data
        self.assertEqual(update_call["name"], "Updated User")
        self.assertEqual(update_call["username"], "updateduser")
        self.assertEqual(update_call["country"], "Canada")
        self.assertEqual(update_call["unit_system"], "Metric")
        self.assertEqual(update_call["profile_complete"], False)
        self.assertEqual(update_call["roles"], ["user", "admin"])

        # Verify success message and rerun
        mock_st.success.assert_called_with("✅ User updated successfully!")
        mock_st.rerun.assert_called()

    @patch("admin.users_tab.st")
    def test_render_user_edit_form_submission_failure(self, mock_st):
        """Test user edit form submission failure"""
        # Mock form context
        mock_form_context = Mock()
        mock_st.form.return_value.__enter__ = Mock(return_value=mock_form_context)
        mock_st.form.return_value.__exit__ = Mock(return_value=None)
        
        # Mock form inputs
        mock_st.text_input.side_effect = ["Test User", "testuser", "test@example.com", "United States", "California", ""]
        mock_st.selectbox.return_value = "Imperial"
        mock_st.checkbox.side_effect = [True, True, False]
        mock_st.form_submit_button.return_value = True
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]

        # Mock failed database update
        mock_response = Mock()
        mock_response.data = []  # Empty data indicates failure
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response

        # Call the function
        render_user_edit_form(self.sample_user, self.mock_supabase)

        # Verify error message
        mock_st.error.assert_called_with("❌ Failed to update user.")

    @patch("admin.users_tab.st")
    def test_render_user_edit_form_database_error(self, mock_st):
        """Test user edit form with database error"""
        # Mock form context
        mock_form_context = Mock()
        mock_st.form.return_value.__enter__ = Mock(return_value=mock_form_context)
        mock_st.form.return_value.__exit__ = Mock(return_value=None)
        
        # Mock form inputs
        mock_st.text_input.side_effect = ["Test User", "testuser", "test@example.com", "United States", "California", ""]
        mock_st.selectbox.return_value = "Imperial"
        mock_st.checkbox.side_effect = [True, True, False]
        mock_st.form_submit_button.return_value = True
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]

        # Mock database error
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception("Database error")

        # Call the function
        render_user_edit_form(self.sample_user, self.mock_supabase)

        # Verify error message
        mock_st.error.assert_called()
        error_message = mock_st.error.call_args[0][0]
        self.assertIn("Error updating user", error_message)

    @patch("admin.users_tab.st")
    def test_render_user_edit_form_role_validation(self, mock_st):
        """Test user edit form role validation"""
        # Mock form context
        mock_form_context = Mock()
        mock_st.form.return_value.__enter__ = Mock(return_value=mock_form_context)
        mock_st.form.return_value.__exit__ = Mock(return_value=None)
        
        # Mock form inputs - no roles selected
        mock_st.text_input.side_effect = ["Test User", "testuser", "test@example.com", "United States", "California", ""]
        mock_st.selectbox.return_value = "Imperial"
        mock_st.checkbox.side_effect = [True, False, False]  # Neither user nor admin role
        mock_st.form_submit_button.return_value = False  # Not submitted
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]

        # Call the function
        render_user_edit_form(self.sample_user, self.mock_supabase)

        # Verify warning about requiring at least user role
        mock_st.warning.assert_called_with("⚠️ Users must have at least the 'user' role.")

    @patch("admin.users_tab.st")
    def test_render_user_edit_form_image_display(self, mock_st):
        """Test user edit form image display"""
        # Mock form context
        mock_form_context = Mock()
        mock_st.form.return_value.__enter__ = Mock(return_value=mock_form_context)
        mock_st.form.return_value.__exit__ = Mock(return_value=None)
        
        # Mock form inputs
        mock_st.text_input.side_effect = ["Test User", "testuser", "test@example.com", "United States", "California", "https://example.com/pic.jpg"]
        mock_st.selectbox.return_value = "Imperial"
        mock_st.checkbox.side_effect = [True, True, False]
        mock_st.form_submit_button.return_value = False
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]

        # Call the function
        render_user_edit_form(self.sample_user, self.mock_supabase)

        # Verify image was displayed
        mock_st.image.assert_called()
        image_call_args = mock_st.image.call_args
        self.assertEqual(image_call_args[0][0], "https://example.com/pic.jpg")
        self.assertEqual(image_call_args[1]["width"], 100)


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
            "country": "United States",
            "state": "California",
            "unit_system": "Imperial",
            "profile_complete": True,
            "roles": ["user"],
            "created_at": "2024-01-01T00:00:00Z",
        }
        
        self.admin_user = {
            "id": "admin-123",
            "email": "admin@example.com",
            "name": "Admin User",
            "username": "adminuser",
            "roles": ["admin", "user"],
        }

    @patch("admin.users_tab.st")
    def test_render_user_delete_form_display(self, mock_st):
        """Test user delete form display"""
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]
        mock_st.text_input.return_value = ""  # No confirmation entered
        mock_st.button.return_value = False

        # Mock related data check
        mock_count_responses = []
        for _ in range(9):  # Number of tables checked
            mock_response = Mock()
            mock_response.count = 0
            mock_count_responses.append(mock_response)
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = mock_count_responses

        # Call the function
        render_user_delete_form(self.sample_user, self.mock_supabase)

        # Verify user information is displayed
        mock_st.write.assert_called()
        write_calls = mock_st.write.call_args_list
        write_texts = [call[0][0] for call in write_calls]
        
        # Check that user details are shown
        self.assertTrue(any("Test User" in text for text in write_texts))
        self.assertTrue(any("test@example.com" in text for text in write_texts))

        # Verify warning messages
        mock_st.error.assert_called()
        mock_st.warning.assert_called()

    @patch("admin.users_tab.st")
    def test_render_user_delete_form_admin_warning(self, mock_st):
        """Test delete form shows warning for admin users"""
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]
        mock_st.text_input.return_value = ""
        mock_st.button.return_value = False

        # Mock related data check (no related data)
        mock_count_responses = []
        for _ in range(9):
            mock_response = Mock()
            mock_response.count = 0
            mock_count_responses.append(mock_response)
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = mock_count_responses

        # Call the function with admin user
        render_user_delete_form(self.admin_user, self.mock_supabase)

        # Verify admin warning is shown
        error_calls = mock_st.error.call_args_list
        error_messages = [call[0][0] for call in error_calls]
        self.assertTrue(any("admin privileges" in msg for msg in error_messages))

    @patch("admin.users_tab.st")
    def test_render_user_delete_form_related_data_check(self, mock_st):
        """Test delete form checks for related data"""
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]
        mock_st.text_input.return_value = ""
        mock_st.button.return_value = False

        # Mock related data responses - some tables have data
        mock_count_responses = []
        for i in range(9):
            mock_response = Mock()
            if i < 2:  # First two tables have data
                mock_response.count = 5
            else:
                mock_response.count = 0
            mock_count_responses.append(mock_response)
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = mock_count_responses

        # Call the function
        render_user_delete_form(self.sample_user, self.mock_supabase)

        # Verify related data warning is shown
        warning_calls = mock_st.warning.call_args_list
        warning_messages = [call[0][0] for call in warning_calls]
        self.assertTrue(any("associated data" in msg for msg in warning_messages))

    @patch("admin.users_tab.st")
    def test_render_user_delete_form_confirmation_mismatch(self, mock_st):
        """Test delete form with incorrect email confirmation"""
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]
        mock_st.text_input.return_value = "wrong@example.com"  # Wrong confirmation
        mock_st.button.return_value = False

        # Mock related data check (no related data)
        mock_count_responses = []
        for _ in range(9):
            mock_response = Mock()
            mock_response.count = 0
            mock_count_responses.append(mock_response)
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = mock_count_responses

        # Call the function
        render_user_delete_form(self.sample_user, self.mock_supabase)

        # Verify error message for mismatch
        error_calls = mock_st.error.call_args_list
        error_messages = [call[0][0] for call in error_calls]
        self.assertTrue(any("Email confirmation does not match" in msg for msg in error_messages))

        # Verify delete button is disabled
        button_call = mock_st.button.call_args
        self.assertTrue(button_call[1]["disabled"])

    @patch("admin.users_tab.st")
    def test_render_user_delete_form_successful_deletion(self, mock_st):
        """Test successful user deletion"""
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]
        mock_st.text_input.return_value = "test@example.com"  # Correct confirmation
        mock_st.button.return_value = True  # Delete button clicked

        # Mock successful deletion
        mock_delete_response = Mock()
        mock_delete_response.data = [{"id": "user-123"}]
        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_delete_response

        # Mock related data check (no related data)
        mock_count_responses = []
        for _ in range(9):
            mock_response = Mock()
            mock_response.count = 0
            mock_count_responses.append(mock_response)
        
        # Configure side effects - first 9 calls are for related data check, last is for deletion
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = mock_count_responses
        
        # Call the function
        render_user_delete_form(self.sample_user, self.mock_supabase)

        # Verify delete operation
        self.mock_supabase.table.assert_called_with("users")
        self.mock_supabase.table.return_value.delete.assert_called()
        self.mock_supabase.table.return_value.delete.return_value.eq.assert_called_with("id", "user-123")

        # Verify success message and rerun
        mock_st.success.assert_called()
        success_message = mock_st.success.call_args[0][0]
        self.assertIn("permanently deleted", success_message)
        mock_st.rerun.assert_called()

    @patch("admin.users_tab.st")
    def test_render_user_delete_form_deletion_failure(self, mock_st):
        """Test user deletion failure"""
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]
        mock_st.text_input.return_value = "test@example.com"
        mock_st.button.return_value = True

        # Mock failed deletion (empty data)
        mock_delete_response = Mock()
        mock_delete_response.data = []
        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_delete_response

        # Mock related data check (no related data)
        mock_count_responses = []
        for _ in range(9):
            mock_response = Mock()
            mock_response.count = 0
            mock_count_responses.append(mock_response)
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = mock_count_responses

        # Call the function
        render_user_delete_form(self.sample_user, self.mock_supabase)

        # Verify error message
        mock_st.error.assert_called()
        error_calls = mock_st.error.call_args_list
        error_messages = [call[0][0] for call in error_calls]
        self.assertTrue(any("Failed to delete user" in msg for msg in error_messages))

    @patch("admin.users_tab.st")
    def test_render_user_delete_form_foreign_key_error(self, mock_st):
        """Test user deletion with foreign key constraint error"""
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]
        mock_st.text_input.return_value = "test@example.com"
        mock_st.button.return_value = True

        # Mock foreign key constraint error
        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.side_effect = Exception(
            "foreign key constraint violation"
        )

        # Mock related data check (no related data)
        mock_count_responses = []
        for _ in range(9):
            mock_response = Mock()
            mock_response.count = 0
            mock_count_responses.append(mock_response)
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = mock_count_responses

        # Call the function
        render_user_delete_form(self.sample_user, self.mock_supabase)

        # Verify specific foreign key error message
        error_calls = mock_st.error.call_args_list
        error_messages = [call[0][0] for call in error_calls]
        self.assertTrue(any("Cannot delete user" in msg for msg in error_messages))
        self.assertTrue(any("associated data" in msg for msg in error_messages))

    @patch("admin.users_tab.st")
    def test_render_user_delete_form_related_data_error(self, mock_st):
        """Test delete form when related data check fails"""
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]
        mock_st.text_input.return_value = ""
        mock_st.button.return_value = False

        # Mock error when checking related data
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception(
            "Table not found"
        )

        # Call the function
        render_user_delete_form(self.sample_user, self.mock_supabase)

        # Verify warning about unable to check related data
        warning_calls = mock_st.warning.call_args_list
        warning_messages = [call[0][0] for call in warning_calls]
        self.assertTrue(any("Unable to check for related data" in msg for msg in warning_messages))


class TestAdminModuleIntegration(unittest.TestCase):
    """Test admin module integration functionality"""

    def test_admin_module_imports(self):
        """Test that admin module components can be imported"""
        # Test that functions can be imported successfully
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


if __name__ == "__main__":
    unittest.main(verbosity=2)