import streamlit as st
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import handle_auth
from supabase import create_client
from dope.create_session_tab import render_create_session_tab
from dope.sessions_tab import render_sessions_tab
from dope.view_session_tab import render_view_session_tab

def main():
    """Main function for the Sessions page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(
        page_title="DOPE",
        page_icon="📊",
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
        supabase = create_client(url, key)
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return
    
    # Display title
    st.title("Data on Prior Engagements")
    
    # Create tabs for Create, Sessions, and View Session
    tab1, tab2, tab3 = st.tabs(["Create", "Sessions", "View Session"])
    
    with tab1:
        render_create_session_tab(user, supabase)
    
    with tab2:
        render_sessions_tab(user, supabase)
    
    with tab3:
        render_view_session_tab(user, supabase)

if __name__ == "__main__":
    main()