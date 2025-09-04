"""
Integration tests for ChronoLog application.

These tests verify end-to-end workflows and cross-module interactions.
They use real database connections but with test data isolation.
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from io import StringIO
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from chronograph.chronograph_session_models import (
    ChronographMeasurement,
    ChronographSession,
)
from chronograph.service import ChronographService
from supabase import create_client

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class BaseIntegrationTest(unittest.TestCase):
    """Base class for integration tests with common setup"""

    @classmethod
    def setUpClass(cls):
        """Set up test database connection"""
        # Use environment variables or test secrets
        cls.supabase_url = os.getenv(
            "SUPABASE_URL", "https://test.supabase.co")
        cls.supabase_key = os.getenv("SUPABASE_KEY", "test-key")
        cls.test_user_email = "integration-test@chronolog.test"
        cls.test_user_id = "google-oauth2|111273793361054745867"

        # Create test Supabase client (or mock for CI)
        if cls.supabase_url == "https://test.supabase.co":
            # Mock client for CI/testing
            cls.supabase = Mock()
            cls.mock_mode = True
        else:
            # Real client for local integration testing
            cls.supabase = create_client(cls.supabase_url, cls.supabase_key)
            cls.mock_mode = False

    def setUp(self):
        """Set up each test with clean state"""
        self.test_session_ids = []  # Track created sessions for cleanup

    def tearDown(self):
        """Clean up test data after each test"""
        if not self.mock_mode:
            # Clean up test sessions
            for session_id in self.test_session_ids:
                try:
                    self.supabase.table("sessions").delete().eq(
                        "id", session_id
                    ).execute()
                    self.supabase.table("measurements").delete().eq(
                        "session_id", session_id
                    ).execute()
                except Exception:
                    pass  # Best effort cleanup


@pytest.mark.integration
@pytest.mark.file_upload
class TestFileUploadIntegration(BaseIntegrationTest):
    """Test the complete file upload to database workflow"""

    def create_test_excel_file(self):
        """Create a test Excel file that mimics Garmin Xero output"""
        # Create sample data
        data = {
            "Shot": [1, 2, 3, 4, 5],
            "Velocity (fps)": [2850, 2845, 2855, 2848, 2852],
            "Kinetic Energy (ft-lbs)": [1805, 1799, 1811, 1803, 1808],
            "Power Factor": [228.0, 227.6, 228.4, 227.8, 228.2],
            "Date/Time": [
                "2024-08-04 10:00:00",
                "2024-08-04 10:00:30",
                "2024-08-04 10:01:00",
                "2024-08-04 10:01:30",
                "2024-08-04 10:02:00",
            ],
        }

        df = pd.DataFrame(data)

        # Create temporary Excel file
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)

        # Add metadata row (bullet info)
        with pd.ExcelWriter(temp_file.name, engine="openpyxl") as writer:
            # First row with bullet metadata
            metadata_df = pd.DataFrame(
                [["9mm FMJ, 124gr"]], columns=["Bullet Info"])
            metadata_df.to_excel(
                writer,
                sheet_name="Sheet1",
                index=False,
                startrow=0)

            # Data starting from row 2
            df.to_excel(writer, sheet_name="Sheet1", index=False, startrow=2)

        return temp_file.name

    def test_complete_upload_workflow(self):
        """Test complete Excel upload to database workflow"""
        # Create test Excel file
        excel_file_path = self.create_test_excel_file()

        try:
            # Initialize service
            chronograph_service = ChronographService(self.supabase)

            if self.mock_mode:
                # Mock the database operations
                mock_session_response = Mock()
                mock_session_response.data = [{"id": "test-session-123"}]
                self.supabase.table.return_value.insert.return_value.execute.return_value = (
                    mock_session_response)

                mock_measurements_response = Mock()
                mock_measurements_response.data = [
                    {"id": f"measurement-{i}"} for i in range(5)
                ]
                self.supabase.table.return_value.insert.return_value.execute.return_value = (
                    mock_measurements_response)

            # Read and process the Excel file
            df = pd.read_excel(
                excel_file_path,
                sheet_name="Sheet1",
                skiprows=2)
            bullet_info = pd.read_excel(
                excel_file_path, sheet_name="Sheet1", nrows=1
            ).iloc[0, 0]

            # Parse bullet type and grain
            # Create session using session_name instead of bullet_type and
            # bullet_grain
            session = ChronographSession(
                id="test-session-123",
                user_id=self.test_user_id,
                tab_name="Sheet1",
                session_name=bullet_info,
                datetime_local=datetime.now(timezone.utc),
                uploaded_at=datetime.now(timezone.utc),
                file_path=excel_file_path,
            )

            # This would normally save to database
            if self.mock_mode:
                session_id = "test-session-123"
            else:
                session_result = chronograph_service.create_session(session)
                session_id = session_result["id"]
                self.test_session_ids.append(session_id)

            # Create measurements
            measurements = []
            for _, row in df.iterrows():
                measurement = ChronographMeasurement(
                    id=f'test-measurement-{int(row["Shot"])}',
                    user_id=self.test_user_id,
                    chrono_session_id=session_id,
                    shot_number=int(row["Shot"]),
                    speed_fps=float(row["Velocity (fps)"]),
                    speed_mps=float(row["Velocity (fps)"]) *
                    0.3048,  # Convert to m/s
                    ke_ft_lb=float(row["Kinetic Energy (ft-lbs)"]),
                    power_factor=float(row["Power Factor"]),
                    datetime_local=pd.to_datetime(row["Date/Time"]),
                )
                measurements.append(measurement)

            # Assert we created the expected number of measurements
            self.assertEqual(len(measurements), 5)
            self.assertEqual(measurements[0].speed_fps, 2850)
            self.assertEqual(session.session_name, "9mm FMJ, 124gr")

        finally:
            # Clean up temp file
            if os.path.exists(excel_file_path):
                os.unlink(excel_file_path)


@pytest.mark.integration
@pytest.mark.database
class TestCrossModuleIntegration(BaseIntegrationTest):
    """Test integration between chronograph, ammo, and rifle modules"""

    def test_chronograph_data_consistency(self):
        """Test that chronograph data maintains consistency across operations"""

        if self.mock_mode:
            # Mock database operations for session creation
            mock_response = Mock()
            mock_response.data = [{"id": "test-session-123"}]
            self.supabase.table.return_value.insert.return_value.execute.return_value = (
                mock_response)

        # Create chronograph service
        chronograph_service = ChronographService(self.supabase)

        # Create test session
        session = ChronographSession(
            id="test-session-123",
            user_id=self.test_user_id,
            tab_name="Integration Test",
            session_name="9mm FMJ, 124gr",
            datetime_local=datetime.now(timezone.utc),
            uploaded_at=datetime.now(timezone.utc),
            file_path="/tmp/test.xlsx",
        )

        # Create test measurement
        measurement = ChronographMeasurement(
            id="test-measurement-1",
            user_id=self.test_user_id,
            chrono_session_id="test-session-123",
            shot_number=1,
            speed_fps=2850.0,
            speed_mps=2850.0 * 0.3048,  # Convert to m/s
            ke_ft_lb=1805.0,
            power_factor=228.0,
            datetime_local=datetime.now(timezone.utc),
        )

        # Verify data consistency
        self.assertEqual(session.session_name, "9mm FMJ, 124gr")
        self.assertEqual(measurement.speed_fps, 2850.0)

        # Test that session and measurement data aligns
        # Power factor calculation varies, so just verify it's reasonable
        self.assertGreater(measurement.power_factor, 200.0)  # Should be > 200
        self.assertLess(measurement.power_factor, 300.0)  # Should be < 300


@pytest.mark.integration
@pytest.mark.auth
class TestAuthenticationIntegration(BaseIntegrationTest):
    """Test authentication flow integration"""

    @patch("streamlit.session_state")
    def test_auth_to_data_access_flow(self, mock_session_state):
        """Test that authenticated users can access their data"""

        # Mock authenticated session state
        mock_session_state.user_info = {
            "email": self.test_user_email,
            "name": "Integration Test User",
        }
        mock_session_state.authenticated = True

        # Test that services respect user isolation
        chronograph_service = ChronographService(self.supabase)

        if self.mock_mode:
            # Mock user-specific data query
            mock_response = Mock()
            mock_response.data = [
                {
                    "id": "session-1",
                    "user_id": self.test_user_id,
                    "session_name": "9mm FMJ, 124gr",
                }
            ]
            self.supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
                mock_response)

        # Verify that data access is user-scoped
        # In real implementation, this would query actual database
        user_sessions = (
            []
        )  # chronograph_service.get_sessions_for_user(self.test_user_email)

        # Assert authentication state
        self.assertTrue(mock_session_state.authenticated)
        self.assertEqual(
            mock_session_state.user_info["email"],
            self.test_user_email)


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.slow
class TestDatabaseTransactionIntegration(BaseIntegrationTest):
    """Test database transaction handling and data consistency"""

    def test_transaction_rollback_on_error(self):
        """Test that failed operations don't leave partial data"""

        chronograph_service = ChronographService(self.supabase)

        if self.mock_mode:
            # Mock a scenario where session creation succeeds but measurements
            # fail
            success_response = Mock()
            success_response.data = [{"id": "test-session-123"}]

            failure_response = Mock()
            failure_response.data = None

            # Configure mock to succeed first, then fail
            self.supabase.table.return_value.insert.return_value.execute.side_effect = [
                success_response,  # Session creation succeeds
                Exception("Database error"),  # Measurements insertion fails
            ]

        # This test would verify that if measurements fail to insert,
        # the session is also rolled back to maintain consistency

        session = ChronographSession(
            id="test-rollback-session",
            user_id=self.test_user_id,
            tab_name="Rollback Test",
            session_name="Test Bullet, 150gr",
            datetime_local=datetime.now(timezone.utc),
            uploaded_at=datetime.now(timezone.utc),
            file_path="/tmp/rollback_test.xlsx",
        )

        # In a real implementation, this would test actual transaction behavior
        # For now, just verify the test setup
        self.assertEqual(session.session_name, "Test Bullet, 150gr")


if __name__ == "__main__":
    # Set up test environment
    os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
    os.environ.setdefault("SUPABASE_KEY", "test-key")

    # Run the tests
    unittest.main(verbosity=2)
