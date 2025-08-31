import os
import sys

import streamlit as st

import navigation

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import handle_auth
from files_tab import render_files_tab
from supabase import create_client
from weather.import_tab import render_weather_import_tab
from weather.view_tab import render_weather_view_tab


def main():
    """Main function for the Weather page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(page_title="Weather - ChronoLog", page_icon="🌤️", layout="wide", initial_sidebar_state="expanded")

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
        bucket = st.secrets["supabase"]["bucket"]
        supabase = create_client(url, key)
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return

    # Display title
    st.title("️ Weather")

    # Create tabs for Import, View, and My Files
    tab1, tab2, tab3 = st.tabs(
        ["Import", "View", "My Files"]
    )

    with tab1:
        render_weather_import_tab(user, supabase, bucket)

    with tab2:
        render_weather_view_tab(user, supabase)

    with tab3:
        # Filter files to show only weather/kestrel files
        render_files_tab(user, supabase, bucket, file_type_filter="kestrel")


if __name__ == "__main__":
    main()
