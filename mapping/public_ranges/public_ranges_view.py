import streamlit as st
import folium
from typing import List, Dict, Any


class PublicRangesView:
    def __init__(self):
        pass

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

    def display_public_ranges_table_readonly(self, ranges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Display a read-only table of public ranges."""
        return self._display_public_ranges_table(ranges, is_admin=False)

    def display_public_ranges_table_admin(self, ranges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Display an admin table of public ranges with edit/delete capabilities."""
        return self._display_public_ranges_table(ranges, is_admin=True)

    def _display_public_ranges_table(self, ranges: List[Dict[str, Any]], is_admin: bool = False) -> Dict[str, Any]:
        """Internal method to display public ranges table with optional admin controls."""
        if not ranges:
            st.info("🌍 No public ranges available yet.")
            return {"action": None, "selected_indices": []}

        # Extract all unique states for dropdown
        all_states = set()
        for range_data in ranges:
            address_components = self._extract_address_components(range_data)
            state = address_components.get('state', '').strip()
            if state:
                all_states.add(state)
        
        # Search controls
        st.subheader("🔍 Search & Filter")
        col1, col2 = st.columns(2)
        
        with col1:
            # State dropdown filter - use different keys for admin vs readonly
            state_key = "public_ranges_admin_state_filter" if is_admin else "public_ranges_state_filter"
            state_options = ["All States"] + sorted(list(all_states))
            selected_state = st.selectbox(
                "Filter by State:",
                options=state_options,
                index=0,
                key=state_key
            )
        
        with col2:
            # Location text search - use different keys for admin vs readonly
            location_key = "public_ranges_admin_location_search" if is_admin else "public_ranges_location_search"
            location_search = st.text_input(
                "Search Location:",
                placeholder="Enter city, county, or location name...",
                key=location_key
            )
        
        # Apply filters
        filtered_ranges = ranges.copy()
        
        # Filter by state
        if selected_state != "All States":
            filtered_ranges = [
                range_data for range_data in filtered_ranges
                if self._extract_address_components(range_data).get('state', '') == selected_state
            ]
        
        # Filter by location text search
        if location_search:
            search_lower = location_search.lower()
            filtered_ranges = [
                range_data for range_data in filtered_ranges
                if search_lower in range_data.get('display_name', '').lower()
            ]
        
        # Show filtered count
        if len(filtered_ranges) != len(ranges):
            st.info(f"📍 Showing {len(filtered_ranges)} of {len(ranges)} ranges")
        else:
            if not is_admin:
                st.subheader(f"Public Ranges ({len(ranges)})")
        
        # Check if no results after filtering
        if not filtered_ranges:
            st.warning("🔍 No ranges match your search criteria. Try adjusting your filters.")
            return {"action": None, "selected_indices": []}

        # Prepare data for display with checkboxes
        table_data = []
        for i, range_data in enumerate(filtered_ranges):
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
                'Distance (m)': f"{range_data.get('distance_m', 0):.1f}",
                'Firing lat': f"{range_data.get('start_lat', 0):.6f}",
                'Firing lon': f"{range_data.get('start_lon', 0):.6f}",
                'Firing alt (m)': f"{range_data.get('start_altitude_m', 0):.1f}",
                'Azimuth angle (°)': f"{range_data.get('azimuth_deg', 0):.1f}",
                'Elevation angle (°)': f"{range_data.get('elevation_angle_deg', 0):.2f}",
                'Elevation change (m)': f"{range_data.get('start_altitude_m', 0) - range_data.get('end_altitude_m', 0):.1f}",
                'County': address_components['county'],
                'State': address_components['state'],
                'Country': address_components['country'],
                'Location': range_data.get('display_name', '')[:85] + ('...' if len(range_data.get('display_name', '')) > 85 else ''),
                'Description': range_data.get('range_description', '')[:50] + ('...' if len(range_data.get('range_description', '')) > 50 else ''),
                'Submitted': formatted_date
            })
        
        # Display as an editable dataframe with checkboxes
        import pandas as pd
        df = pd.DataFrame(table_data)
        
        # Use different keys for admin vs readonly to avoid conflicts
        table_key = "public_ranges_table_checkboxes" if is_admin else "public_ranges_readonly_table_checkboxes"
        
        # Use st.data_editor with checkbox column
        edited_df = (st.data_editor
            (
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Select": st.column_config.CheckboxColumn("Select", width="small", default=False),
                "Name": st.column_config.TextColumn("Name", width="medium", disabled=True),
                "Distance (m)": st.column_config.TextColumn("Distance (m)", width="small", disabled=True),
                "Firing lat": st.column_config.TextColumn("Firing lat", width="small", disabled=True),
                "Firing lon": st.column_config.TextColumn("Firing lon", width="small", disabled=True),
                "Firing alt (m)": st.column_config.TextColumn("Firing alt (m)", width="small", disabled=True),
                "Azimuth angle (°)": st.column_config.TextColumn("Azimuth angle (°)", width="small", disabled=True),
                "Elevation angle (°)": st.column_config.TextColumn("Elevation angle (°)", width="small", disabled=True),
                "Elevation change (m)": st.column_config.TextColumn("Elevation change (m)", width="small", disabled=True),
                "County": st.column_config.TextColumn("County", width="medium", disabled=True),
                "State": st.column_config.TextColumn("State", width="medium", disabled=True),
                "Country": st.column_config.TextColumn("Country", width="medium", disabled=True),
                "Location": st.column_config.TextColumn("Location", width="large", disabled=True),
                "Description": st.column_config.TextColumn("Description", width="large", disabled=True),
                "Submitted": st.column_config.TextColumn("Submitted", width="medium", disabled=True)
            },
            key=table_key
        ))
        
        # Get selected rows
        selected_indices = []
        if edited_df is not None:
            selected_rows = edited_df[edited_df['Select'] == True]
            selected_indices = selected_rows.index.tolist()
        
        action_result = {"action": None, "selected_indices": selected_indices}
        
        if is_admin:
            # Admin controls
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                if selected_indices:
                    st.info(f"📋 {len(selected_indices)} range(s) selected")
                else:
                    st.info("📍 Check boxes in the table above to select ranges")
            
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
        else:
            # Readonly user controls
            if selected_indices:
                st.info(f"📋 {len(selected_indices)} range(s) selected")
                # Auto-map selected ranges for readonly users (same as admin)
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
                            popup=f"🎯 {range_data.get('range_name', 'Range')} - Firing Position<br><a href='https://www.google.com/maps?q={start_lat},{start_lon}' target='_blank'>📍 View in Google Maps</a>",
                            tooltip=f"Firing Position: {range_data.get('range_name', 'Range')}",
                            icon=folium.Icon(color=color, icon='play')
                        ).add_to(m)
                        
                        # Add target position marker
                        folium.Marker(
                            location=[end_lat, end_lon],
                            popup=f"🎯 {range_data.get('range_name', 'Range')} - Target<br><a href='https://www.google.com/maps?q={end_lat},{end_lon}' target='_blank'>📍 View in Google Maps</a>",
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