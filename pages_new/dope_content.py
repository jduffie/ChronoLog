import os
import sys
import streamlit as st

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dope.create_session_tab import render_create_session_tab
from supabase import create_client

def render_dope_content():
    """Render the DOPE creation page content."""
    
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
    st.title("📊 Create DOPE Session")

    # Clear DOPE model state when Create tab is accessed
    if "dope_tab_create_visited" not in st.session_state:
        st.session_state.dope_tab_create_visited = True

        # Clear DOPE model data
        if "dope_model" in st.session_state:
            for tab_name in list(st.session_state.dope_model.get_all_tabs()):
                st.session_state.dope_model.clear_tab_data(tab_name)

        # Reset other tab visit flags
        st.session_state.pop("dope_tab_sessions_visited", None)
        st.session_state.pop("dope_tab_view_visited", None)

        # Clear any Create tab related session state
        keys_to_clear = []
        for key in st.session_state.keys():
            if key.startswith(
                (
                    "edit_range_",
                    "edit_weather_",
                    "edit_rifle_",
                    "edit_cartridge_",
                    "dope_cartridge_selection_",
                    "dope_measurements_table_",
                )
            ):
                keys_to_clear.append(key)

        for key in keys_to_clear:
            del st.session_state[key]

    render_create_session_tab(user, supabase)
