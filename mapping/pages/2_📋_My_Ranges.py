import streamlit as st
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mapping.mapping_model import MappingModel
from mapping.mapping_view import MappingView
from auth import handle_auth
from supabase import create_client

# Set page configuration
st.set_page_config(
    page_title="My Ranges - ChronoLog Mapping",
    page_icon="📋",
    layout="wide"
)

def main():
    """Main function for the My Ranges page."""
    # Set app identifier for auth system
    if "app" not in st.query_params:
        st.query_params["app"] = "mapping"
        
    # Handle authentication
    user = handle_auth()
    if not user:
        return
        
    # Display user info in sidebar
    st.sidebar.success(f"Logged in as {user['name']}")
    
    # Initialize model and view
    model = MappingModel()
    view = MappingView()
    
    # Check range limit and display count
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        supabase = create_client(url, key)
        range_count = model.get_user_range_count(user["email"], supabase)
        
        # Show current range count
        st.sidebar.info(f"Ranges submitted: {range_count}/15")
        
    except Exception as e:
        st.error(f"Error checking range limit: {str(e)}")
        return
    
    # Display title
    st.title("My Submitted Ranges")
    
    # Fetch and display user ranges table
    try:
        user_ranges = model.get_user_ranges(user["email"], supabase)
        view.display_ranges_table(user_ranges)
    except Exception as e:
        st.error(f"Error loading your submitted ranges: {str(e)}")

if __name__ == "__main__":
    main()