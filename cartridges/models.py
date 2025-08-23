from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class CartridgeModel:
    """Entity representing a cartridge specification"""

    # Core identification fields
    id: Optional[str] = None
    owner_id: Optional[str] = None  # NULL for global/admin records

    # Required cartridge information
    make: str = ""  # NOT NULL - Manufacturer name
    model: str = ""  # NOT NULL - Model name
    bullet_id: Optional[str] = None  # NOT NULL - Foreign key to bullets
    cartridge_type: str = ""  # NOT NULL - Cartridge type designation

    # Data source tracking
    data_source_name: Optional[str] = None
    data_source_link: Optional[str] = None

    # Generated and timestamp fields
    cartridge_key: Optional[str] = None  # Generated natural key
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Related data from joins (populated when fetched with bullet info)
    bullet_manufacturer: Optional[str] = None
    bullet_model: Optional[str] = None
    bullet_weight_grains: Optional[int] = None
    bullet_diameter_groove_mm: Optional[float] = None
    bore_diameter_land_mm: Optional[float] = None
    bullet_length_mm: Optional[float] = None
    ballistic_coefficient_g1: Optional[float] = None
    ballistic_coefficient_g7: Optional[float] = None
    sectional_density: Optional[float] = None
    min_req_twist_rate_in_per_rev: Optional[float] = None
    pref_twist_rate_in_per_rev: Optional[float] = None

    @classmethod
    def from_supabase_record(cls, record: dict) -> "CartridgeModel":
        """Create a CartridgeModel from a Supabase record"""
        return cls(
            id=record.get("id"),
            owner_id=record.get("owner_id"),
            make=record.get("make", ""),
            model=record.get("model", ""),
            bullet_id=record.get("bullet_id"),
            cartridge_type=record.get("cartridge_type", ""),
            data_source_name=record.get("data_source_name"),
            data_source_link=record.get("data_source_link"),
            cartridge_key=record.get("cartridge_key"),
            created_at=record.get("created_at"),
            updated_at=record.get("updated_at"),
            # Bullet information from joins
            bullet_manufacturer=record.get("bullet_manufacturer"),
            bullet_model=record.get("bullet_model"),
            bullet_weight_grains=record.get("bullet_weight_grains"),
            bullet_diameter_groove_mm=record.get("bullet_diameter_groove_mm"),
            bore_diameter_land_mm=record.get("bore_diameter_land_mm"),
            bullet_length_mm=record.get("bullet_length_mm"),
            ballistic_coefficient_g1=record.get("ballistic_coefficient_g1"),
            ballistic_coefficient_g7=record.get("ballistic_coefficient_g7"),
            sectional_density=record.get("sectional_density"),
            min_req_twist_rate_in_per_rev=record.get("min_req_twist_rate_in_per_rev"),
            pref_twist_rate_in_per_rev=record.get("pref_twist_rate_in_per_rev"),
        )

    @classmethod
    def from_supabase_records(cls, records: List[dict]) -> List["CartridgeModel"]:
        """Create a list of CartridgeModel from Supabase records"""
        return [cls.from_supabase_record(record) for record in records]

    def to_dict(self) -> dict:
        """Convert CartridgeModel to dictionary for database operations"""
        return {
            "owner_id": self.owner_id,
            "make": self.make,
            "model": self.model,
            "bullet_id": self.bullet_id,
            "cartridge_type": self.cartridge_type,
            "data_source_name": self.data_source_name,
            "data_source_link": self.data_source_link,
        }

    @property
    def display_name(self) -> str:
        """Get a friendly display name for the cartridge"""
        parts = []
        if self.make:
            parts.append(self.make)
        if self.model:
            parts.append(self.model)
        if self.cartridge_type:
            parts.append(f"({self.cartridge_type})")
        return " ".join(parts) if parts else "Unknown Cartridge"

    @property
    def bullet_display(self) -> str:
        """Get a display string for the associated bullet"""
        if not self.bullet_manufacturer and not self.bullet_model:
            return "Unknown Bullet"

        parts = []
        if self.bullet_manufacturer:
            parts.append(self.bullet_manufacturer)
        if self.bullet_model:
            parts.append(self.bullet_model)
        if self.bullet_weight_grains:
            parts.append(f"{self.bullet_weight_grains}gr")
        return " ".join(parts)

    @property
    def is_global(self) -> bool:
        """Check if this is a global/admin record"""
        return self.owner_id is None

    @property
    def is_user_owned(self) -> bool:
        """Check if this is a user-owned record"""
        return self.owner_id is not None

    @property
    def ballistic_data_summary(self) -> str:
        """Get a summary of ballistic data"""
        data = []
        if self.ballistic_coefficient_g1:
            data.append(f"G1 BC: {self.ballistic_coefficient_g1}")
        if self.ballistic_coefficient_g7:
            data.append(f"G7 BC: {self.ballistic_coefficient_g7}")
        if self.sectional_density:
            data.append(f"SD: {self.sectional_density}")
        return ", ".join(data) if data else "No ballistic data"

    @property
    def twist_rate_recommendation(self) -> str:
        """Get twist rate recommendation"""
        if self.min_req_twist_rate_in_per_rev and self.pref_twist_rate_in_per_rev:
            return f'Min: 1:{self.min_req_twist_rate_in_per_rev}", Pref: 1:{self.pref_twist_rate_in_per_rev}"'
        elif self.min_req_twist_rate_in_per_rev:
            return f'Min: 1:{self.min_req_twist_rate_in_per_rev}"'
        elif self.pref_twist_rate_in_per_rev:
            return f'Pref: 1:{self.pref_twist_rate_in_per_rev}"'
        else:
            return "No twist rate data"

    def is_complete(self) -> bool:
        """Check if all mandatory fields are filled"""
        mandatory_fields = [
            self.make,
            self.model,
            self.bullet_id,
            self.cartridge_type,
        ]
        return all(
            field.strip() if isinstance(field, str) else field
            for field in mandatory_fields
        )

    def get_missing_mandatory_fields(self) -> List[str]:
        """Get list of missing mandatory fields"""
        missing = []
        mandatory_fields = {
            "make": self.make,
            "model": self.model,
            "bullet_id": self.bullet_id,
            "cartridge_type": self.cartridge_type,
        }

        for field_name, value in mandatory_fields.items():
            if not value or (isinstance(value, str) and not value.strip()):
                missing.append(field_name.replace("_", " ").title())

        return missing


@dataclass
class CartridgeTypeModel:
    """Entity representing a cartridge type from the lookup table"""

    name: str = ""  # Primary key - cartridge type name

    @classmethod
    def from_supabase_record(cls, record: dict) -> "CartridgeTypeModel":
        """Create a CartridgeTypeModel from a Supabase record"""
        return cls(name=record.get("name", ""))

    @classmethod
    def from_supabase_records(cls, records: List[dict]) -> List["CartridgeTypeModel"]:
        """Create a list of CartridgeTypeModel from Supabase records"""
        return [cls.from_supabase_record(record) for record in records]

    def to_dict(self) -> dict:
        """Convert CartridgeTypeModel to dictionary for database operations"""
        return {
            "name": self.name,
        }

    @property
    def display_name(self) -> str:
        """Get a friendly display name for the cartridge type"""
        return self.name if self.name else "Unknown Type"
