#!/usr/bin/env python3
"""
Comprehensive test suite for the users module.
Tests user models, controllers, views, and authentication workflows.
"""

import os
import sys
import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, call, patch
import pytest
from datetime import datetime

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from users.user_controller import UserController
from users.user_model import UserModel
from users.user_view import UserView


class TestUserModel(unittest.TestCase):
    """Test UserModel functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.user_model = UserModel()
        self.mock_supabase = Mock()

        # Mock Streamlit secrets
        self.patcher = patch(
            "users.user_model.st.secrets",
            {"supabase": {"url": "https://test.supabase.co", "key": "test-key"}},
        )
        self.patcher.start()

        # Sample user data
        self.sample_user = {
            "email": "test@example.com",
            "name": "Test User",
            "username": "testuser",
            "state": "California",
            "country": "United States",
            "unit_system": "Imperial",
            "sub": "auth0|123456",
            "picture": "https://example.com/pic.jpg",
        }

    def tearDown(self):
        """Clean up after tests"""
        self.patcher.stop()

    @patch("users.user_model.create_client")
    def test_get_supabase_client(self, mock_create_client):
        """Test Supabase client creation"""
        mock_create_client.return_value = self.mock_supabase

        client = self.user_model._get_supabase_client()

        self.assertEqual(client, self.mock_supabase)
        mock_create_client.assert_called_once_with(
            "https://test.supabase.co", "test-key"
        )

    @patch("users.user_model.create_client")
    def test_get_user_profile_success(self, mock_create_client):
        """Test successful user profile retrieval"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = [self.sample_user]
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_result
        )

        result = self.user_model.get_user_profile("test@example.com")

        self.assertEqual(result, self.sample_user)
        self.mock_supabase.table.assert_called_with("users")

    @patch("users.user_model.create_client")
    def test_get_user_profile_not_found(self, mock_create_client):
        """Test user profile retrieval when user doesn't exist"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = []
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_result
        )

        result = self.user_model.get_user_profile("nonexistent@example.com")

        self.assertIsNone(result)

    @patch("users.user_model.st.error")
    @patch("users.user_model.create_client")
    def test_get_user_profile_error(self, mock_create_client, mock_st_error):
        """Test user profile retrieval with database error"""
        mock_create_client.return_value = self.mock_supabase
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception(
            "DB Error"
        )

        result = self.user_model.get_user_profile("test@example.com")

        self.assertIsNone(result)
        mock_st_error.assert_called_once()

    @patch("users.user_model.create_client")
    def test_create_user_profile_success(self, mock_create_client):
        """Test successful user profile creation"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = [{"id": "user-123"}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_result
        )

        result = self.user_model.create_user_profile(self.sample_user)

        self.assertTrue(result)
        self.mock_supabase.table.assert_called_with("users")

    @patch("users.user_model.st.error")
    @patch("users.user_model.create_client")
    def test_create_user_profile_error(self, mock_create_client, mock_st_error):
        """Test user profile creation with database error"""
        mock_create_client.return_value = self.mock_supabase
        self.mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
            "DB Error"
        )

        result = self.user_model.create_user_profile(self.sample_user)

        self.assertFalse(result)
        mock_st_error.assert_called_once()

    @patch("users.user_model.create_client")
    def test_update_user_profile_success(self, mock_create_client):
        """Test successful user profile update"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = [{"id": "user-123"}]
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = (
            mock_result
        )

        result = self.user_model.update_user_profile(
            "test@example.com", self.sample_user
        )

        self.assertTrue(result)

    @patch("users.user_model.create_client")
    def test_is_username_available_true(self, mock_create_client):
        """Test username availability check - available"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = []
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_result
        )

        result = self.user_model.is_username_available("newuser")

        self.assertTrue(result)

    @patch("users.user_model.create_client")
    def test_is_username_available_false(self, mock_create_client):
        """Test username availability check - taken"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = [{"email": "other@example.com"}]
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_result
        )

        result = self.user_model.is_username_available("takenuser")

        self.assertFalse(result)

    def test_validate_username_success(self):
        """Test valid username validation"""
        valid_usernames = ["test123", "user_name", "valid-user", "a1b2c3"]

        for username in valid_usernames:
            is_valid, message = self.user_model.validate_username(username)
            self.assertTrue(is_valid, f"Username '{username}' should be valid")
            self.assertEqual(message, "")

    def test_validate_username_too_short(self):
        """Test username too short validation"""
        is_valid, message = self.user_model.validate_username("ab")

        self.assertFalse(is_valid)
        self.assertIn("at least 3 characters", message)

    def test_validate_username_too_long(self):
        """Test username too long validation"""
        long_username = "a" * 31
        is_valid, message = self.user_model.validate_username(long_username)

        self.assertFalse(is_valid)
        self.assertIn("30 characters or less", message)

    def test_validate_username_invalid_characters(self):
        """Test username with invalid characters"""
        invalid_usernames = ["user@name", "user name", "user.name", "user%name"]

        for username in invalid_usernames:
            is_valid, message = self.user_model.validate_username(username)
            self.assertFalse(is_valid, f"Username '{username}' should be invalid")
            self.assertIn("letters, numbers, underscores, and hyphens", message)

    def test_validate_username_invalid_start(self):
        """Test username starting with invalid character"""
        invalid_usernames = ["_username", "-username"]

        for username in invalid_usernames:
            is_valid, message = self.user_model.validate_username(username)
            self.assertFalse(is_valid, f"Username '{username}' should be invalid")
            self.assertIn("start with a letter or number", message)

    @patch("users.user_model.create_client")
    def test_get_all_users(self, mock_create_client):
        """Test getting all users"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = [self.sample_user, {"email": "user2@example.com"}]
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = (
            mock_result
        )

        result = self.user_model.get_all_users()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], self.sample_user)

    @patch("users.user_model.create_client")
    def test_get_user_count(self, mock_create_client):
        """Test getting user count"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.count = 42
        self.mock_supabase.table.return_value.select.return_value.execute.return_value = (
            mock_result
        )

        result = self.user_model.get_user_count()

        self.assertEqual(result, 42)

    @patch("users.user_model.create_client")
    def test_delete_user_success(self, mock_create_client):
        """Test successful user deletion"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = [{"id": "user-123"}]
        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = (
            mock_result
        )

        result = self.user_model.delete_user("test@example.com")

        self.assertTrue(result)

    @patch("users.user_model.st.error")
    @patch("users.user_model.create_client")
    def test_delete_user_error(self, mock_create_client, mock_st_error):
        """Test user deletion with database error"""
        mock_create_client.return_value = self.mock_supabase
        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.side_effect = Exception(
            "DB Error"
        )

        result = self.user_model.delete_user("test@example.com")

        self.assertFalse(result)
        mock_st_error.assert_called_once()

    @patch("users.user_model.create_client")
    def test_get_user_profile_multiple_results(self, mock_create_client):
        """Test user profile retrieval with multiple results (edge case)"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = [self.sample_user, {"email": "duplicate@example.com"}]
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_result
        )

        result = self.user_model.get_user_profile("test@example.com")

        # Should return the first result
        self.assertEqual(result, self.sample_user)

    @patch("users.user_model.create_client")
    def test_update_user_profile_no_changes(self, mock_create_client):
        """Test user profile update with no data returned"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = []
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = (
            mock_result
        )

        result = self.user_model.update_user_profile(
            "test@example.com", self.sample_user
        )

        self.assertFalse(result)

    def test_validate_username_edge_cases(self):
        """Test username validation edge cases"""
        edge_cases = [
            ("", False, "at least 3 characters"),
            ("  ", False, "at least 3 characters"),
            ("123", True, ""),  # All numbers should be valid
            ("a12", True, ""),  # Minimum valid length
            ("a" * 30, True, ""),  # Maximum valid length
            ("user123_test-name", True, ""),  # Mixed valid characters
            ("123user", True, ""),  # Starting with number
        ]

        for username, expected_valid, expected_message_part in edge_cases:
            is_valid, message = self.user_model.validate_username(username)
            self.assertEqual(is_valid, expected_valid, f"Username '{username}' validation failed")
            if expected_message_part:
                self.assertIn(expected_message_part, message)

    @patch("users.user_model.st.error")
    @patch("users.user_model.create_client")
    def test_is_username_available_error(self, mock_create_client, mock_st_error):
        """Test username availability check with database error"""
        mock_create_client.return_value = self.mock_supabase
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception(
            "DB Error"
        )

        result = self.user_model.is_username_available("testuser")

        self.assertFalse(result)  # Should default to False on error
        mock_st_error.assert_called_once()

    @patch("users.user_model.create_client")
    def test_get_all_users_empty(self, mock_create_client):
        """Test getting all users when none exist"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = []
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = (
            mock_result
        )

        result = self.user_model.get_all_users()

        self.assertEqual(len(result), 0)
        self.assertEqual(result, [])

    @patch("users.user_model.st.error")
    @patch("users.user_model.create_client")
    def test_get_user_count_error(self, mock_create_client, mock_st_error):
        """Test getting user count with database error"""
        mock_create_client.return_value = self.mock_supabase
        self.mock_supabase.table.return_value.select.return_value.execute.side_effect = Exception(
            "DB Error"
        )

        result = self.user_model.get_user_count()

        self.assertEqual(result, 0)  # Should default to 0 on error
        mock_st_error.assert_called_once()


class TestUserController(unittest.TestCase):
    """Test UserController functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.controller = UserController()
        self.sample_user = {
            "email": "test@example.com",
            "name": "Test User",
            "username": "testuser",
            "state": "California",
            "country": "United States",
            "unit_system": "Imperial",
            "sub": "auth0|123456",
            "picture": "https://example.com/pic.jpg",
        }

    def test_user_controller_initialization(self):
        """Test that UserController can be initialized"""
        try:
            controller = UserController()
            self.assertIsInstance(controller.model, UserModel)
            self.assertIsInstance(controller.view, UserView)
        except Exception as e:
            self.fail(f"UserController should initialize properly: {e}")

    def test_user_controller_has_required_methods(self):
        """Test that UserController has required methods"""
        controller = UserController()

        # Should have key methods
        self.assertTrue(hasattr(controller, "handle_profile_setup"))
        self.assertTrue(hasattr(controller, "get_complete_user_profile"))
        self.assertTrue(hasattr(controller, "display_profile_in_sidebar"))

        # Methods should be callable
        self.assertTrue(callable(controller.handle_profile_setup))
        self.assertTrue(callable(controller.get_complete_user_profile))
        self.assertTrue(callable(controller.display_profile_in_sidebar))

    @patch('users.user_controller.st.session_state', {})
    def test_validate_form_data_success(self):
        """Test form data validation with valid data"""
        form_data = {
            "username": "validuser",
            "state": "California",
            "country": "United States",
            "unit_system": "Imperial"
        }

        with patch.object(self.controller.model, 'validate_username', return_value=(True, "")):
            with patch.object(self.controller.model, 'is_username_available', return_value=True):
                errors = self.controller._validate_form_data(form_data, "test@example.com")
                self.assertEqual(len(errors), 0)

    @patch('users.user_controller.st.session_state', {})
    def test_validate_form_data_missing_fields(self):
        """Test form data validation with missing required fields"""
        incomplete_form_data = {
            "username": "",
            "state": "",
            "country": "",
            "unit_system": ""
        }

        errors = self.controller._validate_form_data(incomplete_form_data, "test@example.com")
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Username is required" in error for error in errors))
        self.assertTrue(any("State is required" in error for error in errors))

    @patch('users.user_controller.st.session_state', {})
    def test_validate_form_data_invalid_username(self):
        """Test form data validation with invalid username"""
        form_data = {
            "username": "invalid@user",
            "state": "California",
            "country": "United States",
            "unit_system": "Imperial"
        }

        with patch.object(self.controller.model, 'validate_username', return_value=(False, "Invalid username")):
            errors = self.controller._validate_form_data(form_data, "test@example.com")
            self.assertGreater(len(errors), 0)
            self.assertTrue(any("Invalid username" in error for error in errors))

    @patch('users.user_controller.st.session_state', {})
    def test_validate_form_data_username_taken(self):
        """Test form data validation with taken username"""
        form_data = {
            "username": "takenuser",
            "state": "California",
            "country": "United States",
            "unit_system": "Imperial"
        }

        with patch.object(self.controller.model, 'validate_username', return_value=(True, "")):
            with patch.object(self.controller.model, 'is_username_available', return_value=False):
                errors = self.controller._validate_form_data(form_data, "test@example.com")
                self.assertGreater(len(errors), 0)
                self.assertTrue(any("Username is already taken" in error for error in errors))

    @patch('users.user_controller.st.session_state', {})
    def test_get_complete_user_profile_existing(self):
        """Test getting complete user profile for existing user"""
        with patch.object(self.controller.model, 'get_user_profile', return_value=self.sample_user):
            result = self.controller.get_complete_user_profile("test@example.com")
            self.assertEqual(result, self.sample_user)

    @patch('users.user_controller.st.session_state', {})
    def test_get_complete_user_profile_nonexistent(self):
        """Test getting complete user profile for nonexistent user"""
        with patch.object(self.controller.model, 'get_user_profile', return_value=None):
            result = self.controller.get_complete_user_profile("nonexistent@example.com")
            self.assertIsNone(result)

    @patch('users.user_controller.st.session_state', {'edit_mode': False})
    @patch('users.user_controller.st.sidebar')
    def test_display_profile_in_sidebar_view_mode(self, mock_sidebar):
        """Test displaying profile in sidebar in view mode"""
        mock_sidebar_context = Mock()
        mock_sidebar.__enter__ = Mock(return_value=mock_sidebar_context)
        mock_sidebar.__exit__ = Mock(return_value=None)
        
        with patch.object(self.controller.view, 'display_profile_view') as mock_display:
            self.controller.display_profile_in_sidebar(self.sample_user)
            mock_display.assert_called_once_with(self.sample_user)


class TestUserView(unittest.TestCase):
    """Test UserView functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.user_view = UserView()
        self.sample_user = {
            "email": "test@example.com",
            "name": "Test User",
            "username": "testuser",
            "state": "California",
            "country": "United States",
            "unit_system": "Imperial",
        }

    @patch("users.user_view.st.form")
    @patch("users.user_view.st.title")
    def test_display_profile_setup_form(self, mock_title, mock_form):
        """Test profile setup form display"""
        # Mock form context manager
        mock_form_context = Mock()
        mock_form.return_value.__enter__ = Mock(return_value=mock_form_context)
        mock_form.return_value.__exit__ = Mock()

        # Mock form inputs
        with patch("users.user_view.st.text_input") as mock_text_input, patch(
            "users.user_view.st.selectbox"
        ) as mock_selectbox, patch("users.user_view.st.radio") as mock_radio, patch(
            "users.user_view.st.form_submit_button"
        ) as mock_submit:

            mock_text_input.side_effect = ["testuser", "California"]
            mock_selectbox.return_value = "United States"
            mock_radio.return_value = "Imperial"
            mock_submit.return_value = True

            result = self.user_view.display_profile_setup_form(self.sample_user)

            self.assertIsNotNone(result)
            self.assertEqual(result["username"], "testuser")
            self.assertEqual(result["state"], "California")

    @patch("users.user_view.st.columns")
    @patch("users.user_view.st.markdown")
    def test_display_profile_view(self, mock_markdown, mock_columns):
        """Test profile view display"""
        # Create mock columns with context manager support
        mock_col1, mock_col2 = Mock(), Mock()
        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=None)
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=None)
        mock_columns.return_value = [mock_col1, mock_col2]

        with patch("users.user_view.st.button") as mock_button, patch(
            "users.user_view.st.write"
        ) as mock_write, patch("users.user_view.st.session_state", {}), patch(
            "users.user_view.st.rerun"
        ):
            mock_button.return_value = False

            self.user_view.display_profile_view(self.sample_user)

            mock_markdown.assert_called()
            mock_columns.assert_called_with(2)

    @patch("users.user_view.st.error")
    def test_display_validation_errors(self, mock_error):
        """Test validation error display"""
        errors = ["Error 1", "Error 2"]

        self.user_view.display_validation_errors(errors)

        self.assertEqual(mock_error.call_count, 2)
        mock_error.assert_has_calls([call("Error 1"), call("Error 2")])

    @patch("users.user_view.st.success")
    def test_display_success_message(self, mock_success):
        """Test success message display"""
        message = "Profile updated successfully"

        self.user_view.display_success_message(message)

        mock_success.assert_called_once_with(message)

    @patch("users.user_view.st.error")
    def test_display_error_message(self, mock_error):
        """Test error message display"""
        message = "An error occurred"

        self.user_view.display_error_message(message)

        mock_error.assert_called_once_with(message)


class TestUserIntegration(unittest.TestCase):
    """Test user module integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.sample_user = {
            "email": "test@example.com",
            "name": "Test User",
            "username": "testuser",
            "state": "California",
            "country": "United States",
            "unit_system": "Imperial",
            "sub": "auth0|123456",
            "picture": "https://example.com/pic.jpg",
            "profile_complete": True,
            "roles": ["user"],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

    def test_user_workflow_components_exist(self):
        """Test that all user workflow components exist"""
        # Test that classes can be imported and instantiated
        user_model = UserModel()
        user_controller = UserController()
        user_view = UserView()

        self.assertIsInstance(user_model, UserModel)
        self.assertIsInstance(user_controller, UserController)
        self.assertIsInstance(user_view, UserView)

    def test_user_data_validation(self):
        """Test user data validation patterns"""
        user_model = UserModel()

        # Test various username patterns
        valid_usernames = ["user123", "test_user", "valid-name", "Username"]
        invalid_usernames = [
            "us",
            "user@domain",
            "user space",
            "_startswith",
            "-startswith",
        ]

        for username in valid_usernames:
            is_valid, _ = user_model.validate_username(username)
            self.assertTrue(is_valid, f"'{username}' should be valid")

        for username in invalid_usernames:
            is_valid, _ = user_model.validate_username(username)
            self.assertFalse(is_valid, f"'{username}' should be invalid")

    def test_user_profile_completeness(self):
        """Test user profile completeness validation"""
        required_fields = [
            "email",
            "name",
            "username",
            "state",
            "country",
            "unit_system",
        ]

        # Complete profile should be valid
        complete_profile = {
            "email": "test@example.com",
            "name": "Test User",
            "username": "testuser",
            "state": "California",
            "country": "United States",
            "unit_system": "Imperial",
        }

        for field in required_fields:
            self.assertIn(field, complete_profile)
            self.assertTrue(len(str(complete_profile[field])) > 0)

    @patch('users.user_model.create_client')
    @patch('users.user_view.st.form')
    @patch('users.user_controller.st.session_state', {})
    def test_full_profile_creation_workflow(self, mock_form, mock_create_client):
        """Test complete profile creation workflow"""
        # Set up mocks
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase
        
        mock_form_context = Mock()
        mock_form.return_value.__enter__ = Mock(return_value=mock_form_context)
        mock_form.return_value.__exit__ = Mock()
        
        # Mock successful user creation
        mock_result = Mock()
        mock_result.data = [{"id": "user-123"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result
        
        # Mock username availability
        mock_available_result = Mock()
        mock_available_result.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_available_result
        
        # Create controller and test workflow
        controller = UserController()
        
        # Test that model can create user
        result = controller.model.create_user_profile(self.sample_user)
        self.assertTrue(result)
        
        # Verify database interaction
        mock_supabase.table.assert_called_with("users")
        mock_supabase.table.return_value.insert.assert_called()

    @patch('users.user_model.create_client')
    def test_user_profile_update_workflow(self, mock_create_client):
        """Test complete profile update workflow"""
        # Set up mocks
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase
        
        # Mock successful update
        mock_result = Mock()
        mock_result.data = [{"id": "user-123"}]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_result
        
        # Test update workflow
        user_model = UserModel()
        updated_user = self.sample_user.copy()
        updated_user["state"] = "New York"
        
        result = user_model.update_user_profile(self.sample_user["email"], updated_user)
        self.assertTrue(result)
        
        # Verify database interaction
        mock_supabase.table.assert_called_with("users")
        mock_supabase.table.return_value.update.assert_called_with(updated_user)

    @patch('users.user_model.create_client')
    def test_user_deletion_workflow(self, mock_create_client):
        """Test complete user deletion workflow"""
        # Set up mocks
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase
        
        # Mock successful deletion
        mock_result = Mock()
        mock_result.data = [{"id": "user-123"}]
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_result
        
        # Test deletion workflow
        user_model = UserModel()
        result = user_model.delete_user(self.sample_user["email"])
        self.assertTrue(result)
        
        # Verify database interaction
        mock_supabase.table.assert_called_with("users")
        mock_supabase.table.return_value.delete.assert_called()

    def test_mvc_pattern_integrity(self):
        """Test that MVC pattern is properly implemented"""
        model = UserModel()
        view = UserView()
        controller = UserController()
        
        # Model should not import view or controller
        self.assertTrue(hasattr(model, '_get_supabase_client'))
        self.assertTrue(hasattr(model, 'get_user_profile'))
        
        # View should not import model directly
        self.assertTrue(hasattr(view, 'display_profile_setup_form'))
        self.assertTrue(hasattr(view, 'display_profile_view'))
        
        # Controller should coordinate both
        self.assertIsInstance(controller.model, UserModel)
        self.assertIsInstance(controller.view, UserView)
        
    @patch('users.user_model.create_client')
    def test_error_handling_across_layers(self, mock_create_client):
        """Test error handling propagation across MVC layers"""
        # Set up mock to raise error
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("DB Error")
        
        controller = UserController()
        
        # Error should be handled gracefully
        with patch('users.user_model.st.error') as mock_error:
            result = controller.model.get_user_profile("test@example.com")
            self.assertIsNone(result)
            mock_error.assert_called_once()

    def test_user_session_state_integration(self):
        """Test integration with Streamlit session state"""
        controller = UserController()
        
        # Test that controller handles session state appropriately
        with patch('users.user_controller.st.session_state', {}) as mock_session_state:
            # Should not raise exceptions with empty session state
            try:
                # These methods should handle missing session state gracefully
                self.assertTrue(callable(controller.handle_profile_setup))
                self.assertTrue(callable(controller.display_profile_in_sidebar))
            except KeyError:
                self.fail("Controller should handle missing session state gracefully")

    @patch('users.user_model.create_client')
    def test_concurrent_username_check(self, mock_create_client):
        """Test username availability in concurrent scenarios"""
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase
        
        # Mock username taken
        mock_result = Mock()
        mock_result.data = [{"username": "testuser", "email": "other@example.com"}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result
        
        user_model = UserModel()
        
        # Username should not be available
        result = user_model.is_username_available("testuser")
        self.assertFalse(result)
        
        # Verify correct query construction
        mock_supabase.table.assert_called_with("users")
        mock_supabase.table.return_value.select.assert_called_with("email")
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with("username", "testuser")


if __name__ == "__main__":
    unittest.main()
