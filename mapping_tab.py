from mapping_controller import MappingController

def render_mapping_tab():
    """Render the mapping tab using the MVC pattern"""
    controller = MappingController()
    controller.run()