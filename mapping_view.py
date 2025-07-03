import streamlit as st
import folium
from streamlit_folium import st_folium
from branca.element import MacroElement
from jinja2 import Template
from folium.plugins import LocateControl, Geocoder
from typing import List, Dict, Any


class CssInjector(MacroElement):
    def __init__(self, css_string):
        super().__init__()
        self._template = Template(f"""
        {{% macro header(this, kwargs) %}}
            {css_string}
        {{% endmacro %}}
        """)


class MappingView:
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
        st.title("Select Two Points to Collect Altitude, Range, Azimuth, and Elevation")

    def display_measurements_table(self, measurements: Dict[str, Any]) -> None:
        """Display the measurements table using HTML."""
        # Get display name from GeoJSON response
        location_display = measurements.get("display_name", "")
        
        html_table = f"""
        <div>
            <label for="rangeName">Name:</label>
            <input type="text" id="rangeName" placeholder="Enter range name" />
            <br><br>
            <label for="rangeDescription">Description:</label>
            <textarea id="rangeDescription" placeholder="Enter range description" rows="3" style="width: 100%;"></textarea>
            <br><br>
            <div class="output">
              <div><strong>Firing Position:</strong> <span id="firingPos">{measurements.get("start_lat", "")}, {measurements.get("start_lon", "")}</span></div>
              <div><strong>Target Position:</strong> <span id="targetPos">{measurements.get("end_lat", "")}, {measurements.get("end_lon", "")}</span></div>
              <div><strong>Distance:</strong> <span id="distance">{measurements.get("distance", "")}</span></div>
              <div><strong>Azimuth Angle:</strong> <span id="azimuth">{measurements.get("azimuth", "")}</span></div>
              <div><strong>Elevation Angle:</strong> <span id="elevation">{measurements.get("elevation_angle", "")}</span></div>
              <div><strong>Location:</strong> <span id="location">{location_display}</span></div>
            </div>
        </div>
        """
        
        st.markdown(html_table, unsafe_allow_html=True)

    def create_map(self, map_center: List[float], zoom_level: int, points: List[List[float]]) -> folium.Map:
        """Create and configure the folium map."""
        # Build the map with satellite imagery
        m = folium.Map(
            location=map_center, 
            zoom_start=zoom_level,
            tiles=None  # Start with no base layer
        )

        # Add satellite imagery as base layer
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False,
            control=True
        ).add_to(m)

        # Add road overlay
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Roads',
            overlay=True,
            control=True,
            opacity=0.7
        ).add_to(m)

        # Add layer control
        folium.LayerControl().add_to(m)

        # Add locate control and geocoder
        LocateControl().add_to(m)
        m.get_root().add_child(CssInjector(self.cursor_css))
        Geocoder().add_to(m)

        # Add existing points with color-coded markers
        for i, point in enumerate(points):
            color = 'blue' if i == 0 else 'red'
            folium.Marker(
                location=[point[0], point[1]],
                icon=folium.Icon(color=color)
            ).add_to(m)

        # Draw line between two points
        if len(points) == 2:
            folium.PolyLine(
                points,
                color="yellow",
                weight=3,
                opacity=0.8
            ).add_to(m)

        return m

    def display_map(self, m: folium.Map) -> Dict[str, Any]:
        """Display the map and return interaction data."""
        return st_folium(m, width=700, height=500)

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
