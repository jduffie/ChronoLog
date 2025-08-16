import os
import sys

import streamlit as st

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cartridges.factory.create_tab import render_create_cartridge_tab
from cartridges.factory.view_tab import render_view_cartridge_tab
from auth import handle_auth
from supabase import create_client


def main():
    """Main function for the Factory Cartridges page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(page_title="Factory Cartridges", page_icon="🏭", layout="wide")

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
        supabase = create_client(url, key)
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return

    # Display title
    st.title("🏭 Factory Cartridges Management")

    # Create tabs for Create and View
    tab1, tab2 = st.tabs(["View", "Cretae"])

    with tab1:
        render_view_cartridge_tab(user, supabase)

    with tab2:
        render_create_cartridge_tab(user, supabase)




if __name__ == "__main__":
    main()