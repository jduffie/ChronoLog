import streamlit as st
import pandas as pd
from datetime import datetime
from .models import ChronographSession
from .service import ChronographService

def render_logs_tab(user, supabase):
    """Render the Logs tab showing all chronograph sessions"""
    st.header("📊 Chronograph Logs")
    
    try:
        # Initialize service
        chrono_service = ChronographService(supabase)
        
        # Get all sessions for the user
        sessions = chrono_service.get_sessions_for_user(user["email"])
        
        if not sessions:
            st.info("No chronograph logs found. Import some data files to get started!")
            return
        
        # Create a summary table
        st.subheader("📋 Session Summary")
        
        # Create display columns using entity methods
        display_data = []
        for session in sessions:
            display_data.append({
                "Date": session.datetime_local.strftime("%Y-%m-%d %H:%M"),
                "Session": session.tab_name,
                "Bullet": session.bullet_display(),
                "Shots": session.shot_count,
                "Avg Speed": session.avg_speed_display(),
                "Session ID": session.id[:8] + "..."
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
            bullet_types = chrono_service.get_unique_bullet_types(user["email"])
            selected_bullet = st.selectbox("Filter by Bullet Type", ["All"] + bullet_types)
        
        with col2:
            date_range = st.date_input("Filter by Date Range", value=[], max_value=datetime.now().date())
        
        # Apply filters using service
        start_date_str = None
        end_date_str = None
        
        if date_range:
            if len(date_range) == 2:
                start_date_str = date_range[0].isoformat()
                end_date_str = date_range[1].isoformat()
            elif len(date_range) == 1:
                start_date_str = date_range[0].isoformat()
                end_date_str = date_range[0].isoformat()
        
        # Get filtered sessions from service
        if selected_bullet != "All" or date_range:
            filtered_sessions = chrono_service.get_sessions_filtered(
                user["email"], 
                bullet_type=selected_bullet if selected_bullet != "All" else None,
                start_date=start_date_str,
                end_date=end_date_str
            )
        else:
            filtered_sessions = sessions
        
        # Display filtered sessions
        for session in filtered_sessions:
            with st.expander(f"📊 {session.display_name()}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Bullet:** {session.bullet_type}")
                    st.write(f"**Grain:** {session.bullet_grain}")
                    st.write(f"**Date:** {session.datetime_local.strftime('%Y-%m-%d %H:%M')}")
                    
                with col2:
                    st.write(f"**Session ID:** {session.id}")
                    st.write(f"**Uploaded:** {session.uploaded_at.strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**File:** {session.file_name()}")
                
                # Use pre-calculated session stats from entity
                if session.has_measurements():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Shots", session.shot_count)
                    with col2:
                        st.metric("Avg Speed", session.avg_speed_display())
                    with col3:
                        st.metric("Std Dev", session.std_dev_display())
                    
                    # Quick stats
                    st.write("**Quick Stats:**")
                    st.write(f"• Min: {session.min_speed_fps:.0f} fps" if session.min_speed_fps else "• Min: N/A")
                    st.write(f"• Max: {session.max_speed_fps:.0f} fps" if session.max_speed_fps else "• Max: N/A")
                    st.write(f"• Range: {session.velocity_range_display()}")
                    
                    # View button
                    if st.button(f"View Details", key=f"view_{session.id}"):
                        st.session_state['selected_session_id'] = session.id
                        st.info("Session selected! Go to the 'View Log' tab to see detailed analysis.")
                else:
                    st.info("No measurements found for this session.")
    
    except Exception as e:
        st.error(f"Error loading logs: {str(e)}")