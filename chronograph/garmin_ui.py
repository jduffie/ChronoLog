
import streamlit as st

from .garmin_import import GarminExcelProcessor
from .service import ChronographService
from .unit_mapping_service import UnitMappingService


class GarminImportUI:
    """Garmin-specific UI for chronograph data import"""

    def __init__(self, supabase_client):
        self.chrono_service = ChronographService(supabase_client)
        self.unit_mapping_service = UnitMappingService(supabase_client)
        self.garmin_processor = GarminExcelProcessor(
            self.unit_mapping_service, self.chrono_service)

    def render_file_upload(self, user, supabase, bucket):
        """Render Garmin file upload section"""
        uploaded_file = st.file_uploader(
            "Upload Garmin Xero Excel File", type=["xlsx"])

        if uploaded_file:
            file_bytes = uploaded_file.getvalue()
            file_name = f"{user['email']}/garmin/{uploaded_file.name}"

            # Check if file already exists in storage
            try:
                existing_files = supabase.storage.from_(bucket).list(f"{user['email']}/garmin/")
                file_exists = any(f['name'] == uploaded_file.name for f in existing_files)
            except Exception as e:
                st.error(f"Error checking existing files: {e}")
                return

            if file_exists:
                st.warning(f"File '{uploaded_file.name}' already exists in storage.")

                # Checkbox confirmation to proceed with replacement
                overwrite_confirm = st.checkbox(
                    "I want to replace the existing file and re-import the data",
                    key=f"overwrite_{uploaded_file.name}"
                )

                if not overwrite_confirm:
                    st.info("Upload cancelled. Check the box above to proceed with replacement.")
                    return

                # User confirmed - delete existing file before re-upload
                st.info("Replacing existing file...")
                try:
                    supabase.storage.from_(bucket).remove([file_name])
                except Exception as e:
                    st.error(f"Error removing existing file: {e}")
                    return

            # Upload file to storage (either new or replacement)
            try:
                supabase.storage.from_(bucket).upload(
                    file_name, file_bytes, {"content-type": uploaded_file.type}
                )
            except Exception as e:
                st.error(f"Error uploading file: {e}")
                return

            # Process the Excel file using Garmin processor
            self.garmin_processor.process_garmin_excel(
                uploaded_file, user, file_name)
            st.success("Upload complete!")
