import os
import sys

import streamlit as st

import navigation
from auth import handle_auth
from rifles.create_tab import render_create_rifle_tab
from rifles.view_tab import render_view_rifle_tab
from supabase import create_client

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Main function for the Rifles page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(
        page_title="Rifles",
        page_icon="📏",
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

    # Display title
    st.title(" Rifle Management")

    # Create tabs for View and Create
    tab1, tab2 = st.tabs(["View", "Add"])

    # Initialize rifles page state
    if "rifles_view_tab" not in st.session_state:
        st.session_state.rifles_view_tab = {}
    if "rifles_create_tab" not in st.session_state:
        st.session_state.rifles_create_tab = {}

    with tab1:
        # Clear view tab state
        st.session_state.rifles_view_tab = {}
        render_view_rifle_tab(user, supabase)
    with tab2:
        # Clear create tab state
        st.session_state.rifles_create_tab = {}
        render_create_rifle_tab(user, supabase)


if __name__ == "__main__":
    main()
