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

    def _extract_address_components(self, range_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract county, state, and country from address_geojson."""
        try:
            address_geojson = range_data.get('address_geojson', {})
            if isinstance(address_geojson, dict) and 'features' in address_geojson:
                features = address_geojson['features']
                if features and len(features) > 0:
                    # Get the firing position feature (first feature)
                    firing_position = features[0]
                    if 'properties' in firing_position and 'address' in firing_position['properties']:
                        address = firing_position['properties']['address']
                        return {
                            'county': address.get('county', ''),
                            'state': address.get('state', ''),
                            'country': address.get('country', '')
                        }
        except (TypeError, KeyError, IndexError):
            pass
        
        return {'county': '', 'state': '', 'country': ''}

    def display_title(self) -> None:
        """Display the main title."""
        st.title("Nominate New Range")

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
        
        # Escape HTML and handle newlines properly
        import html
        range_name_escaped = html.escape(range_name_value)
        range_description_escaped = html.escape(range_description_value).replace('\n', '<br>')
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
        range_name = st.text_input("**Range Name**", value=range_name_value, key="range_name", placeholder="Enter range name")
        range_description = st.text_area("**Range Description**", value=range_description_value, key="range_description", placeholder="Enter a description for this range", height=100)

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
            st.info("📍 Submit a new range by selecting firing position and target on the map.")
            
        return None

    def display_range_form_and_table(self, measurements: Dict[str, Any]) -> Dict[str, Any]:
        """Display range form inputs and measurements table in the correct order."""
        # Check if we have complete data for submission
        has_complete_data = (measurements.get("start_lat") and measurements.get("start_lon") and 
                            measurements.get("end_lat") and measurements.get("end_lon"))
        
        # Get form values
        range_name_value = st.session_state.get("range_name", "")
        range_description_value = st.session_state.get("range_description", "")
        
        # Range form inputs
        st.markdown("### Range Information")
        range_name = st.text_input("Range Name", value=range_name_value, key="range_name", placeholder="Enter range name")
        range_description = st.text_area("Range Description", value=range_description_value, key="range_description", placeholder="Enter a description for this range", height=100)
        
        # Get display name from GeoJSON response
        location_display = measurements.get("display_name", "")
        
        # Escape HTML and handle newlines properly
        import html
        range_name_escaped = html.escape(range_name)
        range_description_escaped = html.escape(range_description).replace('\n', '<br>')
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
            
            # Format review reason
            review_reason = range_data.get('review_reason', '')
            if review_reason:
                review_reason_display = review_reason[:30] + ('...' if len(review_reason) > 30 else '')
            else:
                review_reason_display = ''
            
            # Extract address components
            address_components = self._extract_address_components(range_data)
            
            table_data.append({
                'Select': False,  # Checkbox column
                'Name': range_data.get('range_name', ''),
                'Status': range_data.get('status', 'Under Review'),
                'Review Comments': review_reason_display,
                'Description': range_data.get('range_description', '')[:40] + ('...' if len(range_data.get('range_description', '')) > 40 else ''),
                'Distance 2D (m)': f"{range_data.get('distance_m', 0):.1f}",
                'Firing Alt (m)': f"{range_data.get('start_altitude_m', 0):.1f}",
                'Target Alt (m)': f"{range_data.get('end_altitude_m', 0):.1f}",
                'Azimuth (°)': f"{range_data.get('azimuth_deg', 0):.1f}",
                'Elevation (°)': f"{range_data.get('elevation_angle_deg', 0):.2f}",
                'Elev Change (m)': f"{range_data.get('end_altitude_m', 0) - range_data.get('start_altitude_m', 0):.1f}",
                'County': address_components['county'],
                'State': address_components['state'],
                'Country': address_components['country'],
                'Location': range_data.get('display_name', '')[:30] + ('...' if len(range_data.get('display_name', '')) > 30 else ''),
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
                "Review Comments": st.column_config.TextColumn("Review Reason", width="medium", disabled=True),
                "Description": st.column_config.TextColumn("Description", width="large", disabled=True),
                "Distance 2D (m)": st.column_config.TextColumn("Distance 2D (m)", width="small", disabled=True),
                "Firing Alt (m)": st.column_config.TextColumn("Firing Alt (m)", width="small", disabled=True),
                "Target Alt (m)": st.column_config.TextColumn("Target Alt (m)", width="small", disabled=True),
                "Azimuth (°)": st.column_config.TextColumn("Azimuth (°)", width="small", disabled=True),
                "Elevation (°)": st.column_config.TextColumn("Elevation (°)", width="small", disabled=True),
                "Elev Change (m)": st.column_config.TextColumn("Elev Change (m)", width="small", disabled=True),
                "County": st.column_config.TextColumn("County", width="medium", disabled=True),
                "State": st.column_config.TextColumn("State", width="medium", disabled=True),
                "Country": st.column_config.TextColumn("Country", width="medium", disabled=True),
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

    def display_public_ranges_table_readonly(self, ranges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Display a read-only table of public ranges."""
        if not ranges:
            st.info("🌍 No public ranges available yet.")
            return {"action": None, "selected_indices": []}
            
        st.subheader(f"Public Ranges ({len(ranges)})")
        
        # Prepare data for display
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
            
            # Extract address components
            address_components = self._extract_address_components(range_data)
            
            table_data.append({
                'Name': range_data.get('range_name', ''),
                'Description': range_data.get('range_description', '')[:50] + ('...' if len(range_data.get('range_description', '')) > 50 else ''),
                'Distance (m)': f"{range_data.get('distance_m', 0):.1f}",
                'Firing Alt (m)': f"{range_data.get('start_altitude_m', 0):.1f}",
                'Target Alt (m)': f"{range_data.get('end_altitude_m', 0):.1f}",
                'Azimuth (°)': f"{range_data.get('azimuth_deg', 0):.1f}",
                'Elevation (°)': f"{range_data.get('elevation_angle_deg', 0):.2f}",
                'County': address_components['county'],
                'State': address_components['state'],
                'Country': address_components['country'],
                'Location': range_data.get('display_name', '')[:40] + ('...' if len(range_data.get('display_name', '')) > 40 else ''),
                'Submitted': formatted_date,
                'Contributor': range_data.get('user_email', '')
            })
        
        # Display as a static dataframe
        import pandas as pd
        df = pd.DataFrame(table_data)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Description": st.column_config.TextColumn("Description", width="large"),
                "Distance (m)": st.column_config.TextColumn("Distance (m)", width="small"),
                "Firing Alt (m)": st.column_config.TextColumn("Firing Alt (m)", width="small"),
                "Target Alt (m)": st.column_config.TextColumn("Target Alt (m)", width="small"),
                "Azimuth (°)": st.column_config.TextColumn("Azimuth (°)", width="small"),
                "Elevation (°)": st.column_config.TextColumn("Elevation (°)", width="small"),
                "County": st.column_config.TextColumn("County", width="medium"),
                "State": st.column_config.TextColumn("State", width="medium"),
                "Country": st.column_config.TextColumn("Country", width="medium"),
                "Location": st.column_config.TextColumn("Location", width="large"),
                "Submitted": st.column_config.TextColumn("Submitted", width="medium"),
                "Contributor": st.column_config.TextColumn("Contributor", width="medium")
            }
        )
        
        return {"action": None, "selected_indices": []}

    def display_public_ranges_table_admin(self, ranges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Display an admin table of public ranges with edit/delete capabilities."""
        if not ranges:
            st.info("🌍 No public ranges available yet.")
            return {"action": None, "selected_indices": []}

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
            
            # Extract address components
            address_components = self._extract_address_components(range_data)
            
            table_data.append({
                'Select': False,  # Checkbox column
                'Name': range_data.get('range_name', ''),
                'Description': range_data.get('range_description', '')[:50] + ('...' if len(range_data.get('range_description', '')) > 50 else ''),
                'Distance (m)': f"{range_data.get('distance_m', 0):.1f}",
                'Firing Alt (m)': f"{range_data.get('start_altitude_m', 0):.1f}",
                'Target Alt (m)': f"{range_data.get('end_altitude_m', 0):.1f}",
                'Azimuth (°)': f"{range_data.get('azimuth_deg', 0):.1f}",
                'Elevation (°)': f"{range_data.get('elevation_angle_deg', 0):.2f}",
                'County': address_components['county'],
                'State': address_components['state'],
                'Country': address_components['country'],
                'Location': range_data.get('display_name', '')[:40] + ('...' if len(range_data.get('display_name', '')) > 40 else ''),
                'Submitted': formatted_date,
                'Contributor': range_data.get('user_email', '')
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
                "Description": st.column_config.TextColumn("Description", width="large", disabled=True),
                "Distance (m)": st.column_config.TextColumn("Distance (m)", width="small", disabled=True),
                "Firing Alt (m)": st.column_config.TextColumn("Firing Alt (m)", width="small", disabled=True),
                "Target Alt (m)": st.column_config.TextColumn("Target Alt (m)", width="small", disabled=True),
                "Azimuth (°)": st.column_config.TextColumn("Azimuth (°)", width="small", disabled=True),
                "Elevation (°)": st.column_config.TextColumn("Elevation (°)", width="small", disabled=True),
                "County": st.column_config.TextColumn("County", width="medium", disabled=True),
                "State": st.column_config.TextColumn("State", width="medium", disabled=True),
                "Country": st.column_config.TextColumn("Country", width="medium", disabled=True),
                "Location": st.column_config.TextColumn("Location", width="large", disabled=True),
                "Submitted": st.column_config.TextColumn("Submitted", width="medium", disabled=True),
                "Contributor": st.column_config.TextColumn("Contributor", width="medium", disabled=True)
            },
            key="public_ranges_table_checkboxes"
        )
        
        # Get selected rows
        selected_indices = []
        if edited_df is not None:
            selected_rows = edited_df[edited_df['Select'] == True]
            selected_indices = selected_rows.index.tolist()
        
        # Admin controls
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            if selected_indices:
                st.info(f"📋 {len(selected_indices)} range(s) selected")
            else:
                st.info("📍 Check boxes in the table above to select ranges")
        
        action_result = {"action": None, "selected_indices": selected_indices}
        
        with col2:
            st.info(f"📋 {len(ranges)} range(s) available")

        with col3:
            # DELETE button - always visible, disabled when no selection
            if st.button("🗑️ DELETE", use_container_width=True, type="secondary", disabled=not bool(selected_indices)):
                if selected_indices:
                    # Store the delete action and selected indices in session state
                    st.session_state["delete_selected_public_ranges"] = selected_indices
                    action_result["action"] = "delete"
        
        # Check if we have a persisted delete selection first
        if "delete_selected_public_ranges" in st.session_state:
            action_result["action"] = "delete"
            action_result["selected_indices"] = st.session_state["delete_selected_public_ranges"]
        # Auto-map selected ranges - any selected ranges should be mapped immediately
        elif selected_indices:
            action_result["action"] = "map"
            action_result["selected_indices"] = selected_indices
        
        return action_result
