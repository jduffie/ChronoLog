import streamlit as st
import pandas as pd
from datetime import datetime

def render_weather_logs_tab(user, supabase):
    """Render the Weather Logs tab showing all weather measurements"""
    st.header("🌤️ Weather Logs")
    
    try:
        # Get all weather measurements for the user
        measurements_response = supabase.table("weather_measurements").select("*").eq("user_email", user["email"]).order("measurement_timestamp", desc=True).execute()
        
        if not measurements_response.data:
            st.info("No weather logs found. Import some Kestrel data files to get started!")
            return
        
        measurements = measurements_response.data
        
        # Create a summary table
        st.subheader("📋 Weather Measurement Summary")
        
        # Group by device and date for summary
        df_measurements = pd.DataFrame(measurements)
        
        # Create display summary
        summary_data = []
        device_groups = df_measurements.groupby(['device_name', 'device_model', 'serial_number'])
        
        for (device_name, device_model, serial_number), group in device_groups:
            dates = pd.to_datetime(group['measurement_timestamp']).dt.date.unique()
            measurement_count = len(group)
            
            # Get temperature stats if available
            temps = group['temperature_f'].dropna()
            temp_range = f"{temps.min():.1f}°F - {temps.max():.1f}°F" if not temps.empty else "N/A"
            
            # Get humidity stats if available
            humidity = group['relative_humidity_pct'].dropna()
            humidity_range = f"{humidity.min():.1f}% - {humidity.max():.1f}%" if not humidity.empty else "N/A"
            
            summary_data.append({
                "Device": f"{device_name} ({device_model})",
                "Serial": serial_number,
                "Measurements": measurement_count,
                "Date Range": f"{min(dates)} to {max(dates)}" if len(dates) > 1 else str(dates[0]),
                "Temp Range": temp_range,
                "Humidity Range": humidity_range
            })
        
        # Display summary table
        if summary_data:
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True)
        
        # Detailed measurements with filtering
        st.subheader("🌡️ Detailed Weather Measurements")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            devices = list(set([f"{m['device_name']} ({m['device_model']})" for m in measurements]))
            selected_device = st.selectbox("Filter by Device", ["All"] + devices)
        
        with col2:
            date_range = st.date_input("Filter by Date Range", value=[], max_value=datetime.now().date())
        
        with col3:
            # Limit number of records to display
            max_records = st.number_input("Max Records to Display", min_value=10, max_value=1000, value=100, step=10)
        
        # Apply filters
        filtered_measurements = measurements
        
        if selected_device != "All":
            device_parts = selected_device.replace(")", "").split(" (")
            device_name = device_parts[0]
            device_model = device_parts[1] if len(device_parts) > 1 else ""
            filtered_measurements = [m for m in filtered_measurements 
                                   if m['device_name'] == device_name and m['device_model'] == device_model]
        
        if date_range:
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_measurements = [m for m in filtered_measurements 
                                       if start_date <= datetime.fromisoformat(m['measurement_timestamp']).date() <= end_date]
            elif len(date_range) == 1:
                target_date = date_range[0]
                filtered_measurements = [m for m in filtered_measurements 
                                       if datetime.fromisoformat(m['measurement_timestamp']).date() == target_date]
        
        # Limit records
        filtered_measurements = filtered_measurements[:max_records]
        
        # Group measurements by date for display
        if filtered_measurements:
            measurements_by_date = {}
            for measurement in filtered_measurements:
                date_key = datetime.fromisoformat(measurement['measurement_timestamp']).strftime('%Y-%m-%d')
                if date_key not in measurements_by_date:
                    measurements_by_date[date_key] = []
                measurements_by_date[date_key].append(measurement)
            
            # Display each date group
            for date_str, date_measurements in sorted(measurements_by_date.items(), reverse=True):
                with st.expander(f"📅 {date_str} ({len(date_measurements)} measurements)", expanded=False):
                    
                    # Show device info for this date
                    device_info = date_measurements[0]
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Device:** {device_info['device_name']}")
                        st.write(f"**Model:** {device_info['device_model']}")
                    with col2:
                        st.write(f"**Serial:** {device_info['serial_number']}")
                        if device_info.get('location_description'):
                            st.write(f"**Location:** {device_info['location_description']}")
                    
                    # Create DataFrame for this date
                    df_date = pd.DataFrame(date_measurements)
                    
                    # Select and format columns for display
                    display_columns = ['measurement_timestamp', 'temperature_f', 'relative_humidity_pct', 
                                     'barometric_pressure_inhg', 'wind_speed_mph']
                    
                    # Only include columns that exist and have data
                    available_columns = []
                    column_renames = {}
                    
                    for col in display_columns:
                        if col in df_date.columns and not df_date[col].isna().all():
                            available_columns.append(col)
                            if col == 'measurement_timestamp':
                                column_renames[col] = 'Time'
                            elif col == 'temperature_f':
                                column_renames[col] = 'Temp (°F)'
                            elif col == 'relative_humidity_pct':
                                column_renames[col] = 'Humidity (%)'
                            elif col == 'barometric_pressure_inhg':
                                column_renames[col] = 'Pressure (inHg)'
                            elif col == 'wind_speed_mph':
                                column_renames[col] = 'Wind (mph)'
                    
                    if available_columns:
                        display_df = df_date[available_columns].copy()
                        
                        # Format timestamp
                        if 'measurement_timestamp' in display_df.columns:
                            display_df['measurement_timestamp'] = pd.to_datetime(display_df['measurement_timestamp']).dt.strftime('%H:%M:%S')
                        
                        # Round numeric columns
                        numeric_columns = ['temperature_f', 'relative_humidity_pct', 'barometric_pressure_inhg', 'wind_speed_mph']
                        for col in numeric_columns:
                            if col in display_df.columns:
                                display_df[col] = display_df[col].round(1)
                        
                        # Rename columns
                        display_df = display_df.rename(columns=column_renames)
                        
                        st.dataframe(display_df, use_container_width=True)
                        
                        # Quick stats for this date
                        if len(date_measurements) > 1:
                            st.write("**Daily Summary:**")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if 'temperature_f' in df_date.columns:
                                    temps = df_date['temperature_f'].dropna()
                                    if not temps.empty:
                                        st.write(f"• Temp: {temps.min():.1f}°F - {temps.max():.1f}°F")
                            
                            with col2:
                                if 'relative_humidity_pct' in df_date.columns:
                                    humidity = df_date['relative_humidity_pct'].dropna()
                                    if not humidity.empty:
                                        st.write(f"• Humidity: {humidity.min():.1f}% - {humidity.max():.1f}%")
                            
                            with col3:
                                if 'wind_speed_mph' in df_date.columns:
                                    wind = df_date['wind_speed_mph'].dropna()
                                    if not wind.empty:
                                        st.write(f"• Wind: {wind.min():.1f} - {wind.max():.1f} mph")
                        
                        # View button for detailed analysis
                        if st.button(f"View Detailed Analysis", key=f"view_weather_{date_str}"):
                            st.session_state['selected_weather_date'] = date_str
                            st.session_state['selected_weather_device'] = device_info['serial_number']
                            st.info("Date selected! Go to the 'View Log' tab to see detailed weather analysis.")
                    else:
                        st.info("No displayable weather data for this date.")
        else:
            st.info("No weather measurements match the selected filters.")
    
    except Exception as e:
        st.error(f"Error loading weather logs: {str(e)}")