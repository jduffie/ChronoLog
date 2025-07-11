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
            
            # Use chronograph session ID as unique tab name for DOPE session
            tab_name = f"chrono_session_{selected_session['id']}"
            
            # Step 2: Select range and weather sources
            st.subheader("2. Select Range and Weather Sources")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Get range submissions for the user
                range_submissions = supabase.table("ranges_submissions").select("*").eq("user_email", user["email"]).order("submitted_at", desc=True).execute()
                
                range_options = {}
                if range_submissions.data:
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
                # Get weather sources for the user
                weather_sources = supabase.table("weather_source").select("*").eq("user_email", user["email"]).order("created_at", desc=True).execute()
                
                if weather_sources.data:
                    weather_options = {}
                    for weather_source in weather_sources.data:
                        label = f"{weather_source['name']} ({weather_source['make'] or 'Unknown'})"
                        weather_options[label] = weather_source
                    
                    selected_weather_label = st.selectbox(
                        "Choose weather source:",
                        options=list(weather_options.keys()),
                        index=None,
                        placeholder="Select weather source..."
                    )
                    
                    selected_weather = weather_options[selected_weather_label] if selected_weather_label else None
                else:
                    st.warning("No weather sources found.")
                    selected_weather = None
            
            # Step 2.5: Rifle and Ammo Selection
            st.subheader("2.5. Select Rifle and Ammo")
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("**Rifle Selection**")
                # Get rifles for the user
                try:
                    rifles_response = supabase.table("rifles").select("*").eq("user_email", user["email"]).order("name").execute()
                    
                    rifle_options = {}
                    if rifles_response.data:
                        for rifle in rifles_response.data:
                            # Create a descriptive label
                            label = f"{rifle['name']}"
                            details = []
                            if rifle.get('barrel_length'):
                                details.append(f"Length: {rifle['barrel_length']}")
                            if rifle.get('barrel_twist_ratio'):
                                details.append(f"Twist: {rifle['barrel_twist_ratio']}")
                            if details:
                                label += f" ({', '.join(details)})"
                            rifle_options[label] = rifle
                        
                        selected_rifle_label = st.selectbox(
                            "Choose a rifle:",
                            options=list(rifle_options.keys()),
                            index=None,
                            placeholder="Select a rifle..."
                        )
                        
                        selected_rifle = rifle_options[selected_rifle_label] if selected_rifle_label else None
                    else:
                        st.warning("No rifles found. Please add rifles first.")
                        selected_rifle = None
                except Exception as e:
                    st.error(f"Error loading rifles: {str(e)}")
                    selected_rifle = None
            
            with col4:
                st.markdown("**Ammo Selection**")
                # Get ammo for the user
                try:
                    ammo_response = supabase.table("ammo").select("*").eq("user_email", user["email"]).order("make").execute()
                    
                    ammo_options = {}
                    if ammo_response.data:
                        for ammo in ammo_response.data:
                            label = f"{ammo['make']} {ammo['model']} - {ammo['caliber']} - {ammo['weight']}"
                            ammo_options[label] = ammo
                        
                        selected_ammo_label = st.selectbox(
                            "Choose ammo:",
                            options=list(ammo_options.keys()),
                            index=None,
                            placeholder="Select ammo..."
                        )
                        
                        selected_ammo = ammo_options[selected_ammo_label] if selected_ammo_label else None
                    else:
                        st.warning("No ammo found. Please add ammo first.")
                        selected_ammo = None
                except Exception as e:
                    st.error(f"Error loading ammo: {str(e)}")
                    selected_ammo = None
            
            # Prepare selected range and weather data
            selected_range = range_options[selected_range_label] if selected_range_label else None
            
            # Create/update the DOPE session with current selections
            create_dope_session(user, supabase, selected_session, selected_range, selected_weather, selected_rifle, selected_ammo, dope_model, tab_name)
            
            # Add spacing before the table
            st.markdown("---")
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Display the session if it has been created
            if dope_model.is_tab_created(tab_name):
                display_dope_session(user, supabase, dope_model, tab_name)
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

def create_dope_session(user, supabase, chrono_session, range_data, weather_source, selected_rifle, selected_ammo, dope_model, tab_name):
    """Create and store the merged DOPE session data in the model"""
    
    try:
        # Get chronograph measurements for the selected session
        measurements = supabase.table("chrono_measurements").select("*").eq("chrono_session_id", chrono_session["id"]).order("shot_number").execute()
        
        if not measurements.data:
            st.warning("No measurements found for the selected chronograph session.")
            return
        
        # Get weather measurements only if a weather source is selected
        weather_data = []
        if weather_source:
            weather_measurements = supabase.table("weather_measurements").select("*").eq("weather_source_id", weather_source["id"]).execute()
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

                
                # Range position data (repeated for each measurement)
                "start_lat": range_data.get("start_lat", "") if range_data else "",
                "start_lon": range_data.get("start_lon", "") if range_data else "",
                "start_alt": range_data.get("start_altitude_m", "") if range_data else "",
                "azimuth": range_data.get("azimuth_deg", "") if range_data else "",
                "elevation_angle": range_data.get("elevation_angle_deg", "") if range_data else "",
                
                # Weather data (matched by timestamp)
                "temperature": closest_weather.get("temperature_f", "") if closest_weather else "",
                "pressure": closest_weather.get("barometric_pressure_inhg", "") if closest_weather else "",
                "humidity": closest_weather.get("relative_humidity_pct", "") if closest_weather else "",
                
                # Optional DOPE data (to be filled by user later)
                "distance": "",  # User-provided distance (separate from range distance)
                "elevation_adjustment": "",  # Elevation adjustment in RADS or MOA
                "windage_adjustment": "",  # Windage adjustment in RADS or MOA

                "clean_bore": measurement.get("clean_bore") or "",
                "cold_bore": measurement.get("cold_bore") or "",
                "shot_notes": measurement.get("shot_notes") or "",
            }
            measurements_data.append(row)
        
        # Store in model
        dope_model.set_tab_measurements(tab_name, measurements_data)
        
        # Store session details
        session_details = {
            "bullet_type": chrono_session.get("bullet_type", ""),
            "bullet_grain": chrono_session.get("bullet_grain", ""),
            "range_name": range_data.get("range_name", "") if range_data else "",
            "weather_source": weather_source,  # Store entire weather source object
            "weather_source_name": weather_source.get("name", "") if weather_source else "",
            "distance_m": range_data.get("distance_m", "") if range_data else "",
            "chrono_session": chrono_session,  # Store entire chrono session object
            "range_data": range_data,  # Store entire range data object
            "rifle": selected_rifle,  # Store entire rifle object
            "rifle_name": selected_rifle.get("name", "") if selected_rifle else "",
            "ammo": selected_ammo,  # Store entire ammo object
            "ammo_description": f"{selected_ammo.get('make', '')} {selected_ammo.get('model', '')}".strip() if selected_ammo else ""
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
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Bullet Type", session_details.get("bullet_type", ""))
    with col2:
        st.metric("Bullet Grain", f"{session_details.get('bullet_grain', '')}gr")
    with col3:
        st.metric("Range", session_details.get("range_name", ""))
    with col4:
        st.metric("Weather Source", session_details.get("weather_source_name", ""))
    with col5:
        st.metric("Rifle", session_details.get("rifle_name", ""))
    with col6:
        st.metric("Ammo", session_details.get("ammo_description", ""))
    
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
            
            # User DOPE adjustments (editable)
            "distance": st.column_config.TextColumn("Distance", width="small", help="User-provided distance"),
            "elevation_adjustment": st.column_config.TextColumn("Elevation Adj", width="medium", help="Elevation adjustment in RADS or MOA"),
            "windage_adjustment": st.column_config.TextColumn("Windage Adj", width="medium", help="Windage adjustment in RADS or MOA"),
            
            # Shot metadata (editable, far right)
            "clean_bore": st.column_config.TextColumn("Clean Bore", width="small", help="Clean bore indicator"),
            "cold_bore": st.column_config.TextColumn("Cold Bore", width="small", help="Cold bore indicator"),
            "shot_notes": st.column_config.TextColumn("Shot Notes", width="medium", help="Notes for this shot"),
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
        
        chrono_session = session_details.get("chrono_session")
        if not chrono_session:
            st.error("No chronograph session found.")
            return
        
        # Check if DOPE session already exists for this chronograph session
        existing_dope_session = supabase.table("dope_sessions").select("*").eq("chrono_session_id", chrono_session["id"]).execute()
        
        # Generate session name based on bullet type and timestamp
        session_name = f"{session_details.get('bullet_type', 'Unknown')}-{session_details.get('bullet_grain', '')}gr-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        if existing_dope_session.data:
            # Update existing DOPE session
            dope_session_id = existing_dope_session.data[0]["id"]
            session_name = existing_dope_session.data[0]["session_name"]  # Use existing session name
            st.info(f"🔄 Updating existing DOPE session for this chronograph session...")
            
            # Delete existing measurements
            supabase.table("dope_measurements").delete().eq("dope_session_id", dope_session_id).execute()
            
        else:
            # Create new DOPE session
            dope_session_id = str(uuid.uuid4())
            
            weather_source = session_details.get("weather_source")
            range_data = session_details.get("range_data")
            rifle_data = session_details.get("rifle")
            ammo_data = session_details.get("ammo")
            session_data = {
                "id": dope_session_id,
                "user_email": user["email"],
                "session_name": session_name,
                "bullet_type": session_details.get("bullet_type", ""),
                "bullet_grain": int(session_details.get("bullet_grain", 0)) if session_details.get("bullet_grain") else None,
                "range_name": session_details.get("range_name", ""),
                "distance_m": float(session_details.get("distance_m", 0)) if session_details.get("distance_m") else None,
                "chrono_session_id": chrono_session.get("id"),
                "range_submission_id": range_data.get("id") if range_data else None,
                "weather_source_id": weather_source.get("id") if weather_source else None,
                "rifle_id": rifle_data.get("id") if rifle_data else None,
                "ammo_id": ammo_data.get("id") if ammo_data else None,
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