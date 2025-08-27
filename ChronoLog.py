import importlib.util
import os
import sys

# Add the parent directory to the path so we can import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the landing page module
spec = importlib.util.spec_from_file_location("landing", "pages/1_Home.py")
landing_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(landing_module)

if __name__ == "__main__":
    landing_module.run()
