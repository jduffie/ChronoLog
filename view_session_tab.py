import streamlit as st
import pandas as pd

def render_view_session_tab(user, supabase):
    """Render the View Session tab"""
    st.header("View Session")
    
    try:
        # Get user's sessions for selection
        sessions_response = supabase.table("sessions").select("*").eq("user_email", user["email"]).order("uploaded_at", desc=True).execute()
        sessions = sessions_response.data
        
        if sessions:
            # Create session options for selectbox
            session_options = {}
            for session in sessions:
                # Use session_timestamp if available, otherwise fall back to uploaded_at
                if 'session_timestamp' in session and session['session_timestamp']:
                    session_time = pd.to_datetime(session['session_timestamp']).strftime('%Y-%m-%d %H:%M')
                else:
                    session_time = pd.to_datetime(session['uploaded_at']).strftime('%Y-%m-%d %H:%M')
                display_name = f"{session_time} - {session['bullet_type']} ({session['bullet_grain']}gr) - {session['sheet_name']}"
                session_options[display_name] = session
            
            # Check if a session was selected from the Sessions tab table
            default_index = 0
            if "selected_session_from_table" in st.session_state:
                selected_from_table = st.session_state["selected_session_from_table"]
                if selected_from_table in session_options:
                    default_index = list(session_options.keys()).index(selected_from_table)
                # Clear the selection so it doesn't interfere with normal usage
                del st.session_state["selected_session_from_table"]
            
            # Make session selection more prominent
            st.markdown("### Select Session to View")
            selected_session_display = st.selectbox(
                "Sessions:",
                options=list(session_options.keys()),
                index=default_index,
                help="Sessions are ordered by upload time (newest first)",
                key="session_selector"
            )
            
            if selected_session_display:
                selected_session = session_options[selected_session_display]
                
                # Prepare session details values
                if 'session_timestamp' in selected_session and selected_session['session_timestamp']:
                    session_dt = pd.to_datetime(selected_session['session_timestamp'])
                    datetime_value = session_dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    upload_dt = pd.to_datetime(selected_session['uploaded_at'])
                    datetime_value = f"{upload_dt.strftime('%Y-%m-%d %H:%M:%S')} (upload)"
                
                # Create session details table
                session_details_df = pd.DataFrame({
                    'Date/Time': [datetime_value],
                    'Bullet Type': [selected_session['bullet_type']],
                    'Bullet Weight': [f"{selected_session['bullet_grain']} gr"],
                    'Sheet Name': [selected_session['sheet_name']]
                })
                
                st.dataframe(session_details_df, use_container_width=True, hide_index=True)
                
                # Add DELETE SESSION button
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🗑️ DELETE SESSION", type="secondary", key=f"delete_session_{selected_session['id']}"):
                        st.session_state[f"confirm_delete_session_{selected_session['id']}"] = True
                
                # Show confirmation dialog
                if st.session_state.get(f"confirm_delete_session_{selected_session['id']}", False):
                    st.warning("⚠️ Are you sure you want to delete this entire session? This will permanently delete all measurements and cannot be undone!")
                    col_yes, col_no = st.columns(2)
                    
                    with col_yes:
                        if st.button("✅ Yes, Delete Session", key=f"confirm_yes_session_{selected_session['id']}", type="primary"):
                            try:
                                # Security: Verify session belongs to current user before deletion
                                session_check = supabase.table("sessions").select("id").eq("id", selected_session['id']).eq("user_email", user["email"]).execute()
                                
                                if not session_check.data:
                                    st.error("❌ Session not found or access denied")
                                else:
                                    # Delete all measurements for this session (CASCADE should handle this, but being explicit)
                                    supabase.table("measurements").delete().eq("session_id", selected_session['id']).execute()
                                    
                                    # Delete the session
                                    supabase.table("sessions").delete().eq("id", selected_session['id']).eq("user_email", user["email"]).execute()
                                    
                                    # Clear confirmation state
                                    del st.session_state[f"confirm_delete_session_{selected_session['id']}"]
                                    
                                    st.success("✅ Session deleted successfully!")
                                    st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error deleting session: {e}")
                    
                    with col_no:
                        if st.button("❌ Cancel", key=f"confirm_no_session_{selected_session['id']}"):
                            del st.session_state[f"confirm_delete_session_{selected_session['id']}"]
                            st.rerun()
                
                # Location Section
                st.subheader("Location")
                
                # Get locations for dropdown (all approved locations)
                try:
                    locations_response = supabase.table("locations").select("*").execute()
                    active_locations = locations_response.data
                except:
                    active_locations = []
                
                # Location dropdown
                location_options = ["None"] + [f"{loc['name']}" for loc in active_locations]
                location_ids = [None] + [loc['id'] for loc in active_locations]
                
                # Find current location index
                current_location_index = 0
                if selected_session.get('location_id'):
                    try:
                        current_location_index = location_ids.index(selected_session['location_id'])
                    except ValueError:
                        current_location_index = 0
                
                selected_location = st.selectbox(
                    "Location:",
                    options=location_options,
                    index=current_location_index,
                    help="Select the shooting location for this session"
                )
                
                # Update location if changed
                if selected_location != "None":
                    selected_location_id = location_ids[location_options.index(selected_location)]
                    if selected_location_id != selected_session.get('location_id'):
                        try:
                            supabase.table("sessions").update({"location_id": selected_location_id}).eq("id", selected_session['id']).execute()
                            st.success(f"Location updated to: {selected_location}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update location: {e}")
                elif selected_session.get('location_id'):
                    # User selected "None" but session had a location - clear it
                    try:
                        supabase.table("sessions").update({"location_id": None}).eq("id", selected_session['id']).execute()
                        st.success("Location cleared")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to clear location: {e}")
                
                # Get current location details for display
                if selected_session.get('location_id'):
                    # Get full location details from database
                    try:
                        location_response = supabase.table("locations").select("*").eq("id", selected_session['location_id']).execute()
                        if location_response.data:
                            current_location = location_response.data[0]
                            
                            # Create location details table
                            location_df = pd.DataFrame({
                                'Name': [current_location['name']],
                                'Altitude (ft)': [current_location['altitude']],
                                'Azimuth (°)': [current_location['azimuth']],
                                'Latitude': [f"{current_location['latitude']:.6f}" if current_location['latitude'] else ""],
                                'Longitude': [f"{current_location['longitude']:.6f}" if current_location['longitude'] else ""]
                            })
                            
                            st.dataframe(location_df, use_container_width=True, hide_index=True)
                            
                            # Add Google Maps link if available
                            if current_location.get('google_maps_link'):
                                st.markdown(f"📍 [View on Google Maps]({current_location['google_maps_link']})")
                        
                        else:
                            st.info("Location details not found")
                    except Exception as e:
                        st.error(f"Error loading location details: {e}")
                else:
                    st.info("No location assigned to this session")
                
                # Get measurement count and statistics
                measurements_response = supabase.table("measurements").select("*").eq("session_id", selected_session['id']).execute()
                measurements = measurements_response.data
                
                if measurements:
                    df = pd.DataFrame(measurements)
                    
                    # Statistics
                    st.subheader("Session Statistics")
                    
                    # Calculate statistics
                    avg_velocity = df['speed_fps'].mean()
                    std_velocity = df['speed_fps'].std()
                    max_velocity = df['speed_fps'].max()
                    min_velocity = df['speed_fps'].min()
                    velocity_spread = max_velocity - min_velocity if not pd.isna(max_velocity) and not pd.isna(min_velocity) else None
                    
                    # Create statistics table
                    statistics_df = pd.DataFrame({
                        'Total Shots': [len(measurements)],
                        'Avg Velocity (fps)': [f"{avg_velocity:.1f}" if not pd.isna(avg_velocity) else "N/A"],
                        'Std Deviation (fps)': [f"{std_velocity:.1f}" if not pd.isna(std_velocity) else "N/A"],
                        'Velocity Spread (fps)': [f"{velocity_spread:.1f}" if velocity_spread is not None else "N/A"]
                    })
                    
                    st.dataframe(statistics_df, use_container_width=True, hide_index=True)
                    
                    # Display measurement data table
                    st.subheader("Measurement Data")
                    
                    # Reorder columns for better display
                    display_columns = ['shot_number', 'speed_fps', 'delta_avg_fps', 'ke_ft_lb', 'power_factor', 'time_local']
                    if 'clean_bore' in df.columns:
                        display_columns.append('clean_bore')
                    if 'cold_bore' in df.columns:
                        display_columns.append('cold_bore')
                    if 'shot_notes' in df.columns:
                        display_columns.append('shot_notes')
                    
                    # Only show columns that exist
                    display_columns = [col for col in display_columns if col in df.columns]
                    st.dataframe(df[display_columns], use_container_width=True)
                else:
                    st.warning("No measurement data found for this session.")
        else:
            st.info("No sessions found. Upload a file first to create sessions.")
            
    except Exception as e:
        st.error(f"Error loading sessions: {e}")