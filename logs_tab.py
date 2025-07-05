import streamlit as st
import pandas as pd
from datetime import datetime

def render_logs_tab(user, supabase):
    """Render the Logs tab showing all chronograph sessions"""
    st.header("📊 Chronograph Logs")
    
    try:
        # Get all sessions for the user
        sessions_response = supabase.table("sessions").select("*").eq("user_email", user["email"]).order("session_timestamp", desc=True).execute()
        
        if not sessions_response.data:
            st.info("No chronograph logs found. Import some data files to get started!")
            return
        
        sessions = sessions_response.data
        
        # Create a summary table
        st.subheader("📋 Session Summary")
        
        # Convert to DataFrame for better display
        df_sessions = pd.DataFrame(sessions)
        
        # Create display columns
        display_data = []
        for session in sessions:
            # Get measurement count for this session
            measurements_response = supabase.table("measurements").select("*", count="exact").eq("session_id", session["id"]).execute()
            measurement_count = measurements_response.count if measurements_response.count else 0
            
            # Get basic stats if measurements exist
            avg_speed = None
            if measurement_count > 0:
                stats_response = supabase.table("measurements").select("speed_fps").eq("session_id", session["id"]).execute()
                if stats_response.data:
                    speeds = [m["speed_fps"] for m in stats_response.data if m["speed_fps"]]
                    if speeds:
                        avg_speed = sum(speeds) / len(speeds)
            
            display_data.append({
                "Date": datetime.fromisoformat(session["session_timestamp"]).strftime("%Y-%m-%d %H:%M"),
                "Session": session["sheet_name"],
                "Bullet": f"{session['bullet_type']} {session['bullet_grain']}gr",
                "Shots": measurement_count,
                "Avg Speed": f"{avg_speed:.0f} fps" if avg_speed else "N/A",
                "Session ID": session["id"][:8] + "..."
            })
        
        # Display as table
        if display_data:
            df_display = pd.DataFrame(display_data)
            st.dataframe(df_display, use_container_width=True)
        
        # Detailed session cards
        st.subheader("📁 Session Details")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            bullet_types = list(set([s["bullet_type"] for s in sessions]))
            selected_bullet = st.selectbox("Filter by Bullet Type", ["All"] + bullet_types)
        
        with col2:
            date_range = st.date_input("Filter by Date Range", value=[], max_value=datetime.now().date())
        
        # Apply filters
        filtered_sessions = sessions
        if selected_bullet != "All":
            filtered_sessions = [s for s in filtered_sessions if s["bullet_type"] == selected_bullet]
        
        if date_range:
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_sessions = [s for s in filtered_sessions 
                                   if start_date <= datetime.fromisoformat(s["session_timestamp"]).date() <= end_date]
            elif len(date_range) == 1:
                target_date = date_range[0]
                filtered_sessions = [s for s in filtered_sessions 
                                   if datetime.fromisoformat(s["session_timestamp"]).date() == target_date]
        
        # Display filtered sessions
        for session in filtered_sessions:
            with st.expander(f"📊 {session['sheet_name']} - {datetime.fromisoformat(session['session_timestamp']).strftime('%Y-%m-%d %H:%M')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Bullet:** {session['bullet_type']}")
                    st.write(f"**Grain:** {session['bullet_grain']}")
                    st.write(f"**Date:** {datetime.fromisoformat(session['session_timestamp']).strftime('%Y-%m-%d %H:%M')}")
                    
                with col2:
                    st.write(f"**Session ID:** {session['id']}")
                    st.write(f"**Uploaded:** {datetime.fromisoformat(session['uploaded_at']).strftime('%Y-%m-%d %H:%M')}")
                    if session.get('file_path'):
                        st.write(f"**File:** {session['file_path'].split('/')[-1]}")
                
                # Get measurements for this session
                measurements_response = supabase.table("measurements").select("*").eq("session_id", session["id"]).execute()
                
                if measurements_response.data:
                    measurements = measurements_response.data
                    speeds = [m["speed_fps"] for m in measurements if m["speed_fps"]]
                    
                    if speeds:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Shots", len(measurements))
                        with col2:
                            st.metric("Avg Speed", f"{sum(speeds)/len(speeds):.0f} fps")
                        with col3:
                            st.metric("Std Dev", f"{pd.Series(speeds).std():.1f} fps")
                        
                        # Quick stats
                        st.write("**Quick Stats:**")
                        st.write(f"• Min: {min(speeds):.0f} fps")
                        st.write(f"• Max: {max(speeds):.0f} fps")
                        st.write(f"• Range: {max(speeds) - min(speeds):.0f} fps")
                        
                        # View button
                        if st.button(f"View Details", key=f"view_{session['id']}"):
                            st.session_state['selected_session_id'] = session['id']
                            st.info("Session selected! Go to the 'View Log' tab to see detailed analysis.")
                else:
                    st.info("No measurements found for this session.")
    
    except Exception as e:
        st.error(f"Error loading logs: {str(e)}")