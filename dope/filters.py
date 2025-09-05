"""
Filter helpers for DOPE sessions to reduce complexity in service layer.
"""

from typing import Any, Dict, List

from .models import DopeSessionModel


class DopeSessionFilter:
    """Helper class for filtering DOPE sessions"""
    
    def __init__(self, sessions: List[DopeSessionModel]):
        self.sessions = sessions
    
    def apply_status_filter(self, status: str) -> 'DopeSessionFilter':
        """Apply status filter"""
        if status and status != "All":
            self.sessions = [s for s in self.sessions if s.status == status]
        return self
    
    def apply_cartridge_type_filter(self, cartridge_type: str) -> 'DopeSessionFilter':
        """Apply cartridge type filter"""
        if cartridge_type:
            if cartridge_type == "Not Defined":
                self.sessions = [
                    s for s in self.sessions 
                    if not s.cartridge_type or s.cartridge_type.strip() == ""
                ]
            else:
                self.sessions = [
                    s for s in self.sessions 
                    if s.cartridge_type == cartridge_type
                ]
        return self
    
    def apply_date_filter(self, date_from=None, date_to=None) -> 'DopeSessionFilter':
        """Apply date range filter"""
        if date_from:
            self.sessions = [
                s for s in self.sessions 
                if s.datetime_local and s.datetime_local >= date_from
            ]
        if date_to:
            self.sessions = [
                s for s in self.sessions 
                if s.datetime_local and s.datetime_local <= date_to
            ]
        return self
    
    def apply_rifle_filter(self, rifle_name: str) -> 'DopeSessionFilter':
        """Apply rifle name filter"""
        if rifle_name:
            if rifle_name == "Not Defined":
                self.sessions = [
                    s for s in self.sessions 
                    if not s.rifle_name or s.rifle_name.strip() == ""
                ]
            else:
                self.sessions = [
                    s for s in self.sessions 
                    if s.rifle_name == rifle_name
                ]
        return self
    
    def apply_distance_filter(self, distance_range: tuple) -> 'DopeSessionFilter':
        """Apply distance range filter"""
        if distance_range:
            min_dist, max_dist = distance_range
            self.sessions = [
                s for s in self.sessions 
                if s.distance_m and min_dist <= s.distance_m <= max_dist
            ]
        return self
    
    def apply_cartridge_make_filter(self, cartridge_make: str) -> 'DopeSessionFilter':
        """Apply cartridge make filter"""
        if cartridge_make:
            if cartridge_make == "Not Defined":
                self.sessions = [
                    s for s in self.sessions 
                    if not s.cartridge_make or s.cartridge_make.strip() == ""
                ]
            else:
                self.sessions = [
                    s for s in self.sessions 
                    if s.cartridge_make == cartridge_make
                ]
        return self
    
    def apply_bullet_make_filter(self, bullet_make: str) -> 'DopeSessionFilter':
        """Apply bullet make filter"""
        if bullet_make:
            if bullet_make == "Not Defined":
                self.sessions = [
                    s for s in self.sessions 
                    if not s.bullet_make or s.bullet_make.strip() == ""
                ]
            else:
                self.sessions = [
                    s for s in self.sessions 
                    if s.bullet_make == bullet_make
                ]
        return self
    
    def apply_range_filter(self, range_name: str) -> 'DopeSessionFilter':
        """Apply range name filter"""
        if range_name:
            if range_name == "Not Defined":
                self.sessions = [
                    s for s in self.sessions 
                    if not s.range_name or s.range_name.strip() == ""
                ]
            else:
                self.sessions = [
                    s for s in self.sessions 
                    if s.range_name == range_name
                ]
        return self
    
    def apply_bullet_weight_filter(self, weight_range: tuple) -> 'DopeSessionFilter':
        """Apply bullet weight range filter"""
        if weight_range:
            min_weight, max_weight = weight_range
            self.sessions = [
                s for s in self.sessions 
                if (s.bullet_weight and 
                    min_weight <= float(s.bullet_weight) <= max_weight)
            ]
        return self
    
    def apply_temperature_filter(self, temp_range: tuple) -> 'DopeSessionFilter':
        """Apply temperature range filter"""
        if temp_range:
            min_temp, max_temp = temp_range
            self.sessions = [
                s for s in self.sessions 
                if (s.temperature_c is not None and 
                    min_temp <= s.temperature_c <= max_temp)
            ]
        return self
    
    def apply_humidity_filter(self, humidity_range: tuple) -> 'DopeSessionFilter':
        """Apply humidity range filter"""
        if humidity_range:
            min_humidity, max_humidity = humidity_range
            self.sessions = [
                s for s in self.sessions 
                if (s.relative_humidity_pct is not None and 
                    min_humidity <= s.relative_humidity_pct <= max_humidity)
            ]
        return self
    
    def apply_wind_speed_filter(self, wind_range: tuple) -> 'DopeSessionFilter':
        """Apply wind speed range filter"""
        if wind_range:
            min_wind, max_wind = wind_range
            self.sessions = [
                s for s in self.sessions 
                if (s.wind_speed_1_kmh is not None and 
                    min_wind <= s.wind_speed_1_kmh <= max_wind)
            ]
        return self
    
    def apply_all_filters(self, filters: Dict[str, Any]) -> 'DopeSessionFilter':
        """Apply all filters using method chaining"""
        return (self
                .apply_status_filter(filters.get("status"))
                .apply_cartridge_type_filter(filters.get("cartridge_type"))
                .apply_date_filter(filters.get("date_from"), filters.get("date_to"))
                .apply_rifle_filter(filters.get("rifle_name"))
                .apply_distance_filter(filters.get("distance_range"))
                .apply_cartridge_make_filter(filters.get("cartridge_make"))
                .apply_bullet_make_filter(filters.get("bullet_make"))
                .apply_range_filter(filters.get("range_name"))
                .apply_bullet_weight_filter(filters.get("bullet_weight_range"))
                .apply_temperature_filter(filters.get("temperature_range"))
                .apply_humidity_filter(filters.get("humidity_range"))
                .apply_wind_speed_filter(filters.get("wind_speed_range")))
    
    def get_results(self) -> List[DopeSessionModel]:
        """Get filtered results"""
        return self.sessions