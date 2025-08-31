from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import pandas as pd


@dataclass
class Rifle:
    """Entity representing a rifle"""

    id: str
    user_id: str
    name: str
    cartridge_type: str
    barrel_twist_ratio: Optional[str] = None
    barrel_length: Optional[str] = None
    sight_offset: Optional[str] = None
    trigger: Optional[str] = None
    scope: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_supabase_record(cls, record: dict) -> "Rifle":
        """Create a Rifle from a Supabase record"""
        return cls(
            id=record["id"],
            user_id=record["user_id"],
            name=record["name"],
            cartridge_type=record["cartridge_type"],
            barrel_twist_ratio=record.get("barrel_twist_ratio"),
            barrel_length=record.get("barrel_length"),
            sight_offset=record.get("sight_offset"),
            trigger=record.get("trigger"),
            scope=record.get("scope"),
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
    def from_supabase_records(cls, records: List[dict]) -> List["Rifle"]:
        """Create a list of Rifle objects from Supabase records"""
        return [cls.from_supabase_record(record) for record in records]

    def display_name(self) -> str:
        """Get a display-friendly name for the rifle"""
        return f"{self.name} ({self.cartridge_type})"

    def barrel_display(self) -> str:
        """Get formatted barrel information"""
        parts = []
        if self.barrel_length:
            parts.append(self.barrel_length)
        if self.barrel_twist_ratio:
            parts.append(f"Twist: {self.barrel_twist_ratio}")
        return " - ".join(parts) if parts else "Not specified"

    def optics_display(self) -> str:
        """Get formatted optics information"""
        parts = []
        if self.scope:
            parts.append(f"Scope: {self.scope}")
        if self.sight_offset:
            parts.append(f"Offset: {self.sight_offset}")
        return " - ".join(parts) if parts else "Not specified"

    def trigger_display(self) -> str:
        """Get formatted trigger information"""
        return self.trigger if self.trigger else "Not specified"