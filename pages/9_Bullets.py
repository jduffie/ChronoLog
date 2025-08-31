import os
import sys

import streamlit as st

import navigation

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import handle_auth
from bullets.create_tab import render_create_bullets_tab
from bullets.view_tab import render_view_bullets_tab
from supabase import create_client


def main():
    """Main function for the Ammo page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(page_title="Bullets", page_icon="📦", layout="wide", initial_sidebar_state="expanded")

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
    st.title(" Bullets Management")

    # Create tabs for Create and View
    tab1, tab2 = st.tabs(["View", "Add"])

    with tab1:
        render_view_bullets_tab(user, supabase)

    with tab2:
        render_create_bullets_tab(user, supabase)


if __name__ == "__main__":
    main()
