import streamlit as st
import uuid
from datetime import datetime, timezone

def render_create_session_tab(user, supabase):
    """Render the Create Session tab"""
    st.header("📝 Create New Session")
    
    # Session creation form
    with st.form("create_session_form"):
        st.subheader("Session Details")
        
        # Basic session information
        col1, col2 = st.columns(2)
        
        with col1:
            bullet_type = st.text_input("Bullet Type", placeholder="e.g., Hornady ELD-X")
            bullet_grain = st.number_input("Bullet Grain", min_value=0.0, step=0.1, format="%.1f")
            session_name = st.text_input("Session Name (Optional)", placeholder="e.g., Range Session - 100yd")
        
        with col2:
            session_date = st.date_input("Session Date", value=datetime.now().date())
            session_time = st.time_input("Session Time", value=datetime.now().time())
            location = st.text_input("Location (Optional)", placeholder="e.g., Local Range")
        
        # Additional session notes
        st.subheader("Session Notes")
        notes = st.text_area("Notes", placeholder="Additional details about this session...")
        
        # Submit button
        submitted = st.form_submit_button("Create Session", type="primary")
        
        if submitted:
            # Validate required fields
            if not bullet_type or bullet_grain <= 0:
                st.error("Please fill in all required fields (Bullet Type and Grain).")
                return
            
            try:
                # Combine date and time
                session_datetime = datetime.combine(session_date, session_time)
                session_timestamp = session_datetime.replace(tzinfo=timezone.utc).isoformat()
                
                # Create session record
                session_id = str(uuid.uuid4())
                session_data = {
                    "id": session_id,
                    "user_email": user["email"],
                    "sheet_name": session_name if session_name else f"Manual - {session_date}",
                    "bullet_type": bullet_type,
                    "bullet_grain": bullet_grain,
                    "session_timestamp": session_timestamp,
                    "uploaded_at": datetime.now(timezone.utc).isoformat(),
                    "file_path": None,  # Manual sessions don't have file paths
                    "location": location if location else None,
                    "notes": notes if notes else None,
                    "manual_session": True  # Flag to indicate this is a manually created session
                }
                
                # Insert session into database
                response = supabase.table("sessions").insert(session_data).execute()
                
                if response.data:
                    st.success(f"✅ Session created successfully! Session ID: {session_id}")
                    st.info("You can now add measurements to this session manually or import data files.")
                    
                    # Store session ID in session state for easy access
                    st.session_state['current_session_id'] = session_id
                    
                    # Clear form by rerunning
                    st.rerun()
                else:
                    st.error("Failed to create session. Please try again.")
                    
            except Exception as e:
                st.error(f"Error creating session: {str(e)}")
    
    # Display recent sessions for reference
    st.subheader("Recent Sessions")
    try:
        recent_sessions = supabase.table("sessions").select("*").eq("user_email", user["email"]).order("uploaded_at", desc=True).limit(5).execute()
        
        if recent_sessions.data:
            for session in recent_sessions.data:
                with st.expander(f"📊 {session['sheet_name']} - {session['bullet_type']} {session['bullet_grain']}gr"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Date:** {session['session_timestamp'][:10]}")
                        st.write(f"**Bullet:** {session['bullet_type']}")
                        st.write(f"**Grain:** {session['bullet_grain']}")
                    with col2:
                        st.write(f"**Session ID:** {session['id']}")
                        st.write(f"**Created:** {session['uploaded_at'][:10]}")
                        if session.get('location'):
                            st.write(f"**Location:** {session['location']}")
                    if session.get('notes'):
                        st.write(f"**Notes:** {session['notes']}")
        else:
            st.info("No sessions found. Create your first session above!")
            
    except Exception as e:
        st.error(f"Error loading recent sessions: {str(e)}")