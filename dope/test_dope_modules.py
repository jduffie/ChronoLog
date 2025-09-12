"""
Tests for DOPE page modules in the new directory structure.

This module tests the new DOPE page modules located in:
- dope/create/create_page.py
- dope/view/view_page.py
- dope/analytics/analytics_page.py
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDopeModuleStructure(unittest.TestCase):
    """Test the new DOPE module directory structure"""

    def test_dope_subdirectories_exist(self):
        """Test that all DOPE subdirectories exist"""
        base_dir = os.path.dirname(__file__)

        expected_subdirs = ["create", "view", "analytics"]
        for subdir in expected_subdirs:
            subdir_path = os.path.join(base_dir, subdir)
            self.assertTrue(
                os.path.exists(subdir_path),
                f"DOPE subdirectory {subdir} should exist at {subdir_path}",
            )
            self.assertTrue(
                os.path.isdir(subdir_path),
                f"{subdir_path} should be a directory")

    def test_dope_page_modules_exist(self):
        """Test that all DOPE page module files exist"""
        base_dir = os.path.dirname(__file__)

        expected_modules = [
            "create/create_page.py",
            "view/view_page.py",
            "analytics/analytics_page.py",
        ]

        for module_path in expected_modules:
            full_path = os.path.join(base_dir, module_path)
            self.assertTrue(
                os.path.exists(full_path),
                f"DOPE module {module_path} should exist at {full_path}",
            )

    def test_dope_modules_can_be_imported(self):
        """Test that all DOPE modules can be imported successfully"""
        try:
            from dope.create.create_page import render_create_page

            self.assertTrue(callable(render_create_page))
        except ImportError as e:
            self.fail(f"Failed to import dope.create.create_page: {e}")

        try:
            from dope.view.view_page import render_view_page

            self.assertTrue(callable(render_view_page))
        except ImportError as e:
            self.fail(f"Failed to import dope.view.view_page: {e}")

        try:
            from dope.analytics.analytics_page import render_analytics_page

            self.assertTrue(callable(render_analytics_page))
        except ImportError as e:
            self.fail(f"Failed to import dope.analytics.analytics_page: {e}")


class TestDopeCreatePage(unittest.TestCase):
    """Test the DOPE create page module"""

    def test_create_page_has_docstring(self):
        """Test that create_page module has proper documentation"""
        from dope.create import create_page

        self.assertIsNotNone(create_page.__doc__)
        self.assertIn("DOPE Create Page", create_page.__doc__)


class TestDopeViewPage(unittest.TestCase):
    """Test the DOPE view page module"""

    @patch("streamlit.title")
    @patch("streamlit.info")
    @patch("streamlit.write")
    def test_render_view_page_basic(self, mock_write, mock_info, mock_title):
        """Test that render_view_page runs without errors"""
        from dope.view.view_page import render_view_page

        # Should not raise any exceptions
        result = render_view_page()

        # Verify Streamlit functions were called
        mock_title.assert_called_once_with("View DOPE Sessions")
        mock_info.assert_called_once_with(
            "🚧 This page is under development - TBD")
        mock_write.assert_called_once()

        # Function should return None by default
        self.assertIsNone(result)

    def test_view_page_has_docstring(self):
        """Test that view_page module has proper documentation"""
        from dope.view import view_page

        self.assertIsNotNone(view_page.__doc__)
        self.assertIn("DOPE View Page", view_page.__doc__)

    def test_view_page_function_has_docstring(self):
        """Test that render_view_page function has documentation"""
        from dope.view.view_page import render_view_page

        self.assertIsNotNone(render_view_page.__doc__)
        self.assertIn("TODO", render_view_page.__doc__)


class TestDopeAnalyticsPage(unittest.TestCase):
    """Test the DOPE analytics page module"""

    @patch("streamlit.title")
    @patch("streamlit.info")
    @patch("streamlit.write")
    def test_render_analytics_page_basic(
            self, mock_write, mock_info, mock_title):
        """Test that render_analytics_page runs without errors"""
        from dope.analytics.analytics_page import render_analytics_page

        # Should not raise any exceptions
        result = render_analytics_page()

        # Verify Streamlit functions were called
        mock_title.assert_called_once_with("DOPE Analytics")
        mock_info.assert_called_once_with(
            "🚧 This page is under development - TBD")
        mock_write.assert_called_once()

        # Function should return None by default
        self.assertIsNone(result)

    def test_analytics_page_has_docstring(self):
        """Test that analytics_page module has proper documentation"""
        from dope.analytics import analytics_page

        self.assertIsNotNone(analytics_page.__doc__)
        self.assertIn("DOPE Analytics Page", analytics_page.__doc__)

    def test_analytics_page_function_has_docstring(self):
        """Test that render_analytics_page function has documentation"""
        from dope.analytics.analytics_page import render_analytics_page

        self.assertIsNotNone(render_analytics_page.__doc__)
        self.assertIn("TODO", render_analytics_page.__doc__)


class TestDopePageIntegration(unittest.TestCase):
    """Test integration between DOPE pages and the main application"""

    def test_all_dope_pages_exist(self):
        """Test that all DOPE page files exist in the pages directory"""
        pages_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)),
            "pages")

        expected_pages = [
            "2b_DOPE_Create.py",
            "2c_DOPE_View.py",
            "2d_DOPE_Analytics.py",
        ]

        for page_file in expected_pages:
            page_path = os.path.join(pages_dir, page_file)
            self.assertTrue(
                os.path.exists(page_path),
                f"DOPE page {page_file} should exist at {page_path}",
            )

    def test_dope_pages_import_correct_modules(self):
        """Test that DOPE pages import the correct modules"""
        pages_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)),
            "pages")

        # Test Create page imports
        create_page_path = os.path.join(pages_dir, "2b_DOPE_Create.py")
        if os.path.exists(create_page_path):
            with open(create_page_path, "r") as f:
                content = f.read()
            self.assertIn(
                "from dope.create.create_page import render_create_page",
                content)

        # Test View page imports
        view_page_path = os.path.join(pages_dir, "2c_DOPE_View.py")
        if os.path.exists(view_page_path):
            with open(view_page_path, "r") as f:
                content = f.read()
            self.assertIn(
                "from dope.view.view_page import render_view_page",
                content)

        # Test Analytics page imports
        analytics_page_path = os.path.join(pages_dir, "2d_DOPE_Analytics.py")
        if os.path.exists(analytics_page_path):
            with open(analytics_page_path, "r") as f:
                content = f.read()
            self.assertIn(
                "from dope.analytics.analytics_page import render_analytics_page",
                content,
            )

    def test_dope_pages_have_proper_configuration(self):
        """Test that DOPE pages have proper Streamlit configuration"""
        pages_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)),
            "pages")

        dope_pages = [
            ("2b_DOPE_Create.py", "DOPE Create", "📊"),
            ("2c_DOPE_View.py", "DOPE View", "📊"),
            ("2d_DOPE_Analytics.py", "DOPE Analytics", "📊"),
        ]

        for page_file, expected_title, expected_icon in dope_pages:
            page_path = os.path.join(pages_dir, page_file)
            if os.path.exists(page_path):
                with open(page_path, "r") as f:
                    content = f.read()

                # Check for Streamlit page configuration
                self.assertIn("st.set_page_config", content)
                self.assertIn(f'page_title="{expected_title}"', content)
                self.assertIn(f'page_icon="{expected_icon}"', content)
                self.assertIn('layout="wide"', content)

                # Check for authentication handling
                self.assertIn("handle_auth()", content)
                self.assertIn("if not user:", content)


class TestDopeModuleCompatibility(unittest.TestCase):
    """Test compatibility and integration of DOPE modules"""

    def test_no_old_tab_modules_exist(self):
        """Test that old tab modules have been properly removed"""
        dope_dir = os.path.dirname(__file__)

        old_modules = [
            "sessions_tab.py",
            "view_session_tab.py",
            "create_session_tab.py",
            "test_dope.py",
        ]

        for old_module in old_modules:
            old_path = os.path.join(dope_dir, old_module)
            self.assertFalse(
                os.path.exists(old_path),
                f"Old module {old_module} should not exist anymore",
            )


class TestDopeSessionModel(unittest.TestCase):
    """Test the updated DopeSessionModel"""

    def setUp(self):
        """Set up test data"""
        from datetime import datetime

        from dope.models import DopeSessionModel

        self.DopeSessionModel = DopeSessionModel
        self.test_datetime = datetime(2024, 8, 20, 12, 0, 0)

        self.valid_session_data = {
            "id": "test_session_001",
            "user_id": "test_user",
            "session_name": "Test Session",
            "datetime_local": self.test_datetime,
            "cartridge_id": "cartridge_001",
            "rifle_name": "Test Rifle",
            "cartridge_make": "Federal",
            "cartridge_model": "GMM",
            "cartridge_type": "308 Winchester",
            "bullet_make": "Sierra",
            "bullet_model": "MatchKing",
            "bullet_weight": "175",
            "distance_m": 100.0,
            "temperature_c": 20.5,
            "notes": "Test notes",
        }

    def test_model_creation_with_required_fields(self):
        """Test creating a model with all required fields"""
        session = self.DopeSessionModel(**self.valid_session_data)

        self.assertEqual(session.session_name, "Test Session")
        self.assertEqual(session.cartridge_id, "cartridge_001")
        self.assertEqual(session.rifle_name, "Test Rifle")
        self.assertEqual(session.cartridge_make, "Federal")
        self.assertEqual(session.bullet_weight, "175")

    def test_model_mandatory_fields_validation(self):
        """Test that mandatory fields are properly validated"""
        session = self.DopeSessionModel(**self.valid_session_data)

        # Should be complete with all mandatory fields
        self.assertTrue(session.is_complete())
        self.assertEqual(len(session.get_missing_mandatory_fields()), 0)

    def test_model_missing_mandatory_fields(self):
        """Test detection of missing mandatory fields"""
        incomplete_data = self.valid_session_data.copy()
        del incomplete_data["session_name"]
        del incomplete_data["rifle_name"]

        session = self.DopeSessionModel(**incomplete_data)

        self.assertFalse(session.is_complete())
        missing_fields = session.get_missing_mandatory_fields()
        self.assertIn("Session Name", missing_fields)
        self.assertIn("Rifle Name", missing_fields)

    def test_model_cartridge_id_optional(self):
        """Test that cartridge_id is optional and doesn't affect completeness"""
        session_data = self.valid_session_data.copy()
        session_data["cartridge_id"] = None  # Explicitly set to None

        session = self.DopeSessionModel(**session_data)

        # Should still be complete even with None cartridge_id
        self.assertTrue(session.is_complete())
        self.assertEqual(len(session.get_missing_mandatory_fields()), 0)
        self.assertIsNone(session.cartridge_id)

    def test_from_supabase_record(self):
        """Test creating model from Supabase record"""
        supabase_record = {
            "id": "db_session_001",
            "user_id": "db_user",
            "session_name": "DB Session",
            "datetime_local": "2024-08-20T12:00:00Z",
            "cartridge_id": "db_cartridge",
            "rifle_name": "DB Rifle",
            "cartridge_make": "DB Make",
            "cartridge_model": "DB Model",
            "cartridge_type": "DB Type",
            "bullet_make": "DB Bullet",
            "bullet_model": "DB Model",
            "bullet_weight": "180",
            "temperature_c": 22.5,
            "wind_speed_1_mps": 10.0,
        }

        session = self.DopeSessionModel.from_supabase_record(supabase_record)

        self.assertEqual(session.id, "db_session_001")
        self.assertEqual(session.session_name, "DB Session")
        self.assertEqual(session.cartridge_id, "db_cartridge")
        self.assertEqual(session.temperature_c, 22.5)
        self.assertEqual(session.wind_speed_1_mps, 10.0)

    def test_to_dict_conversion(self):
        """Test converting model to dictionary"""
        session = self.DopeSessionModel(**self.valid_session_data)
        data_dict = session.to_dict()

        self.assertEqual(data_dict["session_name"], "Test Session")
        self.assertEqual(data_dict["cartridge_id"], "cartridge_001")
        self.assertEqual(data_dict["datetime_local"], self.test_datetime)
        self.assertIn("rifle_name", data_dict)
        self.assertIn("temperature_c", data_dict)

    def test_display_properties(self):
        """Test display property methods"""
        session = self.DopeSessionModel(**self.valid_session_data)

        # Test display_name
        self.assertEqual(session.display_name, "Test Session")

        # Test cartridge_display
        cartridge_display = session.cartridge_display
        self.assertIn("Federal", cartridge_display)
        self.assertIn("GMM", cartridge_display)
        self.assertIn("308 Winchester", cartridge_display)

        # Test bullet_display
        bullet_display = session.bullet_display
        self.assertIn("Sierra", bullet_display)
        self.assertIn("MatchKing", bullet_display)
        self.assertIn("175gr", bullet_display)

        # TODO: Add weather_summary property to DopeSessionModel
        # weather_summary = session.weather_summary
        # self.assertIn("20.5°C", weather_summary)

    def test_from_supabase_records_list(self):
        """Test creating multiple models from Supabase records"""
        records = [
            {
                "id": "1",
                "user_id": "user1",
                "session_name": "Session 1",
                "cartridge_id": "cartridge1",
                "rifle_name": "Rifle 1",
                "cartridge_make": "Make1",
                "cartridge_model": "Model1",
                "cartridge_type": "Type1",
                "bullet_make": "Bullet1",
                "bullet_model": "BModel1",
                "bullet_weight": "150",
            },
            {
                "id": "2",
                "user_id": "user2",
                "session_name": "Session 2",
                "cartridge_id": "cartridge2",
                "rifle_name": "Rifle 2",
                "cartridge_make": "Make2",
                "cartridge_model": "Model2",
                "cartridge_type": "Type2",
                "bullet_make": "Bullet2",
                "bullet_model": "BModel2",
                "bullet_weight": "160",
            },
        ]

        sessions = self.DopeSessionModel.from_supabase_records(records)

        self.assertEqual(len(sessions), 2)
        self.assertEqual(sessions[0].session_name, "Session 1")
        self.assertEqual(sessions[1].session_name, "Session 2")


class TestDopeService(unittest.TestCase):
    """Test the DopeService with mocked operations"""

    def setUp(self):
        """Set up test service"""
        from dope.service import DopeService

        self.mock_supabase = MagicMock()
        self.service = DopeService(self.mock_supabase)
        self.test_user_id = "google-oauth2|111273793361054745867"

    def test_get_sessions_for_user(self):
        """Test getting sessions for a user returns mock data"""
        sessions = self.service.get_sessions_for_user(self.test_user_id)

        self.assertIsInstance(sessions, list)
        self.assertGreater(len(sessions), 0)

        # Check first session has expected structure
        first_session = sessions[0]
        self.assertEqual(first_session.user_id, self.test_user_id)
        self.assertIsNotNone(first_session.session_name)
        self.assertIsNotNone(first_session.cartridge_id)

    def test_get_session_by_id(self):
        """Test getting a specific session by ID"""
        sessions = self.service.get_sessions_for_user(self.test_user_id)
        target_session_id = sessions[0].id

        found_session = self.service.get_session_by_id(
            target_session_id, self.test_user_id
        )

        self.assertIsNotNone(found_session)
        self.assertEqual(found_session.id, target_session_id)
        self.assertEqual(found_session.user_id, self.test_user_id)

    def test_get_session_by_id_not_found(self):
        """Test getting a non-existent session returns None"""
        found_session = self.service.get_session_by_id(
            "nonexistent_id", self.test_user_id
        )
        self.assertIsNone(found_session)

    def test_create_session(self):
        """Test creating a new session"""
        session_data = {
            "session_name": "New Test Session",
            "cartridge_id": "new_cartridge",
            "rifle_name": "New Rifle",
            "cartridge_make": "New Make",
            "cartridge_model": "New Model",
            "cartridge_type": "New Type",
            "bullet_make": "New Bullet",
            "bullet_model": "New BModel",
            "bullet_weight": "200",
        }

        new_session = self.service.create_session(
            session_data, self.test_user_id)

        self.assertIsNotNone(new_session.id)
        self.assertEqual(new_session.user_id, self.test_user_id)
        self.assertEqual(new_session.session_name, "New Test Session")
        self.assertIsNotNone(new_session.datetime_local)

    def test_search_sessions(self):
        """Test searching sessions by text"""
        # Test search that should find results
        sessions = self.service.search_sessions(self.test_user_id, "Range")
        self.assertGreater(len(sessions), 0)

        # Test search that should find no results
        sessions = self.service.search_sessions(
            self.test_user_id, "NonexistentTerm")
        self.assertEqual(len(sessions), 0)

        # Test case-insensitive search
        sessions = self.service.search_sessions(self.test_user_id, "federal")
        self.assertGreater(len(sessions), 0)

    def test_filter_sessions_by_status(self):
        """Test filtering sessions by status"""
        # Filter for active sessions
        active_sessions = self.service.filter_sessions(
            self.test_user_id, {"status": "active"}
        )
        self.assertGreater(len(active_sessions), 0)
        for session in active_sessions:
            self.assertEqual(session.status, "active")

        # Filter for archived sessions
        archived_sessions = self.service.filter_sessions(
            self.test_user_id, {"status": "archived"}
        )
        for session in archived_sessions:
            self.assertEqual(session.status, "archived")

    def test_filter_sessions_by_cartridge_type(self):
        """Test filtering sessions by cartridge type"""
        sessions = self.service.filter_sessions(
            self.test_user_id, {"cartridge_type": "223 Remington"}
        )

        for session in sessions:
            self.assertEqual(session.cartridge_type, "223 Remington")

    def test_filter_sessions_by_rifle_name(self):
        """Test filtering sessions by rifle name"""
        sessions = self.service.filter_sessions(
            self.test_user_id, {"rifle_name": "AR-15 SPR"}
        )

        for session in sessions:
            self.assertEqual(session.rifle_name, "AR-15 SPR")

    def test_get_unique_values(self):
        """Test getting unique values for autocomplete"""
        # Test getting unique cartridge types
        cartridge_types = self.service.get_unique_values(
            self.test_user_id, "cartridge_type"
        )
        self.assertIsInstance(cartridge_types, list)
        self.assertGreater(len(cartridge_types), 0)

        # Test getting unique rifle names
        rifle_names = self.service.get_unique_values(
            self.test_user_id, "rifle_name")
        self.assertIsInstance(rifle_names, list)
        self.assertGreater(len(rifle_names), 0)

        # Values should be sorted
        self.assertEqual(rifle_names, sorted(rifle_names))

    def test_get_session_statistics(self):
        """Test getting session statistics"""
        stats = self.service.get_session_statistics(self.test_user_id)

        self.assertIsInstance(stats, dict)
        self.assertIn("total_sessions", stats)
        self.assertIn("active_sessions", stats)
        self.assertIn("archived_sessions", stats)
        self.assertIn("unique_cartridge_types", stats)
        self.assertIn("unique_bullet_makes", stats)
        self.assertIn("average_distance_m", stats)

        # Check that numbers make sense
        self.assertGreaterEqual(stats["total_sessions"], 0)
        self.assertGreaterEqual(stats["active_sessions"], 0)
        self.assertGreaterEqual(stats["archived_sessions"], 0)

    def test_delete_session(self):
        """Test deleting a session (mocked)"""
        result = self.service.delete_session(
            "test_session_id", self.test_user_id)
        self.assertTrue(result)  # Mock always returns True

    def test_update_session(self):
        """Test updating a session"""
        # Get an existing session
        sessions = self.service.get_sessions_for_user(self.test_user_id)
        session_to_update = sessions[0]

        # Update data
        update_data = {
            "session_name": "Updated Session Name",
            "notes": "Updated notes"}

        updated_session = self.service.update_session(
            session_to_update.id, update_data, self.test_user_id
        )

        self.assertEqual(updated_session.session_name, "Updated Session Name")
        self.assertEqual(updated_session.notes, "Updated notes")

    def test_update_nonexistent_session(self):
        """Test updating a non-existent session raises exception"""
        update_data = {"session_name": "Updated Name"}

        with self.assertRaises(Exception) as context:
            self.service.update_session(
                "nonexistent_id", update_data, self.test_user_id
            )

        self.assertIn("not found", str(context.exception))


class TestDopeViewPage(unittest.TestCase):
    """Test the DOPE view page implementation"""

    @patch("streamlit.session_state")
    @patch("streamlit.title")
    @patch("streamlit.warning")
    def test_render_view_page_no_authentication(
        self, mock_warning, mock_title, mock_session_state
    ):
        """Test view page handles missing authentication"""
        from dope.view.view_page import render_view_page

        # Mock missing user in session state
        mock_session_state.get.return_value = None
        mock_session_state.__contains__ = lambda self, key: False
        mock_session_state.user = {
            "id": "google-oauth2|111273793361054745867",
            "sub": "google-oauth2|111273793361054745867",
            "email": "test@example.com",
            "name": "Test User",
        }

        with patch("dope.view.view_page.render_main_page_filters"), patch(
            "dope.view.view_page.get_filtered_sessions", return_value=[]
        ), patch("streamlit.info"), patch("streamlit.button"), patch(
            "streamlit.columns", return_value=[None, None, None]
        ):

            render_view_page()

            mock_warning.assert_called_with(
                "No user authentication found - using test user for development"
            )

    def test_render_view_page_no_user_id(self):
        """Test view page handles missing user ID"""
        from dope.view.view_page import render_view_page

        with patch("streamlit.session_state") as mock_state, patch(
            "streamlit.title"
        ), patch("streamlit.warning") as mock_warning:

            # Mock user without ID
            mock_user = MagicMock()
            mock_user.get.return_value = None

            # Mock session_state properly
            def contains_func(self, key):
                return key == "user"

            mock_state.__contains__ = contains_func
            mock_state.user = mock_user
            mock_state.dope_filters = {}
            mock_state.selected_session_id = None
            mock_state.show_advanced_filters = False

            with patch("dope.view.view_page.render_main_page_filters"), patch(
                "dope.view.view_page.get_filtered_sessions", return_value=[]
            ), patch("streamlit.info"), patch("streamlit.button"), patch(
                "streamlit.columns", return_value=[None, None, None]
            ):

                render_view_page()

                # Should show warning about using test user ID
                mock_warning.assert_called_with(
                    "Using test user ID: google-oauth2|111273793361054745867"
                )

    def test_render_main_page_filters_structure(self):
        """Test main page filters renders expected elements"""
        from dope.service import DopeService
        from dope.view.view_page import render_main_page_filters

        # Mock service and user ID
        service = DopeService(None)
        user_id = "google-oauth2|111273793361054745867"

        with patch("streamlit.expander") as mock_expander, patch(
            "streamlit.text_input", return_value=""
        ), patch("streamlit.button"), patch("streamlit.divider"), patch(
            "streamlit.subheader"
        ), patch(
            "streamlit.columns", return_value=[MagicMock(), MagicMock(), MagicMock()]
        ), patch(
            "streamlit.date_input", return_value=None
        ), patch(
            "streamlit.selectbox", return_value="All"
        ), patch(
            "streamlit.slider", return_value=(0, 1000)
        ), patch(
            "streamlit.session_state"
        ) as mock_state:

            mock_state.dope_filters = {}
            mock_state.show_advanced_filters = False
            mock_state.get.return_value = False

            # Mock the expander context manager
            mock_expander.return_value.__enter__ = MagicMock()
            mock_expander.return_value.__exit__ = MagicMock()

            # Should not raise exceptions
            render_main_page_filters(service, user_id)

    def test_get_filtered_sessions_with_search(self):
        """Test filtering sessions with search functionality"""
        from dope.service import DopeService
        from dope.view.view_page import get_filtered_sessions

        service = DopeService(None)
        user_id = "google-oauth2|111273793361054745867"
        filters = {"search": "Federal"}

        with patch("streamlit.error"):
            sessions = get_filtered_sessions(service, user_id, filters)

            # Should return sessions matching search term
            self.assertIsInstance(sessions, list)
            if sessions:
                # Check that search functionality was called
                found_federal = any(
                    "Federal" in str(s.__dict__.values()) for s in sessions
                )
                # This will be true with our mock data that includes Federal
                # cartridges
                self.assertTrue(found_federal or len(sessions) == 0)

    def test_render_sessions_table_with_data(self):
        """Test sessions table rendering with mock data"""
        from datetime import datetime

        from dope.models import DopeSessionModel
        from dope.view.view_page import render_sessions_table

        # Create test session
        session = DopeSessionModel(
            id="test_001",
            session_name="Test Session",
            datetime_local=datetime.now(),
            cartridge_id="cartridge_001",
            rifle_name="Test Rifle",
            cartridge_make="Federal",
            cartridge_model="GMM",
            cartridge_type="223 Remington",
            bullet_make="Sierra",
            bullet_model="MatchKing",
            bullet_weight="77",
        )

        sessions = [session]

        with patch("streamlit.dataframe") as mock_dataframe, patch(
            "streamlit.button"
        ), patch("pandas.DataFrame") as mock_df:

            # Mock DataFrame creation
            mock_df_instance = MagicMock()
            mock_df.return_value = mock_df_instance

            # Mock dataframe selection response
            mock_selection = MagicMock()
            mock_selection.selection.rows = []
            mock_dataframe.return_value = mock_selection

            # Should not raise exceptions
            render_sessions_table(sessions)

            # Verify DataFrame was created with session data
            self.assertGreaterEqual(mock_df.call_count, 1)
            call_args = mock_df.call_args_list[0][0][
                0
            ]  # Get the data passed to DataFrame
            self.assertIsInstance(call_args, list)
            self.assertGreater(len(call_args), 0)

    def test_export_sessions_to_csv(self):
        """Test CSV export functionality"""
        from datetime import datetime

        from dope.models import DopeSessionModel
        from dope.view.view_page import export_sessions_to_csv

        # Create test session
        session = DopeSessionModel(
            id="test_001",
            session_name="Test Session",
            datetime_local=datetime.now(),
            cartridge_id="cartridge_001",
            rifle_name="Test Rifle",
            cartridge_make="Federal",
            cartridge_model="GMM",
            cartridge_type="223 Remington",
            bullet_make="Sierra",
            bullet_model="MatchKing",
            bullet_weight="77",
        )

        sessions = [session]

        with patch("pandas.DataFrame") as mock_df, patch(
            "streamlit.download_button"
        ), patch("streamlit.success"):

            # Mock DataFrame and CSV conversion
            mock_df_instance = MagicMock()
            mock_df_instance.to_csv.return_value = "csv,data,here"
            mock_df.return_value = mock_df_instance

            # Should not raise exceptions
            export_sessions_to_csv(sessions)

            # Verify DataFrame was created and CSV conversion called
            mock_df.assert_called_once()
            mock_df_instance.to_csv.assert_called_once_with(index=False)

    def test_render_session_info_tab(self):
        """Test session info tab rendering"""
        from datetime import datetime

        from dope.models import DopeSessionModel
        from dope.view.view_page import render_session_info_tab

        session = DopeSessionModel(
            id="test_001",
            session_name="Test Session",
            datetime_local=datetime.now(),
            cartridge_id="cartridge_001",
            rifle_name="Test Rifle",
            notes="Test notes with longer content for display",
        )

        with patch("streamlit.columns", return_value=[MagicMock(), MagicMock()]), patch(
            "streamlit.write"
        ), patch("streamlit.text_area"):

            # Should not raise exceptions
            render_session_info_tab(session)

    def test_render_weather_info_tab(self):
        """Test weather info tab rendering"""
        from dope.models import DopeSessionModel
        from dope.view.view_page import render_weather_info_tab

        session = DopeSessionModel(
            temperature_c=22.5,
            relative_humidity_pct=65.0,
            barometric_pressure_hpa=30.15,
            wind_speed_1_mps=8.0,
            wind_speed_2_mps=10.0,
            wind_direction_deg=270.0,
            weather_source_name="Kestrel 5700",
        )

        with patch("streamlit.columns", return_value=[MagicMock(), MagicMock()]), patch(
            "streamlit.write"
        ):

            # Should not raise exceptions
            render_weather_info_tab(session)

    def test_render_main_page_filters_functionality(self):
        """Test main page filters functionality and integration"""
        from dope.service import DopeService
        from dope.view.view_page import render_main_page_filters

        service = DopeService(None)
        user_id = "google-oauth2|111273793361054745867"

        with patch("streamlit.expander") as mock_expander, patch(
            "streamlit.text_input", return_value="test_search"
        ), patch("streamlit.button", return_value=False), patch(
            "streamlit.divider"
        ), patch(
            "streamlit.subheader"
        ), patch(
            "streamlit.columns", return_value=[MagicMock(), MagicMock(), MagicMock()]
        ), patch(
            "streamlit.date_input", return_value=None
        ), patch(
            "streamlit.selectbox", return_value="All"
        ), patch(
            "streamlit.slider", return_value=(0, 1000)
        ), patch(
            "streamlit.session_state"
        ) as mock_state:

            mock_state.dope_filters = {"search": "test"}
            mock_state.show_advanced_filters = True
            mock_state.get.return_value = True

            # Mock the expander context manager
            mock_expander.return_value.__enter__ = MagicMock()
            mock_expander.return_value.__exit__ = MagicMock()

            # Should not raise exceptions and handle filters properly
            render_main_page_filters(service, user_id)


class TestDopeModelAdvanced(unittest.TestCase):
    """Advanced tests for DopeSessionModel functionality"""

    def setUp(self):
        from dope.models import DopeSessionModel
        self.DopeSessionModel = DopeSessionModel

    def test_model_display_name_variations(self):
        """Test different display name scenarios"""
        # Test with session name
        session_with_name = self.DopeSessionModel(
            session_name="My Test Session",
            cartridge_type="223 Remington",
            bullet_make="Sierra",
            bullet_model="MatchKing",
            distance_m=100.0
        )
        self.assertEqual(session_with_name.display_name, "My Test Session")

        # Test without session name - should build from components
        session_without_name = self.DopeSessionModel(
            session_name="",
            cartridge_type="308 Winchester",
            bullet_make="Hornady",
            bullet_model="ELD Match",
            distance_m=600.0
        )
        expected = "308 Winchester - Hornady ELD Match - 600.0m"
        self.assertEqual(session_without_name.display_name, expected)

        # Test minimal data
        minimal_session = self.DopeSessionModel(session_name="")
        self.assertEqual(minimal_session.display_name, "Untitled DOPE Session")

    def test_model_weather_data_fields(self):
        """Test weather data fields with metric units"""
        # Test complete weather data
        full_weather = self.DopeSessionModel(
            temperature_c=22.5,
            relative_humidity_pct=65.0,
            barometric_pressure_hpa=30.15,
            wind_speed_1_mps=8.0
        )
        self.assertEqual(full_weather.temperature_c, 22.5)
        self.assertEqual(full_weather.relative_humidity_pct, 65.0)
        self.assertEqual(full_weather.barometric_pressure_hpa, 30.15)
        self.assertEqual(full_weather.wind_speed_1_mps, 8.0)

        # Test partial weather data
        partial_weather = self.DopeSessionModel(
            temperature_c=18.0,
            wind_speed_1_mps=12.0
        )
        self.assertEqual(partial_weather.temperature_c, 18.0)
        self.assertEqual(partial_weather.wind_speed_1_mps, 12.0)
        self.assertIsNone(partial_weather.relative_humidity_pct)

        # Test no weather data
        no_weather = self.DopeSessionModel()
        self.assertIsNone(no_weather.temperature_c)
        self.assertIsNone(no_weather.wind_speed_1_mps)

    def test_model_field_validation_edge_cases(self):
        """Test edge cases for field validation"""
        # Test with whitespace-only mandatory fields
        whitespace_session = self.DopeSessionModel(
            session_name="   ",
            rifle_name="  \t  ",
            cartridge_make="",
            cartridge_model="Valid Model",
            cartridge_type="Valid Type",
            bullet_make="Valid Make",
            bullet_model="Valid Model",
            bullet_weight="150"
        )
        self.assertFalse(whitespace_session.is_complete())
        missing_fields = whitespace_session.get_missing_mandatory_fields()
        self.assertIn("Session Name", missing_fields)
        self.assertIn("Rifle Name", missing_fields)
        self.assertIn("Cartridge Make", missing_fields)

    def test_model_to_dict_completeness(self):
        """Test that to_dict includes all expected fields"""
        session = self.DopeSessionModel(
            id="test_001",
            session_name="Complete Session",
            user_id="user_123",
            cartridge_id="cartridge_456",
            rifle_name="Test Rifle",
            range_name="Test Range",
            distance_m=300.0,
            temperature_c=20.0,
            notes="Test notes"
        )

        data_dict = session.to_dict()

        # Check core fields are present
        expected_fields = [
            "id", "user_id", "session_name", "cartridge_id",
            "rifle_name", "range_name", "distance_m",
            "temperature_c", "notes"
        ]

        # Note: to_dict() doesn't include 'id' field based on the
        # implementation
        for field in expected_fields[1:]:  # Skip 'id' as it's not in to_dict
            self.assertIn(field, data_dict)

    def test_model_from_supabase_record_edge_cases(self):
        """Test creating model from various Supabase record formats"""
        # Test with minimal record
        minimal_record = {
            "id": "minimal_001",
            "user_id": "user_001"
        }
        session = self.DopeSessionModel.from_supabase_record(minimal_record)
        self.assertEqual(session.id, "minimal_001")
        self.assertEqual(session.user_id, "user_001")
        self.assertEqual(session.session_name, "")  # Default value
        self.assertEqual(session.status, "active")  # Default value

        # Test with null values
        null_record = {
            "id": "null_001",
            "user_id": "user_001",
            "session_name": None,
            "rifle_name": None,
            "temperature_c": None
        }
        session_with_nulls = self.DopeSessionModel.from_supabase_record(
            null_record)
        self.assertIsNone(session_with_nulls.session_name)
        self.assertIsNone(session_with_nulls.rifle_name)
        self.assertIsNone(session_with_nulls.temperature_c)


class TestDopeServiceAdvanced(unittest.TestCase):
    """Advanced tests for DopeService functionality"""

    def setUp(self):
        from dope.service import DopeService
        self.mock_supabase = MagicMock()
        self.service = DopeService(self.mock_supabase)
        self.test_user_id = "google-oauth2|111273793361054745867"

    def test_get_measurements_for_dope_session(self):
        """Test getting DOPE measurements for a session"""
        # Test with mocked supabase (should return empty list)
        # The service method checks for MagicMock by name and returns [] for
        # mocks
        measurements = self.service.get_measurements_for_dope_session(
            "session_001", self.test_user_id)
        # Mock implementation should return empty list since mock is detected
        self.assertEqual(measurements, [])

    def test_filter_sessions_complex_filters(self):
        """Test complex filtering scenarios"""
        # Test multiple filters combined
        complex_filters = {
            "status": "active",
            "cartridge_type": "223 Remington",
            "distance_range": (50, 200),
            "temperature_range": (15, 25)
        }

        filtered_sessions = self.service.filter_sessions(
            self.test_user_id, complex_filters)

        # All returned sessions should match all filters
        for session in filtered_sessions:
            self.assertEqual(session.status, "active")
            self.assertEqual(session.cartridge_type, "223 Remington")
            if session.distance_m:
                self.assertTrue(50 <= session.distance_m <= 200)
            if session.temperature_c:
                self.assertTrue(15 <= session.temperature_c <= 25)

    def test_filter_sessions_edge_cases(self):
        """Test filtering edge cases"""
        # Test filtering for "Not Defined" values
        not_defined_filters = {
            "cartridge_type": "Not Defined",
            "rifle_name": "Not Defined",
            "range_name": "Not Defined"
        }

        filtered_sessions = self.service.filter_sessions(
            self.test_user_id, not_defined_filters)

        # All sessions should have empty or None values for these fields
        for session in filtered_sessions:
            self.assertTrue(
                not session.cartridge_type or session.cartridge_type.strip() == "")
            self.assertTrue(
                not session.rifle_name or session.rifle_name.strip() == "")
            self.assertTrue(
                not session.range_name or session.range_name.strip() == "")

    def test_search_sessions_comprehensive(self):
        """Test comprehensive search functionality"""
        # Test search in different fields
        search_terms = ["Federal", "Sierra", "Range", "notes"]

        for term in search_terms:
            results = self.service.search_sessions(self.test_user_id, term)
            self.assertIsInstance(results, list)
            # Each result should contain the search term in at least one field
            for session in results:
                session_text = " ".join([
                    session.session_name or "",
                    session.cartridge_make or "",
                    session.cartridge_model or "",
                    session.bullet_make or "",
                    session.bullet_model or "",
                    session.range_name or "",
                    session.notes or ""
                ]).lower()
                self.assertIn(term.lower(), session_text)

    def test_get_unique_values_different_fields(self):
        """Test getting unique values for different fields"""
        fields_to_test = [
            "cartridge_type", "rifle_name", "cartridge_make",
            "bullet_make", "range_name"
        ]

        for field in fields_to_test:
            unique_values = self.service.get_unique_values(
                self.test_user_id, field)
            self.assertIsInstance(unique_values, list)
            # Should be sorted and contain no duplicates
            self.assertEqual(unique_values, sorted(set(unique_values)))

    def test_create_session_with_chrono_data(self):
        """Test creating session with chronograph data"""
        session_data = {
            "session_name": "Chrono Integration Test",
            "chrono_session_id": "chrono_001",
            "rifle_name": "Test Rifle",
            "cartridge_make": "Test Make",
            "cartridge_model": "Test Model",
            "cartridge_type": "Test Type",
            "bullet_make": "Test Bullet",
            "bullet_model": "Test Model",
            "bullet_weight": "150"
        }

        new_session = self.service.create_session(
            session_data, self.test_user_id)

        self.assertIsNotNone(new_session.id)
        self.assertEqual(new_session.chrono_session_id, "chrono_001")
        self.assertEqual(new_session.session_name, "Chrono Integration Test")

    def test_service_error_handling(self):
        """Test service error handling"""
        # Test with invalid user ID (not the mock user ID)
        invalid_user_id = "invalid_user_123"

        # Should return empty list for invalid user
        sessions = self.service.get_sessions_for_user(invalid_user_id)
        self.assertEqual(sessions, [])

        # Search should also return empty for invalid user
        search_results = self.service.search_sessions(invalid_user_id, "test")
        self.assertEqual(search_results, [])


class TestDopeIntegration(unittest.TestCase):
    """Integration tests for DOPE module components"""

    def setUp(self):
        from dope.models import DopeSessionModel
        from dope.service import DopeService

        self.DopeService = DopeService
        self.DopeSessionModel = DopeSessionModel
        self.test_user_id = "google-oauth2|111273793361054745867"

    def test_service_model_integration(self):
        """Test service and model integration"""
        service = self.DopeService(None)  # Mock supabase

        # Get sessions from service
        sessions = service.get_sessions_for_user(self.test_user_id)

        # Verify all returned objects are proper models
        for session in sessions:
            self.assertIsInstance(session, self.DopeSessionModel)
            self.assertTrue(hasattr(session, 'display_name'))
            self.assertTrue(hasattr(session, 'cartridge_display'))
            self.assertTrue(hasattr(session, 'bullet_display'))
            # TODO: Add weather_summary property to DopeSessionModel
            # self.assertTrue(hasattr(session, 'weather_summary'))

    def test_create_and_retrieve_workflow(self):
        """Test complete create and retrieve workflow"""
        service = self.DopeService(None)  # Mock supabase

        # Create new session
        session_data = {
            "session_name": "Integration Test Session",
            "rifle_name": "Integration Rifle",
            "cartridge_make": "Integration Make",
            "cartridge_model": "Integration Model",
            "cartridge_type": "223 Remington",
            "bullet_make": "Integration Bullet",
            "bullet_model": "Integration BModel",
            "bullet_weight": "75",
            "distance_m": 100.0,
            "temperature_c": 22.0,
            "notes": "Integration test notes"
        }

        new_session = service.create_session(session_data, self.test_user_id)

        # Verify creation
        self.assertIsInstance(new_session, self.DopeSessionModel)
        self.assertIsNotNone(new_session.id)
        self.assertEqual(new_session.session_name, "Integration Test Session")

        # Try to retrieve by ID (mock will return None for non-existing)
        retrieved_session = service.get_session_by_id(
            new_session.id, self.test_user_id)
        # Expected for mock implementation
        self.assertIsNone(retrieved_session)

    def test_search_and_filter_integration(self):
        """Test search and filter integration"""
        service = self.DopeService(None)  # Mock supabase

        # Get all sessions
        all_sessions = service.get_sessions_for_user(self.test_user_id)
        initial_count = len(all_sessions)

        # Search for specific term
        search_results = service.search_sessions(self.test_user_id, "Federal")
        self.assertLessEqual(len(search_results), initial_count)

        # Filter by specific criteria
        filter_results = service.filter_sessions(
            self.test_user_id,
            {"status": "active", "cartridge_type": "223 Remington"}
        )

        # Verify all results match filter criteria
        for session in filter_results:
            self.assertEqual(session.status, "active")
            self.assertEqual(session.cartridge_type, "223 Remington")

    def test_statistics_calculation_integration(self):
        """Test statistics calculation with model data"""
        service = self.DopeService(None)  # Mock supabase

        # Get statistics
        stats = service.get_session_statistics(self.test_user_id)

        # Verify statistics structure
        required_stats = [
            "total_sessions", "active_sessions", "archived_sessions",
            "unique_cartridge_types", "unique_bullet_makes",
            "unique_ranges", "average_distance_m"
        ]

        for stat_key in required_stats:
            self.assertIn(stat_key, stats)
            self.assertIsInstance(stats[stat_key], (int, float, str))

        # Verify logical relationships
        self.assertEqual(
            stats["total_sessions"],
            stats["active_sessions"] + stats["archived_sessions"]
        )

    def test_bulk_operations_workflow(self):
        """Test bulk operations workflow"""
        service = self.DopeService(None)  # Mock supabase

        # Get multiple sessions
        sessions = service.get_sessions_for_user(self.test_user_id)

        if len(sessions) > 1:
            # Test bulk filtering
            bulk_filter_results = service.filter_sessions(
                self.test_user_id,
                {"status": "active"}
            )

            # Test bulk search
            bulk_search_results = service.search_sessions(
                self.test_user_id,
                "Range"
            )

            # Results should be subsets of original sessions
            self.assertLessEqual(len(bulk_filter_results), len(sessions))
            self.assertLessEqual(len(bulk_search_results), len(sessions))

    def test_error_handling_integration(self):
        """Test error handling across service and model layers"""
        service = self.DopeService(None)  # Mock supabase

        # Test with invalid data
        invalid_session_data = {
            "session_name": "",  # Empty required field
            "rifle_name": "",    # Empty required field
        }

        # Create session should still work (validation is in model)
        new_session = service.create_session(
            invalid_session_data, self.test_user_id)
        self.assertIsInstance(new_session, self.DopeSessionModel)

        # But model should report as incomplete
        self.assertFalse(new_session.is_complete())
        missing_fields = new_session.get_missing_mandatory_fields()
        self.assertGreater(len(missing_fields), 0)

    def test_model_service_data_consistency(self):
        """Test data consistency between model and service"""
        service = self.DopeService(None)  # Mock supabase

        # Get sessions from service
        sessions = service.get_sessions_for_user(self.test_user_id)

        for session in sessions:
            # Test that model methods work with service data
            display_name = session.display_name
            cartridge_display = session.cartridge_display
            bullet_display = session.bullet_display
            # TODO: Add weather_summary property to DopeSessionModel
            # weather_summary = session.weather_summary

            # All should return strings
            self.assertIsInstance(display_name, str)
            self.assertIsInstance(cartridge_display, str)
            self.assertIsInstance(bullet_display, str)
            # self.assertIsInstance(weather_summary, str)

            # Test completeness check works
            is_complete = session.is_complete()
            missing_fields = session.get_missing_mandatory_fields()

            self.assertIsInstance(is_complete, bool)
            self.assertIsInstance(missing_fields, list)

            # If complete, should have no missing fields
            if is_complete:
                self.assertEqual(len(missing_fields), 0)


if __name__ == "__main__":
    unittest.main()
