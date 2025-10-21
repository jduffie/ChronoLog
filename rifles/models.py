from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import pandas as pd


@dataclass
class RifleModel:
    """
    Domain model representing a rifle.

    Rifles are user-scoped entities storing firearm specifications.
    Each rifle is associated with a cartridge type and includes optional
    ballistics-relevant information like barrel twist rate and length.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Owner's user ID
        name: User-defined rifle name
        cartridge_type: Cartridge caliber (e.g., "6.5 Creedmoor")
        barrel_twist_ratio: Rifling twist rate (e.g., "1:8")
        barrel_length: Barrel length with units (e.g., "24 inches")
        sight_offset: Height over bore measurement
        trigger: Trigger description/specs
        scope: Scope/optic description
        created_at: Creation timestamp
        updated_at: Last update timestamp

    Example:
        >>> rifle = RifleModel(
        ...     id="123",
        ...     user_id="user-1",
        ...     name="Remington 700",
        ...     cartridge_type="6.5 Creedmoor",
        ...     barrel_twist_ratio="1:8"
        ... )
        >>> print(rifle.display_name())
        "Remington 700 (6.5 Creedmoor)"
    """

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
    def from_supabase_record(cls, record: dict) -> "RifleModel":
        """Create a RifleModel from a Supabase record"""
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
    def from_supabase_records(cls, records: List[dict]) -> List["RifleModel"]:
        """Create a list of RifleModel objects from Supabase records"""
        return [cls.from_supabase_record(record) for record in records]

    def to_dict(self) -> dict:
        """
        Convert RifleModel to dictionary for database operations.

        Returns:
            Dictionary with all rifle fields

        Example:
            >>> rifle_dict = rifle.to_dict()
            >>> supabase.table("rifles").insert(rifle_dict).execute()
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "cartridge_type": self.cartridge_type,
            "barrel_twist_ratio": self.barrel_twist_ratio,
            "barrel_length": self.barrel_length,
            "sight_offset": self.sight_offset,
            "trigger": self.trigger,
            "scope": self.scope,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }

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
