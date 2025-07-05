import streamlit as st
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import handle_auth
from supabase import create_client
from upload_tab import render_garmin_upload
from logs_tab import render_logs_tab
from view_log_tab import render_view_log_tab
from files_tab import render_files_tab

def main():
    """Main function for the Import page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(
        page_title="Chronograph",
        page_icon="📁",
        layout="wide"
    )
    
    # Handle authentication
    user = handle_auth()
    if not user:
        return
        
    # Display user info in sidebar
    st.sidebar.success(f"Logged in as {user['name']}")
    
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
    st.title("⏱️Chronograph")
    
    # Create tabs for Import, Logs, View Log, and My Files
    tab1, tab2, tab3, tab4 = st.tabs(["Import", "Logs", "View Log", "My Files"])
    
    with tab1:
        st.subheader("Garmin Xero Log Files")
        render_garmin_upload(user, supabase, bucket)
    
    with tab2:
        render_logs_tab(user, supabase)
    
    with tab3:
        render_view_log_tab(user, supabase)
    
    with tab4:
        render_files_tab(user, supabase, bucket, file_type_filter="garmin")

if __name__ == "__main__":
    main()