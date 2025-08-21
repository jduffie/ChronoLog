import os
import sys

import streamlit as st
import navigation

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import handle_auth
from supabase import create_client


def main():
    """Main function for the Custom Cartridges page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(page_title="Custom Cartridges", page_icon="🎯", layout="wide")

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
    st.title("🎯 Custom Cartridges Management")
    
    # TBD placeholder
    st.info("🚧 **Custom Cartridges functionality is coming soon!**")
    st.markdown("""
    This page will allow you to:
    - Create custom cartridge specifications
    - Manage your personal cartridge library
    - Define custom loads and configurations
    - Track lot numbers and performance data
    
    **Status:** To Be Developed (TBD)
    """)


if __name__ == "__main__":
    main()