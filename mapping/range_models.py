from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class RangeSubmission:
    """Model for range submissions (pending approval)."""

    id: Optional[str] = None
    user_email: str = ""
    range_name: str = ""
    range_description: Optional[str] = None

    # Geographic coordinates and measurements
    start_lat: float = 0.0
    start_lon: float = 0.0
    start_altitude_m: Optional[float] = None
    end_lat: float = 0.0
    end_lon: float = 0.0
    end_altitude_m: Optional[float] = None

    # Calculated values
    distance_m: Optional[float] = None
    azimuth_deg: Optional[float] = None
    elevation_angle_deg: Optional[float] = None

    # Address information
    address_geojson: Optional[Dict[str, Any]] = None
    display_name: Optional[str] = None

    # Admin review fields
    status: str = "Under Review"  # 'Under Review', 'Accepted', 'Denied'
    review_reason: Optional[str] = None

    # Timestamps
    submitted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_supabase_record(cls, record: Dict[str, Any]) -> "RangeSubmission":
        """Create RangeSubmission from Supabase record."""
        return cls(
            id=record.get("id"),
            user_email=record.get("user_email", ""),
            range_name=record.get("range_name", ""),
            range_description=record.get("range_description"),
            start_lat=float(record.get("start_lat", 0)),
            start_lon=float(record.get("start_lon", 0)),
            start_altitude_m=record.get("start_altitude_m"),
            end_lat=float(record.get("end_lat", 0)),
            end_lon=float(record.get("end_lon", 0)),
            end_altitude_m=record.get("end_altitude_m"),
            distance_m=record.get("distance_m"),
            azimuth_deg=record.get("azimuth_deg"),
            elevation_angle_deg=record.get("elevation_angle_deg"),
            address_geojson=record.get("address_geojson"),
            display_name=record.get("display_name"),
            status=record.get("status", "Under Review"),
            review_reason=record.get("review_reason"),
            submitted_at=record.get("submitted_at"),
            created_at=record.get("created_at"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Supabase insertion."""
        data = {
            "user_email": self.user_email,
            "range_name": self.range_name,
            "range_description": self.range_description,
            "start_lat": self.start_lat,
            "start_lon": self.start_lon,
            "start_altitude_m": self.start_altitude_m,
            "end_lat": self.end_lat,
            "end_lon": self.end_lon,
            "end_altitude_m": self.end_altitude_m,
            "distance_m": self.distance_m,
            "azimuth_deg": self.azimuth_deg,
            "elevation_angle_deg": self.elevation_angle_deg,
            "address_geojson": self.address_geojson,
            "display_name": self.display_name,
            "status": self.status,
            "review_reason": self.review_reason,
        }

        # Only include id if it exists (for updates)
        if self.id:
            data["id"] = self.id

        return data


@dataclass
class Range:
    """Model for approved public ranges."""

    id: Optional[str] = None
    user_email: str = ""
    range_name: str = ""
    range_description: Optional[str] = None

    # Geographic coordinates and measurements
    start_lat: float = 0.0
    start_lon: float = 0.0
    start_altitude_m: Optional[float] = None
    end_lat: float = 0.0
    end_lon: float = 0.0
    end_altitude_m: Optional[float] = None

    # Calculated values
    distance_m: Optional[float] = None
    azimuth_deg: Optional[float] = None
    elevation_angle_deg: Optional[float] = None

    # Address information
    address_geojson: Optional[Dict[str, Any]] = None
    display_name: Optional[str] = None

    # Timestamps
    submitted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_supabase_record(cls, record: Dict[str, Any]) -> "Range":
        """Create Range from Supabase record."""
        return cls(
            id=record.get("id"),
            user_email=record.get("user_email", ""),
            range_name=record.get("range_name", ""),
            range_description=record.get("range_description"),
            start_lat=float(record.get("start_lat", 0)),
            start_lon=float(record.get("start_lon", 0)),
            start_altitude_m=record.get("start_altitude_m"),
            end_lat=float(record.get("end_lat", 0)),
            end_lon=float(record.get("end_lon", 0)),
            end_altitude_m=record.get("end_altitude_m"),
            distance_m=record.get("distance_m"),
            azimuth_deg=record.get("azimuth_deg"),
            elevation_angle_deg=record.get("elevation_angle_deg"),
            address_geojson=record.get("address_geojson"),
            display_name=record.get("display_name"),
            submitted_at=record.get("submitted_at"),
            created_at=record.get("created_at"),
        )

    @classmethod
    def from_range_submission(cls, submission: RangeSubmission) -> "Range":
        """Create Range from approved RangeSubmission."""
        return cls(
            user_email=submission.user_email,
            range_name=submission.range_name,
            range_description=submission.range_description,
            start_lat=submission.start_lat,
            start_lon=submission.start_lon,
            start_altitude_m=submission.start_altitude_m,
            end_lat=submission.end_lat,
            end_lon=submission.end_lon,
            end_altitude_m=submission.end_altitude_m,
            distance_m=submission.distance_m,
            azimuth_deg=submission.azimuth_deg,
            elevation_angle_deg=submission.elevation_angle_deg,
            address_geojson=submission.address_geojson,
            display_name=submission.display_name,
            submitted_at=submission.submitted_at,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Supabase insertion."""
        data = {
            "user_email": self.user_email,
            "range_name": self.range_name,
            "range_description": self.range_description,
            "start_lat": self.start_lat,
            "start_lon": self.start_lon,
            "start_altitude_m": self.start_altitude_m,
            "end_lat": self.end_lat,
            "end_lon": self.end_lon,
            "end_altitude_m": self.end_altitude_m,
            "distance_m": self.distance_m,
            "azimuth_deg": self.azimuth_deg,
            "elevation_angle_deg": self.elevation_angle_deg,
            "address_geojson": self.address_geojson,
            "display_name": self.display_name,
            "submitted_at": self.submitted_at,
        }

        # Only include id if it exists (for updates)
        if self.id:
            data["id"] = self.id

        return data


@dataclass
class RangeMeasurements:
    """Model for calculated range measurements."""

    start_lat: float = 0.0
    start_lon: float = 0.0
    start_altitude_m: Optional[float] = None
    end_lat: float = 0.0
    end_lon: float = 0.0
    end_altitude_m: Optional[float] = None
    distance_m: float = 0.0
    azimuth_deg: float = 0.0
    elevation_angle_deg: float = 0.0
    display_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "start_lat": self.start_lat,
            "start_lon": self.start_lon,
            "start_altitude_m": self.start_altitude_m,
            "end_lat": self.end_lat,
            "end_lon": self.end_lon,
            "end_altitude_m": self.end_altitude_m,
            "distance_m": self.distance_m,
            "azimuth_deg": self.azimuth_deg,
            "elevation_angle_deg": self.elevation_angle_deg,
            "display_name": self.display_name,
        }
