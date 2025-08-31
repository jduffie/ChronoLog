import streamlit as st

from .garmin_ui import GarminImportUI


def render_chronograph_import_tab(user, supabase, bucket):
    """Render chronograph import tab using device-specific UI"""
    garmin_ui = GarminImportUI(supabase)
    garmin_ui.render_file_upload(user, supabase, bucket)
