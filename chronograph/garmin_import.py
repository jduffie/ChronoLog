"""
Garmin-specific file import and mapping module
Handles Garmin Excel file processing and data mapping
"""
from typing import Dict, List, Optional, Tuple
import pandas as pd

from .business_logic import UnitConverter
from .models import ChronographSession, ChronographMeasurement
from .ui_helpers import safe_float, safe_int, extract_session_timestamp_from_excel, extract_bullet_metadata


class GarminExcelProcessor:
    """Processes Garmin Excel files and maps data to chronograph entities"""
    
    def __init__(self, unit_mapping_service):
        self.unit_mapping_service = unit_mapping_service
        self.converter = UnitConverter()
    
    def process_excel_sheet(self, excel_file: pd.ExcelFile, sheet_name: str, file_path: str) -> Tuple[Dict, List[Dict]]:
        """Process a single Excel sheet and return session data and measurements"""
        # Read the sheet
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        
        # Extract session metadata
        bullet_type, bullet_grain = extract_bullet_metadata(df)
        session_timestamp = extract_session_timestamp_from_excel(df)
        
        session_data = {
            'bullet_type': bullet_type,
            'bullet_grain': bullet_grain,
            'session_timestamp': pd.to_datetime(session_timestamp),
            'tab_name': sheet_name,
            'file_path': file_path
        }
        
        # Process measurement data
        header_row = 1
        data = df.iloc[header_row + 1:].dropna(subset=[1])
        data.columns = df.iloc[header_row]
        
        # Detect units for columns
        column_units = self._detect_column_units(data.columns)
        
        # Process measurements
        measurements = []
        for _, row in data.iterrows():
            measurement = self._process_measurement_row(row, column_units, session_timestamp)
            if measurement:
                measurements.append(measurement)
        
        return session_data, measurements
    
    def _detect_column_units(self, columns) -> Dict[str, str]:
        """Detect units for each column using Garmin unit mapping"""
        unit_mapping = self.unit_mapping_service.get_garmin_units_mapping()
        column_units = {}
        
        for header in columns:
            if header in unit_mapping:
                mapping = unit_mapping[header]
                # Check if column header indicates imperial or metric
                if mapping['imperial'] in str(header):
                    column_units[header] = self._map_unit_type(mapping['imperial'])
                elif mapping['metric'] in str(header):
                    column_units[header] = self._map_unit_type(mapping['metric'])
                else:
                    column_units[header] = self._detect_unit_from_header(header)
            else:
                column_units[header] = self._detect_unit_from_header(header)
        
        return column_units
    
    def _map_unit_type(self, unit_string: str) -> str:
        """Map unit string to standardized unit type"""
        unit_map = {
            'FPS': 'fps',
            'm/s': 'mps', 
            'FT-LB': 'ftlb',
            'J': 'joules',
            'kgr·ft/s': 'kgrft',
            'kg·m/s': 'kgms'
        }
        return unit_map.get(unit_string, 'unknown')
    
    def _detect_unit_from_header(self, header: str) -> str:
        """Detect unit type from column header when not in mapping"""
        header_str = str(header).upper()
        if 'FPS' in header_str:
            return 'fps'
        elif 'M/S' in header_str:
            return 'mps'
        elif 'FT-LB' in header_str:
            return 'ftlb'
        elif 'J)' in header_str:
            return 'joules'
        elif 'KGR' in header_str and 'FT/S' in header_str:
            return 'kgrft'
        elif 'KG' in header_str and 'M/S' in header_str:
            return 'kgms'
        else:
            return 'unknown'
    
    def _process_measurement_row(self, row, column_units: Dict[str, str], session_timestamp: str) -> Optional[Dict]:
        """Process a single measurement row into measurement data"""
        # Validate row has required data
        shot_number = safe_int(row.get("#"))
        if shot_number is None:
            return None
        
        # Process speed with unit conversion
        speed_fps = None
        speed_mps = None
        
        # Check for speed columns
        for col_name in ["Speed (FPS)", "Speed (m/s)"]:
            if col_name in row:
                speed_val = safe_float(row.get(col_name))
                if speed_val is not None:
                    unit_type = column_units.get(col_name, 'fps')
                    if unit_type == 'fps':
                        speed_fps = speed_val
                        speed_mps = self.converter.fps_to_mps(speed_val)
                    elif unit_type == 'mps':
                        speed_mps = speed_val
                        speed_fps = self.converter.mps_to_fps(speed_val)
        
        if speed_fps is None:
            return None
        
        # Process other measurements with conversions
        delta_avg_fps = None
        delta_avg_mps = None
        ke_ft_lb = None
        ke_j = None
        power_factor = None
        power_factor_kgms = None
        
        # Process delta avg
        for col_name in ["Δ AVG (FPS)", "Δ AVG (m/s)"]:
            if col_name in row:
                delta_val = safe_float(row.get(col_name))
                if delta_val is not None:
                    unit_type = column_units.get(col_name, 'fps')
                    if unit_type == 'fps':
                        delta_avg_fps = delta_val
                        delta_avg_mps = self.converter.fps_to_mps(delta_val)
                    elif unit_type == 'mps':
                        delta_avg_mps = delta_val
                        delta_avg_fps = self.converter.mps_to_fps(delta_val)
        
        # Process kinetic energy
        for col_name in ["KE (FT-LB)", "KE (J)"]:
            if col_name in row:
                ke_val = safe_float(row.get(col_name))
                if ke_val is not None:
                    unit_type = column_units.get(col_name, 'ftlb')
                    if unit_type == 'ftlb':
                        ke_ft_lb = ke_val
                        ke_j = self.converter.ftlb_to_joules(ke_val)
                    elif unit_type == 'joules':
                        ke_j = ke_val
                        ke_ft_lb = self.converter.joules_to_ftlb(ke_val)
        
        # Process power factor
        for col_name in ["Power Factor (kgr⋅ft/s)", "Power Factor (kg·m/s)"]:
            if col_name in row:
                pf_val = safe_float(row.get(col_name))
                if pf_val is not None:
                    unit_type = column_units.get(col_name, 'kgrft')
                    if unit_type == 'kgrft':
                        power_factor = pf_val
                        power_factor_kgms = self.converter.kgrft_to_kgms(pf_val)
                    elif unit_type == 'kgms':
                        power_factor_kgms = pf_val
                        power_factor = self.converter.kgms_to_kgrft(pf_val)
        
        # Process datetime
        datetime_local = None
        time_str = row.get("Time")
        if time_str and session_timestamp:
            try:
                session_date = pd.to_datetime(session_timestamp).strftime("%Y-%m-%d")
                datetime_str = f"{session_date} {time_str}"
                datetime_local = pd.to_datetime(datetime_str)
            except:
                pass
        
        return {
            "shot_number": shot_number,
            "speed_fps": speed_fps,
            "speed_mps": speed_mps,
            "datetime_local": datetime_local,
            "delta_avg_fps": delta_avg_fps,
            "delta_avg_mps": delta_avg_mps,
            "ke_ft_lb": ke_ft_lb,
            "ke_j": ke_j,
            "power_factor": power_factor,
            "power_factor_kgms": power_factor_kgms,
            "clean_bore": (
                bool(row.get("Clean Bore"))
                if "Clean Bore" in row and not pd.isna(row.get("Clean Bore"))
                else None
            ),
            "cold_bore": (
                bool(row.get("Cold Bore"))
                if "Cold Bore" in row and not pd.isna(row.get("Cold Bore"))
                else None
            ),
            "shot_notes": (
                str(row.get("Shot Notes"))
                if "Shot Notes" in row and not pd.isna(row.get("Shot Notes"))
                else None
            ),
        }


class GarminFileMapper:
    """Maps Garmin Excel file data to standardized chronograph entities"""
    
    def __init__(self, unit_mapping_service):
        self.unit_mapping_service = unit_mapping_service
        self.converter = UnitConverter()
    
    def map_excel_to_entities(self, excel_file: pd.ExcelFile, sheet_name: str, file_path: str):
        """Map Excel data to ChronographSession and ChronographMeasurement entities"""
        # Read the sheet
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        
        # Extract session metadata
        bullet_type, bullet_grain = extract_bullet_metadata(df)
        session_timestamp = extract_session_timestamp_from_excel(df)
        
        # Create session entity
        session = ChronographSession(
            id=str(uuid.uuid4()),
            user_id="",  # Will be set by caller
            tab_name=sheet_name,
            bullet_type=bullet_type,
            bullet_grain=bullet_grain,
            datetime_local=pd.to_datetime(session_timestamp),
            uploaded_at=datetime.now(timezone.utc),
            file_path=file_path
        )
        
        # Process measurements
        header_row = 1
        data = df.iloc[header_row + 1:].dropna(subset=[1])
        data.columns = df.iloc[header_row]
        
        column_units = self._detect_column_units(data.columns)
        measurements = []
        
        for _, row in data.iterrows():
            measurement_data = self._map_measurement_row(row, column_units, session_timestamp)
            if measurement_data:
                measurement = ChronographMeasurement(
                    id=str(uuid.uuid4()),
                    user_id="",  # Will be set by caller
                    chrono_session_id="",  # Will be set by caller
                    **measurement_data
                )
                measurements.append(measurement)
        
        return session, measurements
    
    def _detect_column_units(self, columns) -> Dict[str, str]:
        """Detect units for each column"""
        unit_mapping = self.unit_mapping_service.get_garmin_units_mapping()
        column_units = {}
        
        for header in columns:
            if header in unit_mapping:
                mapping = unit_mapping[header]
                if mapping['imperial'] in str(header):
                    column_units[header] = self._standardize_unit(mapping['imperial'])
                elif mapping['metric'] in str(header):
                    column_units[header] = self._standardize_unit(mapping['metric'])
            else:
                column_units[header] = self._detect_unit_from_header(header)
        
        return column_units
    
    def _standardize_unit(self, unit_string: str) -> str:
        """Standardize unit strings to consistent format"""
        unit_map = {
            'FPS': 'fps',
            'm/s': 'mps',
            'FT-LB': 'ftlb',
            'J': 'joules',
            'kgr·ft/s': 'kgrft',
            'kg·m/s': 'kgms'
        }
        return unit_map.get(unit_string, 'unknown')
    
    def _detect_unit_from_header(self, header: str) -> str:
        """Detect unit from column header"""
        header_str = str(header).upper()
        if 'FPS' in header_str:
            return 'fps'
        elif 'M/S' in header_str:
            return 'mps'
        elif 'FT-LB' in header_str:
            return 'ftlb'
        elif 'J)' in header_str:
            return 'joules'
        else:
            return 'unknown'
    
    def _map_measurement_row(self, row, column_units: Dict[str, str], session_timestamp: str) -> Optional[Dict]:
        """Map a single row to measurement data"""
        shot_number = safe_int(row.get("#"))
        if shot_number is None:
            return None
        
        # Process speed with unit conversion
        speed_fps = None
        speed_mps = None
        
        for col_name in ["Speed (FPS)", "Speed (m/s)"]:
            if col_name in row:
                speed_val = safe_float(row.get(col_name))
                if speed_val is not None:
                    unit_type = column_units.get(col_name, 'fps')
                    if unit_type == 'fps':
                        speed_fps = speed_val
                        speed_mps = self.converter.fps_to_mps(speed_val)
                    elif unit_type == 'mps':
                        speed_mps = speed_val
                        speed_fps = self.converter.mps_to_fps(speed_val)
        
        if speed_fps is None:
            return None
        
        # Process other measurements
        delta_avg_fps = None
        delta_avg_mps = None
        ke_ft_lb = None
        ke_j = None
        power_factor = None
        power_factor_kgms = None
        
        # Process delta measurements
        for col_name in ["Δ AVG (FPS)", "Δ AVG (m/s)"]:
            if col_name in row:
                delta_val = safe_float(row.get(col_name))
                if delta_val is not None:
                    unit_type = column_units.get(col_name, 'fps')
                    if unit_type == 'fps':
                        delta_avg_fps = delta_val
                        delta_avg_mps = self.converter.fps_to_mps(delta_val)
                    elif unit_type == 'mps':
                        delta_avg_mps = delta_val
                        delta_avg_fps = self.converter.mps_to_fps(delta_val)
        
        # Process kinetic energy
        for col_name in ["KE (FT-LB)", "KE (J)"]:
            if col_name in row:
                ke_val = safe_float(row.get(col_name))
                if ke_val is not None:
                    unit_type = column_units.get(col_name, 'ftlb')
                    if unit_type == 'ftlb':
                        ke_ft_lb = ke_val
                        ke_j = self.converter.ftlb_to_joules(ke_val)
                    elif unit_type == 'joules':
                        ke_j = ke_val
                        ke_ft_lb = self.converter.joules_to_ftlb(ke_val)
        
        # Process power factor
        for col_name in ["Power Factor (kgr⋅ft/s)", "Power Factor (kg·m/s)"]:
            if col_name in row:
                pf_val = safe_float(row.get(col_name))
                if pf_val is not None:
                    unit_type = column_units.get(col_name, 'kgrft')
                    if unit_type == 'kgrft':
                        power_factor = pf_val
                        power_factor_kgms = self.converter.kgrft_to_kgms(pf_val)
                    elif unit_type == 'kgms':
                        power_factor_kgms = pf_val
                        power_factor = self.converter.kgms_to_kgrft(pf_val)
        
        # Process datetime
        datetime_local = None
        time_str = row.get("Time")
        if time_str and session_timestamp:
            try:
                session_date = pd.to_datetime(session_timestamp).strftime("%Y-%m-%d")
                datetime_str = f"{session_date} {time_str}"
                datetime_local = pd.to_datetime(datetime_str)
            except:
                datetime_local = pd.to_datetime(session_timestamp)
        
        return {
            "shot_number": shot_number,
            "speed_fps": speed_fps,
            "speed_mps": speed_mps,
            "datetime_local": datetime_local,
            "delta_avg_fps": delta_avg_fps,
            "delta_avg_mps": delta_avg_mps,
            "ke_ft_lb": ke_ft_lb,
            "ke_j": ke_j,
            "power_factor": power_factor,
            "power_factor_kgms": power_factor_kgms,
            "clean_bore": (
                bool(row.get("Clean Bore"))
                if "Clean Bore" in row and not pd.isna(row.get("Clean Bore"))
                else None
            ),
            "cold_bore": (
                bool(row.get("Cold Bore"))
                if "Cold Bore" in row and not pd.isna(row.get("Cold Bore"))
                else None
            ),
            "shot_notes": (
                str(row.get("Shot Notes"))
                if "Shot Notes" in row and not pd.isna(row.get("Shot Notes"))
                else None
            ),
        }