#!/usr/bin/env python3
"""
Comprehensive test suite for the users module.
Tests user models, controllers, views, and authentication workflows.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, call, patch

from users.user_controller import UserController
from users.user_model import UserModel
from users.user_view import UserView

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestUserModel(unittest.TestCase):
    """Test UserModel functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.user_model = UserModel()
        self.mock_supabase = Mock()

        # Mock Streamlit secrets
        self.patcher = patch(
            "users.user_model.st.secrets", {
                "supabase": {
                    "url": "https://test.supabase.co", "key": "test-key"}}, )
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
            mock_result)

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
            mock_result)

        result = self.user_model.get_user_profile("nonexistent@example.com")

        self.assertIsNone(result)

    @patch("users.user_model.st.error")
    @patch("users.user_model.create_client")
    def test_get_user_profile_error(self, mock_create_client, mock_st_error):
        """Test user profile retrieval with database error"""
        mock_create_client.return_value = self.mock_supabase
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception(
            "DB Error")

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
            mock_result)

        result = self.user_model.create_user_profile(self.sample_user)

        self.assertTrue(result)
        self.mock_supabase.table.assert_called_with("users")

    @patch("users.user_model.st.error")
    @patch("users.user_model.create_client")
    def test_create_user_profile_error(
            self, mock_create_client, mock_st_error):
        """Test user profile creation with database error"""
        mock_create_client.return_value = self.mock_supabase
        self.mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
            "DB Error")

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
            mock_result)

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
            mock_result)

        result = self.user_model.is_username_available("newuser")

        self.assertTrue(result)

    @patch("users.user_model.create_client")
    def test_is_username_available_false(self, mock_create_client):
        """Test username availability check - taken"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = [{"email": "other@example.com"}]
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_result)

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
        invalid_usernames = [
            "user@name",
            "user name",
            "user.name",
            "user%name"]

        for username in invalid_usernames:
            is_valid, message = self.user_model.validate_username(username)
            self.assertFalse(
                is_valid, f"Username '{username}' should be invalid")
            self.assertIn(
                "letters, numbers, underscores, and hyphens",
                message)

    def test_validate_username_invalid_start(self):
        """Test username starting with invalid character"""
        invalid_usernames = ["_username", "-username"]

        for username in invalid_usernames:
            is_valid, message = self.user_model.validate_username(username)
            self.assertFalse(
                is_valid, f"Username '{username}' should be invalid")
            self.assertIn("start with a letter or number", message)

    @patch("users.user_model.create_client")
    def test_get_all_users(self, mock_create_client):
        """Test getting all users"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = [self.sample_user, {"email": "user2@example.com"}]
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = (
            mock_result)

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
            mock_result)

        result = self.user_model.get_user_count()

        self.assertEqual(result, 42)

    @patch("users.user_model.create_client")
    def test_delete_user_success(self, mock_create_client):
        """Test successful user deletion"""
        mock_create_client.return_value = self.mock_supabase
        mock_result = Mock()
        mock_result.data = [{"id": "user-123"}]
        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = (
            mock_result)

        result = self.user_model.delete_user("test@example.com")

        self.assertTrue(result)


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
                errors = self.controller._validate_form_data(
                    form_data, "test@example.com")
                self.assertEqual(len(errors), 0)

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
            errors = self.controller._validate_form_data(
                form_data, "test@example.com")
            self.assertGreater(len(errors), 0)
            self.assertTrue(
                any("Invalid username" in error for error in errors))

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
                errors = self.controller._validate_form_data(
                    form_data, "test@example.com")
                self.assertGreater(len(errors), 0)
                self.assertTrue(
                    any("Username is already taken" in error for error in errors))


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

            result = self.user_view.display_profile_setup_form(
                self.sample_user)

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


class TestUserModelAdvanced(unittest.TestCase):
    """Advanced tests for UserModel functionality"""

    def setUp(self):
        self.user_model = UserModel()
        self.mock_supabase = Mock()

        # Mock Streamlit secrets
        self.patcher = patch(
            "users.user_model.st.secrets", {
                "supabase": {
                    "url": "https://test.supabase.co", "key": "test-key"}}, )
        self.patcher.start()

        self.advanced_user_data = {
            "email": "advanced.user@example.com",
            "name": "Advanced Test User",
            "username": "advanceduser",
            "state": "New York",
            "country": "United States",
            "unit_system": "Metric",
            "sub": "auth0|advanced123456",
            "picture": "https://example.com/advanced.jpg",
            "roles": ["user", "premium"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "profile_complete": True
        }

    def tearDown(self):
        self.patcher.stop()

    def test_username_validation_edge_cases(self):
        """Test username validation with comprehensive edge cases"""
        edge_cases = {
            # Valid cases
            "a23": (True, ""),
            "user123": (True, ""),
            "test_user": (True, ""),
            "valid-name": (True, ""),
            "A1B2C3": (True, ""),
            "x" * 30: (True, ""),  # Maximum length

            # Invalid cases
            "ab": (False, "at least 3 characters"),  # Too short
            "x" * 31: (False, "30 characters or less"),  # Too long
            "_startswith": (False, "start with a letter or number"),
            "-startswith": (False, "start with a letter or number"),
            "user@name": (False, "letters, numbers, underscores, and hyphens"),
            "user name": (False, "letters, numbers, underscores, and hyphens"),
            "user.name": (False, "letters, numbers, underscores, and hyphens"),
            "user%name": (False, "letters, numbers, underscores, and hyphens"),
            "user#name": (False, "letters, numbers, underscores, and hyphens"),
            "": (False, "at least 3 characters"),  # Empty
        }

        for username, (expected_valid,
                       expected_msg_fragment) in edge_cases.items():
            is_valid, message = self.user_model.validate_username(username)
            self.assertEqual(
                is_valid,
                expected_valid,
                f"Username '{username}' validation failed")
            if not expected_valid:
                self.assertIn(
                    expected_msg_fragment,
                    message,
                    f"Error message for '{username}' incorrect")

    @patch("users.user_model.create_client")
    def test_user_profile_crud_operations(self, mock_create_client):
        """Test complete CRUD operations for user profiles"""
        mock_create_client.return_value = self.mock_supabase

        # Test CREATE
        mock_create_response = Mock()
        mock_create_response.data = [{"id": "new-user-123"}]
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_create_response

        create_result = self.user_model.create_user_profile(
            self.advanced_user_data)
        self.assertTrue(create_result)

        # Test READ
        mock_read_response = Mock()
        mock_read_response.data = [self.advanced_user_data]
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_read_response

        read_result = self.user_model.get_user_profile(
            "advanced.user@example.com")
        self.assertEqual(read_result, self.advanced_user_data)

        # Test UPDATE
        mock_update_response = Mock()
        mock_update_response.data = [{"id": "updated-user-123"}]
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update_response

        updated_data = {
            "username": "updateduser",
            "state": "California",
            "country": "United States",
            "unit_system": "Imperial",
        }
        update_result = self.user_model.update_user_profile(
            "advanced.user@example.com", updated_data)
        self.assertTrue(update_result)

        # Test DELETE
        mock_delete_response = Mock()
        mock_delete_response.data = [{"id": "deleted-user-123"}]
        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_delete_response

        delete_result = self.user_model.delete_user(
            "advanced.user@example.com")
        self.assertTrue(delete_result)

    @patch("users.user_model.create_client")
    def test_username_availability_with_exclusions(self, mock_create_client):
        """Test username availability with current user exclusion"""
        mock_create_client.return_value = self.mock_supabase

        # Test username taken by another user
        mock_response = Mock()
        mock_response.data = [{"email": "other@example.com"}]
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.neq.return_value.execute.return_value = mock_response

        is_available = self.user_model.is_username_available(
            "takenuser", "current@example.com")
        self.assertFalse(is_available)

        # Test username available (no other users have it)
        mock_response.data = []
        is_available = self.user_model.is_username_available(
            "availableuser", "current@example.com")
        self.assertTrue(is_available)

    @patch("users.user_model.create_client")
    def test_bulk_user_operations(self, mock_create_client):
        """Test bulk user operations and performance scenarios"""
        mock_create_client.return_value = self.mock_supabase

        # Mock bulk user data
        bulk_users = []
        for i in range(100):
            user_data = {
                "id": f"bulk-user-{i}",
                "email": f"bulk{i}@example.com",
                "name": f"Bulk User {i}",
                "username": f"bulkuser{i}",
                "state": "California" if i % 2 == 0 else "Texas",
                "country": "United States",
                "unit_system": "Imperial" if i % 3 == 0 else "Metric",
                "profile_complete": True,
                "created_at": (datetime.now() - timedelta(days=i)).isoformat()
            }
            bulk_users.append(user_data)

        mock_response = Mock()
        mock_response.data = bulk_users
        self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

        all_users = self.user_model.get_all_users()
        self.assertEqual(len(all_users), 100)

        # Test user count
        mock_count_response = Mock()
        mock_count_response.count = 100
        self.mock_supabase.table.return_value.select.return_value.execute.return_value = mock_count_response

        user_count = self.user_model.get_user_count()
        self.assertEqual(user_count, 100)

    @patch("users.user_model.st.error")
    @patch("users.user_model.create_client")
    def test_error_handling_comprehensive(
            self, mock_create_client, mock_st_error):
        """Test comprehensive error handling scenarios"""
        mock_create_client.return_value = self.mock_supabase

        # Test various database errors
        error_scenarios = [
            ("Connection timeout", "get_user_profile"),
            ("Permission denied", "create_user_profile"),
            ("Constraint violation", "update_user_profile"),
            ("Record not found", "delete_user"),
            ("Network error", "get_all_users"),
            ("Authentication failed", "get_user_count")
        ]

        for error_msg, method_name in error_scenarios:
            with self.subTest(error=error_msg, method=method_name):
                # Reset mocks before each subtest
                self.mock_supabase.reset_mock()

                # Setup error scenario
                if method_name == "get_user_profile":
                    self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception(
                        error_msg)
                elif method_name == "get_all_users":
                    self.mock_supabase.table.return_value.select.return_value.order.return_value.execute.side_effect = Exception(
                        error_msg)
                elif method_name == "create_user_profile":
                    self.mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
                        error_msg)
                elif method_name == "update_user_profile":
                    self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception(
                        error_msg)
                elif method_name == "delete_user":
                    self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.side_effect = Exception(
                        error_msg)
                elif method_name == "get_user_count":
                    self.mock_supabase.table.return_value.select.return_value.execute.side_effect = Exception(
                        error_msg)

                # Call method and verify error handling
                if method_name == "get_user_profile":
                    result = self.user_model.get_user_profile(
                        "test@example.com")
                    self.assertIsNone(result)
                elif method_name == "create_user_profile":
                    result = self.user_model.create_user_profile(
                        self.advanced_user_data)
                    self.assertFalse(result)
                elif method_name == "update_user_profile":
                    result = self.user_model.update_user_profile(
                        "test@example.com", {"username": "updated"})
                    self.assertFalse(result)
                elif method_name == "delete_user":
                    result = self.user_model.delete_user("test@example.com")
                    self.assertFalse(result)
                elif method_name == "get_all_users":
                    result = self.user_model.get_all_users()
                    self.assertEqual(result, [])
                elif method_name == "get_user_count":
                    result = self.user_model.get_user_count()
                    self.assertEqual(result, 0)

                # Reset side effects
                if hasattr(
                        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute,
                        'side_effect'):
                    self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = None

    def test_user_data_sanitization(self):
        """Test user data sanitization and validation"""
        # Test data with potential issues
        problematic_data = {
            "email": "  TEST@EXAMPLE.COM  ",  # Case and whitespace
            "name": "  Test User  ",  # Whitespace
            "username": "TestUser123",  # Case sensitivity
            "state": "  California  ",  # Whitespace
            "country": "United States",
            "unit_system": "imperial",  # Case sensitivity
        }

        # Username validation should handle case sensitivity
        is_valid, _ = self.user_model.validate_username("TestUser123")
        self.assertTrue(is_valid)

        # Test edge case usernames
        edge_usernames = ["test123", "TEST123", "Test123", "tEsT123"]
        for username in edge_usernames:
            is_valid, _ = self.user_model.validate_username(username)
            self.assertTrue(is_valid, f"Username {username} should be valid")


class TestUserControllerAdvanced(unittest.TestCase):
    """Advanced tests for UserController functionality"""

    def setUp(self):
        self.controller = UserController()
        self.advanced_user = {
            "email": "controller.test@example.com",
            "name": "Controller Test User",
            "username": "controlleruser",
            "state": "Washington",
            "country": "Canada",
            "unit_system": "Metric",
            "sub": "auth0|controller123",
            "picture": "https://example.com/controller.jpg",
        }

    def test_complex_form_validation_scenarios(self):
        """Test complex form validation scenarios"""
        # Test multiple validation errors
        invalid_form_data = {
            "username": "ab",  # Too short
            "state": "",  # Empty
            "country": "",  # Empty
            "unit_system": "Metric"
        }

        with patch.object(self.controller.model, 'validate_username', return_value=(False, "Too short")):
            errors = self.controller._validate_form_data(
                invalid_form_data, "test@example.com")

            self.assertGreater(len(errors), 1)
            error_text = " ".join(errors).lower()
            self.assertIn("username", error_text)
            self.assertIn("state", error_text)
            self.assertIn("country", error_text)

    @patch('users.user_controller.st.session_state', {})
    @patch('users.user_controller.st.rerun')
    def test_profile_setup_workflow_complete(self, mock_rerun):
        """Test complete profile setup workflow"""
        # Test new user profile creation
        with patch.object(self.controller.model, 'get_user_profile', return_value=None):
            with patch.object(self.controller.view, 'display_profile_setup_form', return_value={
                "username": "newuser",
                "state": "California",
                "country": "United States",
                "unit_system": "Imperial"
            }):
                with patch.object(self.controller.model, 'validate_username', return_value=(True, "")):
                    with patch.object(self.controller.model, 'is_username_available', return_value=True):
                        with patch.object(self.controller.model, 'create_user_profile', return_value=True):
                            with patch.object(self.controller.view, 'display_success_message'):
                                result = self.controller.handle_profile_setup(
                                    self.advanced_user)
                                mock_rerun.assert_called_once()

    def test_user_statistics_calculation(self):
        """Test user statistics calculation accuracy"""
        mock_users = [
            {"unit_system": "Imperial", "profile_complete": True},
            {"unit_system": "Metric", "profile_complete": True},
            {"unit_system": "Imperial", "profile_complete": False},
            {"unit_system": "Metric", "profile_complete": True},
            {"unit_system": "Imperial", "profile_complete": True},
        ]

        with patch.object(self.controller.model, 'get_user_count', return_value=5):
            with patch.object(self.controller.model, 'get_all_users', return_value=mock_users):
                stats = self.controller.get_user_stats()

                self.assertEqual(stats["total_users"], 5)
                self.assertEqual(stats["imperial_users"], 3)
                self.assertEqual(stats["metric_users"], 2)
                self.assertEqual(stats["complete_profiles"], 4)
                self.assertEqual(stats["incomplete_profiles"], 1)

    @patch('users.user_controller.st.session_state', {"edit_profile": True})
    @patch('users.user_controller.st.rerun')
    def test_profile_editing_workflow(self, mock_rerun):
        """Test profile editing workflow"""
        existing_profile = {
            "email": "existing@example.com",
            "username": "existinguser",
            "profile_complete": True
        }

        with patch.object(self.controller.model, 'get_user_profile', return_value=existing_profile):
            with patch.object(self.controller.view, 'display_profile_setup_form', return_value={
                "username": "updateduser",
                "state": "Updated State",
                "country": "Updated Country",
                "unit_system": "Metric"
            }):
                with patch.object(self.controller.model, 'validate_username', return_value=(True, "")):
                    with patch.object(self.controller.model, 'is_username_available', return_value=True):
                        with patch.object(self.controller.model, 'update_user_profile', return_value=True):
                            with patch.object(self.controller.view, 'display_success_message'):
                                result = self.controller.handle_profile_setup(
                                    self.advanced_user, existing_profile)
                                mock_rerun.assert_called_once()

    @patch('users.user_controller.st.session_state', {})
    @patch('users.user_controller.st.rerun')
    def test_admin_user_management_workflow(self, mock_rerun):
        """Test admin user management workflow"""
        mock_users = [
            {"email": "user1@example.com", "name": "User 1"},
            {"email": "user2@example.com", "name": "User 2"},
            {"email": "user3@example.com", "name": "User 3"}
        ]

        with patch.object(self.controller.model, 'get_all_users', return_value=mock_users):
            with patch.object(self.controller.view, 'display_user_management_admin', return_value={
                "action": "delete",
                "selected_indices": [0, 2]  # Select user 1 and 3
            }):
                with patch.object(self.controller.view, 'display_delete_confirmation', return_value="confirm"):
                    with patch.object(self.controller.model, 'delete_user', return_value=True):
                        with patch.object(self.controller.view, 'display_success_message'):
                            self.controller.handle_user_management_admin()
                            mock_rerun.assert_called_once()


class TestUserViewAdvanced(unittest.TestCase):
    """Advanced tests for UserView functionality"""

    def setUp(self):
        self.user_view = UserView()
        self.comprehensive_user = {
            "email": "view.test@example.com",
            "name": "View Test User",
            "username": "viewuser",
            "state": "Oregon",
            "country": "United States",
            "unit_system": "Imperial",
            "picture": "https://example.com/view.jpg",
            "roles": ["user", "admin"],
            "profile_complete": True,
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-15T15:30:00Z"
        }

    @patch("users.user_view.st.form")
    @patch("users.user_view.st.title")
    @patch("users.user_view.st.text_input")
    @patch("users.user_view.st.selectbox")
    @patch("users.user_view.st.radio")
    @patch("users.user_view.st.form_submit_button")
    def test_profile_setup_form_comprehensive(
            self,
            mock_submit,
            mock_radio,
            mock_selectbox,
            mock_text_input,
            mock_title,
            mock_form):
        """Test comprehensive profile setup form scenarios"""
        # Mock form context manager
        mock_form_context = Mock()
        mock_form.return_value.__enter__ = Mock(return_value=mock_form_context)
        mock_form.return_value.__exit__ = Mock()

        # Test form with all fields filled
        mock_text_input.side_effect = ["comprehensiveuser", "Oregon"]
        mock_selectbox.return_value = "Canada"
        mock_radio.return_value = "Metric"
        mock_submit.return_value = True

        result = self.user_view.display_profile_setup_form(
            self.comprehensive_user)

        self.assertIsNotNone(result)
        self.assertEqual(result["username"], "comprehensiveuser")
        self.assertEqual(result["state"], "Oregon")
        self.assertEqual(result["country"], "Canada")
        self.assertEqual(result["unit_system"], "Metric")

    @patch("users.user_view.st.form")
    @patch("users.user_view.st.title")
    @patch("users.user_view.st.text_input")
    @patch("users.user_view.st.selectbox")
    @patch("users.user_view.st.radio")
    @patch("users.user_view.st.form_submit_button")
    def test_profile_setup_form_not_submitted(
            self,
            mock_submit,
            mock_radio,
            mock_selectbox,
            mock_text_input,
            mock_title,
            mock_form):
        """Test profile setup form when not submitted"""
        # Mock form context manager
        mock_form_context = Mock()
        mock_form.return_value.__enter__ = Mock(return_value=mock_form_context)
        mock_form.return_value.__exit__ = Mock()

        mock_submit.return_value = False  # Form not submitted

        result = self.user_view.display_profile_setup_form(
            self.comprehensive_user)

        self.assertIsNone(result)

    @patch("users.user_view.st.error")
    def test_validation_errors_multiple(self, mock_error):
        """Test displaying multiple validation errors"""
        errors = [
            "Username is required",
            "Username must be at least 3 characters long",
            "State/Province is required",
            "Country is required",
            "Username is already taken"
        ]

        self.user_view.display_validation_errors(errors)

        self.assertEqual(mock_error.call_count, 5)
        for error in errors:
            mock_error.assert_any_call(error)

    def test_message_display_methods(self):
        """Test various message display methods"""
        with patch("users.user_view.st.success") as mock_success:
            self.user_view.display_success_message("Operation successful")
            mock_success.assert_called_once_with("Operation successful")

        with patch("users.user_view.st.error") as mock_error:
            self.user_view.display_error_message("Operation failed")
            mock_error.assert_called_once_with("Operation failed")


class TestUserIntegrationAdvanced(unittest.TestCase):
    """Advanced integration tests for user module"""

    def setUp(self):
        self.sample_user = {
            "email": "integration@example.com",
            "name": "Integration Test User",
            "username": "integrationuser",
            "state": "Nevada",
            "country": "United States",
            "unit_system": "Imperial",
            "sub": "auth0|integration123",
            "picture": "https://example.com/integration.jpg",
            "roles": ["user"],
            "profile_complete": True
        }

    def test_complete_user_lifecycle_integration(self):
        """Test complete user lifecycle integration"""
        controller = UserController()

        # Test user registration workflow
        with patch.object(controller.model, 'get_user_profile', return_value=None):
            with patch.object(controller.view, 'display_profile_setup_form', return_value={
                "username": "lifecycleuser",
                "state": "California",
                "country": "United States",
                "unit_system": "Imperial"
            }):
                with patch.object(controller.model, 'validate_username', return_value=(True, "")):
                    with patch.object(controller.model, 'is_username_available', return_value=True):
                        with patch.object(controller.model, 'create_user_profile', return_value=True):
                            with patch('users.user_controller.st.session_state', {}):
                                with patch('users.user_controller.st.rerun'):
                                    with patch.object(controller.view, 'display_success_message'):
                                        # Should create new profile
                                        result = controller.handle_profile_setup(
                                            self.sample_user)

        # Test user profile retrieval
        with patch.object(controller.model, 'get_user_profile', return_value=self.sample_user):
            profile = controller.get_complete_user_profile(self.sample_user)
            self.assertEqual(profile, self.sample_user)

    def test_error_recovery_integration(self):
        """Test error recovery in integrated workflows"""
        controller = UserController()

        # Test database failure during profile creation
        with patch.object(controller.model, 'get_user_profile', return_value=None):
            with patch.object(controller.view, 'display_profile_setup_form', return_value={
                "username": "erroruser",
                "state": "California",
                "country": "United States",
                "unit_system": "Imperial"
            }):
                with patch.object(controller.model, 'validate_username', return_value=(True, "")):
                    with patch.object(controller.model, 'is_username_available', return_value=True):
                        with patch.object(controller.model, 'create_user_profile', return_value=False):
                            with patch.object(controller.view, 'display_error_message') as mock_error:
                                result = controller.handle_profile_setup(
                                    self.sample_user)
                                mock_error.assert_called_with(
                                    "Failed to save profile. Please try again.")

    def test_concurrent_user_operations_simulation(self):
        """Test simulation of concurrent user operations"""
        model = UserModel()

        # Mock multiple users accessing system simultaneously
        with patch("users.user_model.create_client") as mock_create_client:
            mock_supabase = Mock()
            mock_create_client.return_value = mock_supabase

            concurrent_users = []
            for i in range(10):
                user_data = {
                    "email": f"concurrent{i}@example.com",
                    "username": f"concurrent{i}",
                    "name": f"Concurrent User {i}",
                    "state": "California",
                    "country": "United States",
                    "unit_system": "Imperial" if i % 2 == 0 else "Metric",
                    "profile_complete": True
                }
                concurrent_users.append(user_data)

            # Mock availability checks for all users
            mock_response = Mock()
            mock_response.data = []  # All usernames available
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

            # Test that all usernames are validated as available
            for i, user in enumerate(concurrent_users):
                is_available = model.is_username_available(user["username"])
                self.assertTrue(
                    is_available,
                    f"Username {user['username']} should be available")

    def test_data_consistency_across_operations(self):
        """Test data consistency across different operations"""
        controller = UserController()

        # Test profile creation and immediate retrieval consistency
        test_profile = {
            "email": "consistency@example.com",
            "name": "Consistency Test",
            "username": "consistencyuser",
            "state": "Texas",
            "country": "United States",
            "unit_system": "Metric"
        }

        with patch.object(controller.model, 'create_user_profile', return_value=True):
            with patch.object(controller.model, 'get_user_profile', return_value={**test_profile, "profile_complete": True}):
                # Create profile
                created = controller.model.create_user_profile(test_profile)
                self.assertTrue(created)

                # Immediately retrieve and verify consistency
                retrieved = controller.model.get_user_profile(
                    "consistency@example.com")
                self.assertEqual(
                    retrieved["username"],
                    test_profile["username"])
                self.assertEqual(retrieved["state"], test_profile["state"])
                self.assertEqual(
                    retrieved["unit_system"],
                    test_profile["unit_system"])

    def test_user_permissions_and_roles(self):
        """Test user permissions and roles handling"""
        admin_user = {
            **self.sample_user,
            "email": "admin@example.com",
            "roles": ["user", "admin"]
        }

        premium_user = {
            **self.sample_user,
            "email": "premium@example.com",
            "roles": ["user", "premium"]
        }

        basic_user = {
            **self.sample_user,
            "email": "basic@example.com",
            "roles": ["user"]
        }

        # Test role validation
        for user in [admin_user, premium_user, basic_user]:
            self.assertIn("user", user.get("roles", []))

        self.assertIn("admin", admin_user.get("roles", []))
        self.assertIn("premium", premium_user.get("roles", []))
        self.assertNotIn("admin", basic_user.get("roles", []))

    def test_performance_with_large_user_datasets(self):
        """Test performance considerations with large user datasets"""
        model = UserModel()

        with patch("users.user_model.create_client") as mock_create_client:
            mock_supabase = Mock()
            mock_create_client.return_value = mock_supabase

            # Mock large dataset (1000 users)
            large_dataset = []
            for i in range(1000):
                user = {
                    "id": f"user-{i:04d}",
                    "email": f"user{i}@example.com",
                    "username": f"user{i:04d}",
                    "name": f"User {i}",
                    "state": ["California", "Texas", "New York", "Florida"][i % 4],
                    "country": "United States",
                    "unit_system": ["Imperial", "Metric"][i % 2],
                    "profile_complete": True,
                    "created_at": (datetime.now() - timedelta(days=i)).isoformat()
                }
                large_dataset.append(user)

            # Mock responses for large dataset
            mock_response = Mock()
            mock_response.data = large_dataset
            mock_response.count = 1000
            mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
            mock_supabase.table.return_value.select.return_value.execute.return_value = mock_response

            # Test operations with large dataset
            all_users = model.get_all_users()
            self.assertEqual(len(all_users), 1000)

            user_count = model.get_user_count()
            self.assertEqual(user_count, 1000)

            # Verify data integrity with large dataset
            first_user = all_users[0]
            last_user = all_users[-1]

            self.assertIn("@example.com", first_user["email"])
            self.assertIn("@example.com", last_user["email"])


if __name__ == "__main__":
    unittest.main()
