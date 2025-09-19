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
    start_time: datetime = None  # NOT NULL - session start time
    end_time: datetime = None  # NOT NULL - session end time

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

    # Median weather fields from weather association (all metric)
    temperature_c_median: Optional[float] = None
    relative_humidity_pct_median: Optional[float] = None
    barometric_pressure_hpa_median: Optional[float] = None  # Metric barometric pressure in hectopascals
    wind_speed_mps_median: Optional[float] = None
    wind_direction_deg_median: Optional[float] = None

    @classmethod
    def from_supabase_record(cls, record: dict) -> "DopeSessionModel":
        """Create a DopeSessionModel from a Supabase record"""
        def parse_datetime(dt_str):
            """Parse datetime string from various Supabase formats"""
            if not dt_str:
                return None
            try:
                # Handle different datetime formats from Supabase
                if dt_str.endswith('Z'):
                    # ISO format with Z suffix: "2025-08-10T14:00:46Z"
                    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                elif dt_str.endswith('+00'):
                    # Postgres format with +00 suffix: "2025-08-10 14:00:46+00"
                    return datetime.fromisoformat(dt_str + ':00')
                elif '+00:00' in dt_str:
                    # ISO format with +00:00 suffix: "2025-08-10T14:00:46+00:00"
                    return datetime.fromisoformat(dt_str)
                else:
                    # Try direct parsing as fallback
                    return datetime.fromisoformat(dt_str)
            except ValueError as e:
                print(f"Warning: Could not parse datetime '{dt_str}': {e}")
                return None

        start_time_dt = parse_datetime(record.get("start_time"))
        end_time_dt = parse_datetime(record.get("end_time"))
        datetime_local_dt = parse_datetime(record.get("datetime_local"))
        return cls(
            id=record.get("id"),
            user_id=record.get("user_id"),
            session_name=record.get("session_name", ""),
            datetime_local=datetime_local_dt,
            cartridge_id=record.get("cartridge_id"),
            bullet_id=record.get("bullet_id"),
            chrono_session_id=record.get("chrono_session_id"),
            range_submission_id=record.get("range_submission_id"),
            weather_source_id=record.get("weather_source_id"),
            rifle_id=record.get("rifle_id"),
            start_time=start_time_dt,
            end_time=end_time_dt,
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
            barometric_pressure_hpa_median=record.get("barometric_pressure_hpa_median"),
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
            "barometric_pressure_hpa_median": self.barometric_pressure_hpa_median,
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


@dataclass
class DopeMeasurementModel:
    """Entity representing a DOPE measurement (individual shot data)"""

    # Core identification fields
    id: Optional[str] = None
    dope_session_id: str = ""  # NOT NULL - foreign key to dope_sessions
    user_id: str = ""  # NOT NULL - for user isolation

    # Shot data
    shot_number: Optional[int] = None
    datetime_shot: Optional[datetime] = None

    # Ballistic data (metric only)
    speed_mps: Optional[float] = None  # Projectile velocity in meters per second
    ke_j: Optional[float] = None  # Kinetic energy in Joules
    power_factor_kgms: Optional[float] = None  # Power factor in kg⋅m/s

    # Targeting data
    azimuth_deg: Optional[float] = None
    elevation_angle_deg: Optional[float] = None

    # Environmental conditions (metric only)
    temperature_c: Optional[float] = None  # Air temperature in Celsius
    pressure_hpa: Optional[float] = None  # Barometric pressure in hectopascals
    humidity_pct: Optional[float] = None  # Relative humidity as percentage

    # Bore conditions (text fields)
    clean_bore: Optional[str] = None  # "yes"/"no" or descriptive text
    cold_bore: Optional[str] = None   # "yes"/"no" or descriptive text

    # Adjustments (metric fields for precise ballistic tracking)
    distance_m: Optional[float] = None  # Target distance in meters
    elevation_adjustment: Optional[float] = None  # Elevation scope adjustment in milliradians
    windage_adjustment: Optional[float] = None  # Windage scope adjustment in milliradians

    # Notes
    shot_notes: Optional[str] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_supabase_record(cls, record: dict) -> "DopeMeasurementModel":
        """Create a DopeMeasurementModel from a Supabase record"""
        def parse_datetime(dt_str):
            """Parse datetime string from various Supabase formats"""
            if not dt_str:
                return None
            try:
                # Handle different datetime formats from Supabase
                if dt_str.endswith('Z'):
                    # ISO format with Z suffix: "2025-08-10T14:00:46Z"
                    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                elif dt_str.endswith('+00'):
                    # Postgres format with +00 suffix: "2025-08-10 14:00:46+00"
                    return datetime.fromisoformat(dt_str + ':00')
                elif '+00:00' in dt_str:
                    # ISO format with +00:00 suffix: "2025-08-10T14:00:46+00:00"
                    return datetime.fromisoformat(dt_str)
                else:
                    # Try direct parsing as fallback
                    return datetime.fromisoformat(dt_str)
            except ValueError as e:
                print(f"Warning: Could not parse datetime '{dt_str}': {e}")
                return None

        datetime_shot_dt = parse_datetime(record.get("datetime_shot"))
        created_at_dt = parse_datetime(record.get("created_at"))
        updated_at_dt = parse_datetime(record.get("updated_at"))

        return cls(
            id=record.get("id"),
            dope_session_id=record.get("dope_session_id", ""),
            user_id=record.get("user_id", ""),
            shot_number=record.get("shot_number"),
            datetime_shot=datetime_shot_dt,
            speed_mps=record.get("speed_mps"),
            ke_j=record.get("ke_j"),
            power_factor_kgms=record.get("power_factor_kgms"),
            azimuth_deg=record.get("azimuth_deg"),
            elevation_angle_deg=record.get("elevation_angle_deg"),
            temperature_c=record.get("temperature_c"),
            pressure_hpa=record.get("pressure_hpa"),
            humidity_pct=record.get("humidity_pct"),
            clean_bore=record.get("clean_bore"),
            cold_bore=record.get("cold_bore"),
            distance_m=record.get("distance_m"),
            elevation_adjustment=record.get("elevation_adjustment"),
            windage_adjustment=record.get("windage_adjustment"),
            shot_notes=record.get("shot_notes"),
            created_at=created_at_dt,
            updated_at=updated_at_dt,
        )

    @classmethod
    def from_supabase_records(cls, records: List[dict]) -> List["DopeMeasurementModel"]:
        """Create a list of DopeMeasurementModel from Supabase records"""
        return [cls.from_supabase_record(record) for record in records]

    def to_dict(self) -> dict:
        """Convert DopeMeasurementModel to dictionary for database operations"""
        return {
            "dope_session_id": self.dope_session_id,
            "user_id": self.user_id,
            "shot_number": self.shot_number,
            "datetime_shot": self.datetime_shot.isoformat() if self.datetime_shot else None,
            "speed_mps": self.speed_mps,
            "ke_j": self.ke_j,
            "power_factor_kgms": self.power_factor_kgms,
            "azimuth_deg": self.azimuth_deg,
            "elevation_angle_deg": self.elevation_angle_deg,
            "temperature_c": self.temperature_c,
            "pressure_hpa": self.pressure_hpa,
            "humidity_pct": self.humidity_pct,
            "clean_bore": self.clean_bore,
            "cold_bore": self.cold_bore,
            "distance_m": self.distance_m,
            "elevation_adjustment": self.elevation_adjustment,
            "windage_adjustment": self.windage_adjustment,
            "shot_notes": self.shot_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def display_name(self) -> str:
        """Get a friendly display name for the measurement"""
        parts = []
        if self.shot_number is not None:
            parts.append(f"Shot #{self.shot_number}")
        if self.speed_mps:
            parts.append(f"{self.speed_mps:.1f} m/s")
        return " - ".join(parts) if parts else "Measurement"

    @property
    def bore_conditions_display(self) -> str:
        """Get a display string for bore conditions"""
        conditions = []
        if self.clean_bore:
            conditions.append(f"Clean: {self.clean_bore}")
        if self.cold_bore:
            conditions.append(f"Cold: {self.cold_bore}")
        return ", ".join(conditions) if conditions else "Not specified"

    @property
    def environmental_display(self) -> str:
        """Get a display string for environmental conditions"""
        conditions = []
        if self.temperature_c is not None:
            conditions.append(f"Temp: {self.temperature_c:.1f}°C")
        
        if self.humidity_pct is not None:
            conditions.append(f"Humidity: {self.humidity_pct:.0f}%")
        
        if self.pressure_hpa is not None:
            conditions.append(f"Pressure: {self.pressure_hpa:.1f} hPa")
        
        return ", ".join(conditions) if conditions else "Not recorded"

    @property
    def adjustments_display(self) -> str:
        """Get a display string for scope adjustments"""
        adjustments = []
        if self.distance_m is not None:
            adjustments.append(f"Distance: {self.distance_m:.0f}m")
        if self.elevation_adjustment is not None:
            adjustments.append(f"Elevation: {self.elevation_adjustment:.2f} mrad")
        if self.windage_adjustment is not None:
            adjustments.append(f"Windage: {self.windage_adjustment:.2f} mrad")
        return ", ".join(adjustments) if adjustments else "No adjustments recorded"

    def has_ballistic_data(self) -> bool:
        """Check if measurement has any ballistic data"""
        return any([
            self.speed_mps,
            self.ke_j,
            self.power_factor_kgms
        ])

    def has_environmental_data(self) -> bool:
        """Check if measurement has environmental data"""
        return any([
            self.temperature_c,
            self.pressure_hpa,
            self.humidity_pct
        ])

    def has_targeting_data(self) -> bool:
        """Check if measurement has targeting data"""
        return any([self.azimuth_deg, self.elevation_angle_deg])

    def get_speed_display(self, user_unit_system: str = "Metric") -> str:
        """Get speed display in user's preferred units using edge conversion"""
        if self.speed_mps is None:
            return "No speed data"

        # Import here to avoid circular imports
        from utils.ui_formatters import format_speed
        return format_speed(self.speed_mps, user_unit_system)

    def get_energy_display(self, user_unit_system: str = "Metric") -> str:
        """Get kinetic energy display in user's preferred units using edge conversion"""
        if self.ke_j is None:
            return "No energy data"

        # Import here to avoid circular imports
        from utils.ui_formatters import format_energy
        return format_energy(self.ke_j, user_unit_system)

    def get_power_factor_display(self, user_unit_system: str = "Metric") -> str:
        """Get power factor display in user's preferred units using edge conversion"""
        if self.power_factor_kgms is None:
            return "No power factor data"

        # Import here to avoid circular imports
        from utils.ui_formatters import format_power_factor
        return format_power_factor(self.power_factor_kgms, user_unit_system)
