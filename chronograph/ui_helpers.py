"""
UI Helper utilities for chronograph views
Handles UI-specific data processing and validation
"""
import math
import pandas as pd
from typing import Optional, Any


def safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    """Safely convert value to float, returning None for NaN/invalid values"""
    try:
        if pd.isna(value) or value == "" or value is None:
            return default
        float_val = float(value)
        return None if math.isnan(float_val) else float_val
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    """Safely convert value to int"""
    try:
        if pd.isna(value) or value == "" or value is None:
            return default
        return int(float(value))  # Convert via float first to handle "1.0" format
    except (ValueError, TypeError):
        return default


def extract_session_timestamp_from_excel(df: pd.DataFrame) -> str:
    """Extract session timestamp from Excel file DATE cell"""
    from datetime import datetime, timezone
    
    session_timestamp = None
    try:
        # Look for the date in the last few rows of the sheet
        for i in range(len(df) - 1, max(len(df) - 10, 0), -1):
            for col in range(df.shape[1]):
                cell_value = df.iloc[i, col]
                if pd.notna(cell_value):
                    cell_str = str(cell_value).strip()
                    # Look for date patterns like "May 26, 2025 at 11:01 AM"
                    if " at " in cell_str and any(
                        month in cell_str
                        for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                    ):
                        try:
                            parsed_date = pd.to_datetime(cell_str)
                            session_timestamp = parsed_date.isoformat()
                            break
                        except:
                            continue
            if session_timestamp:
                break
    except:
        pass
    
    # Fall back to current date if we couldn't extract from sheet
    if not session_timestamp:
        session_timestamp = datetime.now(timezone.utc).isoformat()
    
    return session_timestamp


def extract_session_name(df: pd.DataFrame) -> str:
    """Extract session name from Excel file metadata"""
    return str(df.iloc[0, 0]).strip()





def extract_bullet_metadata(df: pd.DataFrame) -> tuple[str, Optional[float]]:
    """Extract bullet type and grain from Excel file metadata"""
    bullet_meta = df.iloc[0, 0]
    parts = bullet_meta.split(",")
    bullet_type = parts[0].strip()
    bullet_grain = float(parts[1].strip().replace("gr", "")) if len(parts) > 1 else None
    return bullet_type, bullet_grain