"""
DOPE Analytics Filters

Defines filter criteria for selecting DOPE sessions for analysis.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class SessionFilter:
    """Filter criteria for DOPE session selection"""

    # Rifle and cartridge filters
    rifle_id: Optional[str] = None
    rifle_ids: Optional[List[str]] = None
    cartridge_id: Optional[str] = None
    cartridge_ids: Optional[List[str]] = None
    bullet_id: Optional[str] = None
    bullet_ids: Optional[List[str]] = None
    cartridge_type: Optional[str] = None

    # Date range filters
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # Environmental condition filters
    temperature_min_c: Optional[float] = None
    temperature_max_c: Optional[float] = None
    humidity_min_pct: Optional[float] = None
    humidity_max_pct: Optional[float] = None
    pressure_min_hpa: Optional[float] = None
    pressure_max_hpa: Optional[float] = None

    # Range filters
    range_submission_id: Optional[str] = None
    range_distance_min_m: Optional[float] = None
    range_distance_max_m: Optional[float] = None

    # Velocity filters (for quality control)
    velocity_min_mps: Optional[float] = None
    velocity_max_mps: Optional[float] = None

    # Session metadata filters
    session_ids: Optional[List[str]] = None
    exclude_session_ids: Optional[List[str]] = None

    def has_filters(self) -> bool:
        """Check if any filters are set"""
        return any([
            self.rifle_id,
            self.rifle_ids,
            self.cartridge_id,
            self.cartridge_ids,
            self.bullet_id,
            self.bullet_ids,
            self.cartridge_type,
            self.start_date,
            self.end_date,
            self.temperature_min_c,
            self.temperature_max_c,
            self.humidity_min_pct,
            self.humidity_max_pct,
            self.pressure_min_hpa,
            self.pressure_max_hpa,
            self.range_submission_id,
            self.range_distance_min_m,
            self.range_distance_max_m,
            self.velocity_min_mps,
            self.velocity_max_mps,
            self.session_ids,
            self.exclude_session_ids,
        ])

    def to_dict(self) -> dict:
        """Convert filter to dictionary (for caching and serialization)"""
        return {
            "rifle_id": self.rifle_id,
            "rifle_ids": self.rifle_ids,
            "cartridge_id": self.cartridge_id,
            "cartridge_ids": self.cartridge_ids,
            "bullet_id": self.bullet_id,
            "bullet_ids": self.bullet_ids,
            "cartridge_type": self.cartridge_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "temperature_min_c": self.temperature_min_c,
            "temperature_max_c": self.temperature_max_c,
            "humidity_min_pct": self.humidity_min_pct,
            "humidity_max_pct": self.humidity_max_pct,
            "pressure_min_hpa": self.pressure_min_hpa,
            "pressure_max_hpa": self.pressure_max_hpa,
            "range_submission_id": self.range_submission_id,
            "range_distance_min_m": self.range_distance_min_m,
            "range_distance_max_m": self.range_distance_max_m,
            "velocity_min_mps": self.velocity_min_mps,
            "velocity_max_mps": self.velocity_max_mps,
            "session_ids": self.session_ids,
            "exclude_session_ids": self.exclude_session_ids,
        }