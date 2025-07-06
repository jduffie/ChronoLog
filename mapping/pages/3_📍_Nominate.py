import streamlit as st
import sys
import os

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mapping.nominate_controller import NominateController

def main():
    """Main function for the Nominate New Range page."""
    controller = NominateController()
    controller.run()

if __name__ == "__main__":
    main()