from typing import Any, Dict, List, Optional, Tuple

import folium
import streamlit as st
from branca.element import MacroElement
from folium.plugins import Draw, LocateControl
from geopy.geocoders import Nominatim
from jinja2 import Template
from streamlit_folium import st_folium


class CssInjector(MacroElement):
    def __init__(self, css_string):
        super().__init__()
        self._template = Template(
            f"""
        {{% macro header(this, kwargs) %}}
            {css_string}
        {{% endmacro %}}
        """
        )


class NominateView:
    def __init__(self):
        self.cursor_css = """
        <style>
            .leaflet-container {
                cursor: crosshair !important;
            }
        </style>
        """

    def display_title(self) -> None:
        """Display the main title."""
        st.title("Nominate New Range")

    def display_instruction_message(self) -> None:
        """Display instruction message for range nomination."""
        st.info(
            "📍 To submit a new range for review, use the **Draw** toolbar on the map to add markers for the firing position and target. \n\n" +
            "1. Click the marker tool (📍) in the map's draw toolbar\n" +
            "2. Click on the map to place the firing position (1st point)\n" +
            "3. Click again to place the target position (2nd point)\n\n" +
            "The app will automatically look up addresses and elevations, then compute distance, azimuth, and elevation angles.")

    def display_search_controls(
        self, default_lat: float = 37.76, default_lon: float = -122.4
    ) -> Tuple[float, float, bool]:
        """Display search controls for address or lat/lon and return coordinates and whether to zoom."""
        method = st.radio("Navigate:", ["Address", "Lat/Lon"])

        lat, lon = default_lat, default_lon
        should_zoom_to_max = False

        if method == "Address":
            address = st.text_input("Enter address:")
            if address:
                try:
                    geolocator = Nominatim(
                        user_agent="streamlit_map", timeout=10)
                    location = geolocator.geocode(address)
                    if location:
                        lat, lon = location.latitude, location.longitude
                        should_zoom_to_max = True  # Zoom to max for address searches
                    else:
                        st.warning("Address not found.")
                except Exception as e:
                    st.error(f"Geocoding error: {e}")
        else:
            # Single text input for comma-separated lat,lon
            default_coords = f"{default_lat:.6f}, {default_lon:.6f}"
            coords_input = st.text_input(
                "Coordinates (lat, lon):",
                value=default_coords,
                placeholder="39.144281414690745, -108.32961991597905",
            )

            # Parse the input
            try:
                if coords_input.strip():
                    # Split by comma and clean up whitespace
                    parts = [part.strip() for part in coords_input.split(",")]
                    if len(parts) == 2:
                        new_lat = float(parts[0])
                        new_lon = float(parts[1])
                        # Check if user changed the coordinates from defaults
                        if (
                            abs(new_lat - default_lat) > 0.000001
                            or abs(new_lon - default_lon) > 0.000001
                        ):
                            lat, lon = new_lat, new_lon
                            should_zoom_to_max = (
                                True  # Zoom to max for manual coordinate entry
                            )
                        else:
                            lat, lon = new_lat, new_lon
                    else:
                        st.error(
                            "Please enter coordinates in the format: lat, lon (e.g., 39.144281414690745, -108.32961991597905)"
                        )
                        lat, lon = default_lat, default_lon
                else:
                    lat, lon = default_lat, default_lon
            except ValueError:
                st.error(
                    "Invalid coordinate format. Please enter valid numbers separated by a comma."
                )
                lat, lon = default_lat, default_lon

        return lat, lon, should_zoom_to_max

    def display_measurements_table(
        self, measurements: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Display the measurements table using HTML."""
        # Get display name from GeoJSON response
        location_display = measurements.get("display_name", "")

        # Check if we have complete data for submission
        has_complete_data = (
            measurements.get("start_lat")
            and measurements.get("start_lon")
            and measurements.get("end_lat")
            and measurements.get("end_lon")
        )

        # Get form values
        range_name_value = st.session_state.get("range_name", "")
        range_description_value = st.session_state.get("range_description", "")

        # Escape HTML and handle newlines properly
        import html

        range_name_escaped = html.escape(range_name_value)
        range_description_escaped = html.escape(
            range_description_value).replace("\n", "<br>")
        location_escaped = html.escape(location_display)

        html_table = f"""
        <div class="output">
          <div><strong>Range Name       :</strong> <span id="rangeName">{range_name_escaped}</span></div>
          <div><strong>Range Description:</strong> <span id="rangeDesc">{range_description_escaped}</span></div>

          <div><strong>Firing Position  :</strong> <span id="firingPos">{measurements.get("start_lat", "")}, {measurements.get("start_lon", "")}</span></div>
          <div><strong>Firing Altitude  :</strong> <span id="firingAlt">{measurements.get("start_alt", "")}</span></div>
          <div><strong>Firing Address   :</strong> <span id="firingAddr">{html.escape(measurements.get("start_address", ""))}</span></div>
          <div><strong>Target Position  :</strong> <span id="targetPos">{measurements.get("end_lat", "")}, {measurements.get("end_lon", "")}</span></div>
          <div><strong>Target Altitude  :</strong> <span id="targetAlt">{measurements.get("end_alt", "")}</span></div>
          <div><strong>Target Address   :</strong> <span id="targetAddr">{html.escape(measurements.get("end_address", ""))}</span></div>
          <div><strong>Distance (2D)    :</strong> <span id="distance2d">{measurements.get("distance_2d", "")}</span></div>
          <div><strong>Distance (3D)    :</strong> <span id="distance3d">{measurements.get("distance_3d", "")}</span></div>
          <div><strong>Azimuth Angle    :</strong> <span id="azimuth">{measurements.get("azimuth", "")}</span></div>
          <div><strong>Elevation Angle  :</strong> <span id="elevation">{measurements.get("elevation_angle", "")}</span></div>
          <div><strong>Elevation Change :</strong> <span id="elevChange">{measurements.get("elevation_change", "")}</span></div>
          <div><strong>Location         :</strong> <span id="location">{location_escaped}</span></div>
        </div>
        """

        st.markdown(html_table, unsafe_allow_html=True)

        # Form inputs below the table
        st.markdown("### Range Information")
        range_name = st.text_input(
            "**Range Name**",
            value=range_name_value,
            key="range_name",
            placeholder="Enter range name",
        )
        range_description = st.text_area(
            "**Range Description**",
            value=range_description_value,
            key="range_description",
            placeholder="Enter a description for this range",
            height=100,
        )

        # Submit button (only show if we have complete measurement data)
        if has_complete_data:
            if st.button("Submit Range Data", type="primary"):

                return {
                    "action": "submit",
                    "range": {
                        "range_name": range_name,
                        "range_description": range_description,
                        "measurements": measurements,
                    },
                }
        else:
            st.info(
                "📍 Submit a new range by selecting firing position and target on the map."
            )

        return None

    def display_range_form_and_table(
        self, measurements: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Display range form inputs and measurements table in the correct order."""
        # Check if we have complete data for submission
        has_complete_data = (
            measurements.get("start_lat")
            and measurements.get("start_lon")
            and measurements.get("end_lat")
            and measurements.get("end_lon")
        )

        # Get form values
        range_name_value = st.session_state.get("range_name", "")
        range_description_value = st.session_state.get("range_description", "")

        # Range form inputs
        st.markdown("### Range Information")
        range_name = st.text_input(
            "Range Name",
            value=range_name_value,
            key="range_name",
            placeholder="Enter range name",
        )
        range_description = st.text_area(
            "Range Description",
            value=range_description_value,
            key="range_description",
            placeholder="Enter a description for this range",
            height=100,
        )

        # Get display name from GeoJSON response
        location_display = measurements.get("display_name", "")

        # Escape HTML and handle newlines properly
        import html

        range_name_escaped = html.escape(range_name)
        range_description_escaped = html.escape(
            range_description).replace("\n", "<br>")
        location_escaped = html.escape(location_display)

        # Update form values in the measurements table
        html_table = f"""
        <div class="output">
          <div><strong>Range Name       :</strong> <span id="rangeName">{range_name_escaped}</span></div>
          <div><strong>Range Description:</strong> <span id="rangeDesc">{range_description_escaped}</span></div>

          <div><strong>Firing Position  :</strong> <span id="firingPos">{measurements.get("start_lat", "")}, {measurements.get("start_lon", "")}</span></div>
          <div><strong>Firing Altitude  :</strong> <span id="firingAlt">{measurements.get("start_alt", "")}</span></div>
          <div><strong>Firing Address   :</strong> <span id="firingAddr">{html.escape(measurements.get("start_address", ""))}</span></div>
          <div><strong>Target Position  :</strong> <span id="targetPos">{measurements.get("end_lat", "")}, {measurements.get("end_lon", "")}</span></div>
          <div><strong>Target Altitude  :</strong> <span id="targetAlt">{measurements.get("end_alt", "")}</span></div>
          <div><strong>Target Address   :</strong> <span id="targetAddr">{html.escape(measurements.get("end_address", ""))}</span></div>
          <div><strong>Distance (2D)    :</strong> <span id="distance2d">{measurements.get("distance_2d", "")}</span></div>
          <div><strong>Distance (3D)    :</strong> <span id="distance3d">{measurements.get("distance_3d", "")}</span></div>
          <div><strong>Azimuth Angle    :</strong> <span id="azimuth">{measurements.get("azimuth", "")}</span></div>
          <div><strong>Elevation Angle  :</strong> <span id="elevation">{measurements.get("elevation_angle", "")}</span></div>
          <div><strong>Elevation Change :</strong> <span id="elevChange">{measurements.get("elevation_change", "")}</span></div>
          <div><strong>Location         :</strong> <span id="location">{location_escaped}</span></div>
        </div>
        """

        st.markdown(html_table, unsafe_allow_html=True)

        # Submit button (only show if we have complete measurement data)
        if has_complete_data:
            if st.button("Submit Range Data", type="primary"):
                return {
                    "action": "submit",
                    "range": {
                        "range_name": range_name,
                        "range_description": range_description,
                        "measurements": measurements,
                    },
                }
        else:
            st.info("📍 Select two points on the map to enable range submission")

        return None

    def create_map(
        self,
        map_center: List[float],
        zoom_level: int,
        points: List[List[float]],
        disable_draw: bool = False,
    ) -> folium.Map:
        """Create and configure the folium map."""
        # Build the map with satellite imagery
        m = folium.Map(
            location=map_center,
            zoom_start=zoom_level,
            tiles=None,  # Start with no base layer
        )

        # Add satellite imagery as base layer
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

        # Add locate control
        LocateControl().add_to(m)
        m.get_root().add_child(CssInjector(self.cursor_css))

        # Add draw plugin with specific configuration to allow multiple markers
        draw = Draw(
            export=True,
            draw_options={
                "polyline": False,
                "polygon": False,
                "circle": False,
                "rectangle": False,
                "marker": not disable_draw,  # Disable marker tool when we have 2 points
                "circlemarker": False,
            },
            edit_options={"edit": True, "remove": True},
        )
        draw.add_to(m)

        # Add existing points with color-coded markers
        for i, point in enumerate(points):
            color = "blue" if i == 0 else "red"

            # Handle both list [lat, lng] and dict {"lat": lat, "lng": lng}
            # formats
            if isinstance(point, dict):
                lat = point.get("lat", 0)
                lng = point.get("lng", 0)
            else:
                lat = point[0]
                lng = point[1]

            folium.Marker(
                location=[
                    lat, lng], icon=folium.Icon(
                    color=color)).add_to(m)

        # Draw line between two points
        if len(points) == 2:
            # Convert points to proper format for PolyLine
            polyline_points = []
            for point in points:
                if isinstance(point, dict):
                    lat = point.get("lat", 0)
                    lng = point.get("lng", 0)
                else:
                    lat = point[0]
                    lng = point[1]
                polyline_points.append([lat, lng])

            folium.PolyLine(
                polyline_points, color="yellow", weight=3, opacity=0.8
            ).add_to(m)

        return m

    def display_map(self, m: folium.Map) -> Dict[str, Any]:
        """Display the map and return interaction data."""
        map_info = st_folium(
            m, use_container_width=True, height=600, key="nominate_map"
        )
        return map_info

    def display_reset_button(self) -> bool:
        """Display reset button and return True if clicked."""
        return st.button("Reset")

    def display_spinner(self, message: str):
        """Return a spinner context manager."""
        return st.spinner(message)

    def display_map_events(self, map_info: Dict[str, Any]) -> None:
        """Show only non-null events from map_info for debugging."""
        if not map_info:
            return
        filtered = {k: v for k, v in map_info.items() if v is not None}
        if filtered:
            print("Map event data:", filtered)
            print("")
