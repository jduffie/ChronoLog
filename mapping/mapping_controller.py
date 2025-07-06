import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mapping.mapping_model import MappingModel
from mapping.mapping_view import MappingView
from auth import handle_auth
from supabase import create_client
from typing import Dict, Any


class MappingController:
    """Controller for general mapping functionality (excluding nomination)."""
    def __init__(self):
        self.model = MappingModel()
        self.view = MappingView()

    def get_public_ranges(self, supabase_client):
        """Get all public ranges."""
        return self.model.get_public_ranges(supabase_client)
    
    def get_user_ranges(self, user_email: str, supabase_client):
        """Get ranges for a specific user."""
        return self.model.get_user_ranges(user_email, supabase_client)
    
    def display_ranges_table(self, ranges):
        """Display ranges table with actions."""
        return self.view.display_ranges_table(ranges)
    
    def display_ranges_map(self, ranges, selected_indices):
        """Display ranges on map."""
        return self.view.display_ranges_map(ranges, selected_indices)
    
    def display_public_ranges_table_readonly(self, ranges):
        """Display public ranges table in read-only mode."""
        return self.view.display_public_ranges_table_readonly(ranges)
    
    def display_public_ranges_table_admin(self, ranges):
        """Display public ranges table with admin controls."""
        return self.view.display_public_ranges_table_admin(ranges)
    
    def delete_user_ranges(self, user_email: str, range_ids, supabase_client):
        """Delete user ranges."""
        return self.model.delete_user_ranges(user_email, range_ids, supabase_client)
    
    def delete_public_range(self, range_id, supabase_client):
        """Delete a public range."""
        return self.model.delete_public_range(range_id, supabase_client)