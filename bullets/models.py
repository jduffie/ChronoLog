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
            weight_grains=record["weight_grains"],
            bullet_diameter_groove_mm=record["bullet_diameter_groove_mm"],
            bore_diameter_land_mm=record["bore_diameter_land_mm"],
            bullet_length_mm=record.get("bullet_length_mm"),
            ballistic_coefficient_g1=record.get("ballistic_coefficient_g1"),
            ballistic_coefficient_g7=record.get("ballistic_coefficient_g7"),
            sectional_density=record.get("sectional_density"),
            min_req_twist_rate_in_per_rev=record.get("min_req_twist_rate_in_per_rev"),
            pref_twist_rate_in_per_rev=record.get("pref_twist_rate_in_per_rev"),
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
        return f"{self.manufacturer} {self.model} - {self.weight_grains}gr - {self.bullet_diameter_groove_mm}mm"
