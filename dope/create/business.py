"""
DOPE Create Business Logic

Handles the business logic and data processing for DOPE session creation.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from chronograph.service import ChronographService
from cartridges.service import CartridgeService
from dope.models import DopeSessionModel
from dope.service import DopeService
from dope.weather_associator import WeatherSessionAssociator
from mapping.submission.submission_model import SubmissionModel
from rifles.service import RifleService
from weather.service import WeatherService


class DopeCreateBusiness:
    """Business logic for DOPE session creation"""
    
    def __init__(self, supabase):
        self.supabase = supabase
        self.chrono_service = ChronographService(supabase)
        self.dope_service = DopeService(supabase)
        self.cartridge_service = CartridgeService(supabase)
        self.rifle_service = RifleService(supabase)
        self.weather_service = WeatherService(supabase)
        self.weather_associator = WeatherSessionAssociator(supabase)
        self.submission_model = SubmissionModel()
    
    def get_unused_chrono_sessions(self, user_id: str):
        """Get chronograph sessions not yet used in any DOPE session"""
        try:
            # Get all chrono sessions for user
            all_chrono_sessions = self.chrono_service.get_sessions_for_user(user_id)
            
            # Get all DOPE sessions to find used chrono session IDs
            all_dope_sessions = self.dope_service.get_sessions_for_user(user_id)
            used_chrono_ids = {
                session.chrono_session_id for session in all_dope_sessions 
                if session.chrono_session_id
            }
            
            # Filter out already used sessions
            unused_sessions = [
                session for session in all_chrono_sessions 
                if session.id not in used_chrono_ids
            ]
            
            return unused_sessions
        except Exception as e:
            raise Exception(f"Error loading chronograph sessions: {str(e)}")
    
    def get_rifles_for_user(self, user_id: str):
        """Get rifles for user"""
        try:
            return self.rifle_service.get_rifles_for_user(user_id)
        except Exception as e:
            raise Exception(f"Error loading rifles: {str(e)}")
    
    def get_cartridges_for_user(self, user_id: str):
        """Get cartridges for user"""
        try:
            return self.cartridge_service.get_cartridges_for_user(user_id)
        except Exception as e:
            raise Exception(f"Error loading cartridges: {str(e)}")
    
    def get_cartridge_types(self):
        """Get available cartridge types"""
        try:
            return self.cartridge_service.get_cartridge_types()
        except Exception as e:
            raise Exception(f"Error loading cartridge types: {str(e)}")
    
    def get_ranges_for_user(self, user_id: str):
        """Get ranges for user"""
        try:
            return self.submission_model.get_user_ranges(user_id, self.supabase)
        except Exception as e:
            raise Exception(f"Error loading ranges: {str(e)}")
    
    def get_weather_sources_for_user(self, user_id: str):
        """Get weather sources for user"""
        try:
            return self.weather_service.get_sources_for_user(user_id)
        except Exception as e:
            raise Exception(f"Error loading weather sources: {str(e)}")
    
    def get_chrono_session_time_window(self, user_id: str, chrono_session_id: str):
        """Get time window for chronograph session"""
        try:
            return self.weather_associator.get_chrono_session_time_window(
                user_id, chrono_session_id
            )
        except Exception as e:
            raise Exception(f"Error getting time window: {str(e)}")
    
    def filter_cartridges_by_rifle_type(self, cartridges, rifle_cartridge_type: str):
        """Filter cartridges to match rifle cartridge type"""
        if not rifle_cartridge_type:
            return cartridges
            
        return [c for c in cartridges if c.cartridge_type == rifle_cartridge_type]
    
    def get_unique_cartridge_makes(self, cartridges):
        """Extract unique cartridge makes from CartridgeModel objects"""
        makes = set()
        for cartridge in cartridges:
            if cartridge.make:
                makes.add(cartridge.make)
        return sorted(list(makes))
    
    def get_unique_bullet_grains(self, cartridges):
        """Extract unique bullet grain weights from CartridgeModel objects"""
        grains = set()
        for cartridge in cartridges:
            if cartridge.bullet_weight_grains:
                grains.add(cartridge.bullet_weight_grains)
        return sorted(list(grains))
    
    def filter_cartridges(
        self,
        cartridges,
        cartridge_type_filter,
        cartridge_make_filter,
        bullet_grain_filter
    ):
        """Filter CartridgeModel objects based on selected filters"""
        filtered = cartridges
        
        # Filter by cartridge type
        if cartridge_type_filter and cartridge_type_filter != "All":
            filtered = [c for c in filtered if c.cartridge_type == cartridge_type_filter]
        
        # Filter by cartridge make
        if cartridge_make_filter and cartridge_make_filter != "All":
            filtered = [c for c in filtered if c.make == cartridge_make_filter]
        
        # Filter by bullet grain
        if bullet_grain_filter and bullet_grain_filter != "All":
            filtered = [c for c in filtered if c.bullet_weight_grains == bullet_grain_filter]
        
        return filtered
    
    def create_dope_session(self, session_data: dict, user_id: str):
        """Create a new DOPE session"""
        try:
            return self.dope_service.create_session(session_data, user_id)
        except Exception as e:
            raise Exception(f"Error creating DOPE session: {str(e)}")
    
    def associate_weather_with_session(
        self, 
        user_id: str, 
        session_id: str, 
        weather_source_id: str, 
        start_time: datetime, 
        end_time: datetime
    ):
        """Associate weather measurements with DOPE session"""
        try:
            return self.weather_associator.associate_weather_with_dope_session(
                user_id, session_id, weather_source_id, start_time, end_time
            )
        except Exception as e:
            raise Exception(f"Weather association failed: {str(e)}")
    
    def update_session_with_weather_data(
        self, 
        session_id: str, 
        weather_association_results: dict
    ):
        """Update DOPE session with median weather values"""
        try:
            median_weather = weather_association_results.get("median_weather", {})
            if not median_weather:
                return
            
            weather_update_data = {}
            
            # Store both metric and imperial values in dope_sessions
            for weather_field, metric_value in median_weather.items():
                if weather_field == 'temperature_c':
                    weather_update_data['temperature_c'] = metric_value
                    weather_update_data['temperature_f'] = (metric_value * 9.0/5.0) + 32
                
                elif weather_field == 'relative_humidity_pct':
                    weather_update_data['humidity_pct'] = metric_value
                
                elif weather_field == 'barometric_pressure_hpa':
                    weather_update_data['pressure_hpa'] = metric_value
                    weather_update_data['pressure_inhg'] = metric_value / 33.8639
                
                elif weather_field == 'wind_speed_mps':
                    weather_update_data['wind_speed_mps'] = metric_value
                    weather_update_data['wind_speed_mph'] = metric_value * 2.237
            
            if weather_update_data:
                # Update the DOPE session with median weather values
                self.supabase.table("dope_sessions").update(
                    weather_update_data
                ).eq("id", session_id).execute()
                
        except Exception as e:
            raise Exception(f"Error updating session with weather data: {str(e)}")
    
    def prepare_session_data(
        self,
        chrono_session,
        rifle,
        cartridge,
        range_data,
        weather_data,
        session_details,
        time_window
    ):
        """Prepare session data dictionary for database creation"""
        return {
            "session_name": session_details.get("session_name") or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "chrono_session_id": chrono_session.id,
            "rifle_id": rifle.id if hasattr(rifle, 'id') else rifle["id"],
            "cartridge_id": cartridge.id if hasattr(cartridge, 'id') else cartridge["id"],
            "bullet_id": cartridge.bullet_id if hasattr(cartridge, 'bullet_id') else cartridge["bullet_id"],
            "range_submission_id": range_data["id"] if range_data else None,
            "weather_source_id": weather_data.id if weather_data else None,
            "start_time": time_window[0].isoformat() if time_window else None,
            "end_time": time_window[1].isoformat() if time_window else None,
            "notes": session_details.get("notes"),
            "status": "active",
        }