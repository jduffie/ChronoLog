import os
import sys

import streamlit as st
import navigation

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import handle_auth
from dope.create_session_tab import render_create_session_tab
from supabase import create_client


def main():
    """Main function for the DOPE Create page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(page_title="DOPE Create", page_icon="📊", layout="wide")

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
    st.title("📈 Create DOPE Session")

    # Clear DOPE model state when Create page is accessed
    if "dope_page_create_visited" not in st.session_state:
        st.session_state.dope_page_create_visited = True

        # Clear DOPE model data
        if "dope_model" in st.session_state:
            for tab_name in list(st.session_state.dope_model.get_all_tabs()):
                st.session_state.dope_model.clear_tab_data(tab_name)

        # Reset other page visit flags
        st.session_state.pop("dope_page_sessions_visited", None)
        st.session_state.pop("dope_page_view_visited", None)
        st.session_state.pop("dope_page_overview_visited", None)

        # Clear any Create page related session state
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


if __name__ == "__main__":
    main()
