import streamlit as st
import pandas as pd

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
        
        st.subheader("3. DOPE Session Data")
        
        # Create the merged data table
        merged_data = []
        
        for measurement in measurements.data:
            row = {
                # Chronograph data
                "datetime": measurement.get("datetime_local", ""),
                "shot_number": measurement.get("shot_number", ""),
                "speed": measurement.get("speed_fps", ""),
                "bullet_type": chrono_session.get("bullet_type", ""),
                "bullet_grain": chrono_session.get("bullet_grain", ""),
                "ke_ft_lb": measurement.get("ke_ft_lb", ""),
                "power_factor": measurement.get("power_factor", ""),
                "clean_bore": measurement.get("clean_bore", ""),
                "cold_bore": measurement.get("cold_bore", ""),
                "shot_notes": measurement.get("shot_notes", ""),
                
                # Range data
                "start_lat": range_data.get("start_lat", ""),
                "start_lon": range_data.get("start_lon", ""),
                "start_alt": range_data.get("start_altitude_m", ""),
                "azimuth": range_data.get("azimuth_deg", ""),
                "elevation_angle": range_data.get("elevation_angle_deg", ""),
                "range_name": range_data.get("range_name", ""),
                "distance_m": range_data.get("distance_m", ""),
                
                # Weather source (placeholder for now)
                "weather_source": weather_source
            }
            merged_data.append(row)
        
        # Create DataFrame and display
        df = pd.DataFrame(merged_data)
        
        # Display session info
        st.info(f"**Chronograph Session:** {chrono_session['tab_name']} | **Range:** {range_data['range_name']} | **Weather:** {weather_source}")
        
        # Display the table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "datetime": st.column_config.TextColumn("DateTime", width="medium"),
                "shot_number": st.column_config.NumberColumn("Shot #", width="small"),
                "speed": st.column_config.NumberColumn("Speed (fps)", width="small"),
                "bullet_type": st.column_config.TextColumn("Bullet Type", width="medium"),
                "bullet_grain": st.column_config.NumberColumn("Grain", width="small"),
                "ke_ft_lb": st.column_config.NumberColumn("KE (ft-lb)", width="small"),
                "power_factor": st.column_config.NumberColumn("PF", width="small"),
                "clean_bore": st.column_config.TextColumn("Clean Bore", width="small"),
                "cold_bore": st.column_config.TextColumn("Cold Bore", width="small"),
                "shot_notes": st.column_config.TextColumn("Shot Notes", width="medium"),
                "start_lat": st.column_config.NumberColumn("Start Lat", width="small", format="%.6f"),
                "start_lon": st.column_config.NumberColumn("Start Lon", width="small", format="%.6f"),
                "start_alt": st.column_config.NumberColumn("Start Alt (m)", width="small"),
                "azimuth": st.column_config.NumberColumn("Azimuth (°)", width="small", format="%.2f"),
                "elevation_angle": st.column_config.NumberColumn("Elev Angle (°)", width="small", format="%.2f"),
                "range_name": st.column_config.TextColumn("Range", width="medium"),
                "distance_m": st.column_config.NumberColumn("Distance (m)", width="small"),
                "weather_source": st.column_config.TextColumn("Weather", width="medium")
            }
        )
        
        st.success(f"✅ DOPE session created with {len(merged_data)} measurements")
        
        # Option to save the session (future enhancement)
        st.info("💡 Future: Save this DOPE session to database for later analysis")
        
    except Exception as e:
        st.error(f"Error creating DOPE session: {str(e)}")