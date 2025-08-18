import os
import sys
import streamlit as st

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rifles.create_tab import render_create_rifle_tab
from rifles.view_tab import render_view_rifle_tab
from supabase import create_client

def render_rifles_content():
    """Render the rifles page content."""
    
    # Get user from session state (should be set by main app)
    if "user" not in st.session_state:
        st.error("User not authenticated")
        return
    
    user = st.session_state.user
    
    # Supabase setup
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        supabase = create_client(url, key)
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return

    # Display title
    st.title("📏 Rifle Management")

    # Create tabs for Create and View
    tab1, tab2 = st.tabs(["Create", "View"])

    with tab1:
        render_create_rifle_tab(user, supabase)

    with tab2:
        render_view_rifle_tab(user, supabase)
