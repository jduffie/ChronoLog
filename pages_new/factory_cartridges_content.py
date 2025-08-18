import os
import sys
import streamlit as st

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cartridges.factory.create_tab import render_create_cartridge_tab
from cartridges.factory.view_tab import render_view_cartridge_tab
from supabase import create_client

def render_factory_cartridges_content():
    """Render the factory cartridges page content."""
    
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
    st.title("🏭 Factory Cartridges Management")

    # Create tabs for Create and View
    tab1, tab2 = st.tabs(["View", "Create"])

    with tab1:
        render_view_cartridge_tab(user, supabase)

    with tab2:
        render_create_cartridge_tab(user, supabase)
