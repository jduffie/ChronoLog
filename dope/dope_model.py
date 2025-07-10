from typing import Dict, List, Any, Optional
import pandas as pd


class DopeModel:
    """Model for managing DOPE session data across different tabs"""
    
    def __init__(self):
        self.tabs_data: Dict[str, Dict[str, Any]] = {}
    
    def get_tab_data(self, tab_name: str) -> Dict[str, Any]:
        """Get data for a specific tab"""
        if tab_name not in self.tabs_data:
            self.tabs_data[tab_name] = {
                "measurements_data": [],
                "edited_measurements": None,
                "session_details": {},
                "is_created": False
            }
        return self.tabs_data[tab_name]
    
    def set_tab_measurements(self, tab_name: str, measurements_data: List[Dict[str, Any]]):
        """Set the initial measurements data for a tab"""
        tab_data = self.get_tab_data(tab_name)
        tab_data["measurements_data"] = measurements_data
        tab_data["is_created"] = True
    
    def get_tab_measurements_df(self, tab_name: str) -> Optional[pd.DataFrame]:
        """Get measurements as DataFrame for a tab"""
        tab_data = self.get_tab_data(tab_name)
        if tab_data["edited_measurements"] is not None:
            return tab_data["edited_measurements"]
        elif tab_data["measurements_data"]:
            return pd.DataFrame(tab_data["measurements_data"])
        return None
    
    def update_tab_measurements(self, tab_name: str, edited_df: pd.DataFrame):
        """Update the edited measurements for a tab"""
        tab_data = self.get_tab_data(tab_name)
        tab_data["edited_measurements"] = edited_df.copy()
    
    def set_tab_session_details(self, tab_name: str, session_details: Dict[str, Any]):
        """Set session details for a tab"""
        tab_data = self.get_tab_data(tab_name)
        tab_data["session_details"] = session_details
    
    def get_tab_session_details(self, tab_name: str) -> Dict[str, Any]:
        """Get session details for a tab"""
        tab_data = self.get_tab_data(tab_name)
        return tab_data.get("session_details", {})
    
    def is_tab_created(self, tab_name: str) -> bool:
        """Check if a DOPE session has been created for this tab"""
        tab_data = self.get_tab_data(tab_name)
        return tab_data.get("is_created", False)
    
    def clear_tab_data(self, tab_name: str):
        """Clear all data for a specific tab"""
        if tab_name in self.tabs_data:
            del self.tabs_data[tab_name]
    
    def get_all_tabs(self) -> List[str]:
        """Get list of all tabs with data"""
        return list(self.tabs_data.keys())