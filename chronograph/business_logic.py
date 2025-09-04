"""
Chronograph Business Logic Layer
Contains core domain logic, unit conversions, and data processing rules
"""
import math
from typing import Any, Dict, Optional

import pandas as pd


class UnitConverter:
    """Handles unit conversions for chronograph measurements"""

    @staticmethod
    def fps_to_mps(fps: Optional[float]) -> Optional[float]:
        """Convert feet per second to meters per second"""
        return fps * 0.3048 if fps is not None else None

    @staticmethod
    def mps_to_fps(mps: Optional[float]) -> Optional[float]:
        """Convert meters per second to feet per second"""
        return mps / 0.3048 if mps is not None else None

    @staticmethod
    def ftlb_to_joules(ftlb: Optional[float]) -> Optional[float]:
        """Convert foot-pounds to joules"""
        return ftlb * 1.35582 if ftlb is not None else None

    @staticmethod
    def joules_to_ftlb(joules: Optional[float]) -> Optional[float]:
        """Convert joules to foot-pounds"""
        return joules / 1.35582 if joules is not None else None

    @staticmethod
    def kgrft_to_kgms(kgrft: Optional[float]) -> Optional[float]:
        """Convert kgr·ft/s to kg·m/s"""
        return kgrft * 0.3048 if kgrft is not None else None

    @staticmethod
    def kgms_to_kgrft(kgms: Optional[float]) -> Optional[float]:
        """Convert kg·m/s to kgr·ft/s"""
        return kgms / 0.3048 if kgms is not None else None


class ChronographDataProcessor:
    """Generic chronograph data processing business logic"""

    def __init__(self, device_adapter):
        self.device_adapter = device_adapter

    def process_file_data(self, df: pd.DataFrame,
                          data_columns) -> Dict[str, Any]:
        """Process chronograph file data using device-specific adapter"""
        # Extract metadata using device adapter
        metadata = self.device_adapter.extract_session_metadata(df)

        # Detect units using device adapter
        column_units = self.device_adapter.detect_units(data_columns)

        return {
            'metadata': metadata,
            'column_units': column_units
        }

    def process_measurement_row(
            self, row_data: Dict[str, Any], column_units: Dict[str, str]) -> Dict[str, Any]:
        """Process a single measurement row using device adapter"""
        return self.device_adapter.process_measurement_row(
            row_data, column_units)

    def validate_measurement_row(
            self, row_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate measurement row using device adapter"""
        return self.device_adapter.validate_required_fields(row_data)


class SessionStatisticsCalculator:
    """Handles calculation of session statistics"""

    @staticmethod
    def calculate_session_stats(speeds: list) -> Dict[str, float]:
        """Calculate session statistics from speed measurements"""
        if not speeds:
            return {}

        avg_speed = sum(speeds) / len(speeds)
        min_speed = min(speeds)
        max_speed = max(speeds)

        # Calculate standard deviation
        std_dev = 0
        if len(speeds) > 1:
            variance = sum((x - avg_speed) ** 2 for x in speeds) / len(speeds)
            std_dev = variance ** 0.5

        return {
            "shot_count": len(speeds),
            "avg_speed_fps": avg_speed,
            "std_dev_fps": std_dev,
            "min_speed_fps": min_speed,
            "max_speed_fps": max_speed,
        }
