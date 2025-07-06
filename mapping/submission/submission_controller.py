import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .submission_model import SubmissionModel
from .submission_view import SubmissionView
from mapping.session_state_manager import SessionStateManager
from auth import handle_auth
from supabase import create_client
from typing import Dict, Any, List


class SubmissionController:
    """Controller for managing user range submissions."""
    
    def __init__(self):
        self.model = SubmissionModel()
        self.view = SubmissionView()

    def _get_supabase_client(self):
        """Get authenticated Supabase client."""
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)

    def _handle_delete_confirmation(self, user: Dict[str, Any], ranges: List[Dict[str, Any]]) -> None:
        """Handle the delete confirmation dialog and action."""
        selected_indices = st.session_state.get("delete_selected_ranges", [])
        
        if not selected_indices:
            return

        confirmation = self.view.display_delete_confirmation(ranges, selected_indices)
        
        if confirmation == "confirm":
            # Perform deletion
            try:
                supabase = self._get_supabase_client()
                range_ids = [ranges[i]["id"] for i in selected_indices]
                
                with self.view.display_loading_spinner("Deleting ranges..."):
                    success = self.model.delete_user_ranges(user["email"], range_ids, supabase)
                
                if success:
                    self.view.display_success_message(f"✅ Successfully deleted {len(range_ids)} range(s)!")
                    # Clear the delete session state
                    if "delete_selected_ranges" in st.session_state:
                        del st.session_state["delete_selected_ranges"]
                    if "selected_ranges" in st.session_state:
                        del st.session_state["selected_ranges"]
                    st.rerun()
                else:
                    self.view.display_error_message("❌ Failed to delete some ranges. Please try again.")
                    
            except Exception as e:
                self.view.display_error_message(f"❌ Error deleting ranges: {str(e)}")
                
        elif confirmation == "cancel":
            # Clear the delete session state when canceling
            if "delete_selected_ranges" in st.session_state:
                del st.session_state["delete_selected_ranges"]
            st.rerun()

    def _check_range_limit(self, user: Dict[str, Any]) -> bool:
        """Check user's range limit and display count. Returns True if under limit."""
        try:
            supabase = self._get_supabase_client()
            range_count = self.model.get_user_range_count(user["email"], supabase)
            
            # Display current count
            self.view.display_range_count(range_count, max_count=40)
            
            return True  # Allow access regardless of count for viewing submissions
            
        except Exception as e:
            self.view.display_error_message(f"Error checking range limit: {str(e)}")
            return False

    def run(self) -> None:
        """Main controller method to run the submissions page."""
        # Set page configuration
        st.set_page_config(
            page_title="Submissions - ChronoLog Mapping",
            page_icon="📋",
            layout="wide"
        )
        
        # Set app identifier for auth system
        if "app" not in st.query_params:
            st.query_params["app"] = "mapping"
            
        # Handle authentication
        user = handle_auth()
        if not user:
            return

        # Manage page-specific session state
        SessionStateManager.set_current_page("submission")

        # Display title
        self.view.display_title()

        # Check range limit (always allow viewing)
        if not self._check_range_limit(user):
            return

        try:
            supabase = self._get_supabase_client()
            
            # Fetch user ranges
            user_ranges = self.model.get_user_ranges(user["email"], supabase)
            
            # Check if we're in delete confirmation mode
            if "delete_selected_ranges" in st.session_state:
                self._handle_delete_confirmation(user, user_ranges)
                return

            # Display ranges table and get user actions
            table_result = self.view.display_ranges_table(user_ranges)
            
            # Handle table actions
            if table_result["action"] == "delete" and table_result["selected_indices"]:
                # Set up for delete confirmation
                st.session_state["delete_selected_ranges"] = table_result["selected_indices"]
                st.rerun()
                
            elif table_result["action"] == "map" or table_result["selected_indices"]:
                # Display map with selected ranges
                self.view.display_map_section(user_ranges, table_result["selected_indices"])
            else:
                # Display empty map section
                self.view.display_map_section(user_ranges, [])
                
        except Exception as e:
            self.view.display_error_message(f"Error loading your submitted ranges: {str(e)}")

    def get_user_ranges(self, user_email: str):
        """Get ranges for a specific user."""
        try:
            supabase = self._get_supabase_client()
            return self.model.get_user_ranges(user_email, supabase)
        except Exception as e:
            self.view.display_error_message(f"Error fetching user ranges: {str(e)}")
            return []

    def delete_ranges(self, user_email: str, range_ids: List[str]) -> bool:
        """Delete user ranges."""
        try:
            supabase = self._get_supabase_client()
            return self.model.delete_user_ranges(user_email, range_ids, supabase)
        except Exception as e:
            self.view.display_error_message(f"Error deleting ranges: {str(e)}")
            return False