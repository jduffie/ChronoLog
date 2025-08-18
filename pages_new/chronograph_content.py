import os
import sys
import streamlit as st

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chronograph.import_tab import render_chronograph_import_tab
from chronograph.logs_tab import render_logs_tab
from files_tab import render_files_tab
from supabase import create_client

def render_chronograph_content():
    """Render the chronograph page content."""
    
    # Get user from session state (should be set by main app)
    if "user" not in st.session_state:
        st.error("User not authenticated")
        return
    
    user = st.session_state.user
    
    # Supabase setup
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        bucket = st.secrets["supabase"]["bucket"]
        supabase = create_client(url, key)
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return

    # Display title
    st.title("⏱️ Chronograph")

    # Create tabs for Import, View, Edit, and My Files
    tab1, tab2, tab3, tab4 = st.tabs(["Import", "View", "Edit", "My Files"])

    with tab1:
        st.subheader("Garmin Xero Log Files")
        render_chronograph_import_tab(user, supabase, bucket)

    with tab2:
        render_logs_tab(user, supabase)

    with tab3:
        st.subheader("Edit Chronograph Data")
        st.info("📝 Edit functionality coming soon...")

    with tab4:
        render_files_tab(user, supabase, bucket, file_type_filter="garmin")
