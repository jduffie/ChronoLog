import os
import sys

import streamlit as st

import navigation

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import handle_auth
from dope.create.create_page import render_create_page
from supabase import create_client


def run():
    """Main function for the DOPE Create page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(page_title="DOPE Create", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

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
    st.title(" Create DOPE Session")

    render_create_page(user, supabase)


if __name__ == "__main__":
    run()
