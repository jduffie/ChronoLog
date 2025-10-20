from dataclasses import dataclass
from typing import List, Optional


@dataclass
class BulletModel:
    """Entity representing a bullet specification"""

    id: str
    user_id: str
    manufacturer: str
    model: str
    weight_grains: float
    bullet_diameter_groove_mm: float
    bore_diameter_land_mm: float
    bullet_length_mm: Optional[float] = None
    ballistic_coefficient_g1: Optional[float] = None
    ballistic_coefficient_g7: Optional[float] = None
    sectional_density: Optional[float] = None
    min_req_twist_rate_in_per_rev: Optional[float] = None
    pref_twist_rate_in_per_rev: Optional[float] = None
    data_source_name: Optional[str] = None
    data_source_url: Optional[str] = None

    @classmethod
    def from_supabase_record(cls, record: dict) -> "BulletModel":
        """Create a BulletModel from a Supabase record"""
        return cls(
            id=record["id"],
            user_id=record["user_id"],
            manufacturer=record["manufacturer"],
            model=record["model"],
            weight_grains=float(record["weight_grains"]),
            bullet_diameter_groove_mm=float(record["bullet_diameter_groove_mm"]),
            bore_diameter_land_mm=float(record["bore_diameter_land_mm"]),
            bullet_length_mm=float(record["bullet_length_mm"]) if record.get("bullet_length_mm") is not None else None,
            ballistic_coefficient_g1=float(record["ballistic_coefficient_g1"]) if record.get("ballistic_coefficient_g1") is not None else None,
            ballistic_coefficient_g7=float(record["ballistic_coefficient_g7"]) if record.get("ballistic_coefficient_g7") is not None else None,
            sectional_density=float(record["sectional_density"]) if record.get("sectional_density") is not None else None,
            min_req_twist_rate_in_per_rev=float(record["min_req_twist_rate_in_per_rev"]) if record.get("min_req_twist_rate_in_per_rev") is not None else None,
            pref_twist_rate_in_per_rev=float(record["pref_twist_rate_in_per_rev"]) if record.get("pref_twist_rate_in_per_rev") is not None else None,
            data_source_name=record.get("data_source_name"),
            data_source_url=record.get("data_source_url"),
        )

    @classmethod
    def from_supabase_records(cls, records: List[dict]) -> List["BulletModel"]:
        """Create a list of BulletModel from Supabase records"""
        return [cls.from_supabase_record(record) for record in records]

    def to_dict(self) -> dict:
        """Convert BulletModel to dictionary for database operations"""
        return {
            "user_id": self.user_id,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "weight_grains": self.weight_grains,
            "bullet_diameter_groove_mm": self.bullet_diameter_groove_mm,
            "bore_diameter_land_mm": self.bore_diameter_land_mm,
            "bullet_length_mm": self.bullet_length_mm,
            "ballistic_coefficient_g1": self.ballistic_coefficient_g1,
            "ballistic_coefficient_g7": self.ballistic_coefficient_g7,
            "sectional_density": self.sectional_density,
            "min_req_twist_rate_in_per_rev": self.min_req_twist_rate_in_per_rev,
            "pref_twist_rate_in_per_rev": self.pref_twist_rate_in_per_rev,
            "data_source_name": self.data_source_name,
            "data_source_url": self.data_source_url,
        }

    @property
    def display_name(self) -> str:
        """Get a friendly display name for the bullet"""
        return f"{self.manufacturer} {self.model} {self.weight_grains}gr {self.bore_diameter_land_mm}mm/{self.bullet_diameter_groove_mm}mm"
