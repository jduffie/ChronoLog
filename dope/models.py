from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class DopeSessionModel:
    """Entity representing a DOPE (Data On Previous Engagement) session"""

    # Core identification fields
    id: Optional[str] = None
    user_id: Optional[str] = None
    session_name: str = ""  # NOT NULL
    datetime_local: Optional[datetime] = None  # NOT NULL - from chrono_sessions
    
    # Foreign key relationships
    cartridge_id: Optional[str] = None  # Foreign key to cartridges table
    chrono_session_id: Optional[str] = None
    range_submission_id: Optional[str] = None
    weather_source_id: Optional[str] = None
    rifle_id: Optional[str] = None
    
    # Range and session data
    range_name: Optional[str] = None
    distance_m: Optional[float] = None  # real type
    notes: Optional[str] = None
    status: Optional[str] = "active"
    
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
    
    # Weather conditions
    weather_source_name: Optional[str] = None
    temperature_c: Optional[float] = None  # numeric(3,1)
    relative_humidity_pct: Optional[float] = None  # numeric(5,2)
    barometric_pressure_inhg: Optional[float] = None  # numeric(6,2)
    wind_speed_1_kmh: Optional[float] = None  # numeric(4,1)
    wind_speed_2_kmh: Optional[float] = None  # numeric(4,1)
    wind_direction_deg: Optional[float] = None  # numeric(5,1)
    
    # Range position data
    start_lat: Optional[float] = None  # numeric(10,6)
    start_lon: Optional[float] = None  # numeric(10,6)
    start_altitude_m: Optional[float] = None  # numeric(8,2)
    azimuth_deg: Optional[float] = None  # numeric(6,2)
    elevation_angle_deg: Optional[float] = None  # numeric(6,2)

    @classmethod
    def from_supabase_record(cls, record: dict) -> "DopeSessionModel":
        """Create a DopeSessionModel from a Supabase record"""
        return cls(
            id=record.get("id"),
            user_id=record.get("user_id"),
            session_name=record.get("session_name", ""),
            datetime_local=record.get("datetime_local"),
            cartridge_id=record.get("cartridge_id"),
            chrono_session_id=record.get("chrono_session_id"),
            range_submission_id=record.get("range_submission_id"),
            weather_source_id=record.get("weather_source_id"),
            rifle_id=record.get("rifle_id"),
            range_name=record.get("range_name"),
            distance_m=record.get("distance_m"),
            notes=record.get("notes"),
            status=record.get("status", "active"),
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
            weather_source_name=record.get("weather_source_name"),
            temperature_c=record.get("temperature_c"),
            relative_humidity_pct=record.get("relative_humidity_pct"),
            barometric_pressure_inhg=record.get("barometric_pressure_inhg"),
            wind_speed_1_kmh=record.get("wind_speed_1_kmh"),
            wind_speed_2_kmh=record.get("wind_speed_2_kmh"),
            wind_direction_deg=record.get("wind_direction_deg"),
            start_lat=record.get("start_lat"),
            start_lon=record.get("start_lon"),
            start_altitude_m=record.get("start_altitude_m"),
            azimuth_deg=record.get("azimuth_deg"),
            elevation_angle_deg=record.get("elevation_angle_deg"),
        )

    @classmethod
    def from_supabase_records(cls, records: List[dict]) -> List["DopeSessionModel"]:
        """Create a list of DopeSessionModel from Supabase records"""
        return [cls.from_supabase_record(record) for record in records]

    def to_dict(self) -> dict:
        """Convert DopeSessionModel to dictionary for database operations"""
        return {
            "user_id": self.user_id,
            "session_name": self.session_name,
            "datetime_local": self.datetime_local,
            "cartridge_id": self.cartridge_id,
            "chrono_session_id": self.chrono_session_id,
            "range_submission_id": self.range_submission_id,
            "weather_source_id": self.weather_source_id,
            "rifle_id": self.rifle_id,
            "range_name": self.range_name,
            "distance_m": self.distance_m,
            "notes": self.notes,
            "status": self.status,
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
            "weather_source_name": self.weather_source_name,
            "temperature_c": self.temperature_c,
            "relative_humidity_pct": self.relative_humidity_pct,
            "barometric_pressure_inhg": self.barometric_pressure_inhg,
            "wind_speed_1_kmh": self.wind_speed_1_kmh,
            "wind_speed_2_kmh": self.wind_speed_2_kmh,
            "wind_direction_deg": self.wind_direction_deg,
            "start_lat": self.start_lat,
            "start_lon": self.start_lon,
            "start_altitude_m": self.start_altitude_m,
            "azimuth_deg": self.azimuth_deg,
            "elevation_angle_deg": self.elevation_angle_deg,
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
            if self.distance_m:
                parts.append(f"{self.distance_m}m")
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

    @property
    def weather_summary(self) -> str:
        """Get a summary of weather conditions"""
        conditions = []
        if self.temperature_c is not None:
            conditions.append(f"{self.temperature_c}°C")
        if self.relative_humidity_pct is not None:
            conditions.append(f"{self.relative_humidity_pct}% RH")
        if self.barometric_pressure_inhg is not None:
            conditions.append(f"{self.barometric_pressure_inhg}\" Hg")
        if self.wind_speed_1_kmh is not None:
            conditions.append(f"{self.wind_speed_1_kmh} km/h wind")
        return ", ".join(conditions) if conditions else "No weather data"

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
        return all(field.strip() if isinstance(field, str) else field for field in mandatory_fields)

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