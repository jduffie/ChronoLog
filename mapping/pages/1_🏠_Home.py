import streamlit as st
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from auth import handle_auth


def run():
    """Main function for the Landing page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(
        page_title="Landing - ChronoLog Mapping", page_icon="🏠", layout="wide"
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
    st.subheader("Precision range data for ballistic calculations and range discovery")

    # Key benefits
    st.markdown("---")
    st.warning(" **This is a prototype. There are no guarantees.**")
    st.markdown("---")

    # Introduction section
    st.markdown(
        """


    ---

    """
    )

    # Feature cards
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        ### 🌍 **Browse Ranges**
        Access approved range data from the community library:
        - **Ballistic Calculator Data**
        - **Range Discovery**
        - **Interactive Maps**
        """
        )

    with col2:
        st.markdown(
            """
        ### 📍 **Nominate New Range**
        Submit new ranges using GIS technology
        - **Interactive Map Selection**
        - **Automatic GIS Calculations**
        - **Approval Process**
        """
        )

    # How it works section
    st.markdown("---")
    st.markdown(
        """
    ## How It Works
    
    1. **Submit Range Data**: Select starting and ending points on the interactive map
    2. **GIS Processing**: System automatically computes:
       - Precise three-dimensional distance measurements
       - Azimuth and Elevation angles
       - Geographic coordinates
       - Addresses
    3. **Admin Review**: Submitted ranges undergo approval before being added to the library
    4. **Community Access**: Approved ranges become available for ballistic calculations and range discovery
    
    Use the navigation menu on the left to access different sections of the application.
    """
    )


if __name__ == "__main__":
    run()
