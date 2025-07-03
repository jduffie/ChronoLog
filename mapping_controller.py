import streamlit as st
from mapping_model import MappingModel
from mapping_view import MappingView
from auth import handle_auth
from supabase import create_client
from typing import Dict, Any


class MappingController:
    def __init__(self):
        self.model = MappingModel()
        self.view = MappingView()
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        """Initialize session state variables."""
        if "points" not in st.session_state:
            st.session_state.points = []
        if "elevations_m" not in st.session_state:
            st.session_state.elevations_m = []
        if "map_center" not in st.session_state:
            st.session_state.map_center = [36.222278, -78.051833]
        if "zoom_level" not in st.session_state:
            st.session_state.zoom_level = 13

    def _sync_model_with_session_state(self) -> None:
        """Sync model state with Streamlit session state."""
        self.model.points = st.session_state.points
        self.model.elevations_m = st.session_state.elevations_m
        self.model.map_center = st.session_state.map_center
        self.model.zoom_level = st.session_state.zoom_level

    def _sync_session_state_with_model(self) -> None:
        """Sync Streamlit session state with model state."""
        st.session_state.points = self.model.points
        st.session_state.elevations_m = self.model.elevations_m
        st.session_state.map_center = self.model.map_center
        st.session_state.zoom_level = self.model.zoom_level

    def _clear_all_form_data(self) -> None:
        """Clear all form data and model state."""
        # Clear model state
        self.model.reset_points()
        
        # Clear form input session state
        form_keys = ["range_name", "range_description"]
        for key in form_keys:
            if key in st.session_state:
                del st.session_state[key]
        
        # Sync model state to session state
        self._sync_session_state_with_model()

    def _handle_elevation_fetching(self) -> None:
        """Handle elevation data fetching with spinner."""
        if self.model.needs_elevation_fetch():
            with self.view.display_spinner("Fetching elevation data..."):
                self.model.fetch_missing_elevations()
                self._sync_session_state_with_model()

    def _handle_map_interactions(self, map_info: Dict[str, Any]) -> None:
        """Handle map click and movement interactions."""
        if not map_info:
            return

        rerun_needed = False

        # Handle point clicks
        if map_info.get("last_clicked"):
            lat = map_info["last_clicked"]["lat"]
            lng = map_info["last_clicked"]["lng"]
            
            if len(self.model.points) < 2:
                self.model.add_point(lat, lng)
                self._sync_session_state_with_model()
                rerun_needed = True

        # Handle map state changes
        if map_info.get("center"):
            center = map_info["center"]
            self.model.update_map_state(center=center)
            self._sync_session_state_with_model()

        if map_info.get("zoom"):
            zoom = map_info["zoom"]
            self.model.update_map_state(zoom=zoom)
            self._sync_session_state_with_model()

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
        """Main controller method to run the application."""
        # Set app identifier for auth system
        if "app" not in st.query_params:
            st.query_params["app"] = "mapping"
            
        # Handle authentication
        user = handle_auth()
        if not user:
            return
            
        # Display user info in sidebar
        st.sidebar.success(f"Logged in as {user['name']}")
        
        # Sync model with session state
        self._sync_model_with_session_state()

        # Display title
        self.view.display_title()

        # Handle elevation fetching
        self._handle_elevation_fetching()

        # Get measurements and display table
        if len(self.model.points) == 2 and len(self.model.elevations_m) == 2:
            measurements = self.model.calculate_measurements()
        else:
            measurements = self.model.get_partial_measurements()
        
        # Display measurements table and handle submission
        submission_result = self.view.display_measurements_table(measurements)
        
        # Handle range submission
        if submission_result and submission_result.get("action") == "submit":
            self._handle_range_submission(user, submission_result)

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

        # Debug session state
        self._debug_session_state()