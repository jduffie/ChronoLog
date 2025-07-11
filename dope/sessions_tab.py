import streamlit as st
import pandas as pd

def render_sessions_tab(user, supabase):
    """Render the Sessions tab - simple table view only"""
    st.header("📊 Sessions")
    
    try:
        # Get user's sessions
        sessions_response = supabase.table("dope_sessions").select("*").eq("user_email", user["email"]).order("created_at", desc=True).execute()
        sessions = sessions_response.data
        
        if sessions:
            # Process sessions with aggregated measurement data
            session_summaries = []
            
            for session in sessions:
                # Get measurements for this session
                measurements_response = supabase.table("dope_measurements").select("*").eq("dope_session_id", session['id']).execute()
                measurements = measurements_response.data
                
                # Prepare session timestamp
                if session.get('created_at'):
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
            
            # Create DataFrame and display
            if session_summaries:
                sessions_df = pd.DataFrame(session_summaries)
                
                st.markdown("### Session Summary")
                st.write(f"Total sessions: {len(sessions)}")
                
                # Display the sessions table (read-only)
                st.dataframe(
                    sessions_df,
                    use_container_width=True,
                    hide_index=True,
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
            else:
                st.info("No sessions found.")
        else:
            st.info("No sessions found. Upload files first to create sessions.")
            
    except Exception as e:
        st.error(f"Error loading sessions: {e}")