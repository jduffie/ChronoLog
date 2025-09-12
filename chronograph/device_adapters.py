"""
Device Adapter Layer for Chronographs
Provides device-agnostic interface for different chronograph types
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional

import pandas as pd

from .business_logic import UnitConverter
from .ui_helpers import (
    extract_session_name,
    extract_session_timestamp_from_excel,
    safe_float,
    safe_int,
)


@dataclass
class ChronographSessionEntity:
    """Entity representing a chronograph session from any device type"""
    session_name: str
    session_timestamp: datetime
    tab_name: str
    file_path: Optional[str] = None
    device_type: Optional[str] = None
    device_info: Optional[dict] = None


@dataclass
class ChronographMeasurementEntity:
    """Entity representing a single chronograph measurement from any device type"""
    shot_number: int
    speed_mps: float
    datetime_local: Optional[datetime] = None
    delta_avg_mps: Optional[float] = None
    ke_j: Optional[float] = None
    power_factor_kgms: Optional[float] = None
    clean_bore: Optional[bool] = None
    cold_bore: Optional[bool] = None
    shot_notes: Optional[str] = None


@dataclass
class ChronographIngestResult:
    """Result of device-specific data ingestion"""
    session: ChronographSessionEntity
    measurements: List[ChronographMeasurementEntity]
    device_type: str
    ingestion_metadata: Optional[dict] = None


class ChronographDeviceAdapter(ABC):
    """Abstract base class for chronograph device adapters"""

    @abstractmethod
    def get_device_type(self) -> str:
        """Return the device type identifier"""

    @abstractmethod
    def ingest_data(
            self,
            data_source: Any,
            **kwargs) -> ChronographIngestResult:
        """
        Ingest data from any source (file, API, etc.) and return standardized entities
        data_source: Could be Excel file, CSV file, API response, etc.
        kwargs: Additional context like user info, file metadata, etc.
        """


class GarminExcelAdapter(ChronographDeviceAdapter):
    """Adapter for Garmin Xero chronograph Excel files"""

    def __init__(self, unit_mapping_service):
        self.unit_mapping_service = unit_mapping_service
        self.converter = UnitConverter()

    def get_device_type(self) -> str:
        return "garmin_excel"

    def ingest_data(self, excel_file: pd.ExcelFile, **
                    kwargs) -> ChronographIngestResult:
        """Ingest data from Garmin Excel file and return standardized entities"""
        sheet_name = kwargs.get('sheet_name')
        file_path = kwargs.get('file_path')

        # Read the specific sheet
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)

        # Extract session metadata
        session_name = extract_session_name(df)
        # bullet_type, bullet_grain = extract_bullet_metadata(df)
        session_timestamp = extract_session_timestamp_from_excel(df)

        session_entity = ChronographSessionEntity(
            session_name=session_name,
            session_timestamp=pd.to_datetime(session_timestamp),
            tab_name=sheet_name,
            file_path=file_path,
            device_type=self.get_device_type()
        )

        # Process measurement data
        header_row = 1
        data = df.iloc[header_row + 1:].dropna(subset=[1])
        data.columns = df.iloc[header_row]

        # Detect units
        column_units = self._detect_units(data.columns)

        # Process each measurement row
        measurements = []
        for _, row in data.iterrows():
            # Validate row
            is_valid, error_msg = self._validate_row(row)
            if not is_valid:
                continue

            # Create measurement entity
            measurement = self._create_measurement_entity(
                row, column_units, session_timestamp)
            if measurement:
                measurements.append(measurement)

        return ChronographIngestResult(
            session=session_entity,
            measurements=measurements,
            device_type=self.get_device_type(),
            ingestion_metadata={'columns_processed': len(data.columns)}
        )

    def _detect_units(self, data_columns) -> dict[str, str]:
        """Detect unit system from Garmin Excel column headers"""
        unit_mapping = self.unit_mapping_service.get_garmin_units_mapping()
        column_units = {}

        for header in data_columns:
            if header in unit_mapping:
                mapping = unit_mapping[header]
                if mapping['imperial'] in header:
                    column_units[header] = self._map_imperial_unit(
                        mapping['imperial'])
                elif mapping['metric'] in header:
                    column_units[header] = self._map_metric_unit(
                        mapping['metric'])
                else:
                    column_units[header] = self._detect_default_unit(header)
            else:
                column_units[header] = 'unknown'

        return column_units

    def _validate_row(self, row) -> tuple[bool, Optional[str]]:
        """Validate Garmin measurement row has required fields"""
        shot_number = safe_int(row.get("#"))
        speed_fps = safe_float(row.get("Speed (FPS)"))
        speed_mps = safe_float(row.get("Speed (m/s)"))

        if shot_number is None:
            return False, "Missing shot number"

        # Ensure we have at least one speed measurement (will be converted to metric)
        if speed_fps is None and speed_mps is None:
            return False, "Missing speed measurement"

        return True, None

    def _create_measurement_entity(
            self,
            row,
            column_units: dict,
            session_timestamp: str) -> Optional[ChronographMeasurementEntity]:
        """Create a measurement entity from row data"""
        shot_number = safe_int(row.get("#"))

        # Process speed with conversion to metric only
        speed_mps = None

        for col_name in ["Speed (FPS)", "Speed (m/s)"]:
            if col_name in row:
                speed_val = safe_float(row.get(col_name))
                if speed_val is not None:
                    unit_type = column_units.get(col_name, 'fps')
                    if unit_type == 'fps':
                        speed_mps = self.converter.fps_to_mps(speed_val)
                    elif unit_type == 'mps':
                        speed_mps = speed_val

        if speed_mps is None:
            return None

        # Process other measurements - convert to metric only
        delta_avg_mps = None
        ke_j = None
        power_factor_kgms = None

        # Process delta avg
        for col_name in ["Δ AVG (FPS)", "Δ AVG (m/s)"]:
            if col_name in row:
                delta_val = safe_float(row.get(col_name))
                if delta_val is not None:
                    unit_type = column_units.get(col_name, 'fps')
                    if unit_type == 'fps':
                        delta_avg_mps = self.converter.fps_to_mps(delta_val)
                    elif unit_type == 'mps':
                        delta_avg_mps = delta_val

        # Process kinetic energy
        for col_name in ["KE (FT-LB)", "KE (J)"]:
            if col_name in row:
                ke_val = safe_float(row.get(col_name))
                if ke_val is not None:
                    unit_type = column_units.get(col_name, 'ftlb')
                    if unit_type == 'ftlb':
                        ke_j = self.converter.ftlb_to_joules(ke_val)
                    elif unit_type == 'joules':
                        ke_j = ke_val

        # Process power factor
        for col_name in ["Power Factor (kgr⋅ft/s)", "Power Factor (kg·m/s)"]:
            if col_name in row:
                pf_val = safe_float(row.get(col_name))
                if pf_val is not None:
                    unit_type = column_units.get(col_name, 'kgrft')
                    if unit_type == 'kgrft':
                        power_factor_kgms = self.converter.kgrft_to_kgms(pf_val)
                    elif unit_type == 'kgms':
                        power_factor_kgms = pf_val

        # Create datetime
        datetime_local = None
        time_str = row.get("Time")
        if time_str and session_timestamp:
            try:
                session_date = pd.to_datetime(
                    session_timestamp).strftime("%Y-%m-%d")
                datetime_str = f"{session_date} {time_str}"
                datetime_local = pd.to_datetime(datetime_str)
            except BaseException:
                pass

        return ChronographMeasurementEntity(
            shot_number=shot_number,
            speed_mps=speed_mps,
            datetime_local=datetime_local,
            delta_avg_mps=delta_avg_mps,
            ke_j=ke_j,
            power_factor_kgms=power_factor_kgms,
            clean_bore=bool(
                row.get("Clean Bore")) if "Clean Bore" in row and not pd.isna(
                row.get("Clean Bore")) else None,
            cold_bore=bool(
                row.get("Cold Bore")) if "Cold Bore" in row and not pd.isna(
                    row.get("Cold Bore")) else None,
            shot_notes=str(
                row.get("Shot Notes")) if "Shot Notes" in row and not pd.isna(
                row.get("Shot Notes")) else None)

    def _map_imperial_unit(self, unit: str) -> str:
        """Map imperial unit string to unit type"""
        unit_map = {'FPS': 'fps', 'FT-LB': 'ftlb', 'kgr·ft/s': 'kgrft'}
        return unit_map.get(unit, 'unknown')

    def _map_metric_unit(self, unit: str) -> str:
        """Map metric unit string to unit type"""
        unit_map = {'m/s': 'mps', 'J': 'joules', 'kg·m/s': 'kgms'}
        return unit_map.get(unit, 'unknown')

    def _detect_default_unit(self, header: str) -> str:
        """Detect default unit from header when not in mapping"""
        if 'FPS' in header:
            return 'fps'
        elif 'FT-LB' in header:
            return 'ftlb'
        elif 'kgr⋅ft/s' in header or 'kgr·ft/s' in header:
            return 'kgrft'
        else:
            return 'unknown'


class ChronographDeviceFactory:
    """Factory for creating device-specific adapters"""

    @staticmethod
    def create_adapter(
            device_type: str,
            unit_mapping_service) -> ChronographDeviceAdapter:
        """Create the appropriate device adapter based on device type"""
        if device_type.lower() == "garmin_excel":
            return GarminExcelAdapter(unit_mapping_service)
        else:
            raise ValueError(
                f"Unsupported chronograph device type: {device_type}")

    @staticmethod
    def detect_device_type(file_name: str, data_source: Any) -> str:
        """Auto-detect device type from data source characteristics"""
        if file_name.lower().endswith('.xlsx') and hasattr(data_source, 'iloc'):
            # Check if it has Garmin-specific structure
            if len(data_source) > 1 and data_source.iloc[0, 0] and ',' in str(
                    data_source.iloc[0, 0]):
                return "garmin_excel"

        # Default to garmin for now - can be extended for other devices
        return "garmin_excel"
