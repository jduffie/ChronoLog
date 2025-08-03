import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timezone
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather.service import WeatherService
from weather.models import WeatherLog, WeatherMeasurement
from weather.import_tab import render_weather_import_tab


class TestWeatherService(unittest.TestCase):
    
    def setUp(self):
        self.mock_supabase = Mock()
        self.service = WeatherService(self.mock_supabase)
        self.user_email = "test@example.com"
    
    def test_get_logs_for_user(self):
        mock_data = [{
            'id': 'log-1',
            'user_email': 'test@example.com',
            'log_name': 'Test Log',
            'device_serial': 'KES123456',
            'start_time': '2023-12-01T10:00:00',
            'end_time': '2023-12-01T12:00:00',
            'uploaded_at': '2023-12-01T12:05:00',
            'file_path': 'test/weather.csv',
            'measurement_count': 24
        }]
        
        mock_response = Mock()
        mock_response.data = mock_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        logs = self.service.get_logs_for_user(self.user_email)
        
        self.assertEqual(len(logs), 1)
        self.assertIsInstance(logs[0], WeatherLog)
        self.assertEqual(logs[0].log_name, 'Test Log')
        self.assertEqual(logs[0].measurement_count, 24)
    
    def test_get_logs_for_user_empty(self):
        mock_response = Mock()
        mock_response.data = []
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        logs = self.service.get_logs_for_user(self.user_email)
        
        self.assertEqual(len(logs), 0)
    
    def test_get_log_by_id(self):
        log_id = "log-1"
        mock_data = {
            'id': log_id,
            'user_email': self.user_email,
            'log_name': 'Test Log',
            'device_serial': 'KES123456',
            'start_time': '2023-12-01T10:00:00',
            'end_time': '2023-12-01T12:00:00',
            'uploaded_at': '2023-12-01T12:05:00',
            'file_path': 'test/weather.csv'
        }
        
        mock_response = Mock()
        mock_response.data = mock_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        
        log = self.service.get_log_by_id(log_id, self.user_email)
        
        self.assertIsInstance(log, WeatherLog)
        self.assertEqual(log.id, log_id)
        self.assertEqual(log.log_name, 'Test Log')
    
    def test_get_measurements_for_log(self):
        log_id = "log-1"
        mock_data = [{
            'id': 'measurement-1',
            'user_email': self.user_email,
            'weather_log_id': log_id,
            'timestamp': '2023-12-01T10:00:00',
            'temperature_f': 72.5,
            'humidity_percent': 65.0,
            'pressure_inhg': 29.92,
            'wind_speed_mph': 5.2,
            'wind_direction_deg': 270
        }]
        
        mock_response = Mock()
        mock_response.data = mock_data
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        measurements = self.service.get_measurements_for_log(self.user_email, log_id)
        
        self.assertEqual(len(measurements), 1)
        self.assertIsInstance(measurements[0], WeatherMeasurement)
        self.assertEqual(measurements[0].temperature_f, 72.5)
        self.assertEqual(measurements[0].wind_speed_mph, 5.2)
    
    def test_log_exists_true(self):
        mock_response = Mock()
        mock_response.data = [{'id': 'log-1'}]
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        exists = self.service.log_exists(self.user_email, "Test Log", "2023-12-01T10:00:00")
        
        self.assertTrue(exists)
    
    def test_log_exists_false(self):
        mock_response = Mock()
        mock_response.data = []
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        exists = self.service.log_exists(self.user_email, "Test Log", "2023-12-01T10:00:00")
        
        self.assertFalse(exists)
    
    def test_create_log(self):
        log_data = {
            'user_email': self.user_email,
            'log_name': 'Test Log',
            'device_serial': 'KES123456'
        }
        
        mock_response = Mock()
        mock_response.data = [{'id': 'new-log-id'}]
        
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        log_id = self.service.create_log(log_data)
        
        self.assertEqual(log_id, 'new-log-id')
        self.mock_supabase.table.assert_called_with("weather_logs")


class TestWeatherModels(unittest.TestCase):
    
    def test_weather_log_from_supabase_record(self):
        record = {
            'id': 'log-1',
            'user_email': 'test@example.com',
            'log_name': 'Test Log',
            'device_serial': 'KES123456',
            'start_time': '2023-12-01T10:00:00',
            'end_time': '2023-12-01T12:00:00',
            'uploaded_at': '2023-12-01T12:05:00',
            'file_path': 'test/weather.csv',
            'measurement_count': 24
        }
        
        log = WeatherLog.from_supabase_record(record)
        
        self.assertEqual(log.id, 'log-1')
        self.assertEqual(log.log_name, 'Test Log')
        self.assertEqual(log.device_serial, 'KES123456')
        self.assertEqual(log.measurement_count, 24)
    
    def test_weather_log_display_methods(self):
        log = WeatherLog(
            id='log-1',
            user_email='test@example.com',
            log_name='Test Log',
            device_serial='KES123456',
            start_time=pd.to_datetime('2023-12-01T10:00:00'),
            end_time=pd.to_datetime('2023-12-01T12:00:00'),
            uploaded_at=pd.to_datetime('2023-12-01T12:05:00'),
            file_path='test/folder/weather.csv',
            measurement_count=24
        )
        
        self.assertEqual(log.display_name(), 'Test Log - 2023-12-01 10:00')
        self.assertEqual(log.duration_display(), '2h 0m')
        self.assertEqual(log.file_name(), 'weather.csv')
        self.assertTrue(log.has_measurements())
    
    def test_weather_measurement_from_supabase_record(self):
        record = {
            'id': 'measurement-1',
            'user_email': 'test@example.com',
            'weather_log_id': 'log-1',
            'timestamp': '2023-12-01T10:00:00',
            'temperature_f': 72.5,
            'humidity_percent': 65.0,
            'pressure_inhg': 29.92,
            'wind_speed_mph': 5.2,
            'wind_direction_deg': 270,
            'density_altitude_ft': 2150
        }
        
        measurement = WeatherMeasurement.from_supabase_record(record)
        
        self.assertEqual(measurement.id, 'measurement-1')
        self.assertEqual(measurement.temperature_f, 72.5)
        self.assertEqual(measurement.humidity_percent, 65.0)
        self.assertEqual(measurement.wind_speed_mph, 5.2)
        self.assertEqual(measurement.wind_direction_deg, 270)


class TestWeatherImportTab(unittest.TestCase):
    
    @patch('streamlit.file_uploader')
    @patch('streamlit.success')
    @patch('streamlit.error')
    def test_render_weather_import_tab_no_file(self, mock_error, mock_success, mock_file_uploader):
        mock_file_uploader.return_value = None
        
        user = {'email': 'test@example.com'}
        mock_supabase = Mock()
        bucket = 'test-bucket'
        
        result = render_weather_import_tab(user, mock_supabase, bucket)
        
        self.assertIsNone(result)
    
    @patch('streamlit.file_uploader')
    @patch('streamlit.success')
    @patch('streamlit.error')
    def test_render_weather_import_tab_upload_error(self, mock_error, mock_success, mock_file_uploader):
        mock_file = Mock()
        mock_file.name = 'test.csv'
        mock_file.type = 'text/csv'
        mock_file.getvalue.return_value = b'fake_csv_data'
        mock_file_uploader.return_value = mock_file
        
        user = {'email': 'test@example.com'}
        mock_supabase = Mock()
        mock_supabase.storage.from_.return_value.upload.side_effect = Exception("Upload failed")
        bucket = 'test-bucket'
        
        result = render_weather_import_tab(user, mock_supabase, bucket)
        
        self.assertIsNone(result)
        mock_error.assert_called()


class TestWeatherPageStructure(unittest.TestCase):
    """Test the weather page structure and configuration"""
    
    def test_weather_page_exists(self):
        """Test that the weather page file exists"""
        page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages", "4_🌤️_Weather.py")
        self.assertTrue(os.path.exists(page_path), "Weather page should exist")
    
    def test_weather_page_has_required_imports(self):
        """Test that weather page has required imports"""
        page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages", "4_🌤️_Weather.py")
        if os.path.exists(page_path):
            with open(page_path, 'r') as f:
                content = f.read()
            
            required_imports = ["streamlit", "handle_auth", "create_client", "render_weather_import_tab"]
            for required_import in required_imports:
                self.assertIn(required_import, content, f"Weather page should import {required_import}")
    
    def test_weather_page_has_correct_tabs(self):
        """Test that weather page has expected tabs"""
        page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages", "4_🌤️_Weather.py")
        if os.path.exists(page_path):
            with open(page_path, 'r') as f:
                content = f.read()
            
            expected_tabs = ["Sources", "Import", "Logs", "View Log", "My Files"]
            for tab in expected_tabs:
                self.assertIn(f'"{tab}"', content, f"Weather page should have {tab} tab")
    
    def test_weather_page_configuration(self):
        """Test weather page configuration"""
        page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages", "4_🌤️_Weather.py")
        if os.path.exists(page_path):
            with open(page_path, 'r') as f:
                content = f.read()
            
            self.assertIn('page_title="Weather - ChronoLog"', content)
            self.assertIn('page_icon="🌤️"', content)
            self.assertIn('layout="wide"', content)


if __name__ == '__main__':
    unittest.main()