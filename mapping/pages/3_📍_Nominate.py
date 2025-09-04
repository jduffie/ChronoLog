import os
import sys

import streamlit as st

from mapping.nominate.nominate_controller import NominateController

# Add the root directory to the path so we can import our modules
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))


def main():
    """Main function for the Nominate New Range page."""
    controller = NominateController()
    controller.run()


if __name__ == "__main__":
    main()
