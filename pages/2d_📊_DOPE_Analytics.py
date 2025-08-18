import os
import sys

import streamlit as st
import navigation

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import handle_auth
from dope.sessions_tab import render_sessions_tab
from supabase import create_client


def main():
    """Main function for the DOPE Analytics page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(page_title="DOPE Analytics", page_icon="📊", layout="wide")

    # Load custom navigation
    navigation.load()

    # Handle authentication
    user = handle_auth()
    if not user:
        return

    # Supabase setup
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        supabase = create_client(url, key)
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return

    # Display title
    st.title("📊 DOPE Analytics")

    # Clear DOPE model state when Analytics page is accessed
    if "dope_page_sessions_visited" not in st.session_state:
        st.session_state.dope_page_sessions_visited = True

        # Clear DOPE model data
        if "dope_model" in st.session_state:
            for tab_name in list(st.session_state.dope_model.get_all_tabs()):
                st.session_state.dope_model.clear_tab_data(tab_name)

        # Reset other page visit flags
        st.session_state.pop("dope_page_create_visited", None)
        st.session_state.pop("dope_page_view_visited", None)
        st.session_state.pop("dope_page_overview_visited", None)

        # Clear any Analytics page related session state
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

    render_sessions_tab(user, supabase)


if __name__ == "__main__":
    main()
