import streamlit as st
from mapping_model import MappingModel
from mapping_view import MappingView
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
                self.model.reset_points()
                self._sync_session_state_with_model()
                st.rerun()

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
        
        self.view.display_measurements_table(measurements)

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