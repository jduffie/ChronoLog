import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import handle_auth
from mapping.mapping_model import MappingModel
from supabase import create_client

# Set page configuration
st.set_page_config(
    page_title="ChronoLog Mapping Tool",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main landing page for the ChronoLog Mapping Tool."""
    # Set app identifier for auth system
    if "app" not in st.query_params:
        st.query_params["app"] = "mapping"
        
    # Handle authentication
    user = handle_auth()
    if not user:
        return
        
    # Display user info in sidebar
    st.sidebar.success(f"Logged in as {user['name']}")
    
    # Initialize model for getting user stats
    model = MappingModel()
    
    # Get user statistics
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        supabase = create_client(url, key)
        range_count = model.get_user_range_count(user["email"], supabase)
        
        # Show current range count in sidebar
        st.sidebar.info(f"Ranges submitted: {range_count}/15")
        
        if range_count >= 15:
            st.sidebar.warning("⚠️ Range limit reached")
        
    except Exception as e:
        st.sidebar.error("Error loading stats")
        range_count = 0
    
    # Main page content
    st.title("🎯 ChronoLog Mapping Tool")
    st.markdown("---")
    
    # Welcome message and navigation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Welcome to the ChronoLog Mapping Tool
        
        This application allows you to:
        - **Submit new shooting ranges** by selecting two points on an interactive map
        - **Calculate range measurements** including distance, azimuth, and elevation angles
        - **View your submitted ranges** in an organized table format
        - **Track your submission progress** (up to 15 ranges per user)
        """)
        
        if range_count >= 15:
            st.error("🚫 **Maximum range limit reached**")
            st.warning("You have submitted the maximum number of ranges (15). You can still view your existing ranges.")
        else:
            st.success(f"✅ You can submit {15 - range_count} more ranges.")
    
    with col2:
        st.markdown("### Quick Navigation")
        
        if range_count < 15:
            if st.button("📍 Submit New Range", type="primary", use_container_width=True):
                st.switch_page("pages/1_📍_Submit_Range.py")
        else:
            st.button("📍 Submit New Range", disabled=True, use_container_width=True, help="Range limit reached")
            
        if st.button("📋 View My Ranges", use_container_width=True):
            st.switch_page("pages/2_📋_My_Ranges.py")
    
    # Statistics section
    if range_count > 0:
        st.markdown("---")
        st.markdown("### Your Range Statistics")
        
        # Display basic stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Ranges", range_count)
        with col2:
            st.metric("Remaining Slots", max(0, 15 - range_count))
        with col3:
            completion_pct = round((range_count / 15) * 100, 1)
            st.metric("Completion", f"{completion_pct}%")

if __name__ == "__main__":
    main()