import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import math
from branca.element import MacroElement
from jinja2 import Template
import pandas as pd
import requests
from folium.plugins import LocateControl
from folium.plugins import Geocoder
from branca.element import MacroElement
from jinja2 import Template



prev_session_state = dict(st.session_state)

# log the current session_state
# print("Session State:", st.session_state)
filtered = {k: v for k, v in st.session_state.items() if v is not None}
if filtered:
    print("Starting State:", st.session_state)
    print("")

st.title("Register Range Entry")

# Initialize session state
if "points" not in st.session_state:
    st.session_state.points = []
if "elevations_m" not in st.session_state:
    st.session_state.elevations_m = []
if "map_center" not in st.session_state:
    st.session_state.map_center = [36.222278, -78.051833]  # Default: 36°13'20.2"N 78°03'06.6"W
if "zoom_level" not in st.session_state:
    st.session_state.zoom_level = 13

# st.header("Enter Description")
# description_input = st.text_area("Description:", value=st.session_state.get("description", ""), height=68)
# st.session_state.description = description_input

def display_map_events(map_info):
    """Show only non-null events from map_info."""
    if not map_info:
        return
    filtered = {k: v for k, v in map_info.items() if v is not None}
    if filtered:
        print("Map event data:", filtered)
        print("")

# Function to get elevation from Open Elevation API
def get_elevation(lat, lng):
    """Get elevation in meters from Open Elevation API"""
    try:
        url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lng}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        elevation_m = data['results'][0]['elevation']
        # elevation_ft = elevation_m * 3.28084  # Convert meters to feet
        return elevation_m
    except Exception as e:
        st.warning(f"Could not fetch elevation data: {e}")
        return 0.0


# Display elevation fetching status
if len(st.session_state.points) > 0 and len(st.session_state.elevations_m) < len(st.session_state.points):
    with st.spinner("Fetching elevation data..."):
        # Fetch missing elevations_m
        for i in range(len(st.session_state.elevations_m), len(st.session_state.points)):
            point = st.session_state.points[i]
            elevation_m = get_elevation(point[0], point[1])
            st.session_state.elevations_m.append(elevation_m)

# Pre-fill table with empty or partial data
table_data = {
    "Start Latitude": [""],
    "Start Longitude": [""],
    "Start Altitude (m)": [""],
    "End Latitude": [""],
    "End Longitude": [""],
    "End Altitude (m)": [""],
    "Distance (m)": [""],
    "Azimuth (°)": [""],
    "Elevation Angle (°)": [""]
}

if len(st.session_state.points) >= 1 and len(st.session_state.elevations_m) >= 1:
    p1 = st.session_state.points[0]
    table_data["Start Latitude"][0] = f"{p1[0]:.6f}"
    table_data["Start Longitude"][0] = f"{p1[1]:.6f}"
    table_data["Start Altitude (m)"][0] = f"{st.session_state.elevations_m[0]:.1f}"

if len(st.session_state.points) == 2 and len(st.session_state.elevations_m) == 2:
    p2 = st.session_state.points[1]
    distance_m = geodesic(p1, p2).m

    def calculate_bearing(pointA, pointB):
        lat1, lon1 = math.radians(pointA[0]), math.radians(pointA[1])
        lat2, lon2 = math.radians(pointB[0]), math.radians(pointB[1])
        dLon = lon2 - lon1
        x = math.sin(dLon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
        initial_bearing = math.atan2(x, y)
        return (math.degrees(initial_bearing) + 360) % 360

    azimuth = calculate_bearing(p1, p2)

    # Calculate elevation angle
    elevation_diff_m = st.session_state.elevations_m[1] - st.session_state.elevations_m[0]
    elevation_angle = math.degrees(math.atan2(elevation_diff_m, distance_m))

    table_data["End Latitude"][0] = f"{p2[0]:.6f}"
    table_data["End Longitude"][0] = f"{p2[1]:.6f}"
    table_data["End Altitude (m)"][0] = f"{st.session_state.elevations_m[1]:.1f}"
    table_data["Distance (m)"][0] = f"{distance_m:.2f}"
    table_data["Azimuth (°)"][0] = f"{azimuth:.2f}"
    table_data["Elevation Angle (°)"][0] = f"{elevation_angle:.2f}"

st.header("Select Two Points to Collect Altitude, Range, Azimuth, and Elevation")

# Create HTML table based on test.html format
html_table = """
<label for="rangeName">Name:</label>
<input type="text" id="rangeName" placeholder="Enter range name" />
    <div class="output">
      <div><strong>Firing Position:</strong> <span id="firingPos">{start_lat}, {start_lon}</span></div>
      <div><strong>Target Position:</strong> <span id="targetPos">33.6690, -117.8660</span></div>
      <div><strong>Range:</strong> <span id="range">405.5 m</span></div>
      <div><strong>Azimuth Angle:</strong> <span id="azimuth">34.7°</span></div>
      <div><strong>Elevation Angle:</strong> <span id="elevation">-3.2°</span></div>
</div>
""".format(
    start_lat=table_data["Start Latitude"][0],
    start_lon=table_data["Start Longitude"][0],
    start_alt=table_data["Start Altitude (m)"][0],
    range=table_data["Distance (m)"][0],
    azimuth=table_data["Azimuth (°)"][0],
    elevation=table_data["Elevation Angle (°)"][0],
    end_lat=table_data["End Latitude"][0],
    end_lon=table_data["End Longitude"][0],
    end_alt=table_data["End Altitude (m)"][0],
    description=st.session_state.get("description", "")
)
st.markdown(html_table, unsafe_allow_html=True)
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

# Build the map with satellite imagery
m = folium.Map(
    location=st.session_state.map_center, 
    zoom_start=st.session_state.zoom_level,
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

LocateControl().add_to(m)
m.get_root().add_child(CssInjector(cursor_css))
Geocoder().add_to(m)

# Add existing points with color-coded markers
for i, point in enumerate(st.session_state.points):
    color = 'blue' if i == 0 else 'red'
    folium.Marker(
        location=[point[0], point[1]],
        icon=folium.Icon(color=color)
    ).add_to(m)

if len(st.session_state.points) == 2:
    # Draw a line between the two points
    folium.PolyLine(
        st.session_state.points,
        color="yellow",
        weight=3,
        opacity=0.8
    ).add_to(m)

map_info = st_folium(m, width=700, height=500)
display_map_events(map_info)


# When a point is clicked or map is moved
if map_info:
    if map_info.get("last_clicked"):
        latlon = [
            map_info["last_clicked"]["lat"],
            map_info["last_clicked"]["lng"]
        ]
        if len(st.session_state.points) < 2:
            st.session_state.points.append(latlon)
            st.rerun()
    if map_info.get("center"):
        st.session_state.map_center = [
            map_info["center"]["lat"],
            map_info["center"]["lng"]
        ]
    if map_info.get("zoom"):
        st.session_state.zoom_level = map_info["zoom"]


# Add a reset button (always show if any points present)
if len(st.session_state.points) > 0:
    if st.button("Reset"):
        st.session_state.points = []
        st.session_state.elevations_m = []
        st.rerun()

#st.subheader("Changed Session State Values")
#
changes = {k: v for k, v in st.session_state.items() if prev_session_state.get(k) != v}
if changes:
     print("STATE changes:", changes)
else:
     print("No STATE changes in this run.")

print("_______________________________________")
print("  ")
print("  ")
print("  ")
