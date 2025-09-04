import os
import sys

import streamlit as st

import navigation
from auth import handle_auth

# Add the root directory to the path so we can import our modules
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))


def run():
    """Main function for the Landing page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(
        page_title="ChronoLog - Home",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded")

    # Load custom navigation
    navigation.load()

    # Set app identifier for auth system (main ChronoLog app)
    if "app" not in st.query_params:
        st.query_params["app"] = "chronolog"

    # Handle authentication
    user = handle_auth()
    if not user:
        return

    st.image(
        "./home/resources/home.png",
        use_container_width=True
    )


if __name__ == "__main__":
    run()
