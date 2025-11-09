"""
Integration tests for Garmin file import validation.

These tests verify that Garmin Excel files are correctly imported and
the data is accurately written to the database tables.

Run with: python -m pytest chronograph/test_garmin_import_integration.py -v -m integration
"""

import os
import sys
import unittest
from datetime import datetime
from io import BytesIO
from typing import List
from unittest.mock import Mock

import pandas as pd
import pytest

from supabase import create_client

# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chronograph import ChronographAPI
from chronograph.garmin_import import GarminExcelProcessor
from chronograph.service import ChronographService
from chronograph.unit_mapping_service import UnitMappingService


class BaseGarminImportIntegrationTest(unittest.TestCase):
    """Base class for Garmin import integration tests with common setup"""

    @classmethod
    def setUpClass(cls):
        """Set up test database connection"""
        # Use environment variables for Supabase connection
        cls.supabase_url = os.getenv(
            "SUPABASE_URL", "https://qnzioartedlrithdxszx.supabase.co"
        )
        cls.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "test-key")
        # Use existing test user ID that's in the users table
        cls.test_user_id = "google-oauth2|111273793361054745867"
        cls.test_user_email = "johnduffie91@gmail.com"

        # Create Supabase client (or mock for CI)
        if cls.supabase_key == "test-key":
            # Mock client for CI/testing without credentials
            cls.supabase = Mock()
            cls.mock_mode = True
        else:
            # Real client for local integration testing
            cls.supabase = create_client(cls.supabase_url, cls.supabase_key)
            cls.mock_mode = False

        # Initialize services
        cls.chrono_service = ChronographService(cls.supabase)
        cls.unit_mapping_service = UnitMappingService(cls.supabase)
        cls.chrono_api = ChronographAPI(cls.supabase)

    def setUp(self):
        """Set up each test with clean state"""
        self.test_session_ids: List[str] = []  # Track created sessions for cleanup

    def tearDown(self):
        """Clean up test data after each test"""
        if not self.mock_mode:
            # Clean up test sessions (measurements will cascade delete)
            for session_id in reversed(self.test_session_ids):
                try:
                    # Delete session by deleting directly from database
                    self.supabase.table("chrono_sessions").delete().eq(
                        "id", session_id
                    ).execute()
                except Exception as e:
                    print(
                        f"Cleanup warning: Could not delete session {session_id}: {e}"
                    )


@pytest.mark.integration
@pytest.mark.database
class TestGarminFileImportValidation(BaseGarminImportIntegrationTest):
    """Test Garmin Excel file import accuracy against real database"""

    def test_garmin_excel_import_accuracy(self):
        """Validate that PhilSessions.xlsx imports correctly to database"""
        if self.mock_mode:
            self.skipTest("Skipping integration test in mock mode")

        # 1. Load test file
        test_file_path = os.path.join(
            os.path.dirname(__file__), "garmin", "PhilSessions.xlsx"
        )

        if not os.path.exists(test_file_path):
            self.skipTest(f"Test file not found: {test_file_path}")

        # 2. Read expected data from Excel
        excel_data = pd.read_excel(test_file_path, sheet_name=None)  # Load all sheets

        # 3. Create file-like object that mimics Streamlit UploadedFile
        with open(test_file_path, "rb") as f:
            file_bytes = f.read()

        # Create a proper file-like object for pandas/zipfile
        class MockUploadedFile:
            """Mock Streamlit UploadedFile with full file-like interface"""
            def __init__(self, file_bytes, name):
                self._bytes = file_bytes
                self.name = name
                self._stream = BytesIO(file_bytes)

            def getvalue(self):
                return self._bytes

            def read(self, size=-1):
                return self._stream.read(size)

            def seek(self, offset, whence=0):
                return self._stream.seek(offset, whence)

            def tell(self):
                return self._stream.tell()

            def seekable(self):
                return self._stream.seekable()

            def readable(self):
                return self._stream.readable()

            def writable(self):
                return self._stream.writable()

        mock_uploaded_file = MockUploadedFile(file_bytes, "PhilSessions.xlsx")

        # 4. Create user dict for import
        user = {
            "id": self.test_user_id,
            "email": self.test_user_email
        }

        # 5. Process the file through GarminExcelProcessor
        processor = GarminExcelProcessor(self.unit_mapping_service, self.chrono_service)

        # Mock file path (not actually uploading to storage in this test)
        file_path = f"{user['email']}/garmin/PhilSessions.xlsx"

        # Process Excel
        processor.process_garmin_excel(mock_uploaded_file, user, file_path)

        # 6. Query database for created sessions
        sessions = self.chrono_service.get_sessions_for_user(user["id"])

        # Track for cleanup
        self.test_session_ids = [s.id for s in sessions if "PhilSessions" in (s.file_path or "")]

        # 7. Validate session data
        self.assertGreater(len(sessions), 0, "No sessions were created from import")

        # Get one session to validate in detail
        test_session_id = sessions[0].id
        # Re-fetch session to get updated statistics (calculated after all measurements saved)
        test_session = self.chrono_service.get_session_by_id(test_session_id, user["id"])

        self.assertIsNotNone(test_session.tab_name, "Session tab_name should not be None")
        self.assertIsNotNone(test_session.datetime_local, "Session datetime_local should not be None")

        # 8. Validate measurements for the session
        measurements = self.chrono_service.get_measurements_for_session(user["id"], test_session.id)

        self.assertGreater(len(measurements), 0, "No measurements were created for session")

        # 9. Validate statistics were calculated
        self.assertIsNotNone(test_session.shot_count, "shot_count should be calculated")
        self.assertEqual(test_session.shot_count, len(measurements), "shot_count should match measurement count")

        if test_session.avg_speed_mps is not None:
            # Validate average calculation
            measured_speeds = [m.speed_mps for m in measurements if m.speed_mps is not None]
            if measured_speeds:
                expected_avg = sum(measured_speeds) / len(measured_speeds)
                self.assertAlmostEqual(
                    test_session.avg_speed_mps,
                    expected_avg,
                    places=1,
                    msg="avg_speed_mps should match calculated average"
                )

                # Validate min/max
                if test_session.min_speed_mps is not None:
                    self.assertAlmostEqual(
                        test_session.min_speed_mps,
                        min(measured_speeds),
                        places=1,
                        msg="min_speed_mps should match minimum speed"
                    )

                if test_session.max_speed_mps is not None:
                    self.assertAlmostEqual(
                        test_session.max_speed_mps,
                        max(measured_speeds),
                        places=1,
                        msg="max_speed_mps should match maximum speed"
                    )

        # 10. Validate shot numbers are sequential
        shot_numbers = sorted([m.shot_number for m in measurements if m.shot_number is not None])
        if shot_numbers:
            self.assertEqual(shot_numbers[0], 1, "First shot should be numbered 1")
            self.assertEqual(
                shot_numbers[-1],
                len(shot_numbers),
                "Last shot number should equal total count"
            )

    def test_duplicate_session_handling_on_reimport(self):
        """Verify duplicate sessions are skipped when re-importing same file"""
        if self.mock_mode:
            self.skipTest("Skipping integration test in mock mode")

        # 1. Load test file
        test_file_path = os.path.join(
            os.path.dirname(__file__), "garmin", "PhilSessions.xlsx"
        )

        if not os.path.exists(test_file_path):
            self.skipTest(f"Test file not found: {test_file_path}")

        # 2. Create file-like object that mimics Streamlit UploadedFile
        with open(test_file_path, "rb") as f:
            file_bytes = f.read()

        # Create a proper file-like object for pandas/zipfile
        class MockUploadedFile:
            """Mock Streamlit UploadedFile with full file-like interface"""
            def __init__(self, file_bytes, name):
                self._bytes = file_bytes
                self.name = name
                self._stream = BytesIO(file_bytes)

            def getvalue(self):
                return self._bytes

            def read(self, size=-1):
                return self._stream.read(size)

            def seek(self, offset, whence=0):
                return self._stream.seek(offset, whence)

            def tell(self):
                return self._stream.tell()

            def seekable(self):
                return self._stream.seekable()

            def readable(self):
                return self._stream.readable()

            def writable(self):
                return self._stream.writable()

        mock_uploaded_file = MockUploadedFile(file_bytes, "PhilSessions.xlsx")

        user = {
            "id": self.test_user_id,
            "email": self.test_user_email
        }

        file_path = f"{user['email']}/garmin/PhilSessions.xlsx"

        # 3. First import
        processor = GarminExcelProcessor(self.unit_mapping_service, self.chrono_service)
        processor.process_garmin_excel(mock_uploaded_file, user, file_path)

        # Get created sessions
        sessions_after_first = self.chrono_service.get_sessions_for_user(user["id"])
        first_session_ids = {s.id for s in sessions_after_first if "PhilSessions" in (s.file_path or "")}

        self.test_session_ids.extend(list(first_session_ids))

        # Get measurement counts
        first_measurement_counts = {}
        for session_id in first_session_ids:
            measurements = self.chrono_service.get_measurements_for_session(user["id"], session_id)
            first_measurement_counts[session_id] = len(measurements)

        # 4. Second import (simulate re-upload of same file)
        mock_uploaded_file.seek(0)  # Reset file pointer
        processor.process_garmin_excel(mock_uploaded_file, user, file_path)

        # Get sessions after re-import
        sessions_after_second = self.chrono_service.get_sessions_for_user(user["id"])
        second_session_ids = {s.id for s in sessions_after_second if "PhilSessions" in (s.file_path or "")}

        # 5. Validate: Session IDs should be identical (no duplicates created)
        self.assertEqual(
            first_session_ids,
            second_session_ids,
            "Re-import should not create duplicate sessions"
        )

        # 6. Validate: Measurement counts should be identical (no duplicate measurements)
        for session_id in second_session_ids:
            measurements = self.chrono_service.get_measurements_for_session(user["id"], session_id)
            self.assertEqual(
                len(measurements),
                first_measurement_counts.get(session_id, 0),
                f"Re-import should not duplicate measurements for session {session_id}"
            )


if __name__ == "__main__":
    unittest.main()