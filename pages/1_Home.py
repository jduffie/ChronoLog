import os
import sys

import streamlit as st

import navigation

# Add the root directory to the path so we can import our modules
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from auth import handle_auth


def run():
    """Main function for the Landing page."""
    # Set page configuration FIRST, before any other Streamlit operations
    st.set_page_config(page_title="ChronoLog - Home", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")

    # Load custom navigation
    navigation.load()

    # Set app identifier for auth system (main ChronoLog app)
    if "app" not in st.query_params:
        st.query_params["app"] = "chronolog"

    # Handle authentication
    user = handle_auth()
    if not user:
        return

    # Display landing page content
    st.title(" ChronoLog")

    # Hero section
    st.markdown(
        """
    ###  **The Power of Automation**
    
    Stop manually transcribing data between spreadsheets, weather apps, and range cards. 
    ChronoLog merges data from multiple sources to build your DOPE (Data On Previous Engagements) 
    with precision and speed.
    """
    )


    # Quick start section
    st.markdown("---")
    st.markdown("##  **Quick Start Guide**")

    st.markdown(
        """
    ### Get started ...
    
   
    """
    )

    # Call to action
    st.markdown("---")
    st.info(
        """
    💡 **Ready to get started?**
    
    Head to the **Chronograph** page to upload your first data file, 
    then visit the **DOPE** page to create your automated ballistic log
    """
    )

    # Disclaimer
    st.markdown("---")
    st.warning(
        "⚠️ **This is a prototype. There are no guarantees. Use at your own risk.**"
    )


if __name__ == "__main__":
    run()
