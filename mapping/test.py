import streamlit as st
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim

st.title("Define Start and End Points")
st.markdown("""
    <style>
        .folium-map {
            cursor: pointer !important;
        }
    </style>
""", unsafe_allow_html=True)

# Default location (e.g., San Francisco)
default_lat, default_lon = 37.76, -122.4
lat, lon = default_lat, default_lon

# User input: Address or lat/lon
search_method = st.radio("Move map by:", ["Address", "Lat/Lon"])

if search_method == "Address":
    address = st.text_input("Enter address:")
    if address:
        try:
            geolocator = Nominatim(user_agent="map_locator")
            location = geolocator.geocode(address)
            if location:
                lat, lon = location.latitude, location.longitude
            else:
                st.warning("Address not found. Using default location.")
        except Exception as e:
            st.error(f"Geocoding error: {e}")
else:
    lat = st.number_input("Latitude", value=default_lat, format="%.6f")
    lon = st.number_input("Longitude", value=default_lon, format="%.6f")

# Render the map centered on the resolved lat/lon
m = folium.Map(location=[lat, lon], zoom_start=15)
# Add locate control and geocoder
LocateControl().add_to(m)
m.get_root().add_child(CssInjector(self.cursor_css))
Geocoder().add_to(m)

st.markdown("Click on the map to set start and stop points (in order).")

# Handle point clicks
if "points" not in st.session_state:
    st.session_state.points = []

map_data = st_folium(m, width=700, height=500)

if map_data and map_data.get("last_clicked") and len(st.session_state.points) < 2:
    clicked = map_data["last_clicked"]
    st.session_state.points.append(clicked)
    folium.Marker([clicked["lat"], clicked["lng"]],
                  popup="Start" if len(st.session_state.points) == 1 else "Stop").add_to(m)

# Display selected points
if st.session_state.points:
    st.write("Selected Points:")
    for i, point in enumerate(st.session_state.points):
        label = "Start" if i == 0 else "Stop"
        st.write(f"{label}: {point['lat']:.6f}, {point['lng']:.6f}")