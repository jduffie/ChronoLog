import uuid
from datetime import datetime, timezone
from typing import List

import pandas as pd
import streamlit as st

from .service import ChronographService
from .unit_mapping_service import UnitMappingService
from .garmin_import import GarminExcelProcessor


class GarminImportUI:
    """Garmin-specific UI for chronograph data import"""
    
    def __init__(self, supabase_client):
        self.chrono_service = ChronographService(supabase_client)
        self.unit_mapping_service = UnitMappingService(supabase_client)
        self.garmin_processor = GarminExcelProcessor(self.unit_mapping_service, self.chrono_service)
    
    def render_file_upload(self, user, supabase, bucket):
        """Render Garmin file upload section"""
        uploaded_file = st.file_uploader("Upload Garmin Xero Excel File", type=["xlsx"])
        
        if uploaded_file:
            file_bytes = uploaded_file.getvalue()
            file_name = f"{user['email']}/garmin/{uploaded_file.name}"
            
            # Upload file to storage
            try:
                supabase.storage.from_(bucket).upload(
                    file_name, file_bytes, {"content-type": uploaded_file.type}
                )
            except Exception as e:
                if "already exists" in str(e) or "409" in str(e):
                    st.error(f"File '{uploaded_file.name}' already exists in storage.")
                    st.info("Go to the 'My Files' tab to delete the existing file if you want to re-upload it.")
                    return
                else:
                    st.error(f"Error uploading file: {e}")
                    return
            
            # Process the Excel file using Garmin processor
            self.garmin_processor.process_garmin_excel(uploaded_file, user, file_name)
            st.success("Upload complete!")