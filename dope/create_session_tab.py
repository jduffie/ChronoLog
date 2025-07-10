import streamlit as st
from datetime import datetime, timedelta
import uuid
from .dope_model import DopeModel

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
    
    # Initialize DOPE model in session state
    if "dope_model" not in st.session_state:
        st.session_state.dope_model = DopeModel()
    
    dope_model = st.session_state.dope_model
    tab_name = "create_session"
    
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
                    create_dope_session(user, supabase, selected_session, selected_range, selected_weather, dope_model, tab_name)
        
        # If session has been created, display it
        if dope_model.is_tab_created(tab_name):
            display_dope_session(user, supabase, dope_model, tab_name)
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

def create_dope_session(user, supabase, chrono_session, range_data, weather_source, dope_model, tab_name):
    """Create and store the merged DOPE session data in the model"""
    
    try:
        # Get chronograph measurements for the selected session
        measurements = supabase.table("chrono_measurements").select("*").eq("chrono_session_id", chrono_session["id"]).order("shot_number").execute()
        
        if not measurements.data:
            st.warning("No measurements found for the selected chronograph session.")
            return
        
        # Get weather measurements for the user (to match by timestamp)
        weather_measurements = supabase.table("weather_measurements").select("*").eq("user_email", user["email"]).execute()
        weather_data = weather_measurements.data if weather_measurements.data else []
        
        # Create the measurements data table
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
        
        # Store in model
        dope_model.set_tab_measurements(tab_name, measurements_data)
        
        # Store session details
        session_details = {
            "bullet_type": chrono_session.get("bullet_type", ""),
            "bullet_grain": chrono_session.get("bullet_grain", ""),
            "range_name": range_data.get("range_name", ""),
            "weather_source": weather_source,
            "distance_m": range_data.get("distance_m", "")
        }
        dope_model.set_tab_session_details(tab_name, session_details)
        
        st.success(f"✅ DOPE session created with {len(measurements_data)} measurements")
        
    except Exception as e:
        st.error(f"Error creating DOPE session: {str(e)}")

def display_dope_session(user, supabase, dope_model, tab_name):
    """Display the DOPE session with editable measurements table"""
    
    # Get session details and measurements from model
    session_details = dope_model.get_tab_session_details(tab_name)
    current_df = dope_model.get_tab_measurements_df(tab_name)
    
    if current_df is None:
        st.warning("No DOPE session data found.")
        return
    
    st.subheader("3. DOPE Session")
    
    # Component 1: DOPE Session Details
    st.markdown("#### Session Details")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Bullet Type", session_details.get("bullet_type", ""))
    with col2:
        st.metric("Bullet Grain", f"{session_details.get('bullet_grain', '')}gr")
    with col3:
        st.metric("Range", session_details.get("range_name", ""))
    with col4:
        st.metric("Weather Source", session_details.get("weather_source", ""))
    
    # Component 2: DOPE Session Measurements Table
    st.markdown("#### Measurements")
    
    # Display editable measurements table
    edited_df = st.data_editor(
        current_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            # Read-only chronograph data columns
            "datetime": st.column_config.TextColumn("DateTime", width="medium", disabled=True),
            "shot_number": st.column_config.NumberColumn("Shot #", width="small", disabled=True),
            "speed": st.column_config.NumberColumn("Speed (fps)", width="small", disabled=True),
            "ke_ft_lb": st.column_config.NumberColumn("KE (ft-lb)", width="small", disabled=True),
            "power_factor": st.column_config.NumberColumn("PF", width="small", disabled=True),
            
            # Read-only range data columns
            "start_lat": st.column_config.NumberColumn("Start Lat", width="small", format="%.6f", disabled=True),
            "start_lon": st.column_config.NumberColumn("Start Lon", width="small", format="%.6f", disabled=True),
            "start_alt": st.column_config.NumberColumn("Start Alt (m)", width="small", disabled=True),
            "azimuth": st.column_config.NumberColumn("Azimuth (°)", width="small", format="%.2f", disabled=True),
            "elevation_angle": st.column_config.NumberColumn("Elevation Angle (°)", width="small", format="%.2f", disabled=True),
            
            # Read-only weather data columns
            "temperature": st.column_config.NumberColumn("Temp (°F)", width="small", format="%.1f", disabled=True),
            "pressure": st.column_config.NumberColumn("Pressure (inHg)", width="small", format="%.2f", disabled=True),
            "humidity": st.column_config.NumberColumn("Humidity (%)", width="small", format="%.1f", disabled=True),
            
            # Editable columns (grouped at the end)
            "clean_bore": st.column_config.TextColumn("Clean Bore", width="small", help="Clean bore indicator"),
            "cold_bore": st.column_config.TextColumn("Cold Bore", width="small", help="Cold bore indicator"),
            "shot_notes": st.column_config.TextColumn("Shot Notes", width="medium", help="Notes for this shot"),
            "distance": st.column_config.TextColumn("Distance", width="small", help="User-provided distance"),
            "elevation_adjustment": st.column_config.TextColumn("Elevation Adj", width="medium", help="Elevation adjustment in RADS or MOA"),
            "windage_adjustment": st.column_config.TextColumn("Windage Adj", width="medium", help="Windage adjustment in RADS or MOA"),
        },
        key=f"dope_measurements_table_{tab_name}"
    )
    
    # Update model with any edits
    if not edited_df.equals(current_df):
        dope_model.update_tab_measurements(tab_name, edited_df)
        st.info("💡 Changes saved automatically. Click 'Save Session' to persist to database.")
    
    # Save session button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("💾 Save Session", type="primary", help="Save this DOPE session to database"):
            save_dope_session(user, supabase, dope_model, tab_name)

def save_dope_session(user, supabase, dope_model, tab_name):
    """Save the DOPE session and measurements to the database"""
    
    try:
        # Get session details and measurements from model
        session_details = dope_model.get_tab_session_details(tab_name)
        measurements_df = dope_model.get_tab_measurements_df(tab_name)
        
        if not session_details or measurements_df is None:
            st.error("No DOPE session data to save.")
            return
        
        # Generate session name based on bullet type and timestamp
        session_name = f"{session_details.get('bullet_type', 'Unknown')}-{session_details.get('bullet_grain', '')}gr-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create dope_session record
        dope_session_id = str(uuid.uuid4())
        session_data = {
            "id": dope_session_id,
            "user_email": user["email"],
            "session_name": session_name,
            "bullet_type": session_details.get("bullet_type", ""),
            "bullet_grain": int(session_details.get("bullet_grain", 0)) if session_details.get("bullet_grain") else None,
            "range_name": session_details.get("range_name", ""),
            "distance_m": float(session_details.get("distance_m", 0)) if session_details.get("distance_m") else None,
            "weather_source": session_details.get("weather_source", ""),
            "notes": f"Created from DOPE session on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        }
        
        # Insert dope_session
        session_response = supabase.table("dope_sessions").insert(session_data).execute()
        
        if not session_response.data:
            st.error("Failed to save DOPE session.")
            return
        
        # Helper function to safely convert values
        def safe_float(value):
            try:
                if value is None or value == "" or str(value).strip() == "":
                    return None
                return float(value)
            except (ValueError, TypeError):
                return None
        
        def safe_int(value):
            try:
                if value is None or value == "" or str(value).strip() == "":
                    return None
                return int(value)
            except (ValueError, TypeError):
                return None
        
        def safe_text(value):
            if value is None or value == "" or str(value).strip() == "":
                return None
            return str(value)
        
        # Create dope_measurements records
        measurements_data = []
        for _, row in measurements_df.iterrows():
            measurement_data = {
                "dope_session_id": dope_session_id,
                "user_email": user["email"],
                "shot_number": safe_int(row.get("shot_number")),
                "datetime_shot": row.get("datetime") if row.get("datetime") else None,
                
                # Source chronograph data
                "speed_fps": safe_float(row.get("speed")),
                "ke_ft_lb": safe_float(row.get("ke_ft_lb")),
                "power_factor": safe_float(row.get("power_factor")),
                
                # Source range data
                "start_lat": safe_float(row.get("start_lat")),
                "start_lon": safe_float(row.get("start_lon")),
                "start_altitude_m": safe_float(row.get("start_alt")),
                "azimuth_deg": safe_float(row.get("azimuth")),
                "elevation_angle_deg": safe_float(row.get("elevation_angle")),
                
                # Source weather data
                "temperature_f": safe_float(row.get("temperature")),
                "pressure_inhg": safe_float(row.get("pressure")),
                "humidity_pct": safe_float(row.get("humidity")),
                
                # User-editable DOPE data
                "clean_bore": safe_text(row.get("clean_bore")),
                "cold_bore": safe_text(row.get("cold_bore")),
                "shot_notes": safe_text(row.get("shot_notes")),
                "distance": safe_text(row.get("distance")),
                "elevation_adjustment": safe_text(row.get("elevation_adjustment")),
                "windage_adjustment": safe_text(row.get("windage_adjustment")),
            }
            measurements_data.append(measurement_data)
        
        # Insert dope_measurements
        if measurements_data:
            measurements_response = supabase.table("dope_measurements").insert(measurements_data).execute()
            
            if not measurements_response.data:
                st.error("Failed to save DOPE measurements.")
                return
        
        # Success message
        st.success(f"✅ DOPE session '{session_name}' saved successfully with {len(measurements_data)} measurements!")
        st.info(f"💾 Session ID: {dope_session_id}")
        
    except Exception as e:
        st.error(f"Error saving DOPE session: {str(e)}")
        print(f"Save error details: {e}")  # For debugging