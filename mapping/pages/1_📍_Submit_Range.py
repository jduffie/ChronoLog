import streamlit as st
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mapping.mapping_controller import MappingController

# Set page configuration
st.set_page_config(
    page_title="Submit Range - ChronoLog Mapping",
    page_icon="📍",
    layout="wide"
)

# Run the mapping controller
controller = MappingController()
controller.run()