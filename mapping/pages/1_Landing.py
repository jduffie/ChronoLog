import streamlit as st
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth import handle_auth

def run():
    """Main function for the Landing page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(
        page_title="Landing - ChronoLog Mapping",
        page_icon="🏠",
        layout="wide"
    )
    
    # Set app identifier for auth system
    if "app" not in st.query_params:
        st.query_params["app"] = "mapping"
        
    # Handle authentication
    user = handle_auth()
    if not user:
        return
        
    # Display user info in sidebar (only on this page to avoid duplication)
    if "user_info_displayed" not in st.session_state:
        st.sidebar.success(f"Logged in as {user['name']}")
        st.session_state["user_info_displayed"] = True
    
    # Display landing page content
    st.title("Welcome to ChronoLog Mapping")
    st.subheader("Your comprehensive range mapping and management solution")
    
    # Introduction section
    st.markdown("""
    ## What is ChronoLog Mapping?
    
    ChronoLog Mapping is a comprehensive tool for managing and exploring shooting ranges. Whether you're looking to find existing ranges or nominate new ones, this platform provides the tools you need.
    
    ## Available Features:
    """)
    
    # Feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🌍 **Ranges**
        Browse all public ranges available to the community. View detailed information including:
        - Range locations and measurements
        - Distance and elevation data
        - Interactive maps
        """)
        
        st.markdown("""
        ### 📋 **My Ranges**
        Manage your personal range nominations:
        - View your submitted ranges
        - Track approval status
        - Edit or delete your submissions
        """)
    
    with col2:
        st.markdown("""
        ### 📍 **Nominate New Range**
        Submit new ranges for community use:
        - Interactive map selection
        - Automatic distance and elevation calculations
        - Detailed range information forms
        """)
        
        st.markdown("""
        ### 👑 **Admin** *(Admin Only)*
        Administrative functions for managing the platform:
        - Review and approve range nominations
        - Manage user permissions
        - System maintenance
        """)
    
    # Getting started section
    st.markdown("---")
    st.markdown("""
    ## Getting Started
    
    1. **Explore Ranges**: Start by browsing the public ranges to see what's available
    2. **Submit Your Own**: Use the nomination feature to add ranges you know about
    3. **Manage Your Data**: Keep track of your submissions in the My Ranges section
    
    Use the navigation menu on the left to access different sections of the application.
    """)
    
    # Quick stats or additional info could go here
    st.markdown("---")
    st.info("💡 **Tip**: Click on any page in the sidebar to navigate to that section.")

if __name__ == "__main__":
    run()