from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class DopeSessionModel:
    """Entity representing a DOPE (Data On Previous Engagement) session"""

    # Core identification fields
    id: Optional[str] = None
    user_id: Optional[str] = None
    session_name: str = ""  # NOT NULL
    # NOT NULL - from chrono_sessions
    datetime_local: Optional[datetime] = None

    # Foreign key relationships
    cartridge_id: Optional[str] = None  # Foreign key to cartridges table
    bullet_id: Optional[str] = None  # Foreign key to bullets table (required)
    chrono_session_id: Optional[str] = None
    range_submission_id: Optional[str] = None
    weather_source_id: Optional[str] = None
    rifle_id: Optional[str] = None

    # Time fields (required)
    start_time: Optional[datetime] = None  # NOT NULL - session start time
    end_time: Optional[datetime] = None  # NOT NULL - session end time

    # Range and session data
    range_name: Optional[str] = None
    range_distance_m: Optional[float] = None  # real type
    notes: Optional[str] = None
    
    # Location and geometry fields (from range data)
    lat: Optional[float] = None
    lon: Optional[float] = None
    start_altitude: Optional[float] = None
    azimuth_deg: Optional[float] = None
    elevation_angle_deg: Optional[float] = None
    location_hyperlink: Optional[str] = None

    # Rifle information (mandatory fields)
    rifle_name: str = ""  # NOT NULL
    rifle_barrel_length_cm: Optional[float] = None  # real type
    rifle_barrel_twist_in_per_rev: Optional[float] = None  # real type

    # Cartridge information (mandatory fields)
    cartridge_make: str = ""  # NOT NULL
    cartridge_model: str = ""  # NOT NULL
    cartridge_type: str = ""  # NOT NULL
    cartridge_lot_number: Optional[str] = None

    # Bullet information (mandatory fields)
    bullet_make: str = ""  # NOT NULL
    bullet_model: str = ""  # NOT NULL
    bullet_weight: str = ""  # NOT NULL (text type)
    bullet_length_mm: Optional[str] = None  # text type
    ballistic_coefficient_g1: Optional[str] = None  # text type
    ballistic_coefficient_g7: Optional[str] = None  # text type
    sectional_density: Optional[str] = None  # text type
    bullet_diameter_groove_mm: Optional[str] = None  # text type
    bore_diameter_land_mm: Optional[str] = None  # text type

    # Median weather fields from weather association
    temperature_c_median: Optional[float] = None
    relative_humidity_pct_median: Optional[float] = None
    barometric_pressure_inhg_median: Optional[float] = None
    wind_speed_mps_median: Optional[float] = None
    wind_direction_deg_median: Optional[float] = None

    @classmethod
    def from_supabase_record(cls, record: dict) -> "DopeSessionModel":
        """Create a DopeSessionModel from a Supabase record"""
        return cls(
            id=record.get("id"),
            user_id=record.get("user_id"),
            session_name=record.get("session_name", ""),
            datetime_local=record.get("datetime_local"),
            cartridge_id=record.get("cartridge_id"),
            bullet_id=record.get("bullet_id"),
            chrono_session_id=record.get("chrono_session_id"),
            range_submission_id=record.get("range_submission_id"),
            weather_source_id=record.get("weather_source_id"),
            rifle_id=record.get("rifle_id"),
            start_time=record.get("start_time"),
            end_time=record.get("end_time"),
            range_name=record.get("range_name"),
            range_distance_m=record.get("range_distance_m"),
            notes=record.get("notes"),
            lat=record.get("lat"),
            lon=record.get("lon"),
            start_altitude=record.get("start_altitude"),
            azimuth_deg=record.get("azimuth_deg"),
            elevation_angle_deg=record.get("elevation_angle_deg"),
            location_hyperlink=record.get("location_hyperlink"),
            rifle_name=record.get("rifle_name", ""),
            rifle_barrel_length_cm=record.get("rifle_barrel_length_cm"),
            rifle_barrel_twist_in_per_rev=record.get("rifle_barrel_twist_in_per_rev"),
            cartridge_make=record.get("cartridge_make", ""),
            cartridge_model=record.get("cartridge_model", ""),
            cartridge_type=record.get("cartridge_type", ""),
            cartridge_lot_number=record.get("cartridge_lot_number"),
            bullet_make=record.get("bullet_make", ""),
            bullet_model=record.get("bullet_model", ""),
            bullet_weight=record.get("bullet_weight", ""),
            bullet_length_mm=record.get("bullet_length_mm"),
            ballistic_coefficient_g1=record.get("ballistic_coefficient_g1"),
            ballistic_coefficient_g7=record.get("ballistic_coefficient_g7"),
            sectional_density=record.get("sectional_density"),
            bullet_diameter_groove_mm=record.get("bullet_diameter_groove_mm"),
            bore_diameter_land_mm=record.get("bore_diameter_land_mm"),
            temperature_c_median=record.get("temperature_c_median"),
            relative_humidity_pct_median=record.get("relative_humidity_pct_median"),
            barometric_pressure_inhg_median=record.get("barometric_pressure_inhg_median"),
            wind_speed_mps_median=record.get("wind_speed_mps_median"),
            wind_direction_deg_median=record.get("wind_direction_deg_median"),
        )

    @classmethod
    def from_supabase_records(
            cls, records: List[dict]) -> List["DopeSessionModel"]:
        """Create a list of DopeSessionModel from Supabase records"""
        return [cls.from_supabase_record(record) for record in records]

    def to_dict(self) -> dict:
        """Convert DopeSessionModel to dictionary for database operations"""
        return {
            "user_id": self.user_id,
            "session_name": self.session_name,
            "datetime_local": self.datetime_local,
            "cartridge_id": self.cartridge_id,
            "bullet_id": self.bullet_id,
            "chrono_session_id": self.chrono_session_id,
            "range_submission_id": self.range_submission_id,
            "weather_source_id": self.weather_source_id,
            "rifle_id": self.rifle_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "range_name": self.range_name,
            "range_distance_m": self.range_distance_m,
            "notes": self.notes,
            "lat": self.lat,
            "lon": self.lon,
            "start_altitude": self.start_altitude,
            "azimuth_deg": self.azimuth_deg,
            "elevation_angle_deg": self.elevation_angle_deg,
            "location_hyperlink": self.location_hyperlink,
            "rifle_name": self.rifle_name,
            "rifle_barrel_length_cm": self.rifle_barrel_length_cm,
            "rifle_barrel_twist_in_per_rev": self.rifle_barrel_twist_in_per_rev,
            "cartridge_make": self.cartridge_make,
            "cartridge_model": self.cartridge_model,
            "cartridge_type": self.cartridge_type,
            "cartridge_lot_number": self.cartridge_lot_number,
            "bullet_make": self.bullet_make,
            "bullet_model": self.bullet_model,
            "bullet_weight": self.bullet_weight,
            "bullet_length_mm": self.bullet_length_mm,
            "ballistic_coefficient_g1": self.ballistic_coefficient_g1,
            "ballistic_coefficient_g7": self.ballistic_coefficient_g7,
            "sectional_density": self.sectional_density,
            "bullet_diameter_groove_mm": self.bullet_diameter_groove_mm,
            "bore_diameter_land_mm": self.bore_diameter_land_mm,
            "temperature_c_median": self.temperature_c_median,
            "relative_humidity_pct_median": self.relative_humidity_pct_median,
            "barometric_pressure_inhg_median": self.barometric_pressure_inhg_median,
            "wind_speed_mps_median": self.wind_speed_mps_median,
            "wind_direction_deg_median": self.wind_direction_deg_median,
        }

    @property
    def display_name(self) -> str:
        """Get a friendly display name for the DOPE session"""
        if self.session_name:
            return self.session_name
        else:
            parts = []
            if self.cartridge_type:
                parts.append(self.cartridge_type)
            if self.bullet_make and self.bullet_model:
                parts.append(f"{self.bullet_make} {self.bullet_model}")
            if self.range_distance_m:
                parts.append(f"{self.range_distance_m}m")
            return " - ".join(parts) if parts else "Untitled DOPE Session"

    @property
    def cartridge_display(self) -> str:
        """Get a display string for the cartridge information"""
        parts = []
        if self.cartridge_make:
            parts.append(self.cartridge_make)
        if self.cartridge_model:
            parts.append(self.cartridge_model)
        if self.cartridge_type:
            parts.append(f"({self.cartridge_type})")
        return " ".join(parts) if parts else "Unknown Cartridge"

    @property
    def bullet_display(self) -> str:
        """Get a display string for the bullet information"""
        parts = []
        if self.bullet_make:
            parts.append(self.bullet_make)
        if self.bullet_model:
            parts.append(self.bullet_model)
        if self.bullet_weight:
            parts.append(f"{self.bullet_weight}gr")
        return " ".join(parts) if parts else "Unknown Bullet"


    def is_complete(self) -> bool:
        """Check if all mandatory fields are filled"""
        mandatory_fields = [
            self.session_name,
            self.rifle_name,
            self.cartridge_make,
            self.cartridge_model,
            self.cartridge_type,
            self.bullet_make,
            self.bullet_model,
            self.bullet_weight,
        ]
        return all(
            field.strip() if isinstance(field, str) else field
            for field in mandatory_fields
        )

    def get_missing_mandatory_fields(self) -> List[str]:
        """Get list of missing mandatory fields"""
        missing = []
        mandatory_fields = {
            "session_name": self.session_name,
            "rifle_name": self.rifle_name,
            "cartridge_make": self.cartridge_make,
            "cartridge_model": self.cartridge_model,
            "cartridge_type": self.cartridge_type,
            "bullet_make": self.bullet_make,
            "bullet_model": self.bullet_model,
            "bullet_weight": self.bullet_weight,
        }

        for field_name, value in mandatory_fields.items():
            if not value or (isinstance(value, str) and not value.strip()):
                missing.append(field_name.replace("_", " ").title())

        return missing
