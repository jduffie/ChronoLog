import os
import sys

import streamlit as st

# Add the parent directory to the path so we can import shared modules
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from typing import Any, Dict

from auth import handle_auth
from mapping.session_state_manager import SessionStateManager
from supabase import create_client

from .nominate_model import NominateModel
from .nominate_view import NominateView


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
        form_keys = ["range_name", "range_description"]
        for key in form_keys:
            if key in st.session_state:
                del st.session_state[key]

        # Clear processed markers to allow new submissions
        if "processed_markers" in st.session_state:
            del st.session_state["processed_markers"]

    def _handle_elevation_fetching(self) -> None:
        """Handle elevation data fetching with spinner."""
        if self.model.needs_elevation_fetch():
            with self.view.display_spinner("Fetching elevation data..."):
                self.model.fetch_missing_elevations()

    def _handle_map_interactions(self, map_info: Dict[str, Any]) -> None:
        """Handle map draw interactions and navigation."""
        if not map_info:
            return

        # Handle draw events (markers from draw plugin)
        if "all_drawings" in map_info and map_info["all_drawings"]:
            all_drawings = map_info["all_drawings"]
            # Debug: Print raw all_drawings data - pretty print it
            print(f"🔍 Raw all_drawings: {all_drawings}")

            # Filter for markers (points) only
            markers = [
                feature
                for feature in all_drawings
                if feature["geometry"]["type"] == "Point"
            ]

            if len(markers) == 1:
                print(f"📍 First pushpin placed")
            elif len(markers) == 2:
                # Print lat/lon of both features
                point1 = markers[0]["geometry"]["coordinates"]
                point2 = markers[1]["geometry"]["coordinates"]
                print(f"📍 Two pushpins placed:")
                print(f"  Point 1: lat={point1[1]:.6f}, lon={point1[0]:.6f}")
                print(f"  Point 2: lat={point2[1]:.6f}, lon={point2[0]:.6f}")

                # Create a unique key for this set of markers
                markers_key = (
                    f"{point1[1]:.6f},{point1[0]:.6f}|{point2[1]:.6f},{point2[0]:.6f}"
                )

                # Check if we've already processed these exact markers
                if "processed_markers" not in st.session_state:
                    st.session_state.processed_markers = set()

                # Process the points and disable draw only if not already processed
                if markers_key not in st.session_state.processed_markers:
                    # Clear existing points and add the two new ones
                    self.model.points = []
                    self.model.add_point(point1[1], point1[0])  # lat, lon
                    self.model.add_point(point2[1], point2[0])  # lat, lon
                    self.model.disable_draw = True

                    # Fetch elevations first
                    self.model.fetch_missing_elevations()
                    # Calculate and store measurements
                    self.model.measurements = self.model.calculate_measurements()

                    # Mark these markers as processed
                    st.session_state.processed_markers.add(markers_key)

                    print(
                        f"✅ Processed points, calculated measurements, and disabled draw"
                    )

                    # Trigger rerun to update map with polyline and disable draw
                    st.rerun()
                else:
                    print(f"⚠️ Markers already processed, skipping rerun")

        # Handle map state changes (update model but don't trigger rerun for map navigation)
        if map_info.get("center"):
            center = map_info["center"]
            print(f"CENTER : {center}")

        if "zoom" in map_info and map_info["zoom"] is not None:
            zoom = map_info["zoom"]
            print(f" ZOOM: {zoom}")

    def _handle_reset_action(self) -> None:
        """Handle reset button action."""
        if len(self.model.points) > 0:
            if self.view.display_reset_button():
                self._clear_all_form_data()
                st.rerun()

    def _handle_range_submission(
        self, user: Dict[str, Any], submission_data: Dict[str, Any]
    ) -> None:
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
                    supabase_client=supabase,
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
        """Debug nominate module session state changes."""
        prev_session_state = getattr(st.session_state, "_prev_nominate_state", {})

        # Use SessionStateManager to get filtered nominate state
        current_nominate_state = SessionStateManager.debug_session_state("nominate")

        # Log starting state
        if current_nominate_state:
            print("Nominate Starting State:", current_nominate_state)
            print("")

        # Log changes
        changes = {
            k: v
            for k, v in current_nominate_state.items()
            if prev_session_state.get(k) != v
        }
        if changes:
            print("Nominate STATE changes:", changes)
        else:
            print("No Nominate STATE changes in this run.")

        print("_______________________________________")
        print("  ")
        print("  ")
        print("  ")

        # Store current nominate state for next comparison
        st.session_state._prev_nominate_state = current_nominate_state.copy()

    def _run_nominate_functionality(self, user, supabase):
        """Run the core nominate functionality without page setup or auth."""
        # Don't set current page when running as a tab to avoid clearing session state
        # SessionStateManager.set_current_page("nominate")

        # Check range limit
        try:
            range_count = self.model.get_user_range_count(user["email"], supabase)

            if range_count >= 40:
                st.error("🚫 **Maximum range limit reached**")
                st.warning(
                    f"You have submitted {range_count}/40 ranges. You cannot submit any more ranges."
                )
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
        search_lat, search_lon, should_zoom_to_max = self.view.display_search_controls(
            default_lat=self.model.map_center[0], default_lon=self.model.map_center[1]
        )

        # Update map center if coordinates changed
        if [search_lat, search_lon] != self.model.map_center:
            # Set zoom level to max (18) if coordinates were manually entered or from address search
            zoom_level = 18 if should_zoom_to_max else self.model.zoom_level
            self.model.update_map_state(
                center={"lat": search_lat, "lng": search_lon}, zoom=zoom_level
            )

        # Handle elevation fetching
        self._handle_elevation_fetching()

        # Display instruction message
        if not self.model.disable_draw:
            self.view.display_instruction_message()

        # Create and display map
        map_obj = self.view.create_map(
            self.model.map_center,
            self.model.zoom_level,
            self.model.points,
            disable_draw=self.model.disable_draw,
        )

        map_info = self.view.display_map(map_obj)

        # Display map events for debugging
        self.view.display_map_events(map_info)

        # Handle map interactions
        self._handle_map_interactions(map_info)

        # Handle reset action
        self._handle_reset_action()

        # Get measurements from model state
        measurements = (
            self.model.measurements
            if self.model.measurements
            else self.model._empty_measurements()
        )

        # Debug: Print measurements state
        print(f"🔍 Model measurements: {bool(self.model.measurements)}")
        print(f"🔍 Model points: {len(self.model.points)}")
        print(f"🔍 Model disable_draw: {self.model.disable_draw}")
        if self.model.measurements:
            print(
                f"🔍 Sample measurement data: start_lat={self.model.measurements.get('start_lat', 'N/A')}"
            )

        # Display range form and measurements table
        submission_result = self.view.display_range_form_and_table(measurements)

        # Handle range submission
        if submission_result and submission_result.get("action") == "submit":
            self._handle_range_submission(user, submission_result)

        # Debug session state
        self._debug_session_state()

    def run(self) -> None:
        """Main controller method to run the nomination application."""
        # Set page configuration FIRST, before any other Streamlit operations
        st.set_page_config(
            page_title="Nominate - ChronoLog Mapping", page_icon="📍", layout="wide"
        )

        # Set app identifier for auth system
        if "app" not in st.query_params:
            st.query_params["app"] = "mapping"

        # Handle authentication
        user = handle_auth()
        if not user:
            return

        # Database connection
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            supabase = create_client(url, key)
        except Exception as e:
            st.error(f"Error connecting to database: {str(e)}")
            return

        # Manage page-specific session state for standalone nominate page
        SessionStateManager.set_current_page("nominate")

        # Run the core functionality
        self._run_nominate_functionality(user, supabase)
