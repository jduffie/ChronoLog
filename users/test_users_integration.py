#!/usr/bin/env python3
"""
Integration tests for the users module.
Tests end-to-end workflows and cross-module interactions with real-like scenarios.
"""

import os
import sys
import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch
import pytest

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from users.user_controller import UserController
from users.user_model import UserModel
from users.user_view import UserView


class BaseUserIntegrationTest(unittest.TestCase):
    """Base class for user integration tests with common setup"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_user_email = "integration-test@chronolog.test"
        cls.test_user_id = "auth0|111273793361054745867"

    def setUp(self):
        """Set up each test with clean state"""
        self.sample_user = {
            "id": self.test_user_id,
            "email": self.test_user_email,
            "name": "Integration Test User",
            "username": "integrationuser",
            "state": "California",
            "country": "United States",
            "unit_system": "Imperial",
            "sub": self.test_user_id,
            "picture": "https://example.com/pic.jpg",
            "profile_complete": True,
            "roles": ["user"],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        
        self.incomplete_user = {
            "id": self.test_user_id,
            "email": self.test_user_email,
            "name": "Incomplete User",
            "profile_complete": False,
        }


@pytest.mark.integration
class TestUserProfileWorkflow(BaseUserIntegrationTest):
    """Test complete user profile workflows"""

    @patch("users.user_model.create_client")
    @patch("users.user_controller.st.session_state", {})
    def test_new_user_registration_workflow(self, mock_create_client):
        """Test complete new user registration workflow"""
        # Mock Supabase client
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        # Mock user doesn't exist initially
        mock_result_empty = Mock()
        mock_result_empty.data = []
        
        # Mock successful user creation
        mock_result_success = Mock()
        mock_result_success.data = [{"id": "new-user-123"}]
        
        # Configure mock responses
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result_empty
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_result_success

        # Create controller
        controller = UserController()

        # Step 1: Check if user exists (should return None)
        existing_user = controller.get_complete_user_profile(self.test_user_email)
        self.assertIsNone(existing_user)

        # Step 2: Create new user profile
        result = controller.model.create_user_profile(self.sample_user)
        self.assertTrue(result)

        # Verify database interactions
        mock_supabase.table.assert_called_with("users")
        mock_supabase.table.return_value.insert.assert_called_with(self.sample_user)

    @patch("users.user_model.create_client")
    @patch("users.user_controller.st.session_state", {})
    def test_existing_user_profile_update_workflow(self, mock_create_client):
        """Test complete existing user profile update workflow"""
        # Mock Supabase client
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        # Mock existing user retrieval
        mock_result_existing = Mock()
        mock_result_existing.data = [self.sample_user]
        
        # Mock successful update
        mock_result_update = Mock()
        mock_result_update.data = [{"id": "user-123"}]
        
        # Configure mock responses
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result_existing
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_result_update

        # Create controller
        controller = UserController()

        # Step 1: Retrieve existing user
        existing_user = controller.get_complete_user_profile(self.test_user_email)
        self.assertIsNotNone(existing_user)
        self.assertEqual(existing_user["email"], self.test_user_email)

        # Step 2: Update user profile
        updated_user = self.sample_user.copy()
        updated_user["state"] = "New York"
        updated_user["updated_at"] = datetime.now(timezone.utc).isoformat()

        result = controller.model.update_user_profile(self.test_user_email, updated_user)
        self.assertTrue(result)

        # Verify update was called with correct data
        mock_supabase.table.return_value.update.assert_called_with(updated_user)

    @patch("users.user_model.create_client")
    def test_username_validation_workflow(self, mock_create_client):
        """Test complete username validation workflow"""
        # Mock Supabase client
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        model = UserModel()

        # Test various username scenarios
        test_cases = [
            ("validuser123", True, True, "Valid username should pass all checks"),
            ("ab", False, True, "Too short username should fail validation"),
            ("user@invalid", False, True, "Invalid characters should fail validation"),
            ("_invalidstart", False, True, "Invalid start character should fail validation"),
            ("a" * 31, False, True, "Too long username should fail validation"),
            ("takenuser", True, False, "Valid but taken username should fail availability"),
        ]

        for username, is_valid_format, is_available, description in test_cases:
            # Mock availability check
            if is_available:
                mock_result = Mock()
                mock_result.data = []
            else:
                mock_result = Mock()
                mock_result.data = [{"email": "other@example.com"}]
            
            mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result

            # Test format validation
            format_valid, format_message = model.validate_username(username)
            self.assertEqual(format_valid, is_valid_format, f"{description} - format check")

            # Test availability only if format is valid
            if format_valid:
                availability = model.is_username_available(username)
                self.assertEqual(availability, is_available, f"{description} - availability check")

    @patch("users.user_model.create_client")
    @patch("users.user_controller.st.session_state", {})
    def test_profile_completion_workflow(self, mock_create_client):
        """Test profile completion status workflow"""
        # Mock Supabase client
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        controller = UserController()

        # Test incomplete profile
        mock_result_incomplete = Mock()
        mock_result_incomplete.data = [self.incomplete_user]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result_incomplete

        incomplete_profile = controller.get_complete_user_profile(self.test_user_email)
        self.assertIsNotNone(incomplete_profile)
        self.assertFalse(incomplete_profile.get("profile_complete", True))

        # Test complete profile
        mock_result_complete = Mock()
        mock_result_complete.data = [self.sample_user]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result_complete

        complete_profile = controller.get_complete_user_profile(self.test_user_email)
        self.assertIsNotNone(complete_profile)
        self.assertTrue(complete_profile.get("profile_complete", False))


@pytest.mark.integration
@pytest.mark.auth
class TestUserAuthenticationIntegration(BaseUserIntegrationTest):
    """Test user authentication integration"""

    @patch("users.user_model.create_client")
    @patch("users.user_controller.st.session_state", {"user_info": {"email": "test@example.com"}, "authenticated": True})
    def test_authenticated_user_data_access(self, mock_create_client):
        """Test that authenticated users can access their data correctly"""
        # Mock Supabase client
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        # Mock user data retrieval
        mock_result = Mock()
        mock_result.data = [self.sample_user]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result

        controller = UserController()

        # Test that user can access their profile
        user_profile = controller.get_complete_user_profile(self.test_user_email)
        self.assertIsNotNone(user_profile)
        self.assertEqual(user_profile["email"], self.test_user_email)

        # Verify the query filtered by email correctly
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with("email", self.test_user_email)

    @patch("users.user_model.create_client")
    def test_user_data_isolation(self, mock_create_client):
        """Test that users can only access their own data"""
        # Mock Supabase client
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        model = UserModel()

        # Test different user emails
        user1_email = "user1@example.com"
        user2_email = "user2@example.com"

        # Mock user1 data
        mock_result_user1 = Mock()
        mock_result_user1.data = [{"email": user1_email, "username": "user1"}]

        # Mock user2 data (should not return user1's data)
        mock_result_user2 = Mock()
        mock_result_user2.data = [{"email": user2_email, "username": "user2"}]

        # Configure mock to return different data based on email
        def mock_execute_side_effect():
            # This simulates database filtering by email
            if mock_supabase.table.return_value.select.return_value.eq.call_args[0][1] == user1_email:
                return mock_result_user1
            else:
                return mock_result_user2

        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = mock_execute_side_effect

        # Test user1 access
        user1_profile = model.get_user_profile(user1_email)
        self.assertIsNotNone(user1_profile)
        self.assertEqual(user1_profile["email"], user1_email)

        # Test user2 access
        user2_profile = model.get_user_profile(user2_email)
        self.assertIsNotNone(user2_profile)
        self.assertEqual(user2_profile["email"], user2_email)


@pytest.mark.integration
@pytest.mark.admin
class TestUserAdminIntegration(BaseUserIntegrationTest):
    """Test user administration integration"""

    @patch("users.user_model.create_client")
    def test_admin_user_management_workflow(self, mock_create_client):
        """Test admin user management capabilities"""
        # Mock Supabase client
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        model = UserModel()

        # Test getting all users (admin function)
        mock_result_all = Mock()
        mock_result_all.data = [
            self.sample_user,
            {"email": "user2@example.com", "username": "user2"},
            {"email": "user3@example.com", "username": "user3"}
        ]
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_result_all

        all_users = model.get_all_users()
        self.assertEqual(len(all_users), 3)
        self.assertIn(self.sample_user, all_users)

        # Test getting user count
        mock_result_count = Mock()
        mock_result_count.count = 3
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_result_count

        user_count = model.get_user_count()
        self.assertEqual(user_count, 3)

        # Test user deletion (admin function)
        mock_result_delete = Mock()
        mock_result_delete.data = [{"id": "deleted-user"}]
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_result_delete

        delete_result = model.delete_user("user2@example.com")
        self.assertTrue(delete_result)

        # Verify delete was called with correct email
        mock_supabase.table.return_value.delete.return_value.eq.assert_called_with("email", "user2@example.com")


@pytest.mark.integration
@pytest.mark.error_handling
class TestUserErrorHandlingIntegration(BaseUserIntegrationTest):
    """Test error handling across user module integration points"""

    @patch("users.user_model.create_client")
    @patch("users.user_model.st.error")
    def test_database_error_handling(self, mock_st_error, mock_create_client):
        """Test graceful handling of database errors"""
        # Mock Supabase client that raises errors
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Database connection failed")

        model = UserModel()

        # Test that database errors are handled gracefully
        result = model.get_user_profile(self.test_user_email)
        self.assertIsNone(result)
        mock_st_error.assert_called_once()

    @patch("users.user_model.create_client")
    @patch("users.user_model.st.error")
    def test_partial_failure_scenarios(self, mock_st_error, mock_create_client):
        """Test handling of partial failure scenarios"""
        # Mock Supabase client
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        model = UserModel()

        # Test scenario where user creation fails
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Insert failed")

        result = model.create_user_profile(self.sample_user)
        self.assertFalse(result)
        mock_st_error.assert_called_once()

        # Reset mock
        mock_st_error.reset_mock()

        # Test scenario where update fails
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception("Update failed")

        result = model.update_user_profile(self.test_user_email, self.sample_user)
        self.assertFalse(result)
        mock_st_error.assert_called_once()

    @patch("users.user_model.create_client")
    @patch("users.user_controller.st.session_state", {})
    def test_form_validation_integration(self, mock_create_client):
        """Test form validation integration across MVC layers"""
        # Mock Supabase client
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        controller = UserController()

        # Test form data with multiple validation errors
        invalid_form_data = {
            "username": "",  # Missing required field
            "state": "",     # Missing required field
            "country": "United States",
            "unit_system": "Imperial"
        }

        errors = controller._validate_form_data(invalid_form_data, self.test_user_email)
        
        # Should have multiple validation errors
        self.assertGreater(len(errors), 0)
        error_text = " ".join(errors)
        self.assertIn("Username is required", error_text)
        self.assertIn("State is required", error_text)

    @patch("users.user_model.create_client")
    def test_concurrent_operations_simulation(self, mock_create_client):
        """Test simulation of concurrent operations"""
        # Mock Supabase client
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        model = UserModel()

        # Simulate concurrent username checks
        # First check: username available
        mock_result_available = Mock()
        mock_result_available.data = []
        
        # Second check: username taken (simulating race condition)
        mock_result_taken = Mock()
        mock_result_taken.data = [{"email": "other@example.com"}]

        # Configure mock to return different results
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            mock_result_available,  # First check - available
            mock_result_taken       # Second check - taken
        ]

        # First check should show available
        first_check = model.is_username_available("testuser")
        self.assertTrue(first_check)

        # Second check should show taken
        second_check = model.is_username_available("testuser")
        self.assertFalse(second_check)


@pytest.mark.integration
@pytest.mark.performance
class TestUserPerformanceIntegration(BaseUserIntegrationTest):
    """Test performance aspects of user module integration"""

    @patch("users.user_model.create_client")
    def test_bulk_operations_simulation(self, mock_create_client):
        """Test simulation of bulk operations"""
        # Mock Supabase client
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        model = UserModel()

        # Simulate getting all users (admin operation)
        large_user_list = []
        for i in range(100):
            user = {
                "email": f"user{i}@example.com",
                "username": f"user{i}",
                "name": f"User {i}"
            }
            large_user_list.append(user)

        mock_result = Mock()
        mock_result.data = large_user_list
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_result

        all_users = model.get_all_users()
        
        # Verify we can handle large result sets
        self.assertEqual(len(all_users), 100)
        self.assertEqual(all_users[0]["email"], "user0@example.com")
        self.assertEqual(all_users[99]["email"], "user99@example.com")

    @patch("users.user_model.create_client")
    def test_repeated_operations_simulation(self, mock_create_client):
        """Test simulation of repeated operations"""
        # Mock Supabase client
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase

        model = UserModel()

        # Mock consistent response
        mock_result = Mock()
        mock_result.data = [self.sample_user]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result

        # Perform repeated operations
        for i in range(10):
            result = model.get_user_profile(self.test_user_email)
            self.assertIsNotNone(result)
            self.assertEqual(result["email"], self.test_user_email)

        # Verify database was called multiple times
        self.assertEqual(mock_supabase.table.call_count, 10)


if __name__ == "__main__":
    # Run integration tests with verbose output
    unittest.main(verbosity=2)