import os
import sys

import streamlit as st

# Add the root directory to the path so we can import our modules
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from supabase import create_client

from auth import handle_auth
from mapping.public_ranges.public_ranges_controller import PublicRangesController


def main():
    """Main function for the Public Ranges page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(
        page_title="Ranges - ChronoLog Mapping", page_icon="🌍", layout="wide"
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

    # Initialize controller
    controller = PublicRangesController()

    # Setup page-specific session state
    controller.setup_page_state()

    # Database connection
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        supabase = create_client(url, key)
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return

    # Display title
    st.title("Ranges")
    st.subheader("Range data available to all users.")

    # Fetch all public ranges
    try:
        public_ranges = controller.get_public_ranges(supabase)

        if not public_ranges:
            st.info("🌍 No public ranges available yet.")
            return

        # Check if user is admin
        is_admin = user["email"] == "johnduffie91@gmail.com"

        if is_admin:
            st.info("🔧 **Admin Mode**: You can edit and delete ranges")

        # Display ranges table with admin capabilities
        if is_admin:
            action_result = controller.display_public_ranges_table_admin(public_ranges)
        else:
            action_result = controller.display_public_ranges_table_readonly(
                public_ranges
            )

        # Handle actions from both admin and readonly users
        if action_result and action_result.get("action"):
            if action_result["action"] == "delete" and is_admin:
                # Handle delete confirmation
                selected_indices = action_result.get("selected_indices", [])
                if selected_indices:
                    if "confirm_delete_public_ranges" in st.session_state:
                        # Perform deletion
                        deleted_count = 0
                        for idx in selected_indices:
                            if idx < len(public_ranges):
                                range_id = public_ranges[idx]["id"]
                                if controller.delete_public_range(range_id, supabase):
                                    deleted_count += 1

                        if deleted_count > 0:
                            st.success(
                                f"✅ {deleted_count} range(s) deleted successfully!"
                            )
                        else:
                            st.error("❌ Failed to delete ranges.")

                        # Clear both confirmation and selection state
                        if "confirm_delete_public_ranges" in st.session_state:
                            del st.session_state["confirm_delete_public_ranges"]
                        if "delete_selected_public_ranges" in st.session_state:
                            del st.session_state["delete_selected_public_ranges"]
                        st.rerun()
                    else:
                        # Show confirmation dialog
                        selected_names = [
                            public_ranges[idx]["range_name"]
                            for idx in selected_indices
                            if idx < len(public_ranges)
                        ]
                        st.warning(
                            f"⚠️ Are you sure you want to delete {len(selected_names)} range(s)?"
                        )
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
                                    del st.session_state[
                                        "delete_selected_public_ranges"
                                    ]
                                st.rerun()

            elif action_result["action"] == "map":
                # Display map with selected ranges (both admin and readonly)
                selected_indices = action_result.get("selected_indices", [])
                if selected_indices:
                    ranges_map = controller.display_ranges_map(
                        public_ranges, selected_indices
                    )
                    st_folium = __import__(
                        "streamlit_folium", fromlist=["st_folium"]
                    ).st_folium
                    st_folium(ranges_map, use_container_width=True, height=500)

    except Exception as e:
        st.error(f"Error loading public ranges: {str(e)}")


if __name__ == "__main__":
    main()
