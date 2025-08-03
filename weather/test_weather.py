import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timezone
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather.models import WeatherSource, WeatherMeasurement
from weather.import_tab import render_weather_import_tab


class TestWeatherSource(unittest.TestCase):
    
    def test_weather_source_from_device_info(self):
        """Test creating WeatherSource from device info"""
        source = WeatherSource.from_device_info(
            user_email="test@example.com",
            name="Test Kestrel",
            device_name="Kestrel 5700",
            device_model="5700 Elite",
            serial_number="K123456"
        )
        
        self.assertEqual(source.user_email, "test@example.com")
        self.assertEqual(source.name, "Test Kestrel")
        self.assertEqual(source.device_name, "Kestrel 5700")
        self.assertEqual(source.model, "5700 Elite")
        self.assertEqual(source.serial_number, "K123456")
    
    def test_weather_source_from_supabase_record(self):
        """Test creating WeatherSource from Supabase record"""
        record = {
            'id': 'source-1',
            'user_email': 'test@example.com',
            'name': 'Test Kestrel',
            'source_type': 'meter',
            'device_name': 'Kestrel 5700',
            'make': 'Kestrel',
            'model': '5700 Elite',
            'serial_number': 'K123456',
            'created_at': '2023-12-01T10:00:00',
            'updated_at': '2023-12-01T10:05:00'
        }
        
        source = WeatherSource.from_supabase_record(record)
        
        self.assertEqual(source.id, 'source-1')
        self.assertEqual(source.user_email, 'test@example.com')
        self.assertEqual(source.name, 'Test Kestrel')
        self.assertEqual(source.make, 'Kestrel')
        self.assertEqual(source.model, '5700 Elite')
        self.assertEqual(source.serial_number, 'K123456')
    
    def test_weather_source_display_methods(self):
        """Test WeatherSource display methods"""
        source = WeatherSource(
            id='source-1',
            user_email='test@example.com',
            name='Test Kestrel',
            make='Kestrel',
            model='5700 Elite',
            serial_number='K123456'
        )
        
        self.assertEqual(source.display_name(), 'Test Kestrel')
        self.assertEqual(source.device_display(), 'Kestrel 5700 Elite (S/N: K123456)')
        self.assertEqual(source.short_display(), 'Test Kestrel - Kestrel 5700 Elite (S/N: K123456)')
    
    def test_weather_source_display_methods_minimal(self):
        """Test WeatherSource display methods with minimal data"""
        source = WeatherSource(
            id='source-1',
            user_email='test@example.com',
            name='Basic Meter'
        )
        
        self.assertEqual(source.display_name(), 'Basic Meter')
        self.assertEqual(source.device_display(), 'Unknown Device')
        self.assertEqual(source.short_display(), 'Basic Meter - Unknown Device')


class TestWeatherMeasurement(unittest.TestCase):
    
    def test_weather_measurement_from_supabase_record(self):
        """Test creating WeatherMeasurement from Supabase record"""
        record = {
            'id': 'measurement-1',
            'user_email': 'test@example.com',
            'weather_source_id': 'source-1',
            'measurement_timestamp': '2023-12-01T10:00:00',
            'uploaded_at': '2023-12-01T10:01:00',
            'file_path': 'test/weather.csv',
            'temperature_f': 72.5,
            'relative_humidity_pct': 65.0,
            'barometric_pressure_inhg': 29.92,
            'wind_speed_mph': 5.2,
            'compass_true_deg': 270,
            'density_altitude_ft': 2150,
            'altitude_ft': 1000,
            'dew_point_f': 55.0
        }
        
        measurement = WeatherMeasurement.from_supabase_record(record)
        
        self.assertEqual(measurement.id, 'measurement-1')
        self.assertEqual(measurement.user_email, 'test@example.com')
        self.assertEqual(measurement.weather_source_id, 'source-1')
        self.assertEqual(measurement.temperature_f, 72.5)
        self.assertEqual(measurement.relative_humidity_pct, 65.0)
        self.assertEqual(measurement.barometric_pressure_inhg, 29.92)
        self.assertEqual(measurement.wind_speed_mph, 5.2)
        self.assertEqual(measurement.compass_true_deg, 270)
        self.assertEqual(measurement.density_altitude_ft, 2150)
    
    def test_weather_measurement_display_methods(self):
        """Test WeatherMeasurement display methods"""
        measurement = WeatherMeasurement(
            id='measurement-1',
            user_email='test@example.com',
            weather_source_id='source-1',
            measurement_timestamp=pd.to_datetime('2023-12-01T10:00:00'),
            uploaded_at=pd.to_datetime('2023-12-01T10:01:00'),
            temperature_f=72.5,
            relative_humidity_pct=65.0,
            barometric_pressure_inhg=29.92,
            wind_speed_mph=5.2,
            compass_true_deg=270,
            altitude_ft=1000,
            density_altitude_ft=2150
        )
        
        self.assertEqual(measurement.temperature_display(), '72.5°F')
        self.assertEqual(measurement.humidity_display(), '65.0%')
        self.assertEqual(measurement.pressure_display(), '29.92 inHg')
        self.assertEqual(measurement.wind_display(), '5.2 mph')
        self.assertEqual(measurement.wind_direction_display(), '270°')
        self.assertEqual(measurement.altitude_display(), '1000 ft')
        self.assertEqual(measurement.density_altitude_display(), '2150 ft')
    
    def test_weather_measurement_has_data_methods(self):
        """Test WeatherMeasurement data detection methods"""
        measurement = WeatherMeasurement(
            id='measurement-1',
            user_email='test@example.com',
            weather_source_id='source-1',
            measurement_timestamp=pd.to_datetime('2023-12-01T10:00:00'),
            uploaded_at=pd.to_datetime('2023-12-01T10:01:00'),
            wind_speed_mph=5.2,
            compass_true_deg=270,
            location_description='Test Location'
        )
        
        self.assertTrue(measurement.has_wind_data())
        self.assertTrue(measurement.has_location_data())
    
    def test_weather_measurement_display_na_values(self):
        """Test WeatherMeasurement display methods with None values"""
        measurement = WeatherMeasurement(
            id='measurement-1',
            user_email='test@example.com',
            weather_source_id='source-1',
            measurement_timestamp=pd.to_datetime('2023-12-01T10:00:00'),
            uploaded_at=pd.to_datetime('2023-12-01T10:01:00')
        )
        
        self.assertEqual(measurement.temperature_display(), 'N/A')
        self.assertEqual(measurement.humidity_display(), 'N/A')
        self.assertEqual(measurement.pressure_display(), 'N/A')
        self.assertEqual(measurement.wind_display(), 'N/A')
        self.assertEqual(measurement.wind_direction_display(), 'N/A')
        self.assertEqual(measurement.altitude_display(), 'N/A')
        self.assertEqual(measurement.density_altitude_display(), 'N/A')


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