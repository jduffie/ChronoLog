import os
import sys

import streamlit as st

import navigation
from auth import handle_auth
from dope.view.view_page import render_view_page
from supabase import create_client

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Main function for the DOPE View page."""
    # Set page configuration FIRST, before any other Streamlit operations
    print("start")

    st.set_page_config(
        page_title="DOPE View",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded")

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

    render_view_page()


if __name__ == "__main__":
    main()
