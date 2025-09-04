import os
import sys

from mapping.admin.admin_controller import AdminController

# Add the root directory to the path so we can import our modules
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)))))


def main():
    """Main function for the Admin page."""
    controller = AdminController()
    controller.run()


if __name__ == "__main__":
    main()
