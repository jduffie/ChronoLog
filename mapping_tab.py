from mapping.nominate_controller import NominateController

def render_mapping_tab():
    """Render the mapping tab using the MVC pattern"""
    controller = NominateController()
    controller.run()