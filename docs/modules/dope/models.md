# DOPE Models Documentation

## Overview

The DOPE module uses two main dataclass models: `DopeSessionModel` and `DopeMeasurementModel`. These models represent the convergence of data from all source modules into unified ballistic profiles.

All field values are stored in **metric units** internally, following ChronoLog's metric system philosophy.

## DopeSessionModel

Dataclass representing a complete DOPE session with denormalized data from 6+ source tables.

**Location**: `dope/models.py`

### Class Definition

```python
@dataclass
class DopeSessionModel:
    """Entity representing a DOPE (Data On Previous Engagement) session"""
    # ... 60+ fields ...
```

This is the **MOST COMPLEX model** in ChronoLog with data aggregated from:
- dope_sessions table (core data)
- cartridges table (cartridge details)
- bullets table (via cartridge FK - ballistic specs)
- rifles table (rifle configuration)
- chrono_sessions table (chronograph metadata)
- weather_source table (weather device/source)
- ranges_submissions table (location and geometry)

---

## Fields - Core Identification

### id
- **Type**: `Optional[str]`
- **Required**: Yes (on retrieval)
- **Description**: UUID of the DOPE session
- **Example**: `"123e4567-e89b-12d3-a456-426614174000"`
- **Notes**: Auto-generated on creation

### user_id
- **Type**: `Optional[str]`
- **Required**: Yes
- **Description**: Auth0 user ID who owns this session
- **Example**: `"auth0|507f1f77bcf86cd799439011"`
- **Notes**: All queries filtered by user_id for security

### session_name
- **Type**: `str`
- **Required**: Yes (NOT NULL)
- **Description**: User-provided session name
- **Example**: `"308 Win @ 100m - Morning Session"`
- **Notes**: Primary display identifier

### datetime_local
- **Type**: `Optional[datetime]`
- **Required**: Yes (NOT NULL)
- **Description**: Session datetime from chronograph session
- **Example**: `datetime(2025, 10, 19, 8, 30, 0)`
- **Notes**: Pulled from linked chronograph session

---

## Fields - Foreign Key Relationships

### cartridge_id
- **Type**: `Optional[str]`
- **Description**: FK to cartridges table
- **Example**: `"cart-uuid"`
- **Notes**: Required - links to cartridge (which links to bullet)

### bullet_id
- **Type**: `Optional[str]`
- **Description**: FK to bullets table (via cartridge)
- **Example**: `"bullet-uuid"`
- **Notes**: Required - denormalized from cartridge.bullet_id

### chrono_session_id
- **Type**: `Optional[str]`
- **Description**: FK to chrono_sessions table
- **Example**: `"chrono-uuid"`
- **Notes**: Required - source of velocity data

### range_submission_id
- **Type**: `Optional[str]`
- **Description**: FK to ranges_submissions table
- **Example**: `"range-uuid"`
- **Notes**: Required - shooting location

### weather_source_id
- **Type**: `Optional[str]`
- **Description**: FK to weather_source table
- **Example**: `"weather-uuid"`
- **Notes**: Optional - if provided, weather data is associated

### rifle_id
- **Type**: `Optional[str]`
- **Description**: FK to rifles table
- **Example**: `"rifle-uuid"`
- **Notes**: Required - rifle configuration

---

## Fields - Time Fields

### start_time
- **Type**: `datetime`
- **Required**: Yes (NOT NULL)
- **Unit**: UTC datetime
- **Description**: Session start time from chronograph
- **Example**: `datetime(2025, 10, 19, 8, 30, 0)`
- **Notes**: Automatically pulled from chronograph session (cannot be manually set)

### end_time
- **Type**: `datetime`
- **Required**: Yes (NOT NULL)
- **Unit**: UTC datetime
- **Description**: Session end time from chronograph
- **Example**: `datetime(2025, 10, 19, 10, 30, 0)`
- **Notes**: Automatically pulled from chronograph session (cannot be manually set)

---

## Fields - Range and Session Data

### range_name
- **Type**: `Optional[str]`
- **Description**: Name of the shooting range
- **Example**: `"Pine Valley Range"`
- **Notes**: Denormalized from ranges_submissions

### range_description
- **Type**: `Optional[str]`
- **Description**: Description of the range
- **Example**: `"Outdoor range with 100-600m distances"`

### range_display_name
- **Type**: `Optional[str]`
- **Description**: Display name for the range
- **Example**: `"100m Bay #3"`

### range_distance_m
- **Type**: `Optional[float]`
- **Unit**: Meters (m)
- **Description**: Shooting distance
- **Example**: `100.0`, `274.32` (300 yards)
- **Notes**: Metric only - convert from yards at import edge

### notes
- **Type**: `Optional[str]`
- **Description**: User notes about the session
- **Example**: `"Excellent conditions, testing new load"`

---

## Fields - Location and Geometry

### lat
- **Type**: `Optional[float]`
- **Unit**: Decimal degrees
- **Description**: Shooting position latitude
- **Example**: `34.0522`
- **Notes**: From ranges_submissions.start_lat

### lon
- **Type**: `Optional[float]`
- **Unit**: Decimal degrees
- **Description**: Shooting position longitude
- **Example**: `-118.2437`
- **Notes**: From ranges_submissions.start_lon

### end_lat
- **Type**: `Optional[float]`
- **Unit**: Decimal degrees
- **Description**: Target position latitude
- **Example**: `34.0532`

### end_lon
- **Type**: `Optional[float]`
- **Unit**: Decimal degrees
- **Description**: Target position longitude
- **Example**: `-118.2447`

### start_altitude
- **Type**: `Optional[float]`
- **Unit**: Meters (m)
- **Description**: Shooting position altitude
- **Example**: `100.5`
- **Notes**: From ranges_submissions.start_altitude_m

### azimuth_deg
- **Type**: `Optional[float]`
- **Unit**: Degrees (0-360)
- **Description**: Bearing from shooter to target
- **Example**: `90.0` (due east)

### elevation_angle_deg
- **Type**: `Optional[float]`
- **Unit**: Degrees
- **Description**: Vertical angle from shooter to target
- **Example**: `2.5` (uphill)
- **Notes**: Positive = uphill, Negative = downhill

### location_hyperlink
- **Type**: `Optional[str]`
- **Description**: Google Maps URL for the shooting location
- **Example**: `"https://maps.google.com/?q=34.0522,-118.2437"`
- **Notes**: Auto-generated from lat/lon

---

## Fields - Rifle Information (MANDATORY)

### rifle_name
- **Type**: `str`
- **Required**: Yes (NOT NULL)
- **Description**: Name/model of the rifle
- **Example**: `"Remington 700"`, `"AR-15 SPR"`
- **Notes**: Denormalized from rifles table

### rifle_barrel_length_cm
- **Type**: `Optional[float]`
- **Unit**: Centimeters (cm)
- **Description**: Barrel length
- **Example**: `50.8` (20 inches), `61.0` (24 inches)
- **Notes**: Critical for ballistic calculations

### rifle_barrel_twist_in_per_rev
- **Type**: `Optional[float]`
- **Unit**: Inches per revolution
- **Description**: Barrel rifling twist rate
- **Example**: `8.0` (1:8 twist), `10.0` (1:10 twist)
- **Notes**: **Imperial units** - twist rates always in inches (industry standard)

---

## Fields - Cartridge Information (MANDATORY)

### cartridge_make
- **Type**: `str`
- **Required**: Yes (NOT NULL)
- **Description**: Cartridge manufacturer
- **Example**: `"Federal"`, `"Hornady"`, `"Custom"`
- **Notes**: Denormalized from cartridges table

### cartridge_model
- **Type**: `str`
- **Required**: Yes (NOT NULL)
- **Description**: Cartridge model/product name
- **Example**: `"Gold Medal Match"`, `"Match"`, `"Handload"`
- **Notes**: Denormalized from cartridges table

### cartridge_type
- **Type**: `str`
- **Required**: Yes (NOT NULL)
- **Description**: Cartridge type/caliber designation
- **Example**: `"308 Winchester"`, `"223 Remington"`, `"6.5 Creedmoor"`
- **Notes**: Critical for filtering and grouping

### cartridge_lot_number
- **Type**: `Optional[str]`
- **Description**: Lot/batch number of the ammunition
- **Example**: `"LT2024001"`
- **Notes**: Useful for tracking consistency

---

## Fields - Bullet Information (MANDATORY)

### bullet_make
- **Type**: `str`
- **Required**: Yes (NOT NULL)
- **Description**: Bullet manufacturer
- **Example**: `"Sierra"`, `"Hornady"`, `"Berger"`
- **Notes**: Denormalized from bullets table via cartridge FK

### bullet_model
- **Type**: `str`
- **Required**: Yes (NOT NULL)
- **Description**: Bullet model name
- **Example**: `"MatchKing"`, `"ELD Match"`, `"VLD Target"`
- **Notes**: Denormalized from bullets table via cartridge FK

### bullet_weight
- **Type**: `str`
- **Required**: Yes (NOT NULL)
- **Unit**: Text (stored as string)
- **Description**: Bullet weight in grains
- **Example**: `"168"`, `"175"`, `"147"`
- **Notes**: Stored as text in database, ballistics standard is grains

### bore_diameter_land_mm
- **Type**: `str`
- **Required**: Yes (NOT NULL) - **CRITICAL**
- **Unit**: Text (millimeters when converted to float)
- **Description**: Bore diameter at land (defines caliber)
- **Example**: `"7.62"` (for .308), `"5.56"` (for .223)
- **Notes**: **MANDATORY FIELD** - defines the caliber, stored as text

### bullet_length_mm
- **Type**: `Optional[str]`
- **Unit**: Text (millimeters when converted)
- **Description**: Overall bullet length
- **Example**: `"31.0"`, `"35.5"`
- **Notes**: Stored as text

### ballistic_coefficient_g1
- **Type**: `Optional[str]`
- **Unit**: Text (dimensionless when converted)
- **Description**: Ballistic coefficient using G1 drag model
- **Example**: `"0.462"`, `"0.523"`
- **Notes**: Stored as text, traditional BC model

### ballistic_coefficient_g7
- **Type**: `Optional[str]`
- **Unit**: Text (dimensionless when converted)
- **Description**: Ballistic coefficient using G7 drag model
- **Example**: `"0.243"`, `"0.268"`
- **Notes**: Stored as text, **preferred for modern bullets**

### sectional_density
- **Type**: `Optional[str]`
- **Unit**: Text (dimensionless when converted)
- **Description**: Weight-to-diameter ratio
- **Example**: `"0.253"`
- **Notes**: Stored as text, indicator of penetration

### bullet_diameter_groove_mm
- **Type**: `Optional[str]`
- **Unit**: Text (millimeters when converted)
- **Description**: Bullet diameter at groove (widest part)
- **Example**: `"7.82"` (for .308 bullets)
- **Notes**: Stored as text

---

## Fields - Weather Data (Median Values, Metric)

### temperature_c_median
- **Type**: `Optional[float]`
- **Unit**: Celsius (°C)
- **Description**: Median temperature during session
- **Example**: `22.0`, `18.5`
- **Notes**: Calculated median from weather measurements

### relative_humidity_pct_median
- **Type**: `Optional[float]`
- **Unit**: Percentage (%)
- **Description**: Median relative humidity
- **Example**: `65.0`, `45.0`
- **Notes**: Range 0-100

### barometric_pressure_hpa_median
- **Type**: `Optional[float]`
- **Unit**: Hectopascals (hPa)
- **Description**: Median barometric pressure
- **Example**: `1020.1`, `1013.25`
- **Notes**: **Metric** - hectopascals (not inHg)

### wind_speed_mps_median
- **Type**: `Optional[float]`
- **Unit**: Meters per second (m/s)
- **Description**: Median wind speed
- **Example**: `2.2`, `3.3`
- **Notes**: **Metric** - m/s (not mph or km/h)

### wind_speed_2_mps_median
- **Type**: `Optional[float]`
- **Unit**: Meters per second (m/s)
- **Description**: Median wind speed from secondary sensor
- **Example**: `2.4`, `3.8`
- **Notes**: Some devices have multiple anemometers

### wind_direction_deg_median
- **Type**: `Optional[float]`
- **Unit**: Degrees (0-360)
- **Description**: Median wind direction
- **Example**: `270.0` (west), `135.0` (southeast)

---

## Fields - Source Names (Denormalized)

### weather_source_name
- **Type**: `Optional[str]`
- **Description**: Name of weather device/source
- **Example**: `"Kestrel 5500"`, `"Weather Station #1"`
- **Notes**: Denormalized from weather_source table

### chrono_session_name
- **Type**: `Optional[str]`
- **Description**: Name of chronograph session
- **Example**: `"Morning Session 10-19-2025"`
- **Notes**: Denormalized from chrono_sessions table

---

## Fields - Velocity Statistics (NOT NULL)

### speed_mps_min
- **Type**: `Optional[float]`
- **Unit**: Meters per second (m/s)
- **Description**: Minimum velocity from chronograph session
- **Example**: `790.0`
- **Notes**: Calculated from chronograph measurements

### speed_mps_max
- **Type**: `Optional[float]`
- **Unit**: Meters per second (m/s)
- **Description**: Maximum velocity from chronograph session
- **Example**: `795.0`

### speed_mps_avg
- **Type**: `Optional[float]`
- **Unit**: Meters per second (m/s)
- **Description**: Average velocity from chronograph session
- **Example**: `792.5`
- **Notes**: Mean velocity across all shots

### speed_mps_std_dev
- **Type**: `Optional[float]`
- **Unit**: Meters per second (m/s)
- **Description**: Standard deviation of velocity
- **Example**: `1.2`
- **Notes**: Indicator of consistency

---

## Fields - Timestamps

### created_at
- **Type**: `Optional[datetime]`
- **Description**: When the session was created
- **Example**: `datetime(2025, 10, 19, 10, 30, 0)`
- **Notes**: Auto-generated by database

### updated_at
- **Type**: `Optional[datetime]`
- **Description**: When the session was last updated
- **Example**: `datetime(2025, 10, 19, 11, 00, 0)`
- **Notes**: Auto-updated by database

---

## Class Methods

### from_supabase_record()

Create a `DopeSessionModel` from a Supabase database record with complex JOIN flattening.

**Signature**:
```python
@classmethod
def from_supabase_record(cls, record: dict) -> DopeSessionModel
```

**Parameters**:
- `record` (dict): Dictionary from Supabase query result (with JOINs)

**Returns**:
- `DopeSessionModel`: Fully typed session instance with denormalized data

**Notes**:
- Handles complex datetime parsing (multiple formats)
- Flattens nested JOIN data from 6+ tables
- Converts all fields to appropriate types

---

### from_supabase_records()

Batch convert multiple Supabase records to `DopeSessionModel` instances.

**Signature**:
```python
@classmethod
def from_supabase_records(cls, records: List[dict]) -> List[DopeSessionModel]
```

**Parameters**:
- `records` (List[dict]): List of dictionaries from Supabase

**Returns**:
- `List[DopeSessionModel]`: List of typed session instances

---

### to_dict()

Convert `DopeSessionModel` to dictionary for database operations.

**Signature**:
```python
def to_dict(self) -> dict
```

**Returns**:
- `dict`: Dictionary with all fields for insert/update

**Notes**:
- Includes only database-writable fields
- Excludes denormalized read-only fields
- Handles datetime serialization

---

## Properties

### display_name

Get a user-friendly display name for the session.

**Signature**:
```python
@property
def display_name(self) -> str
```

**Returns**:
- `str`: Formatted display name

**Logic**:
- If `session_name` provided, returns that
- Otherwise constructs from: `{cartridge_type} {bullet_make} {bullet_model} {range_distance_m}m`
- Falls back to "Untitled DOPE Session"

**Example**:
```python
session.display_name
# "308 Win @ 100m - Morning Session"
# or "308 Winchester - Sierra MatchKing - 100m"
```

---

### cartridge_display

Get a display string for the cartridge information.

**Signature**:
```python
@property
def cartridge_display(self) -> str
```

**Returns**:
- `str`: Formatted cartridge name

**Format**: `"{make} {model} ({type})"`

**Example**:
```python
session.cartridge_display
# "Federal Gold Medal Match (308 Winchester)"
```

---

### bullet_display

Get a display string for the bullet information.

**Signature**:
```python
@property
def bullet_display(self) -> str
```

**Returns**:
- `str`: Formatted bullet name

**Format**: `"{make} {model} {weight}gr"`

**Example**:
```python
session.bullet_display
# "Sierra MatchKing 168gr"
```

---

### is_complete()

Check if all mandatory fields are filled.

**Signature**:
```python
def is_complete(self) -> bool
```

**Returns**:
- `bool`: True if all mandatory fields have values

**Mandatory fields checked**:
- session_name
- rifle_name
- cartridge_make, cartridge_model, cartridge_type
- bullet_make, bullet_model, bullet_weight

---

### get_missing_mandatory_fields()

Get list of missing mandatory fields for validation.

**Signature**:
```python
def get_missing_mandatory_fields(self) -> List[str]
```

**Returns**:
- `List[str]`: List of missing field names (human-readable)

**Example**:
```python
missing = session.get_missing_mandatory_fields()
if missing:
    print(f"Missing fields: {', '.join(missing)}")
    # "Missing fields: Rifle Name, Bullet Weight"
```

---

## DopeMeasurementModel

Dataclass representing an individual shot measurement within a DOPE session.

**Location**: `dope/models.py`

### Class Definition

```python
@dataclass
class DopeMeasurementModel:
    """Entity representing a DOPE measurement (individual shot data)"""
    # ... fields ...
```

---

## Measurement Fields - Core Identification

### id
- **Type**: `Optional[str]`
- **Description**: UUID of the measurement
- **Example**: `"meas-uuid"`
- **Notes**: Auto-generated on creation

### dope_session_id
- **Type**: `str`
- **Required**: Yes (NOT NULL)
- **Description**: FK to dope_sessions table
- **Example**: `"session-uuid"`
- **Notes**: Parent session

### user_id
- **Type**: `str`
- **Required**: Yes (NOT NULL)
- **Description**: Auth0 user ID for user isolation
- **Example**: `"auth0|123456"`
- **Notes**: For security filtering

---

## Measurement Fields - Shot Data

### shot_number
- **Type**: `Optional[int]`
- **Description**: Sequential shot number
- **Example**: `1`, `2`, `10`
- **Notes**: Order of shots in session

### datetime_shot
- **Type**: `Optional[datetime]`
- **Description**: When this shot was fired
- **Example**: `datetime(2025, 10, 19, 8, 35, 12)`
- **Notes**: Individual shot timestamp

---

## Measurement Fields - Ballistic Data (Metric)

### speed_mps
- **Type**: `Optional[float]`
- **Unit**: Meters per second (m/s)
- **Description**: Projectile velocity
- **Example**: `792.5`, `807.7`
- **Notes**: Primary ballistic measurement

### ke_j
- **Type**: `Optional[float]`
- **Unit**: Joules (J)
- **Description**: Kinetic energy
- **Example**: `3456.7`
- **Notes**: Energy of projectile

### power_factor_kgms
- **Type**: `Optional[float]`
- **Unit**: kg·m/s
- **Description**: Power factor
- **Example**: `0.1356`
- **Notes**: For competition scoring

---

## Measurement Fields - Targeting Data

### azimuth_deg
- **Type**: `Optional[float]`
- **Unit**: Degrees (0-360)
- **Description**: Horizontal bearing to target
- **Example**: `90.0`

### elevation_angle_deg
- **Type**: `Optional[float]`
- **Unit**: Degrees
- **Description**: Vertical angle to target
- **Example**: `2.5`

---

## Measurement Fields - Environmental (Metric)

### temperature_c
- **Type**: `Optional[float]`
- **Unit**: Celsius (°C)
- **Description**: Air temperature at shot time
- **Example**: `21.0`, `18.5`

### pressure_hpa
- **Type**: `Optional[float]`
- **Unit**: Hectopascals (hPa)
- **Description**: Barometric pressure at shot time
- **Example**: `1013.25`
- **Notes**: **Metric** - hectopascals

### humidity_pct
- **Type**: `Optional[float]`
- **Unit**: Percentage (%)
- **Description**: Relative humidity
- **Example**: `65.0`

---

## Measurement Fields - Bore Conditions

### clean_bore
- **Type**: `Optional[str]`
- **Description**: Clean bore status
- **Example**: `"yes"`, `"no"`, `"fouled"`
- **Notes**: Text field for flexibility

### cold_bore
- **Type**: `Optional[str]`
- **Description**: Cold bore status
- **Example**: `"yes"`, `"no"`
- **Notes**: First shot vs. subsequent shots

---

## Measurement Fields - Adjustments (Metric)

### distance_m
- **Type**: `Optional[float]`
- **Unit**: Meters (m)
- **Description**: Target distance for this shot
- **Example**: `100.0`, `274.32`

### elevation_adjustment
- **Type**: `Optional[str]`
- **Description**: Elevation scope adjustment
- **Example**: `"0.726"` (mrad), `"2.5"` (MOA)
- **Notes**: Stored as text (can be mrad or MOA)

### windage_adjustment
- **Type**: `Optional[str]`
- **Description**: Windage scope adjustment
- **Example**: `"0.145"` (mrad), `"0.5"` (MOA)
- **Notes**: Stored as text (can be mrad or MOA)

---

## Measurement Fields - Notes & Timestamps

### shot_notes
- **Type**: `Optional[str]`
- **Description**: Notes about this specific shot
- **Example**: `"Flyer - wind gust during trigger press"`

### created_at
- **Type**: `Optional[datetime]`
- **Description**: When measurement was created
- **Notes**: Auto-generated

### updated_at
- **Type**: `Optional[datetime]`
- **Description**: When measurement was last updated
- **Notes**: Auto-updated

---

## Measurement Class Methods

### from_supabase_record()

Create a `DopeMeasurementModel` from Supabase record.

**Signature**:
```python
@classmethod
def from_supabase_record(cls, record: dict) -> DopeMeasurementModel
```

---

### from_supabase_records()

Batch convert Supabase records to `DopeMeasurementModel` instances.

**Signature**:
```python
@classmethod
def from_supabase_records(cls, records: List[dict]) -> List[DopeMeasurementModel]
```

---

### to_dict()

Convert to dictionary for database operations.

**Signature**:
```python
def to_dict(self) -> dict
```

---

## Measurement Properties

### display_name

Get friendly display name for the measurement.

**Format**: `"Shot #{shot_number} - {speed_mps} m/s"`

---

### bore_conditions_display

Get display string for bore conditions.

**Format**: `"Clean: {clean_bore}, Cold: {cold_bore}"`

---

### environmental_display

Get display string for environmental conditions.

**Format**: `"Temp: {temperature_c}°C, Humidity: {humidity_pct}%, Pressure: {pressure_hpa} hPa"`

---

### adjustments_display

Get display string for scope adjustments.

**Format**: `"Distance: {distance_m}m, Elevation: {elevation_adjustment} mrad, Windage: {windage_adjustment} mrad"`

---

### has_ballistic_data()

Check if measurement has any ballistic data.

**Returns**: `bool`

---

### has_environmental_data()

Check if measurement has environmental data.

**Returns**: `bool`

---

### has_targeting_data()

Check if measurement has targeting data.

**Returns**: `bool`

---

## Unit Conventions

### Metric (Internal Storage)

**Always metric**:
- Velocity: meters per second (m/s)
- Energy: Joules (J)
- Distance: meters (m)
- Temperature: Celsius (°C)
- Pressure: hectopascals (hPa)
- Wind: meters per second (m/s)
- Length: millimeters (mm) or centimeters (cm)

### Special Cases

**Text fields** (bullet specs):
- Stored as text but represent metric values
- `bore_diameter_land_mm` is text (e.g., "7.62")
- `bullet_weight` is text (e.g., "168") - grains
- Convert to float/int when needed for calculations

**Twist rate**:
- `rifle_barrel_twist_in_per_rev` in inches (industry standard)
- NOT converted to metric

### Display Conversion

UI may convert for display based on user preference:
- Velocity: m/s ↔ fps
- Energy: J ↔ ft-lbs
- Distance: m ↔ yards
- Temperature: °C ↔ °F
- Pressure: hPa ↔ inHg
- Units shown in column headers, not in values

---

## Field Validation

### DopeSessionModel Required Fields

```python
# Core fields
session_name: str  # Non-empty
user_id: str  # Non-empty Auth0 ID
datetime_local: datetime  # NOT NULL

# Foreign keys (all required)
cartridge_id: str
bullet_id: str
chrono_session_id: str
range_submission_id: str
rifle_id: str

# Time fields (auto-managed)
start_time: datetime  # From chronograph
end_time: datetime  # From chronograph

# Denormalized mandatory fields (from JOINs)
rifle_name: str  # NOT NULL
cartridge_make: str  # NOT NULL
cartridge_model: str  # NOT NULL
cartridge_type: str  # NOT NULL
bullet_make: str  # NOT NULL
bullet_model: str  # NOT NULL
bullet_weight: str  # NOT NULL
bore_diameter_land_mm: str  # NOT NULL - CRITICAL
```

### DopeMeasurementModel Required Fields

```python
# Only two required fields
dope_session_id: str  # NOT NULL
user_id: str  # NOT NULL

# All other fields are optional
```

---

## Integration with Other Models

### Composition from Source Modules

DopeSessionModel composes data from:
- `CartridgeModel` (from cartridges.models)
- `BulletModel` (from bullets.models via cartridge FK)
- `Rifle` (from rifles.models)
- `ChronographSession` (from chronograph.models)
- `WeatherMeasurement` (from weather.models)
- `RangeSubmission` (from mapping models)

### Flattened Structure

Rather than nested objects, DOPE uses a flat denormalized structure:

```python
# NOT this (nested):
session.cartridge.bullet.bore_diameter_land_mm

# Instead this (flat):
session.bore_diameter_land_mm
```

This improves:
- Query performance (single JOIN query)
- Type safety (all fields directly accessible)
- Filtering and searching (no nested field access)

---

## Next Steps

- [API Reference](api-reference.md) - Methods for working with DOPE sessions
- [Examples](examples.md) - Common usage patterns
- [Module README](README.md) - Overview and integration

---

**Model Version**: 1.0
**Location**: `dope/models.py`
**Database Tables**: `dope_sessions`, `dope_measurements`
**Critical Note**: `bore_diameter_land_mm` is MANDATORY (NOT NULL)