import os
import sys

import streamlit as st

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import navigation
from auth import handle_auth
from cartridges.edit_tab import render_edit_cartridges_tab
from cartridges.view_tab import render_view_cartridges_tab
from supabase import create_client


def main():
    """Main function for the Cartridges page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(page_title="Cartridges", layout="wide")

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
    st.title("Cartridges Management")
    st.markdown(
        "Manage both factory and custom cartridge specifications with comprehensive bullet data."
    )

    # Create tabs for View and Create
    tab1, tab2 = st.tabs(["View Cartridges", "Create Cartridge"])

    with tab1:
        render_view_cartridges_tab(user, supabase)

    with tab2:
        render_edit_cartridges_tab(user, supabase)


if __name__ == "__main__":
    main()
