import streamlit as st
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import handle_auth
from supabase import create_client
from weather.import_tab import render_weather_import_tab
from weather.logs_tab import render_weather_logs_tab
from weather.view_log_tab import render_weather_view_log_tab
from weather.sources_tab import render_weather_sources_tab
from files_tab import render_files_tab


def main():
    """Main function for the Weather page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(page_title="Weather - ChronoLog", page_icon="🌤️", layout="wide")

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
    st.title("🌤️ Weather")

    # Create tabs for Sources, Import, Logs, View Log, and My Files
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Sources", "Import", "Logs", "View Log", "My Files"]
    )

    with tab1:
        render_weather_sources_tab(user, supabase)

    with tab2:
        st.subheader("Kestrel Log Files")
        render_weather_import_tab(user, supabase, bucket)

    with tab3:
        render_weather_logs_tab(user, supabase)

    with tab4:
        render_weather_view_log_tab(user, supabase)

    with tab5:
        # Filter files to show only weather/kestrel files
        render_files_tab(user, supabase, bucket, file_type_filter="kestrel")


if __name__ == "__main__":
    main()
