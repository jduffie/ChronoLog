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
    st.title("My Ranges")
    st.subheader("Select ranges to map or delete")
    
    # Fetch and display user ranges table with actions
    try:
        user_ranges = model.get_user_ranges(user["email"], supabase)
        table_result = view.display_ranges_table(user_ranges)
        
        # Handle delete action
        if table_result["action"] == "delete" and table_result["selected_indices"]:
            # Confirm deletion
            selected_names = [user_ranges[i].get('range_name', f'Range {i+1}') for i in table_result["selected_indices"]]
            
            st.warning(f"⚠️ Are you sure you want to delete the following {len(selected_names)} range(s)?")
            for name in selected_names:
                st.write(f"• {name}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm Delete", type="primary", use_container_width=True):
                    # Get range IDs for deletion
                    range_ids = [user_ranges[i]["id"] for i in table_result["selected_indices"]]
                    
                    with st.spinner("Deleting ranges..."):
                        success = model.delete_user_ranges(user["email"], range_ids, supabase)
                    
                    if success:
                        st.success(f"✅ Successfully deleted {len(range_ids)} range(s)!")
                        # Clear the delete session state
                        if "delete_selected_ranges" in st.session_state:
                            del st.session_state["delete_selected_ranges"]
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete some ranges. Please try again.")
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    # Clear the delete session state when canceling
                    if "delete_selected_ranges" in st.session_state:
                        del st.session_state["delete_selected_ranges"]
                    st.rerun()
        
        # Map section - always show, but conditionally populate
        st.markdown("---")
        
        if table_result["action"] == "map" and table_result["selected_indices"]:
            st.subheader("🗺️ Selected Ranges Map")
            # Show only selected ranges
            ranges_map = view.display_ranges_map(user_ranges, table_result["selected_indices"])
        elif table_result["selected_indices"] and table_result["action"] != "map":
            st.subheader("🗺️ Map")
            st.info("💡 Click MAP button above to display the selected ranges on the map.")
            # Show empty map when ranges are selected but MAP not clicked
            ranges_map = view.display_ranges_map(user_ranges, [])
        else:
            st.subheader("🗺️ Map")
            st.info("💡 Select ranges in the table above and click MAP to highlight them on the map.")
            # Show empty map when no ranges are selected
            ranges_map = view.display_ranges_map(user_ranges, [])
        
        # Always display the map
        st_folium = __import__('streamlit_folium', fromlist=['st_folium']).st_folium
        st_folium(ranges_map, use_container_width=True, height=600)
            
    except Exception as e:
        st.error(f"Error loading your submitted ranges: {str(e)}")

if __name__ == "__main__":
    main()