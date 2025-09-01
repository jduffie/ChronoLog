from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import pandas as pd


@dataclass
class ChronographSession:
    """Entity representing a chronograph session"""

    id: str
    user_id: str
    tab_name: str
    session_name: str
    bullet_type: str
    bullet_grain: Optional[float]
    datetime_local: datetime
    uploaded_at: datetime
    file_path: Optional[str]
    shot_count: int = 0
    avg_speed_fps: Optional[float] = None
    std_dev_fps: Optional[float] = None
    min_speed_fps: Optional[float] = None
    max_speed_fps: Optional[float] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_supabase_record(cls, record: dict) -> "ChronographSession":
        """Create a ChronographSession from a Supabase record"""
        return cls(
            id=record["id"],
            user_id=record["user_id"],
            tab_name=record["tab_name"],
            session_name=record.get("session_name", ""),
            bullet_type=record["bullet_type"],
            bullet_grain=record.get("bullet_grain"),
            datetime_local=pd.to_datetime(record["datetime_local"]),
            uploaded_at=pd.to_datetime(record["uploaded_at"]),
            file_path=record.get("file_path"),
            shot_count=record.get("shot_count", 0),
            avg_speed_fps=record.get("avg_speed_fps"),
            std_dev_fps=record.get("std_dev_fps"),
            min_speed_fps=record.get("min_speed_fps"),
            max_speed_fps=record.get("max_speed_fps"),
            created_at=(
                pd.to_datetime(record["created_at"])
                if record.get("created_at")
                else None
            ),
        )

    @classmethod
    def from_supabase_records(cls, records: List[dict]) -> List["ChronographSession"]:
        """Create a list of ChronographSession objects from Supabase records"""
        return [cls.from_supabase_record(record) for record in records]

    def display_name(self) -> str:
        """Get a display-friendly name for the session"""
        return f"{self.tab_name} - {self.datetime_local.strftime('%Y-%m-%d %H:%M')}"

    def bullet_display(self) -> str:
        """Get a display-friendly bullet description"""
        grain_str = f" {self.bullet_grain}gr" if self.bullet_grain else ""
        return f"{self.bullet_type}{grain_str}"

    def has_measurements(self) -> bool:
        """Check if this session has any measurements"""
        return self.shot_count > 0

    def avg_speed_display(self) -> str:
        """Get formatted average speed for display"""
        return f"{self.avg_speed_fps:.0f} fps" if self.avg_speed_fps else "N/A"

    def std_dev_display(self) -> str:
        """Get formatted standard deviation for display"""
        return f"{self.std_dev_fps:.1f} fps" if self.std_dev_fps else "N/A"

    def velocity_range_display(self) -> str:
        """Get formatted velocity range for display"""
        if self.min_speed_fps is not None and self.max_speed_fps is not None:
            return f"{self.max_speed_fps - self.min_speed_fps:.0f} fps"
        return "N/A"

    def file_name(self) -> str:
        """Get just the filename from the file path"""
        if self.file_path:
            return self.file_path.split("/")[-1]
        return "N/A"


@dataclass
class ChronographMeasurement:
    """Entity representing a single chronograph measurement"""

    id: str
    user_id: str
    chrono_session_id: str
    shot_number: int
    speed_fps: float
    speed_mps: float
    datetime_local: datetime
    delta_avg_fps: Optional[float] = None
    delta_avg_mps: Optional[float] = None
    ke_ft_lb: Optional[float] = None
    ke_j: Optional[float] = None
    power_factor: Optional[float] = None
    power_factor_kgms: Optional[float] = None
    clean_bore: Optional[bool] = None
    cold_bore: Optional[bool] = None
    shot_notes: Optional[str] = None

    @classmethod
    def from_supabase_record(cls, record: dict) -> "ChronographMeasurement":
        """Create a ChronographMeasurement from a Supabase record"""
        return cls(
            id=record["id"],
            user_id=record["user_id"],
            chrono_session_id=record["chrono_session_id"],
            shot_number=record["shot_number"],
            speed_fps=record["speed_fps"],
            speed_mps=record.get("speed_mps", 0),
            delta_avg_fps=record.get("delta_avg_fps"),
            delta_avg_mps=record.get("delta_avg_mps"),
            ke_ft_lb=record.get("ke_ft_lb"),
            ke_j=record.get("ke_j"),
            power_factor=record.get("power_factor"),
            power_factor_kgms=record.get("power_factor_kgms"),
            datetime_local=pd.to_datetime(record["datetime_local"]),
            clean_bore=record.get("clean_bore"),
            cold_bore=record.get("cold_bore"),
            shot_notes=record.get("shot_notes"),
        )

    @classmethod
    def from_supabase_records(
        cls, records: List[dict]
    ) -> List["ChronographMeasurement"]:
        """Create a list of ChronographMeasurement objects from Supabase records"""
        return [cls.from_supabase_record(record) for record in records]
