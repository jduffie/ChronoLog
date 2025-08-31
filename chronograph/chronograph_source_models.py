from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import pandas as pd


@dataclass
class ChronographSource:
    """Entity representing a chronograph device"""

    id: str
    user_id: str
    name: str
    source_type: str = "chronograph"
    device_name: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_supabase_record(cls, record: dict) -> "ChronographSource":
        """Create a ChronographSource from a Supabase record"""
        return cls(
            id=record["id"],
            user_id=record["user_id"],
            name=record["name"],
            source_type=record.get("source_type", "chronograph"),
            device_name=record.get("device_name"),
            make=record.get("make"),
            model=record.get("model"),
            serial_number=record.get("serial_number"),
            created_at=(
                pd.to_datetime(record["created_at"])
                if record.get("created_at")
                else None
            ),
            updated_at=(
                pd.to_datetime(record["updated_at"])
                if record.get("updated_at")
                else None
            ),
        )

    @classmethod
    def from_supabase_records(cls, records: List[dict]) -> List["ChronographSource"]:
        """Create a list of ChronographSource objects from Supabase records"""
        return [cls.from_supabase_record(record) for record in records]

    def display_name(self) -> str:
        """Get a display-friendly name for the chronograph source"""
        return self.name

    def device_display(self) -> str:
        """Get a display-friendly device description"""
        if self.make and self.model:
            desc = f"{self.make} {self.model}"
        elif self.device_name:
            desc = self.device_name
        elif self.model:
            desc = self.model
        else:
            desc = "Unknown Device"

        if self.serial_number:
            desc += f" (S/N: {self.serial_number})"

        return desc

    def short_display(self) -> str:
        """Get a short display name for dropdowns/lists"""
        return f"{self.name} - {self.device_display()}"