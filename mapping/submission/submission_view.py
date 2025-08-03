from typing import Any, Dict, List, Optional

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium


class SubmissionView:
    """View for displaying user range submissions with management capabilities."""

    def display_title(self) -> None:
        """Display the submissions page title."""
        st.title("Submissions")

    def display_range_count(self, current_count: int, max_count: int = 40) -> None:
        """Display current range submission count in sidebar."""
        st.sidebar.info(f"Ranges submitted: {current_count}/{max_count}")

    def display_no_submissions_message(self) -> None:
        """Display message when user has no submissions."""
        st.info("📋 You haven't submitted any ranges yet.")
        st.markdown("To submit a new range, visit the **Nominate** page.")

    def display_ranges_table(self, ranges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Display user ranges in an interactive table with action buttons."""
        if not ranges:
            self.display_no_submissions_message()
            return {"action": None, "selected_indices": []}

        # Convert to DataFrame for display with checkbox column
        display_data = []
        for i, range_data in enumerate(ranges):
            display_data.append(
                {
                    "Select": False,  # Checkbox column
                    "Index": i,
                    "Range Name": range_data.get("range_name", "Unnamed"),
                    "Description": (
                        range_data.get("range_description", "")[:50] + "..."
                        if range_data.get("range_description", "")
                        and len(range_data.get("range_description", "")) > 50
                        else range_data.get("range_description", "")
                    ),
                    "Status": range_data.get("status", "Unknown"),
                    "Distance (m)": (
                        f"{range_data.get('distance_m', 0):.1f}"
                        if range_data.get("distance_m")
                        else "N/A"
                    ),
                    "Location": (
                        range_data.get("display_name", "Unknown")[:85] + "..."
                        if range_data.get("display_name", "")
                        and len(range_data.get("display_name", "")) > 85
                        else range_data.get("display_name", "Unknown")
                    ),
                    "Submitted": range_data.get("submitted_at", "Unknown"),
                }
            )

        df = pd.DataFrame(display_data)

        # Display as an editable dataframe with checkboxes
        edited_df = st.data_editor(
            df.drop("Index", axis=1),  # Don't show index column to user
            use_container_width=True,
            hide_index=True,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select", width="small", default=False
                ),
                "Range Name": st.column_config.TextColumn(
                    "Range Name", width="medium", disabled=True
                ),
                "Description": st.column_config.TextColumn(
                    "Description", width="large", disabled=True
                ),
                "Status": st.column_config.TextColumn(
                    "Status", width="small", disabled=True
                ),
                "Distance (m)": st.column_config.TextColumn(
                    "Distance (m)", width="small", disabled=True
                ),
                "Location": st.column_config.TextColumn(
                    "Location", width="large", disabled=True
                ),
                "Submitted": st.column_config.TextColumn(
                    "Submitted", width="medium", disabled=True
                ),
            },
            key="ranges_table_checkboxes",
        )

        # Get selected rows
        selected_indices = []
        if edited_df is not None:
            selected_rows = edited_df[edited_df["Select"] == True]
            selected_indices = selected_rows.index.tolist()

        # Selection and action controls
        st.markdown("### Actions")

        # Show selection status
        if selected_indices:
            st.info(f"📋 {len(selected_indices)} range(s) selected")
        else:
            st.info("📍 Check boxes in the table above to select ranges")

        # Action buttons
        col1, col2, col3 = st.columns(3)

        action = None

        with col1:
            if st.button(
                "🗺️ Show on Map", disabled=not selected_indices, use_container_width=True
            ):
                action = "map"

        with col2:
            if st.button(
                "🗑️ Delete Selected",
                disabled=not selected_indices,
                use_container_width=True,
                type="secondary",
            ):
                action = "delete"
                # Store selection in session state for confirmation dialog
                st.session_state["delete_selected_ranges"] = selected_indices

        with col3:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

        return {"action": action, "selected_indices": selected_indices}

    def display_delete_confirmation(
        self, ranges: List[Dict[str, Any]], selected_indices: List[int]
    ) -> Optional[str]:
        """Display delete confirmation dialog."""
        if not selected_indices:
            return None

        selected_names = [
            ranges[i].get("range_name", f"Range {i+1}") for i in selected_indices
        ]

        st.warning(
            f"⚠️ Are you sure you want to delete the following {len(selected_names)} range(s)?"
        )
        for name in selected_names:
            st.write(f"• {name}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Confirm Delete", type="primary", use_container_width=True):
                return "confirm"

        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                return "cancel"

        return None

    def display_ranges_map(
        self, ranges: List[Dict[str, Any]], selected_indices: List[int]
    ) -> folium.Map:
        """Create and return a folium map with selected ranges."""
        # Default center (can be adjusted based on ranges)
        map_center = [36.222278, -78.051833]

        if ranges and selected_indices:
            # Calculate center based on selected ranges
            lats = [ranges[i]["start_lat"] for i in selected_indices if i < len(ranges)]
            lons = [ranges[i]["start_lon"] for i in selected_indices if i < len(ranges)]
            if lats and lons:
                map_center = [sum(lats) / len(lats), sum(lons) / len(lons)]

        # Create map
        m = folium.Map(location=map_center, zoom_start=10, tiles=None)

        # Add satellite imagery
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Satellite",
            overlay=False,
            control=True,
        ).add_to(m)

        # Add road overlay
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Roads",
            overlay=True,
            control=True,
            opacity=0.7,
        ).add_to(m)

        # Add layer control
        folium.LayerControl().add_to(m)

        # Add selected ranges to map
        for i in selected_indices:
            if i < len(ranges):
                range_data = ranges[i]

                # Start point (firing position) - blue
                folium.Marker(
                    location=[range_data["start_lat"], range_data["start_lon"]],
                    popup=f"🔫 Firing Position<br>{range_data.get('range_name', 'Unnamed Range')}<br>Status: {range_data.get('status', 'Unknown')}<br><a href='https://www.google.com/maps?q={range_data['start_lat']},{range_data['start_lon']}' target='_blank'>📍 View in Google Maps</a>",
                    icon=folium.Icon(color="blue", icon="play"),
                ).add_to(m)

                # End point (target) - red
                folium.Marker(
                    location=[range_data["end_lat"], range_data["end_lon"]],
                    popup=f"🎯 Target<br>{range_data.get('range_name', 'Unnamed Range')}<br>Distance: {range_data.get('distance_m', 0):.1f}m<br><a href='https://www.google.com/maps?q={range_data['end_lat']},{range_data['end_lon']}' target='_blank'>📍 View in Google Maps</a>",
                    icon=folium.Icon(color="red", icon="stop"),
                ).add_to(m)

                # Line between points
                folium.PolyLine(
                    locations=[
                        [range_data["start_lat"], range_data["start_lon"]],
                        [range_data["end_lat"], range_data["end_lon"]],
                    ],
                    color="yellow",
                    weight=3,
                    opacity=0.8,
                    popup=f"{range_data.get('range_name', 'Unnamed')}<br>Distance: {range_data.get('distance_m', 0):.1f}m<br>Azimuth: {range_data.get('azimuth_deg', 0):.1f}°",
                ).add_to(m)

        return m

    def display_map_section(
        self, ranges: List[Dict[str, Any]], selected_indices: List[int]
    ) -> None:
        """Display the map section with selected ranges."""
        st.markdown("---")
        st.markdown("### Range Map")

        if not selected_indices:
            st.info("Select ranges from the table above to display them on the map.")
            # Show empty map
            empty_map = self.display_ranges_map([], [])
            st_folium(empty_map, use_container_width=True, height=400)
        else:
            ranges_map = self.display_ranges_map(ranges, selected_indices)
            st_folium(ranges_map, use_container_width=True, height=1200)

    def display_success_message(self, message: str) -> None:
        """Display success message."""
        st.success(message)

    def display_error_message(self, message: str) -> None:
        """Display error message."""
        st.error(message)

    def display_loading_spinner(self, message: str = "Loading..."):
        """Display loading spinner with message."""
        return st.spinner(message)
