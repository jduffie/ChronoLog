import sys
import os

# Add the parent directory to the path so we can import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mapping.mapping_controller import MappingController

if __name__ == "__main__":
    controller = MappingController()
    controller.run()
