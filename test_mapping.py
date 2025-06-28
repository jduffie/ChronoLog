import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import math
from branca.element import MacroElement
from jinja2 import Template
import pandas as pd

st.title("Select Two Points to Compute Azimuth and Distance")

# Initialize session state
if "points" not in st.session_state:
    st.session_state.points = []

# Pre-fill table with empty or partial data
table_data = {
    "Start Latitude": [""],
    "Start Longitude": [""],
    "End Latitude": [""],
    "End Longitude": [""],
    "Distance (km)": [""],
    "Azimuth (°)": [""]
}

if len(st.session_state.points) >= 1:
    p1 = st.session_state.points[0]
    table_data["Start Latitude"][0] = f"{p1[0]:.6f}"
    table_data["Start Longitude"][0] = f"{p1[1]:.6f}"

if len(st.session_state.points) == 2:
    p2 = st.session_state.points[1]
    distance_km = geodesic(p1, p2).kilometers

    def calculate_bearing(pointA, pointB):
        lat1, lon1 = math.radians(pointA[0]), math.radians(pointA[1])
        lat2, lon2 = math.radians(pointB[0]), math.radians(pointB[1])
        dLon = lon2 - lon1
        x = math.sin(dLon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
        initial_bearing = math.atan2(x, y)
        return (math.degrees(initial_bearing) + 360) % 360

    azimuth = calculate_bearing(p1, p2)
    table_data["End Latitude"][0] = f"{p2[0]:.6f}"
    table_data["End Longitude"][0] = f"{p2[1]:.6f}"
    table_data["Distance (km)"][0] = f"{distance_km:.2f}"
    table_data["Azimuth (°)"][0] = f"{azimuth:.2f}"

st.table(pd.DataFrame(table_data))
cursor_css = """
<style>
    .leaflet-container {
        cursor: crosshair !important;
    }
</style>
"""
# Add it to the map using MacroElement
class CssInjector(MacroElement):
    def __init__(self, css_string):
        super().__init__()
        self._template = Template(f"""
        {{% macro header(this, kwargs) %}}
            {css_string}
        {{% endmacro %}}
        """)

# Initial map center
map_center = [37.76, -122.4]


# Build the map
m = folium.Map(location=map_center, zoom_start=13)
m.get_root().add_child(CssInjector(cursor_css))

# Add existing points with color-coded markers
for i, point in enumerate(st.session_state.points):
    color = 'blue' if i == 0 else 'red'
    folium.Marker(
        location=[point[0], point[1]],
        icon=folium.Icon(color=color)
    ).add_to(m)

click_info = st_folium(m, width=700, height=500)

# When a point is clicked
if click_info:
    if click_info.get("last_clicked"):
        latlon = [
            click_info["last_clicked"]["lat"],
            click_info["last_clicked"]["lng"]
        ]
        st.info(f":lat {latlon[0]:.2f} ")
        st.info(f":lon {latlon[1]:.2f} ")

        if len(st.session_state.points) < 2:
            st.session_state.points.append(latlon)
            st.rerun()


# Add a reset button (always show if any points present)
if len(st.session_state.points) > 0:
    if st.button("Reset"):
        st.session_state.points = []
