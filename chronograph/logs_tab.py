import streamlit as st
import pandas as pd
from datetime import datetime

def render_logs_tab(user, supabase):
    """Render the Logs tab showing all chronograph sessions"""
    st.header("📊 Chronograph Logs")
    
    try:
        # Get all sessions for the user
        sessions_response = supabase.table("chrono_sessions").select("*").eq("user_email", user["email"]).order("datetime_local", desc=True).execute()
        
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
            # Use the pre-calculated session stats from chrono_sessions table
            shot_count = session.get("shot_count", 0)
            avg_speed = session.get("avg_speed_fps")
            
            display_data.append({
                "Date": datetime.fromisoformat(session["datetime_local"]).strftime("%Y-%m-%d %H:%M"),
                "Session": session["tab_name"],
                "Bullet": f"{session['bullet_type']} {session['bullet_grain']}gr",
                "Shots": shot_count,
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
                                   if start_date <= datetime.fromisoformat(s["datetime_local"]).date() <= end_date]
            elif len(date_range) == 1:
                target_date = date_range[0]
                filtered_sessions = [s for s in filtered_sessions 
                                   if datetime.fromisoformat(s["datetime_local"]).date() == target_date]
        
        # Display filtered sessions
        for session in filtered_sessions:
            with st.expander(f"📊 {session['tab_name']} - {datetime.fromisoformat(session['datetime_local']).strftime('%Y-%m-%d %H:%M')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Bullet:** {session['bullet_type']}")
                    st.write(f"**Grain:** {session['bullet_grain']}")
                    st.write(f"**Date:** {datetime.fromisoformat(session['datetime_local']).strftime('%Y-%m-%d %H:%M')}")
                    
                with col2:
                    st.write(f"**Session ID:** {session['id']}")
                    st.write(f"**Uploaded:** {datetime.fromisoformat(session['uploaded_at']).strftime('%Y-%m-%d %H:%M')}")
                    if session.get('file_path'):
                        st.write(f"**File:** {session['file_path'].split('/')[-1]}")
                
                # Use pre-calculated session stats
                shot_count = session.get("shot_count", 0)
                avg_speed = session.get("avg_speed_fps")
                std_dev = session.get("std_dev_fps")
                min_speed = session.get("min_speed_fps")
                max_speed = session.get("max_speed_fps")
                
                if shot_count > 0:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Shots", shot_count)
                    with col2:
                        st.metric("Avg Speed", f"{avg_speed:.0f} fps" if avg_speed else "N/A")
                    with col3:
                        st.metric("Std Dev", f"{std_dev:.1f} fps" if std_dev else "N/A")
                    
                    # Quick stats
                    st.write("**Quick Stats:**")
                    st.write(f"• Min: {min_speed:.0f} fps" if min_speed else "• Min: N/A")
                    st.write(f"• Max: {max_speed:.0f} fps" if max_speed else "• Max: N/A")
                    st.write(f"• Range: {max_speed - min_speed:.0f} fps" if max_speed and min_speed else "• Range: N/A")
                    
                    # View button
                    if st.button(f"View Details", key=f"view_{session['id']}"):
                        st.session_state['selected_session_id'] = session['id']
                        st.info("Session selected! Go to the 'View Log' tab to see detailed analysis.")
                else:
                    st.info("No measurements found for this session.")
    
    except Exception as e:
        st.error(f"Error loading logs: {str(e)}")