import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timezone
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chronograph.service import ChronographService
from chronograph.models import ChronographSession, ChronographMeasurement
from chronograph.import_tab import render_chronograph_import_tab


class TestChronographService(unittest.TestCase):
    
    def setUp(self):
        self.mock_supabase = Mock()
        self.service = ChronographService(self.mock_supabase)
        self.user_email = "test@example.com"
    
    def test_get_sessions_for_user(self):
        mock_data = [{
            'id': 'session-1',
            'user_email': 'test@example.com',
            'tab_name': 'Sheet1',
            'bullet_type': '9mm FMJ',
            'bullet_grain': 115.0,
            'datetime_local': '2023-12-01T10:00:00',
            'uploaded_at': '2023-12-01T10:05:00',
            'file_path': 'test/file.xlsx',
            'shot_count': 10,
            'avg_speed_fps': 1200.5,
            'std_dev_fps': 15.2,
            'min_speed_fps': 1180.0,
            'max_speed_fps': 1220.0,
            'created_at': '2023-12-01T10:05:00'
        }]
        
        mock_response = Mock()
        mock_response.data = mock_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        sessions = self.service.get_sessions_for_user(self.user_email)
        
        self.assertEqual(len(sessions), 1)
        self.assertIsInstance(sessions[0], ChronographSession)
        self.assertEqual(sessions[0].bullet_type, '9mm FMJ')
        self.assertEqual(sessions[0].shot_count, 10)
    
    def test_get_sessions_for_user_empty(self):
        mock_response = Mock()
        mock_response.data = []
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        sessions = self.service.get_sessions_for_user(self.user_email)
        
        self.assertEqual(len(sessions), 0)
    
    def test_get_session_by_id(self):
        session_id = "session-1"
        mock_data = {
            'id': session_id,
            'user_email': self.user_email,
            'tab_name': 'Sheet1',
            'bullet_type': '9mm FMJ',
            'bullet_grain': 115.0,
            'datetime_local': '2023-12-01T10:00:00',
            'uploaded_at': '2023-12-01T10:05:00',
            'file_path': 'test/file.xlsx'
        }
        
        mock_response = Mock()
        mock_response.data = mock_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        
        session = self.service.get_session_by_id(session_id, self.user_email)
        
        self.assertIsInstance(session, ChronographSession)
        self.assertEqual(session.id, session_id)
        self.assertEqual(session.bullet_type, '9mm FMJ')
    
    def test_get_measurements_for_session(self):
        session_id = "session-1"
        mock_data = [{
            'id': 'measurement-1',
            'user_email': self.user_email,
            'chrono_session_id': session_id,
            'shot_number': 1,
            'speed_fps': 1200.5,
            'datetime_local': '2023-12-01T10:01:00',
            'delta_avg_fps': 5.2,
            'ke_ft_lb': 368.5,
            'power_factor': 138.1
        }]
        
        mock_response = Mock()
        mock_response.data = mock_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        measurements = self.service.get_measurements_for_session(self.user_email, session_id)
        
        self.assertEqual(len(measurements), 1)
        self.assertIsInstance(measurements[0], ChronographMeasurement)
        self.assertEqual(measurements[0].shot_number, 1)
        self.assertEqual(measurements[0].speed_fps, 1200.5)
    
    def test_session_exists_true(self):
        mock_response = Mock()
        mock_response.data = [{'id': 'session-1'}]
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        exists = self.service.session_exists(self.user_email, "Sheet1", "2023-12-01T10:00:00")
        
        self.assertTrue(exists)
    
    def test_session_exists_false(self):
        mock_response = Mock()
        mock_response.data = []
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        exists = self.service.session_exists(self.user_email, "Sheet1", "2023-12-01T10:00:00")
        
        self.assertFalse(exists)
    
    def test_create_session(self):
        session_data = {
            'user_email': self.user_email,
            'tab_name': 'Sheet1',
            'bullet_type': '9mm FMJ'
        }
        
        mock_response = Mock()
        mock_response.data = [{'id': 'new-session-id'}]
        
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        session_id = self.service.create_session(session_data)
        
        self.assertEqual(session_id, 'new-session-id')
        self.mock_supabase.table.assert_called_with("chrono_sessions")
    
    def test_get_unique_bullet_types(self):
        mock_data = [
            {'bullet_type': '9mm FMJ'},
            {'bullet_type': '.45 ACP'},
            {'bullet_type': '9mm FMJ'},
            {'bullet_type': '.380 Auto'}
        ]
        
        mock_response = Mock()
        mock_response.data = mock_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        bullet_types = self.service.get_unique_bullet_types(self.user_email)
        
        expected_types = ['.380 Auto', '.45 ACP', '9mm FMJ']
        self.assertEqual(bullet_types, expected_types)


class TestChronographModels(unittest.TestCase):
    
    def test_chronograph_session_from_supabase_record(self):
        record = {
            'id': 'session-1',
            'user_email': 'test@example.com',
            'tab_name': 'Sheet1',
            'bullet_type': '9mm FMJ',
            'bullet_grain': 115.0,
            'datetime_local': '2023-12-01T10:00:00',
            'uploaded_at': '2023-12-01T10:05:00',
            'file_path': 'test/file.xlsx',
            'shot_count': 10,
            'avg_speed_fps': 1200.5,
            'std_dev_fps': 15.2,
            'min_speed_fps': 1180.0,
            'max_speed_fps': 1220.0,
            'created_at': '2023-12-01T10:05:00'
        }
        
        session = ChronographSession.from_supabase_record(record)
        
        self.assertEqual(session.id, 'session-1')
        self.assertEqual(session.bullet_type, '9mm FMJ')
        self.assertEqual(session.bullet_grain, 115.0)
        self.assertEqual(session.shot_count, 10)
        self.assertAlmostEqual(session.avg_speed_fps, 1200.5)
    
    def test_chronograph_session_display_methods(self):
        session = ChronographSession(
            id='session-1',
            user_email='test@example.com',
            tab_name='Sheet1',
            bullet_type='9mm FMJ',
            bullet_grain=115.0,
            datetime_local=pd.to_datetime('2023-12-01T10:00:00'),
            uploaded_at=pd.to_datetime('2023-12-01T10:05:00'),
            file_path='test/folder/file.xlsx',
            shot_count=10,
            avg_speed_fps=1200.5,
            std_dev_fps=15.2,
            min_speed_fps=1180.0,
            max_speed_fps=1220.0
        )
        
        self.assertEqual(session.display_name(), 'Sheet1 - 2023-12-01 10:00')
        self.assertEqual(session.bullet_display(), '9mm FMJ 115.0gr')
        self.assertEqual(session.avg_speed_display(), '1200 fps')
        self.assertEqual(session.std_dev_display(), '15.2 fps')
        self.assertEqual(session.velocity_range_display(), '40 fps')
        self.assertEqual(session.file_name(), 'file.xlsx')
        self.assertTrue(session.has_measurements())
    
    def test_chronograph_measurement_from_supabase_record(self):
        record = {
            'id': 'measurement-1',
            'user_email': 'test@example.com',
            'chrono_session_id': 'session-1',
            'shot_number': 1,
            'speed_fps': 1200.5,
            'datetime_local': '2023-12-01T10:01:00',
            'delta_avg_fps': 5.2,
            'ke_ft_lb': 368.5,
            'power_factor': 138.1,
            'clean_bore': True,
            'cold_bore': False,
            'shot_notes': 'Test note'
        }
        
        measurement = ChronographMeasurement.from_supabase_record(record)
        
        self.assertEqual(measurement.id, 'measurement-1')
        self.assertEqual(measurement.shot_number, 1)
        self.assertAlmostEqual(measurement.speed_fps, 1200.5)
        self.assertAlmostEqual(measurement.delta_avg_fps, 5.2)
        self.assertTrue(measurement.clean_bore)
        self.assertFalse(measurement.cold_bore)
        self.assertEqual(measurement.shot_notes, 'Test note')


class TestChronographImportTab(unittest.TestCase):
    
    @patch('streamlit.file_uploader')
    @patch('streamlit.success')
    @patch('streamlit.error')
    @patch('pandas.ExcelFile')
    def test_render_chronograph_import_tab_no_file(self, mock_excel, mock_error, mock_success, mock_file_uploader):
        mock_file_uploader.return_value = None
        
        user = {'email': 'test@example.com'}
        mock_supabase = Mock()
        bucket = 'test-bucket'
        
        result = render_chronograph_import_tab(user, mock_supabase, bucket)
        
        self.assertIsNone(result)
        mock_excel.assert_not_called()
    
    @patch('streamlit.file_uploader')
    @patch('streamlit.success')
    @patch('streamlit.error')
    @patch('pandas.ExcelFile')
    def test_render_chronograph_import_tab_upload_error(self, mock_excel, mock_error, mock_success, mock_file_uploader):
        mock_file = Mock()
        mock_file.name = 'test.xlsx'
        mock_file.type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        mock_file.getvalue.return_value = b'fake_excel_data'
        mock_file_uploader.return_value = mock_file
        
        user = {'email': 'test@example.com'}
        mock_supabase = Mock()
        mock_supabase.storage.from_.return_value.upload.side_effect = Exception("Upload failed")
        bucket = 'test-bucket'
        
        result = render_chronograph_import_tab(user, mock_supabase, bucket)
        
        self.assertIsNone(result)
        mock_error.assert_called()
        mock_excel.assert_not_called()


class TestChronographPageStructure(unittest.TestCase):
    """Test the chronograph page structure and configuration"""
    
    def test_chronograph_page_exists(self):
        """Test that the chronograph page file exists"""
        page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages", "3_⏱️_Chronograph.py")
        self.assertTrue(os.path.exists(page_path), "Chronograph page should exist")
    
    def test_chronograph_page_has_required_imports(self):
        """Test that chronograph page has required imports"""
        page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages", "3_⏱️_Chronograph.py")
        if os.path.exists(page_path):
            with open(page_path, 'r') as f:
                content = f.read()
            
            required_imports = ["streamlit", "handle_auth", "create_client", "render_chronograph_import_tab"]
            for required_import in required_imports:
                self.assertIn(required_import, content, f"Chronograph page should import {required_import}")
    
    def test_chronograph_page_has_correct_tabs(self):
        """Test that chronograph page has expected tabs"""
        page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages", "3_⏱️_Chronograph.py")
        if os.path.exists(page_path):
            with open(page_path, 'r') as f:
                content = f.read()
            
            expected_tabs = ["Import", "View", "Edit", "My Files"]
            for tab in expected_tabs:
                self.assertIn(f'"{tab}"', content, f"Chronograph page should have {tab} tab")
    
    def test_chronograph_page_configuration(self):
        """Test chronograph page configuration"""
        page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages", "3_⏱️_Chronograph.py")
        if os.path.exists(page_path):
            with open(page_path, 'r') as f:
                content = f.read()
            
            self.assertIn('page_title="Chronograph"', content)
            self.assertIn('page_icon="📁"', content)
            self.assertIn('layout="wide"', content)


if __name__ == '__main__':
    unittest.main()