import streamlit as st
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mapping.mapping_model import MappingModel
from mapping.mapping_view import MappingView
from auth import handle_auth
from supabase import create_client

def main():
    """Main function for the Public Ranges page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(
        page_title="Public Ranges - ChronoLog Mapping",
        page_icon="🌍",
        layout="wide"
    )
    
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
    
    # Database connection
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        supabase = create_client(url, key)
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return
    
    # Display title
    st.title("Public Ranges")
    st.subheader("Approved shooting ranges available for public use")
    
    # Fetch all public ranges
    try:
        public_ranges = model.get_public_ranges(supabase)
        
        if not public_ranges:
            st.info("🌍 No public ranges available yet.")
            return
            
        st.markdown(f"### Available Ranges ({len(public_ranges)})")
        
        # Check if user is admin
        is_admin = user["email"] == "johnduffie91@gmail.com"
        
        if is_admin:
            st.info("🔧 **Admin Mode**: You can edit and delete ranges")
        
        # Display ranges table with admin capabilities
        if is_admin:
            action_result = view.display_public_ranges_table_admin(public_ranges)
        else:
            action_result = view.display_public_ranges_table_readonly(public_ranges)
        
        # Handle admin actions
        if is_admin and action_result and action_result.get("action"):
            if action_result["action"] == "delete":
                # Handle delete confirmation
                selected_indices = action_result.get("selected_indices", [])
                if selected_indices:
                    if "confirm_delete_public_ranges" in st.session_state:
                        # Perform deletion
                        deleted_count = 0
                        for idx in selected_indices:
                            if idx < len(public_ranges):
                                range_id = public_ranges[idx]["id"]
                                if model.delete_public_range(range_id, supabase):
                                    deleted_count += 1
                        
                        if deleted_count > 0:
                            st.success(f"✅ {deleted_count} range(s) deleted successfully!")
                        else:
                            st.error("❌ Failed to delete ranges.")
                        
                        # Clear confirmation state
                        del st.session_state["confirm_delete_public_ranges"]
                        st.rerun()
                    else:
                        # Show confirmation dialog
                        selected_names = [public_ranges[idx]["range_name"] for idx in selected_indices if idx < len(public_ranges)]
                        st.warning(f"⚠️ Are you sure you want to delete {len(selected_names)} range(s)?")
                        st.write("Selected ranges:")
                        for name in selected_names:
                            st.write(f"• {name}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Confirm Delete", type="primary"):
                                st.session_state["confirm_delete_public_ranges"] = True
                                st.rerun()
                        with col2:
                            if st.button("❌ Cancel"):
                                # Clear delete selection
                                if "delete_selected_public_ranges" in st.session_state:
                                    del st.session_state["delete_selected_public_ranges"]
                                st.rerun()
            
            elif action_result["action"] == "map":
                # Display map with selected ranges
                selected_indices = action_result.get("selected_indices", [])
                if selected_indices:
                    st.markdown("### Selected Ranges Map")
                    ranges_map = view.display_ranges_map(public_ranges, selected_indices)
                    st_folium = __import__('streamlit_folium', fromlist=['st_folium']).st_folium
                    st_folium(ranges_map, use_container_width=True, height=500)
        
        # Display map for read-only users when ranges are available
        elif not is_admin and public_ranges:
            st.markdown("### All Public Ranges Map")
            all_indices = list(range(len(public_ranges)))
            ranges_map = view.display_ranges_map(public_ranges, all_indices)
            st_folium = __import__('streamlit_folium', fromlist=['st_folium']).st_folium
            st_folium(ranges_map, use_container_width=True, height=500)
    
    except Exception as e:
        st.error(f"Error loading public ranges: {str(e)}")

if __name__ == "__main__":
    main()