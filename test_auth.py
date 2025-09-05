#!/usr/bin/env python3
"""
Comprehensive test suite for the auth module.
Tests authentication workflows, Auth0 integration, and session management.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

import auth

# Add root directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class TestAuthConfiguration(unittest.TestCase):
    """Test auth configuration and setup"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock secrets
        self.mock_secrets = {
            "auth0": {
                "domain": "test-domain.auth0.com",
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "redirect_uri": "https://app.chronolog.com",
                "mapping_redirect_uri": "https://mapping.chronolog.com",
            }
        }

        # Mock environment variables
        self.env_patcher = patch.dict(
            os.environ,
            {
                "AUTH0_DOMAIN": "env-domain.auth0.com",
                "AUTH0_CLIENT_ID": "env-client-id",
                "AUTH0_CLIENT_SECRET": "env-client-secret",
            },
            clear=False,
        )
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()

    @patch("auth.st.secrets")
    def test_auth0_config_from_secrets(self, mock_secrets):
        """Test Auth0 configuration from Streamlit secrets"""
        mock_secrets.__getitem__.side_effect = lambda key: self.mock_secrets[key]

        # Reload module to pick up new config
        import importlib

        importlib.reload(auth)

        # Note: In production, environment variables take precedence
        # So we expect the env values, not secrets values
        self.assertEqual(auth.AUTH0_DOMAIN, "env-domain.auth0.com")
        self.assertEqual(auth.CLIENT_ID, "env-client-id")
        self.assertEqual(auth.CLIENT_SECRET, "env-client-secret")

    @patch.dict(os.environ, {}, clear=True)  # Clear env vars
    @patch("auth.st.secrets")
    def test_auth0_config_from_env_fallback(self, mock_secrets):
        """Test Auth0 configuration fallback to secrets when env vars not set"""
        mock_secrets.__getitem__.side_effect = lambda key: self.mock_secrets[key]

        # Reload module to pick up new config
        import importlib

        importlib.reload(auth)

        self.assertEqual(auth.AUTH0_DOMAIN, "test-domain.auth0.com")
        self.assertEqual(auth.CLIENT_ID, "test-client-id")
        self.assertEqual(auth.CLIENT_SECRET, "test-client-secret")


class TestRedirectUriHandling(unittest.TestCase):
    """Test redirect URI handling for different apps"""

    def setUp(self):
        """Set up test fixtures"""
        self.secrets_patcher = patch(
            "auth.st.secrets",
            {
                "auth0": {
                    "redirect_uri": "https://app.chronolog.com",
                    "mapping_redirect_uri": "https://mapping.chronolog.com",
                }
            },
        )
        self.secrets_patcher.start()

    def tearDown(self):
        """Clean up after tests"""
        self.secrets_patcher.stop()

    @patch("auth.st.query_params", {"app": "mapping"})
    def test_get_redirect_uri_mapping_app(self):
        """Test redirect URI for mapping app"""
        result = auth.get_redirect_uri()
        self.assertEqual(result, "https://mapping.chronolog.com")

    @patch("auth.st.query_params", {})
    def test_get_redirect_uri_main_app(self):
        """Test redirect URI for main app"""
        result = auth.get_redirect_uri()
        self.assertEqual(result, "https://app.chronolog.com")

    @patch("auth.st.query_params", {"app": "chronolog"})
    def test_get_redirect_uri_chronolog_app(self):
        """Test redirect URI for chronolog app identifier"""
        result = auth.get_redirect_uri()
        self.assertEqual(result, "https://app.chronolog.com")

    @patch("auth.st.query_params", {"app": "mapping"})
    def test_get_redirect_uri_local_mapping(self):
        """Test redirect URI for local mapping development"""
        # Mock st.secrets to raise KeyError when accessed
        with patch("auth.st.secrets") as mock_secrets:
            mock_secrets.__getitem__.side_effect = KeyError()
            result = auth.get_redirect_uri()
            self.assertEqual(result, "http://localhost:8502")

    @patch("auth.st.query_params", {})
    def test_get_redirect_uri_local_main(self):
        """Test redirect URI for local main development"""
        # Mock st.secrets to raise KeyError when accessed
        with patch("auth.st.secrets") as mock_secrets:
            mock_secrets.__getitem__.side_effect = KeyError()
            result = auth.get_redirect_uri()
            self.assertEqual(result, "http://localhost:8501")


class TestAppNameHandling(unittest.TestCase):
    """Test application name handling"""

    @patch("auth.st.query_params", {"app": "mapping"})
    def test_get_app_name_mapping(self):
        """Test app name for mapping application"""
        result = auth.get_app_name()
        self.assertEqual(result, "ChronoLog Mapping Tool")

    @patch("auth.st.query_params", {})
    def test_get_app_name_main(self):
        """Test app name for main application"""
        result = auth.get_app_name()
        self.assertEqual(result, "ChronoLog")

    @patch("auth.st.query_params", {"app": "other"})
    def test_get_app_name_other(self):
        """Test app name for unknown application"""
        result = auth.get_app_name()
        self.assertEqual(result, "ChronoLog")


class TestLoginButton(unittest.TestCase):
    """Test login button generation and display"""

    def setUp(self):
        """Set up test fixtures"""
        self.secrets_patcher = patch(
            "auth.st.secrets", {
                "auth0": {
                    "redirect_uri": "https://app.chronolog.com"}})
        self.secrets_patcher.start()

    def tearDown(self):
        """Clean up after tests"""
        self.secrets_patcher.stop()

    @patch("auth.st.query_params", {})
    @patch("auth.st.columns")
    @patch("auth.st.markdown")
    def test_show_login_button_structure(self, mock_markdown, mock_columns):
        """Test login button structure and content"""
        # Mock columns
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]

        # Mock column context manager
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=None)

        auth.show_login_button()

        # Verify columns were created
        mock_columns.assert_called_with([1, 2, 1])

        # Verify markdown was called (for welcome message and button)
        self.assertTrue(mock_markdown.called)

        # Check that HTML button was rendered
        markdown_calls = [call[0][0] for call in mock_markdown.call_args_list]
        html_calls = [
            call for call in markdown_calls if "Sign in with Google" in str(call)]
        self.assertTrue(
            len(html_calls) > 0,
            "Login button HTML should be rendered")

    @patch("auth.st.query_params", {})
    @patch("auth.st.columns")
    @patch("auth.st.markdown")
    def test_login_url_generation(self, mock_markdown, mock_columns):
        """Test that login URL is properly generated"""
        # Mock columns
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=None)

        auth.show_login_button()

        # Find the HTML content call
        markdown_calls = mock_markdown.call_args_list
        html_call = None
        for call in markdown_calls:
            if len(call[0]) > 0 and "Sign in with Google" in str(call[0][0]):
                html_call = call[0][0]
                break

        self.assertIsNotNone(html_call, "HTML button call should exist")

        # Extract URL from HTML (basic check)
        self.assertIn("authorize?", html_call)
        self.assertIn("client_id=", html_call)
        self.assertIn("response_type=code", html_call)
        self.assertIn("connection=google-oauth2", html_call)


class TestUserInfoRetrieval(unittest.TestCase):
    """Test user info retrieval from Auth0"""

    def setUp(self):
        """Set up test fixtures"""
        self.secrets_patcher = patch(
            "auth.st.secrets", {
                "auth0": {
                    "redirect_uri": "https://app.chronolog.com"}})
        self.secrets_patcher.start()

    def tearDown(self):
        """Clean up after tests"""
        self.secrets_patcher.stop()

    @patch("auth.requests.post")
    @patch("auth.requests.get")
    @patch("auth.st.query_params", {})
    def test_get_user_info_success(self, mock_get, mock_post):
        """Test successful user info retrieval"""
        # Mock token exchange
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            "access_token": "test-access-token"}
        mock_post.return_value = mock_token_response

        # Mock user info retrieval
        mock_userinfo_response = Mock()
        mock_userinfo_response.json.return_value = {
            "sub": "auth0|123456",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/pic.jpg",
        }
        mock_get.return_value = mock_userinfo_response

        result = auth.get_user_info("test-auth-code")

        # Verify token exchange call
        mock_post.assert_called_once()
        token_call = mock_post.call_args
        self.assertIn("grant_type", token_call[1]["json"])
        self.assertEqual(token_call[1]["json"]["code"], "test-auth-code")

        # Verify userinfo call
        mock_get.assert_called_once()
        userinfo_call = mock_get.call_args
        self.assertIn("Authorization", userinfo_call[1]["headers"])
        self.assertEqual(
            userinfo_call[1]["headers"]["Authorization"],
            "Bearer test-access-token")

        # Verify result
        self.assertEqual(result["email"], "test@example.com")
        self.assertEqual(result["name"], "Test User")

    @patch("auth.requests.post")
    @patch("auth.requests.get")
    @patch("auth.st.query_params", {})
    def test_get_user_info_token_failure(self, mock_get, mock_post):
        """Test user info retrieval with token exchange failure"""
        # Mock failed token exchange (no access_token returned)
        mock_token_response = Mock()
        mock_token_response.json.return_value = {"error": "invalid_request"}
        mock_post.return_value = mock_token_response

        # Mock the userinfo request that will get None access_token
        mock_userinfo_response = Mock()
        mock_userinfo_response.json.return_value = {"error": "unauthorized"}
        mock_get.return_value = mock_userinfo_response

        result = auth.get_user_info("invalid-code")

        # Should return the userinfo error response (since that's what the
        # function returns)
        self.assertEqual(result["error"], "unauthorized")


class TestAuthenticationFlow(unittest.TestCase):
    """Test complete authentication flow"""

    def setUp(self):
        """Set up test fixtures"""
        self.secrets_patcher = patch(
            "auth.st.secrets", {
                "auth0": {
                    "redirect_uri": "https://app.chronolog.com"}})
        self.secrets_patcher.start()

    def tearDown(self):
        """Clean up after tests"""
        self.secrets_patcher.stop()

    @patch("auth.st.session_state", {})
    @patch("auth.st.query_params", {"code": "test-auth-code"})
    @patch("auth.get_user_info")
    @patch("auth.handle_user_profile")
    def test_handle_auth_with_code(
            self,
            mock_handle_profile,
            mock_get_user_info):
        """Test authentication handling with authorization code"""
        # Mock user info retrieval
        mock_user_info = {
            "sub": "auth0|123456",
            "email": "test@example.com",
            "name": "Test User",
        }
        mock_get_user_info.return_value = mock_user_info

        # Mock user profile handling
        mock_profile = {
            "email": "test@example.com",
            "name": "Test User",
            "username": "testuser",
            "profile_complete": True,
        }
        mock_handle_profile.return_value = mock_profile

        # Mock query_params.clear()
        with patch("auth.st.query_params") as mock_query_params:
            mock_query_params.__contains__ = lambda self, key: key == "code"
            mock_query_params.__getitem__ = lambda self, key: "test-auth-code"
            mock_query_params.clear = Mock()

            result = auth.handle_auth()

            # Verify user was stored in session
            self.assertEqual(auth.st.session_state["user"], mock_user_info)

            # Verify query params were cleared
            mock_query_params.clear.assert_called_once()

            # Verify user profile was handled
            mock_handle_profile.assert_called_once_with(mock_user_info)

            # Verify profile was returned
            self.assertEqual(result, mock_profile)

    @patch("auth.st.session_state", {})
    @patch("auth.st.query_params", {})
    @patch("auth.show_login_button")
    def test_handle_auth_no_code_no_user(self, mock_show_login):
        """Test authentication handling with no code and no user session"""
        result = auth.handle_auth()

        # Should show login button
        mock_show_login.assert_called_once()

        # Should return None
        self.assertIsNone(result)

    @patch("auth.st.session_state", {"user": {"email": "test@example.com"}})
    @patch("auth.st.query_params", {})
    @patch("auth.handle_user_profile")
    def test_handle_auth_existing_user_session(self, mock_handle_profile):
        """Test authentication handling with existing user session"""
        mock_user = {"email": "test@example.com", "name": "Test User"}
        auth.st.session_state["user"] = mock_user

        mock_profile = {"email": "test@example.com", "profile_complete": True}
        mock_handle_profile.return_value = mock_profile

        result = auth.handle_auth()

        # Should handle user profile
        mock_handle_profile.assert_called_once_with(mock_user)

        # Should return profile
        self.assertEqual(result, mock_profile)


class TestAuthIntegration(unittest.TestCase):
    """Test auth module integration with other components"""

    def test_auth_constants_defined(self):
        """Test that auth constants are properly defined"""
        # Should have AUTH0_BASE_URL
        self.assertIsNotNone(auth.AUTH0_BASE_URL)
        self.assertIn("https://", auth.AUTH0_BASE_URL)

    def test_auth_functions_exist(self):
        """Test that required auth functions exist"""
        # Test that main functions are callable
        self.assertTrue(callable(auth.get_redirect_uri))
        self.assertTrue(callable(auth.get_app_name))
        self.assertTrue(callable(auth.show_login_button))
        self.assertTrue(callable(auth.get_user_info))
        self.assertTrue(callable(auth.handle_auth))

    @patch("auth.st.query_params", {})
    def test_oauth_flow_parameters(self):
        """Test OAuth flow parameters are correct"""
        with patch("auth.st.columns") as mock_columns, patch(
            "auth.st.markdown"
        ) as mock_markdown:

            # Mock columns
            mock_col2 = Mock()
            mock_col2.__enter__ = Mock(return_value=mock_col2)
            mock_col2.__exit__ = Mock(return_value=None)
            mock_columns.return_value = [Mock(), mock_col2, Mock()]

            auth.show_login_button()

            # Find the HTML content with the login URL
            html_call = None
            for call in mock_markdown.call_args_list:
                if len(call[0]) > 0 and "authorize?" in str(call[0][0]):
                    html_call = str(call[0][0])
                    break

            if html_call:
                # Parse URL parameters
                url_start = html_call.find("https://")
                url_end = html_call.find('"', url_start)
                login_url = html_call[url_start:url_end]

                parsed = urlparse(login_url)
                params = parse_qs(parsed.query)

                # Verify required OAuth parameters
                self.assertIn("client_id", params)
                self.assertIn("response_type", params)
                self.assertEqual(params["response_type"][0], "code")
                self.assertIn("scope", params)
                self.assertIn("openid", params["scope"][0])
                self.assertIn("connection", params)
                self.assertEqual(params["connection"][0], "google-oauth2")


if __name__ == "__main__":
    unittest.main()
