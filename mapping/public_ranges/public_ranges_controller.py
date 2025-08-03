import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import shared modules
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from .public_ranges_model import PublicRangesModel
from .public_ranges_view import PublicRangesView
from mapping.session_state_manager import SessionStateManager
from typing import Dict, Any


class PublicRangesController:
    """Controller for public ranges functionality."""

    def __init__(self):
        self.model = PublicRangesModel()
        self.view = PublicRangesView()

    def setup_page_state(self):
        """Setup page-specific session state management."""
        SessionStateManager.set_current_page("public_ranges")

    def get_public_ranges(self, supabase_client):
        """Get all public ranges."""
        return self.model.get_public_ranges(supabase_client)

    def display_public_ranges_table_readonly(self, ranges):
        """Display public ranges table in read-only mode."""
        return self.view.display_public_ranges_table_readonly(ranges)

    def display_public_ranges_table_admin(self, ranges):
        """Display public ranges table with admin controls."""
        return self.view.display_public_ranges_table_admin(ranges)

    def display_ranges_map(self, ranges, selected_indices):
        """Display ranges on map."""
        return self.view.display_ranges_map(ranges, selected_indices)

    def delete_public_range(self, range_id, supabase_client):
        """Delete a public range."""
        return self.model.delete_public_range(range_id, supabase_client)
