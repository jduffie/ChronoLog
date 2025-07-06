import streamlit as st
import pandas as pd
import re

def safe_parse_datetime(timestamp_str):
    """Safely parse datetime string, handling microseconds with extra precision"""
    if not timestamp_str:
        return None
    
    try:
        # First try pandas direct parsing
        return pd.to_datetime(timestamp_str)
    except Exception:
        try:
            # If that fails, try to fix microseconds issue
            # Pattern to match ISO format with potentially too many microsecond digits
            pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\.(\d+)(\+\d{2}:\d{2}|Z|$)'
            match = re.match(pattern, timestamp_str)
            
            if match:
                base_time = match.group(1)
                microseconds = match.group(2)
                timezone = match.group(3)
                
                # Truncate microseconds to 6 digits
                if len(microseconds) > 6:
                    microseconds = microseconds[:6]
                elif len(microseconds) < 6:
                    microseconds = microseconds.ljust(6, '0')
                
                # Reconstruct the timestamp
                fixed_timestamp = f"{base_time}.{microseconds}{timezone}"
                return pd.to_datetime(fixed_timestamp)
            else:
                # Try without microseconds
                return pd.to_datetime(timestamp_str.split('.')[0])
        except Exception:
            # Last resort - return current time
            return pd.Timestamp.now()

def render_sessions_tab(user, supabase):
    """Render the Sessions tab"""
    st.header("📊 Sessions")
    
    try:
        # Get user's sessions
        sessions_response = supabase.table("sessions").select("*").eq("user_email", user["email"]).order("session_timestamp", desc=True).execute()
        sessions = sessions_response.data
        
        if sessions:
            # Process sessions with aggregated measurement data
            session_summaries = []
            session_lookup = {}  # For mapping display rows to session data
            
            for session in sessions:
                # Get measurements for this session
                measurements_response = supabase.table("measurements").select("*").eq("session_id", session['id']).execute()
                measurements = measurements_response.data
                
                # Prepare session timestamp
                if session.get('session_timestamp'):
                    session_dt = safe_parse_datetime(session['session_timestamp'])
                    session_date = session_dt.strftime('%Y-%m-%d')
                    session_time = session_dt.strftime('%H:%M')
                else:
                    upload_dt = safe_parse_datetime(session['uploaded_at'])
                    session_date = upload_dt.strftime('%Y-%m-%d')
                    session_time = upload_dt.strftime('%H:%M')
                
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
                    'Bullet Type': session['bullet_type'],
                    'Bullet Weight (gr)': session['bullet_grain'],
                    'Shot Count': shot_count,
                    'Avg Velocity (fps)': avg_velocity,
                    'Std Dev (fps)': std_velocity,
                    'Velocity Spread (fps)': velocity_spread,
                    'Sheet Name': session['sheet_name']
                }
                session_summaries.append(row_data)
                
                # Map this row to session data for lookup
                session_lookup[len(session_summaries) - 1] = session
            
            # Create DataFrame and display
            if session_summaries:
                sessions_df = pd.DataFrame(session_summaries)
                
                st.markdown("### Session Summary")
                st.write(f"Total sessions: {len(sessions)}")
                
                # Add instruction text
                st.info("💡 Click on any row to jump to that session in the View Session tab")
                
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
                        'Bullet Type': st.column_config.TextColumn('Bullet Type'),
                        'Bullet Weight (gr)': st.column_config.NumberColumn('Bullet Weight (gr)', format="%.1f"),
                        'Shot Count': st.column_config.NumberColumn('Shot Count'),
                        'Avg Velocity (fps)': st.column_config.TextColumn('Avg Velocity (fps)'),
                        'Std Dev (fps)': st.column_config.TextColumn('Std Dev (fps)'),
                        'Velocity Spread (fps)': st.column_config.TextColumn('Velocity Spread (fps)'),
                        'Sheet Name': st.column_config.TextColumn('Sheet Name')
                    }
                )
                
                # Handle row selection - jump to View Session tab
                if selected_rows.selection.rows:
                    selected_row_index = selected_rows.selection.rows[0]
                    if selected_row_index in session_lookup:
                        selected_session = session_lookup[selected_row_index]
                        
                        # Store the selected session in session state for the View Session tab
                        if 'session_timestamp' in selected_session and selected_session['session_timestamp']:
                            session_time = safe_parse_datetime(selected_session['session_timestamp']).strftime('%Y-%m-%d %H:%M')
                        else:
                            session_time = safe_parse_datetime(selected_session['uploaded_at']).strftime('%Y-%m-%d %H:%M')
                        session_display_name = f"{session_time} - {selected_session['bullet_type']} ({selected_session['bullet_grain']}gr) - {selected_session['sheet_name']}"
                        
                        # Set the session in session state so View Session tab can pick it up
                        st.session_state["selected_session_from_table"] = session_display_name
                        
                        # Show feedback to user
                        st.success(f"🎯 Selected session: {session_display_name}")
                        st.info("➡️ Navigate to the 'View Session' tab to see details")
                        
                        # Auto-switch to View Session tab by setting a flag
                        st.session_state["switch_to_view_session"] = True
            else:
                st.info("No sessions found.")
        else:
            st.info("No sessions found. Upload files first to create sessions.")
            
    except Exception as e:
        st.error(f"Error loading sessions: {e}")