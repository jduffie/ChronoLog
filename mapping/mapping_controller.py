import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mapping.public_ranges_model import PublicRangesModel
from mapping.submission_model import SubmissionModel
from mapping.mapping_view import MappingView
from auth import handle_auth
from supabase import create_client
from typing import Dict, Any


class MappingController:
    """Controller for general mapping functionality (excluding nomination)."""
    def __init__(self):
        self.public_ranges_model = PublicRangesModel()
        self.submission_model = SubmissionModel()
        self.view = MappingView()

    def get_public_ranges(self, supabase_client):
        """Get all public ranges."""
        return self.public_ranges_model.get_public_ranges(supabase_client)
    
    def get_user_ranges(self, user_email: str, supabase_client):
        """Get ranges for a specific user."""
        return self.submission_model.get_user_ranges(user_email, supabase_client)
    
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
        return self.submission_model.delete_user_ranges(user_email, range_ids, supabase_client)
    
    def delete_public_range(self, range_id, supabase_client):
        """Delete a public range."""
        return self.public_ranges_model.delete_public_range(range_id, supabase_client)