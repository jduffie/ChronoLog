import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .nominate_model import NominateModel
from .nominate_view import NominateView
from mapping.session_state_manager import SessionStateManager
from auth import handle_auth
from supabase import create_client
from typing import Dict, Any


class NominateController:
    def __init__(self):
        # Store model in session state to persist across runs
        if "nominate_model" not in st.session_state:
            st.session_state.nominate_model = NominateModel()
        self.model = st.session_state.nominate_model
        self.view = NominateView()



    def _clear_all_form_data(self) -> None:
        """Clear all form data and model state."""
        # Clear model state
        self.model.reset_points()
        
        # Clear form input session state
        form_keys = ["range_name", "range_description", "last_clicked"]
        for key in form_keys:
            if key in st.session_state:
                del st.session_state[key]
        

    def _handle_elevation_fetching(self) -> None:
        """Handle elevation data fetching with spinner."""
        if self.model.needs_elevation_fetch():
            with self.view.display_spinner("Fetching elevation data..."):
                self.model.fetch_missing_elevations()

    def _handle_map_interactions(self, map_info: Dict[str, Any]) -> None:
        """Handle map click and movement interactions."""
        if not map_info:
            return

        rerun_needed = False

        # Handle point clicks using session state deduplication
        clicked = map_info.get("last_clicked")
        if clicked:
            prev_click = st.session_state.get("last_clicked", None)
            if prev_click != clicked and len(self.model.points) < 2:
                # Store the new click in session state
                st.session_state.last_clicked = clicked
                # Process the new click
                lat = clicked["lat"]
                lng = clicked["lng"]
                self.model.add_point(lat, lng)
                print(f"✅ Added point: {lat}, {lng}. Total points: {len(self.model.points)}")
                rerun_needed = True
            else:
                print(f"⚠️ Click ignored. prev_click == clicked: {prev_click == clicked}, points: {len(self.model.points)}")

        # Handle map state changes (update model but don't trigger rerun for map navigation)
        if map_info.get("center"):
            center = map_info["center"]
            # Only update if center actually changed significantly to avoid constant updates
            current_center = self.model.map_center
            lat_diff = abs(center["lat"] - current_center[0])
            lng_diff = abs(center["lng"] - current_center[1])
            if lat_diff > 0.001 or lng_diff > 0.001:  # Only update if moved more than ~100m
                self.model.update_map_state(center=center)

        if "zoom" in map_info and map_info["zoom"] is not None:
            if map_info["zoom"] != self.model.zoom_level:
                self.model.update_map_state(zoom=map_info["zoom"])

        if rerun_needed:
            st.rerun()

    def _handle_reset_action(self) -> None:
        """Handle reset button action."""
        if len(self.model.points) > 0:
            if self.view.display_reset_button():
                self._clear_all_form_data()
                st.rerun()
    
    def _handle_range_submission(self, user: Dict[str, Any], submission_data: Dict[str, Any]) -> None:
        """Handle range data submission to database."""
        range_data = submission_data.get("range", {})
        range_name = range_data.get("range_name", "").strip()
        range_description = range_data.get("range_description", "").strip()
        measurements = range_data.get("measurements", {})
        
        # Validate required fields
        if not range_name:
            st.error("❌ Range name is required")
            return
            
        if len(range_name) < 3:
            st.error("❌ Range name must be at least 3 characters long")
            return
        
        try:
            # Setup Supabase client
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            supabase = create_client(url, key)
            
            # Save to database
            with st.spinner("Saving range data..."):
                success = self.model.save_range_submission(
                    user_email=user["email"],
                    range_name=range_name,
                    range_description=range_description,
                    measurements=measurements,
                    supabase_client=supabase
                )
            
            if success:
                # Clear all form data and model state
                self._clear_all_form_data()
                
                # Show success message and rerun
                st.success(f"✅ Range '{range_name}' saved successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to save range data. Please try again.")
                
        except Exception as e:
            st.error(f"❌ Error saving range data: {str(e)}")
            print(f"Range submission error: {e}")

    def _debug_session_state(self) -> None:
        """Debug session state changes."""
        prev_session_state = getattr(st.session_state, '_prev_state', dict(st.session_state))
        
        # Log starting state
        filtered = {k: v for k, v in st.session_state.items() if v is not None}
        if filtered:
            print("Starting State:", st.session_state)
            print("")

        # Log changes
        changes = {k: v for k, v in st.session_state.items() if prev_session_state.get(k) != v}
        if changes:
            print("STATE changes:", changes)
        else:
            print("No STATE changes in this run.")

        print("_______________________________________")
        print("  ")
        print("  ")
        print("  ")

        # Store current state for next comparison
        st.session_state._prev_state = dict(st.session_state)

    def run(self) -> None:
        """Main controller method to run the nomination application."""
        # Set page configuration FIRST, before any other Streamlit operations
        st.set_page_config(
            page_title="Nominate - ChronoLog Mapping",
            page_icon="📍",
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
        SessionStateManager.set_current_page("nominate")
        
        # User info displayed by other pages to avoid duplication
        
        # Check range limit
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            supabase = create_client(url, key)
            range_count = self.model.get_user_range_count(user["email"], supabase)
            
            if range_count >= 40:
                st.error("🚫 **Maximum range limit reached**")
                st.warning(f"You have submitted {range_count}/40 ranges. You cannot submit any more ranges.")
                st.info("If you need to submit more ranges, please contact support.")
                return
                
            # Show current range count
            st.sidebar.info(f"Ranges submitted: {range_count}/40")
            
        except Exception as e:
            st.error(f"Error checking range limit: {str(e)}")
            return
        

        # Display title
        self.view.display_title()

        # Display search controls and get coordinates
        search_lat, search_lon = self.view.display_search_controls(
            default_lat=self.model.map_center[0], 
            default_lon=self.model.map_center[1]
        )
        
        # Update map center if coordinates changed
        if [search_lat, search_lon] != self.model.map_center:
            self.model.update_map_state(center={"lat": search_lat, "lng": search_lon})

        # Handle elevation fetching
        self._handle_elevation_fetching()

        # Display instruction message
        has_complete_data = (len(self.model.points) == 2 and len(self.model.elevations_m) == 2)
        if not has_complete_data:
            st.info("To submit a new range for review, start by selecting firing position and target on the map. \n\n" \
            "Subsequently, after the application looks up the address and elevation, it will compute distance, azimuth, and elevation angles.")

        # Create and display map
        map_obj = self.view.create_map(
            self.model.map_center, 
            self.model.zoom_level, 
            self.model.points
        )
        
        map_info = self.view.display_map(map_obj)
        
        # Display map events for debugging
        self.view.display_map_events(map_info)

        # Handle map interactions
        self._handle_map_interactions(map_info)

        # Handle reset action
        self._handle_reset_action()

        # Get measurements
        if has_complete_data:
            measurements = self.model.calculate_measurements()
        else:
            measurements = self.model.get_partial_measurements()
        
        # Display range form and measurements table
        submission_result = self.view.display_range_form_and_table(measurements)
        
        # Handle range submission
        if submission_result and submission_result.get("action") == "submit":
            self._handle_range_submission(user, submission_result)

        # Debug session state
        self._debug_session_state()