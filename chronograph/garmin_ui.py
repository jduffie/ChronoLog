import uuid
from datetime import datetime, timezone
from typing import List

import pandas as pd
import streamlit as st

from .service import ChronographService
from .models import ChronographSession, ChronographMeasurement
from .device_adapters import ChronographDeviceFactory
from .unit_mapping_service import UnitMappingService


class GarminImportUI:
    """Garmin-specific UI for chronograph data import"""
    
    def __init__(self, supabase_client):
        self.chrono_service = ChronographService(supabase_client)
        self.unit_mapping_service = UnitMappingService(supabase_client)
    
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
            
            # Process the Excel file using device adapter
            self._process_garmin_excel(uploaded_file, user, file_name)
            st.success("Upload complete!")
    
    def _process_garmin_excel(self, uploaded_file, user, file_name):
        """Process Garmin Excel file using device adapter architecture"""
        # Create device adapter
        device_factory = ChronographDeviceFactory()
        device_adapter = device_factory.create_adapter("garmin_excel", self.unit_mapping_service)
        
        # Load Excel file
        excel_file = pd.ExcelFile(uploaded_file)
        
        # Process each sheet
        for sheet_name in excel_file.sheet_names:
            # Use device adapter to ingest data
            ingest_result = device_adapter.ingest_data(
                excel_file, 
                sheet_name=sheet_name, 
                file_path=file_name
            )
            
            # Check if session already exists
            if self.chrono_service.session_exists(
                user["id"], 
                sheet_name, 
                ingest_result.session.session_timestamp.isoformat()
            ):
                st.warning(
                    f"Session already exists for {ingest_result.session.session_timestamp.strftime('%Y-%m-%d %H:%M')} - skipping sheet '{sheet_name}'"
                )
                continue
            
            # Convert entities to models and save
            self._save_session_and_measurements(ingest_result, user["id"])
    
    def _save_session_and_measurements(self, ingest_result, user_id: str):
        """Convert entities to models and save to database"""
        # Convert session entity to model
        session_model = ChronographSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            tab_name=ingest_result.session.tab_name,
            bullet_type=ingest_result.session.bullet_type,
            bullet_grain=ingest_result.session.bullet_grain,
            datetime_local=ingest_result.session.session_timestamp,
            uploaded_at=datetime.now(timezone.utc),
            file_path=ingest_result.session.file_path
        )
        
        # Save session
        session_id = self.chrono_service.save_chronograph_session(session_model)
        
        # Convert and save measurements
        valid_measurements = 0
        skipped_measurements = 0
        
        for measurement_entity in ingest_result.measurements:
            try:
                measurement_model = ChronographMeasurement(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    chrono_session_id=session_id,
                    shot_number=measurement_entity.shot_number,
                    speed_fps=measurement_entity.speed_fps,
                    speed_mps=measurement_entity.speed_mps,
                    datetime_local=measurement_entity.datetime_local or ingest_result.session.session_timestamp,
                    delta_avg_fps=measurement_entity.delta_avg_fps,
                    delta_avg_mps=measurement_entity.delta_avg_mps,
                    ke_ft_lb=measurement_entity.ke_ft_lb,
                    ke_j=measurement_entity.ke_j,
                    power_factor=measurement_entity.power_factor,
                    power_factor_kgms=measurement_entity.power_factor_kgms,
                    clean_bore=measurement_entity.clean_bore,
                    cold_bore=measurement_entity.cold_bore,
                    shot_notes=measurement_entity.shot_notes
                )
                
                self.chrono_service.save_chronograph_measurement(measurement_model)
                valid_measurements += 1
                
            except Exception as e:
                st.warning(f"Skipped measurement {measurement_entity.shot_number}: {e}")
                skipped_measurements += 1
        
        # Calculate and update session statistics
        if valid_measurements > 0:
            self.chrono_service.calculate_and_update_session_stats(user_id, session_id)
        
        # Show processing summary
        if skipped_measurements > 0:
            st.warning(
                f"Processed {valid_measurements} measurements, skipped {skipped_measurements} rows with missing data"
            )
        else:
            st.success(f"Successfully processed {valid_measurements} measurements")