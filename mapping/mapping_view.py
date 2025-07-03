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
        
        # Check if we have complete data for submission
        has_complete_data = (measurements.get("start_lat") and measurements.get("start_lon") and 
                            measurements.get("end_lat") and measurements.get("end_lon"))
        
        # Get form values
        range_name_value = st.session_state.get("range_name", "")
        range_description_value = st.session_state.get("range_description", "")
        
        html_table = f"""
        <div class="output">
          <div><strong>Range Name:</strong> <span id="rangeName">{range_name_value}</span></div>
          <div><strong>Firing Position:</strong> <span id="firingPos">{measurements.get("start_lat", "")}, {measurements.get("start_lon", "")}</span></div>
          <div><strong>Target Position:</strong> <span id="targetPos">{measurements.get("end_lat", "")}, {measurements.get("end_lon", "")}</span></div>
          <div><strong>Distance:</strong> <span id="distance">{measurements.get("distance", "")}</span></div>
          <div><strong>Azimuth Angle:</strong> <span id="azimuth">{measurements.get("azimuth", "")}</span></div>
          <div><strong>Elevation Angle:</strong> <span id="elevation">{measurements.get("elevation_angle", "")}</span></div>
          <div><strong>Location:</strong> <span id="location">{location_display}</span></div>
          <div><strong>Range Description:</strong> <span id="rangeDesc">{range_description_value}</span></div>
        </div>
        """
        
        st.markdown(html_table, unsafe_allow_html=True)
        
        # Form inputs below the table
        st.markdown("### Range Information")
        range_name = st.text_input("Range Name", value=range_name_value, key="range_name", placeholder="Enter range name")
        range_description = st.text_area("Range Description", value=range_description_value, key="range_description", placeholder="Enter a description for this range", height=100)
        
        # Submit button (only show if we have complete measurement data)
        if has_complete_data:
            if st.button("Submit Range Data", type="primary"):

                return {
                    "action": "submit",
                    "range": {
                        "range_name": range_name,
                        "range_description": range_description,
                        "measurements": measurements
                    }
                }
        else:
            st.info("📍 Select two points on the map to enable range submission")
            
        return None

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
        return st_folium(m, use_container_width=True, height=500)

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

    def display_ranges_table(self, ranges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Display a table of submitted ranges with checkbox selection and actions."""
        if not ranges:
            st.info("📍 No ranges submitted yet.")
            return {"action": None, "selected_indices": []}
            
        st.subheader(f"You have ({len(ranges)}) ranges")
        
        # Prepare data for display with checkboxes
        table_data = []
        for i, range_data in enumerate(ranges):
            # Format the submitted date
            submitted_at = range_data.get('submitted_at', '')
            if submitted_at:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_date = submitted_at[:16]  # Fallback to first 16 chars
            else:
                formatted_date = 'Unknown'
            
            table_data.append({
                'Select': False,  # Checkbox column
                'Name': range_data.get('range_name', ''),
                'Status': range_data.get('status', 'Under Review'),
                'Description': range_data.get('range_description', '')[:50] + ('...' if len(range_data.get('range_description', '')) > 50 else ''),
                'Distance (m)': f"{range_data.get('distance_m', 0):.1f}",
                'Azimuth (°)': f"{range_data.get('azimuth_deg', 0):.1f}",
                'Elevation (°)': f"{range_data.get('elevation_angle_deg', 0):.2f}",
                'Location': range_data.get('display_name', '')[:40] + ('...' if len(range_data.get('display_name', '')) > 40 else ''),
                'Submitted': formatted_date
            })
        
        # Display as an editable dataframe with checkboxes
        import pandas as pd
        df = pd.DataFrame(table_data)
        
        # Use st.data_editor with checkbox column
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Select": st.column_config.CheckboxColumn("Select", width="small", default=False),
                "Name": st.column_config.TextColumn("Name", width="medium", disabled=True),
                "Status": st.column_config.TextColumn("Status", width="small", disabled=True),
                "Description": st.column_config.TextColumn("Description", width="large", disabled=True),
                "Distance (m)": st.column_config.TextColumn("Distance (m)", width="small", disabled=True),
                "Azimuth (°)": st.column_config.TextColumn("Azimuth (°)", width="small", disabled=True),
                "Elevation (°)": st.column_config.TextColumn("Elevation (°)", width="small", disabled=True),
                "Location": st.column_config.TextColumn("Location", width="large", disabled=True),
                "Submitted": st.column_config.TextColumn("Submitted", width="medium", disabled=True)
            },
            key="ranges_table_checkboxes"
        )
        
        # Get selected rows
        selected_indices = []
        if edited_df is not None:
            selected_rows = edited_df[edited_df['Select'] == True]
            selected_indices = selected_rows.index.tolist()
        
        # Selection controls
        col1, col2 = st.columns([4, 1])
        
        with col1:
            if selected_indices:
                st.info(f"📋 {len(selected_indices)} range(s) selected")
            else:
                st.info("📍 Check boxes in the table above to select ranges")
        
        action_result = {"action": None, "selected_indices": selected_indices}
        
        with col2:
            # DELETE button - always visible, disabled when no selection
            if st.button("🗑️ DELETE", use_container_width=True, type="secondary", disabled=not bool(selected_indices)):
                if selected_indices:
                    # Store the delete action and selected indices in session state
                    st.session_state["delete_selected_ranges"] = selected_indices
                    action_result["action"] = "delete"
        
        # Check if we have a persisted delete selection first
        if "delete_selected_ranges" in st.session_state:
            action_result["action"] = "delete"
            action_result["selected_indices"] = st.session_state["delete_selected_ranges"]
        # Auto-map selected ranges - any selected ranges should be mapped immediately
        elif selected_indices:
            action_result["action"] = "map"
            action_result["selected_indices"] = selected_indices
        
        return action_result

    def display_ranges_map(self, ranges: List[Dict[str, Any]], selected_indices: List[int] = None) -> folium.Map:
        """Display a map with selected ranges plotted."""
        # Default map center
        map_center = [36.222278, -78.051833]
        zoom_start = 12
        
        # Collect all coordinates for selected ranges to calculate bounds
        all_coords = []
        if selected_indices and ranges:
            for idx in selected_indices:
                if idx < len(ranges):
                    range_data = ranges[idx]
                    start_lat = range_data.get('start_lat')
                    start_lon = range_data.get('start_lon')
                    end_lat = range_data.get('end_lat')
                    end_lon = range_data.get('end_lon')
                    
                    if start_lat and start_lon:
                        all_coords.append([float(start_lat), float(start_lon)])
                    if end_lat and end_lon:
                        all_coords.append([float(end_lat), float(end_lon)])
            
            # If we have coordinates, calculate center and appropriate zoom
            if all_coords:
                # Calculate bounds
                lats = [coord[0] for coord in all_coords]
                lons = [coord[1] for coord in all_coords]
                
                min_lat, max_lat = min(lats), max(lats)
                min_lon, max_lon = min(lons), max(lons)
                
                # Calculate center
                map_center = [(min_lat + max_lat) / 2, (min_lon + max_lon) / 2]
                
                # Calculate appropriate zoom level based on bounds
                lat_diff = max_lat - min_lat
                lon_diff = max_lon - min_lon
                max_diff = max(lat_diff, lon_diff)
                
                # Adjust zoom based on coordinate span
                if max_diff < 0.01:  # Very close points
                    zoom_start = 15
                elif max_diff < 0.05:  # Close points
                    zoom_start = 13
                elif max_diff < 0.1:   # Medium distance
                    zoom_start = 11
                elif max_diff < 0.5:   # Far points
                    zoom_start = 9
                else:  # Very far points
                    zoom_start = 7
        
        # Create map
        m = folium.Map(
            location=map_center,
            zoom_start=zoom_start,
            tiles=None
        )
        
        # Add satellite imagery
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
        
        folium.LayerControl().add_to(m)
        
        # Plot selected ranges
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
        
        if selected_indices:
            for i, idx in enumerate(selected_indices):
                if idx < len(ranges):
                    range_data = ranges[idx]
                    color = colors[i % len(colors)]
                    
                    # Get coordinates
                    start_lat = float(range_data.get('start_lat', 0))
                    start_lon = float(range_data.get('start_lon', 0))
                    end_lat = float(range_data.get('end_lat', 0))
                    end_lon = float(range_data.get('end_lon', 0))
                    
                    if start_lat and start_lon and end_lat and end_lon:
                        # Add firing position marker
                        folium.Marker(
                            location=[start_lat, start_lon],
                            popup=f"🎯 {range_data.get('range_name', 'Range')} - Firing Position",
                            tooltip=f"Firing Position: {range_data.get('range_name', 'Range')}",
                            icon=folium.Icon(color=color, icon='play')
                        ).add_to(m)
                        
                        # Add target position marker
                        folium.Marker(
                            location=[end_lat, end_lon],
                            popup=f"🎯 {range_data.get('range_name', 'Range')} - Target",
                            tooltip=f"Target: {range_data.get('range_name', 'Range')}",
                            icon=folium.Icon(color=color, icon='stop')
                        ).add_to(m)
                        
                        # Add line between points
                        folium.PolyLine(
                            [[start_lat, start_lon], [end_lat, end_lon]],
                            color=color,
                            weight=3,
                            opacity=0.8,
                            popup=f"{range_data.get('range_name', 'Range')}<br>Distance: {range_data.get('distance_m', 0):.1f}m"
                        ).add_to(m)
        
        return m
