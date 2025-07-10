import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def find_closest_weather_measurement(shot_datetime, weather_data, max_time_diff_minutes=30):
    """Find the closest weather measurement by timestamp within a time window"""
    if not weather_data or not shot_datetime:
        return None
    
    try:
        # Parse shot datetime
        if isinstance(shot_datetime, str):
            shot_dt = datetime.fromisoformat(shot_datetime.replace('Z', '+00:00'))
        else:
            shot_dt = shot_datetime
        
        closest_weather = None
        min_time_diff = timedelta(minutes=max_time_diff_minutes)
        
        for weather in weather_data:
            # Parse weather measurement timestamp
            weather_timestamp = weather.get("measurement_timestamp")
            if not weather_timestamp:
                continue
                
            if isinstance(weather_timestamp, str):
                weather_dt = datetime.fromisoformat(weather_timestamp.replace('Z', '+00:00'))
            else:
                weather_dt = weather_timestamp
            
            # Calculate time difference
            time_diff = abs(shot_dt - weather_dt)
            
            # Check if this is the closest match within the time window
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_weather = weather
        
        return closest_weather
    except Exception as e:
        print(f"Error finding closest weather measurement: {e}")
        return None

def render_create_session_tab(user, supabase):
    """Render the Create Session tab"""
    st.header("📝 Create New Session")
    
    # Step 1: Select chronograph session
    st.subheader("1. Select Chronograph Session")
    
    try:
        # Get chronograph sessions for the user
        chrono_sessions = supabase.table("chrono_sessions").select("*").eq("user_email", user["email"]).order("datetime_local", desc=True).execute()
        
        if not chrono_sessions.data:
            st.warning("No chronograph sessions found. Please upload chronograph data first.")
            return
        
        # Create dropdown options
        session_options = {}
        for session in chrono_sessions.data:
            label = f"{session['datetime_local']} - {session['bullet_type']} - {session['bullet_grain']}gr "
            session_options[label] = session
        
        selected_session_label = st.selectbox(
            "Choose a chronograph session:",
            options=list(session_options.keys()),
            index=None,
            placeholder="Select a chronograph session..."
        )
        
        if selected_session_label:
            selected_session = session_options[selected_session_label]
            
            # Step 2: Select range and weather sources
            st.subheader("2. Select Range and Weather Sources")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Get range submissions for the user
                range_submissions = supabase.table("ranges_submissions").select("*").eq("user_email", user["email"]).order("submitted_at", desc=True).execute()
                
                if range_submissions.data:
                    range_options = {}
                    for range_sub in range_submissions.data:
                        label = f"{range_sub['range_name']} - {range_sub['distance_m']:.1f}m ({range_sub['submitted_at'][:10]})"
                        range_options[label] = range_sub
                    
                    selected_range_label = st.selectbox(
                        "Choose a range:",
                        options=list(range_options.keys()),
                        index=None,
                        placeholder="Select a range..."
                    )
                else:
                    st.warning("No range submissions found.")
                    selected_range_label = None
            
            with col2:
                # Weather source placeholder
                weather_options = ["Manual Entry", "Weather Station A", "Weather Station B"]
                selected_weather = st.selectbox(
                    "Choose weather source:",
                    options=weather_options,
                    index=None,
                    placeholder="Select weather source..."
                )
            
            # Step 3: Submit button and create merged table
            if selected_range_label and selected_weather:
                selected_range = range_options[selected_range_label]
                
                if st.button("Create DOPE Session", type="primary"):
                    create_dope_session(user, supabase, selected_session, selected_range, selected_weather)
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

def create_dope_session(user, supabase, chrono_session, range_data, weather_source):
    """Create and display the merged DOPE session table"""
    
    try:
        # Get chronograph measurements for the selected session
        measurements = supabase.table("chrono_measurements").select("*").eq("chrono_session_id", chrono_session["id"]).order("shot_number").execute()
        
        if not measurements.data:
            st.warning("No measurements found for the selected chronograph session.")
            return
        
        # Get weather measurements for the user (to match by timestamp)
        weather_measurements = supabase.table("weather_measurements").select("*").eq("user_email", user["email"]).execute()
        weather_data = weather_measurements.data if weather_measurements.data else []
        
        st.subheader("3. DOPE Session")
        
        # Component 1: DOPE Session Details
        st.markdown("#### Session Details")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Bullet Type", chrono_session.get("bullet_type", ""))
        with col2:
            st.metric("Bullet Grain", f"{chrono_session.get('bullet_grain', '')}gr")
        with col3:
            st.metric("Range", range_data.get("range_name", ""))
        with col4:
            st.metric("Weather Source", weather_source)
        
        # Component 2: DOPE Session Measurements Table
        st.markdown("#### Measurements")
        
        # Create the measurements data table (without session-level fields)
        measurements_data = []
        
        for measurement in measurements.data:
            # Find closest weather measurement by timestamp
            shot_datetime = measurement.get("datetime_local", "")
            closest_weather = find_closest_weather_measurement(shot_datetime, weather_data)
            
            row = {
                # Chronograph measurement data
                "datetime": measurement.get("datetime_local", ""),
                "shot_number": measurement.get("shot_number", ""),
                "speed": measurement.get("speed_fps", ""),
                "ke_ft_lb": measurement.get("ke_ft_lb", ""),
                "power_factor": measurement.get("power_factor", ""),
                "clean_bore": measurement.get("clean_bore", ""),
                "cold_bore": measurement.get("cold_bore", ""),
                "shot_notes": measurement.get("shot_notes", ""),
                
                # Range position data (repeated for each measurement)
                "start_lat": range_data.get("start_lat", ""),
                "start_lon": range_data.get("start_lon", ""),
                "start_alt": range_data.get("start_altitude_m", ""),
                "azimuth": range_data.get("azimuth_deg", ""),
                "elevation_angle": range_data.get("elevation_angle_deg", ""),
                
                # Weather data (matched by timestamp)
                "temperature": closest_weather.get("temperature_f", "") if closest_weather else "",
                "pressure": closest_weather.get("barometric_pressure_inhg", "") if closest_weather else "",
                "humidity": closest_weather.get("relative_humidity_pct", "") if closest_weather else "",
                
                # Optional DOPE data (to be filled by user later)
                "distance": "",  # User-provided distance (separate from range distance)
                "elevation_adjustment": "",  # Elevation adjustment in RADS or MOA
                "windage_adjustment": "",  # Windage adjustment in RADS or MOA
            }
            measurements_data.append(row)
        
        # Create DataFrame and display measurements table
        df = pd.DataFrame(measurements_data)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "datetime": st.column_config.TextColumn("DateTime", width="medium"),
                "shot_number": st.column_config.NumberColumn("Shot #", width="small"),
                "speed": st.column_config.NumberColumn("Speed (fps)", width="small"),
                "ke_ft_lb": st.column_config.NumberColumn("KE (ft-lb)", width="small"),
                "power_factor": st.column_config.NumberColumn("PF", width="small"),
                "clean_bore": st.column_config.TextColumn("Clean Bore", width="small"),
                "cold_bore": st.column_config.TextColumn("Cold Bore", width="small"),
                "shot_notes": st.column_config.TextColumn("Shot Notes", width="medium"),
                "start_lat": st.column_config.NumberColumn("Start Lat", width="small", format="%.6f"),
                "start_lon": st.column_config.NumberColumn("Start Lon", width="small", format="%.6f"),
                "start_alt": st.column_config.NumberColumn("Start Alt (m)", width="small"),
                "azimuth": st.column_config.NumberColumn("Azimuth (°)", width="small", format="%.2f"),
                "elevation_angle": st.column_config.NumberColumn("Elevation Angle (°)", width="small", format="%.2f"),
                
                # Weather data columns (matched by timestamp)
                "temperature": st.column_config.NumberColumn("Temp (°F)", width="small", format="%.1f"),
                "pressure": st.column_config.NumberColumn("Pressure (inHg)", width="small", format="%.2f"),
                "humidity": st.column_config.NumberColumn("Humidity (%)", width="small", format="%.1f"),
                
                # Optional DOPE columns (user-editable)
                "distance": st.column_config.TextColumn("Distance", width="small", help="User-provided distance"),
                "elevation_adjustment": st.column_config.TextColumn("Elevation Adj", width="medium", help="Elevation adjustment in RADS or MOA"),
                "windage_adjustment": st.column_config.TextColumn("Windage Adj", width="medium", help="Windage adjustment in RADS or MOA"),
            }
        )
        
        st.success(f"✅ DOPE session created with {len(measurements_data)} measurements")
        
        # Option to save the session (future enhancement)
        st.info("💡 Future: Save this DOPE session to database for later analysis")
        
    except Exception as e:
        st.error(f"Error creating DOPE session: {str(e)}")