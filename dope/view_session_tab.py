import streamlit as st
import pandas as pd

def render_view_session_tab(user, supabase):
    """Render the View Session tab with selectable table and details"""
    st.header("🔍 View Session")
    
    try:
        # Get user's sessions with datetime_local from chrono_sessions
        sessions_response = supabase.table("dope_sessions").select("*, chrono_sessions(datetime_local)").eq("user_email", user["email"]).order("created_at", desc=True).execute()
        sessions = sessions_response.data
        
        if sessions:
            # Process sessions with aggregated measurement data
            session_summaries = []
            session_lookup = {}  # For mapping display rows to session data
            
            for session in sessions:
                # Get measurements for this session
                measurements_response = supabase.table("dope_measurements").select("*").eq("dope_session_id", session['id']).execute()
                measurements = measurements_response.data
                
                # Prepare session timestamp using datetime_local from chrono_sessions
                chrono_session = session.get('chrono_sessions')
                if chrono_session and chrono_session.get('datetime_local'):
                    session_dt = pd.to_datetime(chrono_session['datetime_local'])
                    session_date = session_dt.strftime('%Y-%m-%d')
                    session_time = session_dt.strftime('%H:%M')
                elif session.get('created_at'):
                    # Fallback to created_at if datetime_local not available
                    session_dt = pd.to_datetime(session['created_at'])
                    session_date = session_dt.strftime('%Y-%m-%d')
                    session_time = session_dt.strftime('%H:%M')
                else:
                    session_date = "N/A"
                    session_time = "N/A"
                
                # Calculate statistics from measurements
                shot_count = len(measurements) if measurements else 0
                avg_velocity = std_velocity = velocity_spread = "N/A"
                
                if measurements and shot_count > 0:
                    speeds = [m['speed_fps'] for m in measurements if m.get('speed_fps') is not None]
                    if speeds:
                        avg_velocity = f"{sum(speeds) / len(speeds):.1f}"
                        if len(speeds) > 1:
                            mean_speed = sum(speeds) / len(speeds)
                            variance = sum((x - mean_speed) ** 2 for x in speeds) / len(speeds)
                            std_velocity = f"{variance ** 0.5:.1f}"
                            velocity_spread = f"{max(speeds) - min(speeds):.1f}"
                        else:
                            std_velocity = "0.0"
                            velocity_spread = "0.0"
                
                row_data = {
                    'Date': session_date,
                    'Time': session_time,
                    'Session Name': session.get('session_name', 'N/A'),
                    'Bullet Type': session.get('bullet_type', 'N/A'),
                    'Bullet Weight (gr)': session.get('bullet_grain', 'N/A'),
                    'Shot Count': shot_count,
                    'Avg Velocity (fps)': avg_velocity,
                    'Std Dev (fps)': std_velocity,
                    'Velocity Spread (fps)': velocity_spread
                }
                session_summaries.append(row_data)
                
                # Map this row to session data for lookup
                session_lookup[len(session_summaries) - 1] = session
            
            # Create DataFrame and display
            if session_summaries:
                sessions_df = pd.DataFrame(session_summaries)
                
                st.markdown("### Select Session")
                st.info("💡 Click on any row to view session details and measurements")
                
                # Display the sessions table with selection
                selected_rows = st.dataframe(
                    sessions_df,
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    column_config={
                        'Date': st.column_config.DateColumn('Date'),
                        'Time': st.column_config.TextColumn('Time'),
                        'Session Name': st.column_config.TextColumn('Session Name'),
                        'Bullet Type': st.column_config.TextColumn('Bullet Type'),
                        'Bullet Weight (gr)': st.column_config.NumberColumn('Bullet Weight (gr)', format="%.1f"),
                        'Shot Count': st.column_config.NumberColumn('Shot Count'),
                        'Avg Velocity (fps)': st.column_config.TextColumn('Avg Velocity (fps)'),
                        'Std Dev (fps)': st.column_config.TextColumn('Std Dev (fps)'),
                        'Velocity Spread (fps)': st.column_config.TextColumn('Velocity Spread (fps)')
                    }
                )
                
                # Handle row selection - show session details
                if selected_rows.selection.rows:
                    selected_row_index = selected_rows.selection.rows[0]
                    if selected_row_index in session_lookup:
                        selected_session = session_lookup[selected_row_index]
                        
                        # Display session details
                        st.markdown("---")
                        st.markdown("### Session Details")
                        
                        # Session info
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Session Name", selected_session.get('session_name', 'N/A'))
                        with col2:
                            st.metric("Bullet Type", selected_session.get('bullet_type', 'N/A'))
                        with col3:
                            st.metric("Bullet Weight", f"{selected_session.get('bullet_grain', 'N/A')} gr")
                        with col4:
                            # Use datetime_local from chrono_sessions for the session date/time
                            chrono_session = selected_session.get('chrono_sessions')
                            if chrono_session and chrono_session.get('datetime_local'):
                                session_dt = pd.to_datetime(chrono_session['datetime_local'])
                                st.metric("Session Date", session_dt.strftime('%Y-%m-%d %H:%M'))
                            elif selected_session.get('created_at'):
                                # Fallback to created_at
                                created_dt = pd.to_datetime(selected_session['created_at'])
                                st.metric("Created", created_dt.strftime('%Y-%m-%d %H:%M'))
                            else:
                                st.metric("Date", "N/A")
                        
                        # Component 1: Cartridge Details
                        st.markdown("#### Cartridge")
                        if selected_session.get('ammo_id'):
                            # Get ammo details
                            ammo_response = supabase.table("ammo").select("*").eq("id", selected_session['ammo_id']).execute()
                            if ammo_response.data:
                                ammo_data = ammo_response.data[0]
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.markdown(f"<medium><strong>Make:</strong> {ammo_data.get('make', 'N/A')}</medium>", unsafe_allow_html=True)
                                with col2:
                                    st.markdown(f"<medium><strong>Model:</strong> {ammo_data.get('model', 'N/A')}</medium>", unsafe_allow_html=True)
                                with col3:
                                    st.markdown(f"<medium><strong>Caliber:</strong> {ammo_data.get('caliber', 'N/A')}</medium>", unsafe_allow_html=True)
                                with col4:
                                    st.markdown(f"<medium><strong>Weight:</strong> {ammo_data.get('weight', 'N/A')}</medium>", unsafe_allow_html=True)
                            else:
                                st.info("Ammo details not found")
                        else:
                            # Fallback to session data
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"<medium><strong>Bullet Type:</strong> {selected_session.get('bullet_type', 'N/A')}</medium>", unsafe_allow_html=True)
                            with col2:
                                grain_text = f"{selected_session.get('bullet_grain', 'N/A')}gr" if selected_session.get('bullet_grain') else "N/A"
                                st.markdown(f"<medium><strong>Bullet Grain:</strong> {grain_text}</medium>", unsafe_allow_html=True)
                        
                        # Component 2: Rifle Details
                        st.markdown("#### Rifle")
                        if selected_session.get('rifle_id'):
                            # Get rifle details
                            rifle_response = supabase.table("rifles").select("*").eq("id", selected_session['rifle_id']).execute()
                            if rifle_response.data:
                                rifle_data = rifle_response.data[0]
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.markdown(f"<medium><strong>Name:</strong> {rifle_data.get('name', 'N/A')}</medium>", unsafe_allow_html=True)
                                with col2:
                                    st.markdown(f"<medium><strong>Barrel Length:</strong> {rifle_data.get('barrel_length', 'N/A')}</medium>", unsafe_allow_html=True)
                                with col3:
                                    st.markdown(f"<medium><strong>Twist Ratio:</strong> {rifle_data.get('barrel_twist_ratio', 'N/A')}</medium>", unsafe_allow_html=True)
                                with col4:
                                    st.markdown(f"<medium><strong>Scope:</strong> {rifle_data.get('scope', 'N/A')}</medium>", unsafe_allow_html=True)
                            else:
                                st.info("Rifle details not found")
                        else:
                            st.info("No rifle data available for this session")
                        
                        # Component 3: Firing Position Details
                        st.markdown("#### Firing Position")
                        if selected_session.get('range_submission_id'):
                            # Get range details
                            range_response = supabase.table("ranges_submissions").select("*").eq("id", selected_session['range_submission_id']).execute()
                            if range_response.data:
                                range_data = range_response.data[0]
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    lat_text = f"{range_data.get('start_lat', 'N/A'):.6f}" if range_data.get('start_lat') else "N/A"
                                    st.markdown(f"<medium><strong>Latitude:</strong> {lat_text}</medium>", unsafe_allow_html=True)
                                with col2:
                                    lon_text = f"{range_data.get('start_lon', 'N/A'):.6f}" if range_data.get('start_lon') else "N/A"
                                    st.markdown(f"<medium><strong>Longitude:</strong> {lon_text}</medium>", unsafe_allow_html=True)
                                with col3:
                                    alt_text = f"{range_data.get('start_altitude_m', 'N/A'):.1f}" if range_data.get('start_altitude_m') else "N/A"
                                    st.markdown(f"<medium><strong>Altitude (m):</strong> {alt_text}</medium>", unsafe_allow_html=True)
                            else:
                                st.info("Range details not found")
                        else:
                            st.info("No range data available for this session")
                        
                        # Get and display measurements
                        measurements_response = supabase.table("dope_measurements").select("*").eq("dope_session_id", selected_session['id']).execute()
                        measurements = measurements_response.data
                        
                        if measurements:
                            st.markdown("### Measurements")
                            
                            # Convert to DataFrame
                            measurements_df = pd.DataFrame(measurements)
                            
                            # Select and reorder columns for display
                            display_columns = []
                            if 'shot_number' in measurements_df.columns:
                                display_columns.append('shot_number')
                            if 'speed_fps' in measurements_df.columns:
                                display_columns.append('speed_fps')
                            if 'ke_ft_lb' in measurements_df.columns:
                                display_columns.append('ke_ft_lb')
                            if 'power_factor' in measurements_df.columns:
                                display_columns.append('power_factor')
                            if 'datetime_shot' in measurements_df.columns:
                                display_columns.append('datetime_shot')
                            if 'clean_bore' in measurements_df.columns:
                                display_columns.append('clean_bore')
                            if 'cold_bore' in measurements_df.columns:
                                display_columns.append('cold_bore')
                            if 'shot_notes' in measurements_df.columns:
                                display_columns.append('shot_notes')
                            
                            # Display measurements table
                            if display_columns:
                                st.dataframe(
                                    measurements_df[display_columns],
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        'shot_number': st.column_config.NumberColumn('Shot #'),
                                        'speed_fps': st.column_config.NumberColumn('Speed (fps)', format="%.1f"),
                                        'ke_ft_lb': st.column_config.NumberColumn('KE (ft-lb)', format="%.1f"),
                                        'power_factor': st.column_config.NumberColumn('Power Factor', format="%.1f"),
                                        'datetime_shot': st.column_config.DatetimeColumn('Date/Time'),
                                        'clean_bore': st.column_config.TextColumn('Clean Bore'),
                                        'cold_bore': st.column_config.TextColumn('Cold Bore'),
                                        'shot_notes': st.column_config.TextColumn('Notes')
                                    }
                                )
                            else:
                                st.info("No measurement data columns found.")
                        else:
                            st.info("No measurements found for this session.")
                        
            else:
                st.info("No sessions found.")
        else:
            st.info("No sessions found. Upload files first to create sessions.")
            
    except Exception as e:
        st.error(f"Error loading sessions: {e}")