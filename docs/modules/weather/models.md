# Weather Models Documentation

## Overview

The weather module uses two dataclass models: `WeatherSource` and `WeatherMeasurement`. These models represent weather meters/devices and their measurements.

All field values are stored in **metric units** internally, following ChronoLog's metric system philosophy.

## WeatherSource

Dataclass representing a weather meter/device.

**Location**: `weather/models.py`

### Class Definition

```python
@dataclass
class WeatherSource:
    """Entity representing a weather meter/device"""
    # ... fields ...
```

---

## WeatherSource Fields

### Identity Fields

#### id
- **Type**: `str`
- **Required**: Yes
- **Description**: UUID of the weather source
- **Example**: `"123e4567-e89b-12d3-a456-426614174000"`
- **Notes**: Auto-generated on creation

#### user_id
- **Type**: `str`
- **Required**: Yes
- **Description**: User ID of owner
- **Example**: `"auth0|507f1f77bcf86cd799439011"`
- **Notes**: Enforces user isolation (user-owned data)

---

### Core Specification Fields

#### name
- **Type**: `str`
- **Required**: Yes
- **Description**: User-defined name for the source
- **Example**: `"My Kestrel"`, `"Range Meter"`, `"Home Weather Station"`
- **Notes**: Used for display and identification

#### source_type
- **Type**: `str`
- **Required**: Yes
- **Default**: `"meter"`
- **Description**: Type of weather source
- **Example**: `"meter"`, `"station"`, `"manual"`
- **Notes**: Currently only "meter" is used

---

### Device Information Fields

#### device_name
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Device name from CSV/import
- **Example**: `"Kestrel 5700"`, `"Kestrel DROP D3"`
- **Notes**: Extracted from CSV metadata during import

#### make
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Device manufacturer
- **Example**: `"Kestrel"`, `"Davis Instruments"`
- **Notes**: Can be set manually or extracted during import

#### model
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Device model number
- **Example**: `"5700 Elite"`, `"DROP D3"`, `"Vantage Pro2"`
- **Notes**: Extracted from CSV metadata during import

#### serial_number
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Device serial number
- **Example**: `"K123456"`, `"SN789012"`
- **Notes**: Used for device identification and preventing duplicates

---

### Timestamp Fields

#### created_at
- **Type**: `Optional[datetime]`
- **Required**: No
- **Description**: When source was created
- **Example**: `datetime(2024, 1, 15, 10, 0, 0)`
- **Notes**: Auto-generated on creation

#### updated_at
- **Type**: `Optional[datetime]`
- **Required**: No
- **Description**: When source was last updated
- **Example**: `datetime(2024, 1, 20, 14, 30, 0)`
- **Notes**: Auto-updated on any modification

---

## WeatherSource Class Methods

### from_device_info()

Create a `WeatherSource` from device information (typically from CSV import).

**Signature**:
```python
@classmethod
def from_device_info(
    cls,
    user_id: str,
    name: str,
    device_name: str = None,
    device_model: str = None,
    serial_number: str = None,
) -> WeatherSource
```

**Parameters**:
- `user_id`: Owner's user ID
- `name`: User-defined name
- `device_name`: Optional device name from CSV
- `device_model`: Optional model from CSV
- `serial_number`: Optional serial number from CSV

**Returns**:
- `WeatherSource`: Source instance (id will be empty, to be filled by database)

**Example**:
```python
source = WeatherSource.from_device_info(
    "user-123",
    "My Kestrel",
    "Kestrel 5700",
    "5700 Elite",
    "K123456"
)
```

---

### from_supabase_record()

Create a `WeatherSource` from a Supabase database record.

**Signature**:
```python
@classmethod
def from_supabase_record(cls, record: dict) -> WeatherSource
```

**Parameters**:
- `record` (dict): Dictionary from Supabase query result

**Returns**:
- `WeatherSource`: Fully typed source instance

**Example**:
```python
record = {
    "id": "source-123",
    "user_id": "user-123",
    "name": "My Kestrel",
    "device_name": "Kestrel 5700",
    "model": "5700 Elite",
    "serial_number": "K123456",
    "created_at": "2024-01-15T10:00:00",
    ...
}

source = WeatherSource.from_supabase_record(record)
```

---

### from_supabase_records()

Batch convert multiple Supabase records to `WeatherSource` instances.

**Signature**:
```python
@classmethod
def from_supabase_records(cls, records: List[dict]) -> List[WeatherSource]
```

**Parameters**:
- `records` (List[dict]): List of dictionaries from Supabase

**Returns**:
- `List[WeatherSource]`: List of typed source instances

**Example**:
```python
records = [record1, record2, record3]
sources = WeatherSource.from_supabase_records(records)
```

---

## WeatherSource Properties

### display_name()

Get a user-friendly display name for the weather source.

**Signature**:
```python
def display_name(self) -> str
```

**Returns**:
- `str`: User-defined name

**Example**:
```python
source = WeatherSource(name="My Kestrel", ...)
print(source.display_name())
# Output: "My Kestrel"
```

**Note**: Currently just returns the name field. Could be extended for more complex display logic.

---

### device_display()

Get a formatted device description including make, model, and serial number.

**Signature**:
```python
def device_display(self) -> str
```

**Returns**:
- `str`: Formatted device description

**Format Logic**:
1. If `make` and `model`: `"{make} {model}"`
2. Else if `device_name`: `"{device_name}"`
3. Else if `model`: `"{model}"`
4. Else: `"Unknown Device"`
5. If `serial_number` exists, append: `" (S/N: {serial_number})"`

**Examples**:
```python
# With make and model
source = WeatherSource(make="Kestrel", model="5700 Elite", serial_number="K123456")
print(source.device_display())
# Output: "Kestrel 5700 Elite (S/N: K123456)"

# With device_name only
source = WeatherSource(device_name="Kestrel 5700", serial_number="K123456")
print(source.device_display())
# Output: "Kestrel 5700 (S/N: K123456)"

# Minimal info
source = WeatherSource(model="5700 Elite")
print(source.device_display())
# Output: "5700 Elite"

# No info
source = WeatherSource()
print(source.device_display())
# Output: "Unknown Device"
```

---

### short_display()

Get a concise display combining name and device info (for dropdowns/lists).

**Signature**:
```python
def short_display(self) -> str
```

**Returns**:
- `str`: Combined name and device description

**Format**: `"{name} - {device_display()}"`

**Example**:
```python
source = WeatherSource(
    name="My Kestrel",
    make="Kestrel",
    model="5700 Elite",
    serial_number="K123456"
)

print(source.short_display())
# Output: "My Kestrel - Kestrel 5700 Elite (S/N: K123456)"
```

**Note**: Useful for dropdown options where both name and device info are helpful.

---

## WeatherMeasurement

Dataclass representing a single weather measurement/reading.

**Location**: `weather/models.py`

### Class Definition

```python
@dataclass
class WeatherMeasurement:
    """Entity representing a single weather measurement"""
    # ... fields ...
```

---

## WeatherMeasurement Fields

### Identity Fields

#### id
- **Type**: `str`
- **Required**: Yes
- **Description**: UUID of the measurement
- **Example**: `"123e4567-e89b-12d3-a456-426614174000"`
- **Notes**: Auto-generated on creation

#### user_id
- **Type**: `str`
- **Required**: Yes
- **Description**: User ID of owner
- **Example**: `"auth0|507f1f77bcf86cd799439011"`
- **Notes**: Enforces user isolation

#### weather_source_id
- **Type**: `str`
- **Required**: Yes
- **Description**: UUID of associated weather source
- **Example**: `"source-123"`
- **Notes**: Foreign key to weather_source table

---

### Timestamp Fields

#### measurement_timestamp
- **Type**: `datetime`
- **Required**: Yes
- **Description**: When the weather reading was taken
- **Example**: `datetime(2024, 1, 15, 10, 0, 0)`
- **Notes**: From device/CSV, not when uploaded

#### uploaded_at
- **Type**: `datetime`
- **Required**: Yes
- **Description**: When measurement was uploaded to database
- **Example**: `datetime(2024, 1, 15, 14, 30, 0)`
- **Notes**: Auto-generated on creation

---

### File Metadata

#### file_path
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Path to source CSV file
- **Example**: `"weather/kestrel_2024-01-15.csv"`
- **Notes**: For tracking which file measurement came from

---

### Temperature Fields (Metric - Celsius)

#### temperature_c
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Celsius (°C)
- **Description**: Ambient air temperature
- **Example**: `22.5`, `-5.0`, `35.8`
- **Notes**: Primary temperature reading

#### wet_bulb_temp_c
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Celsius (°C)
- **Description**: Wet bulb temperature (evaporative cooling)
- **Example**: `18.2`
- **Notes**: Used for heat stress calculations

#### dew_point_c
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Celsius (°C)
- **Description**: Dew point temperature
- **Example**: `15.5`
- **Notes**: Temperature at which condensation forms

#### heat_index_c
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Celsius (°C)
- **Description**: Apparent temperature (heat + humidity)
- **Example**: `28.0`
- **Notes**: "Feels like" temperature in hot conditions

#### wind_chill_c
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Celsius (°C)
- **Description**: Apparent temperature (cold + wind)
- **Example**: `-12.0`
- **Notes**: "Feels like" temperature in cold conditions

---

### Humidity Fields

#### relative_humidity_pct
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Percent (%)
- **Description**: Relative humidity
- **Example**: `65.0`, `30.5`, `95.0`
- **Notes**: 0-100 range

---

### Pressure Fields (Metric - Hectopascals)

#### barometric_pressure_hpa
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Hectopascals (hPa)
- **Description**: Barometric pressure (adjusted to sea level)
- **Example**: `1013.25`, `1020.5`
- **Notes**: Standard for ballistic calculations

#### station_pressure_hpa
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Hectopascals (hPa)
- **Description**: Station pressure (actual, not adjusted)
- **Example**: `980.5`
- **Notes**: Actual pressure at measurement location

---

### Altitude Fields (Metric - Meters)

#### altitude_m
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Meters (m)
- **Description**: Altitude/elevation above sea level
- **Example**: `500.0`, `1200.5`
- **Notes**: From GPS or manual entry

#### density_altitude_m
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Meters (m)
- **Description**: Density altitude (performance altitude)
- **Example**: `1500.0`
- **Notes**: Critical for ballistic calculations

---

### Wind Fields (Metric - Meters per Second)

#### wind_speed_mps
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Meters per second (m/s)
- **Description**: Wind speed
- **Example**: `3.5`, `8.2`, `0.0`
- **Notes**: Total wind speed

#### crosswind_mps
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Meters per second (m/s)
- **Description**: Crosswind component (perpendicular to target)
- **Example**: `2.5`, `-1.8`
- **Notes**: Most important for shooting

#### headwind_mps
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Meters per second (m/s)
- **Description**: Headwind component (toward/away from target)
- **Example**: `1.5`, `-2.0` (tailwind)
- **Notes**: Positive = headwind, negative = tailwind

---

### Compass/Direction Fields

#### compass_magnetic_deg
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Degrees (°)
- **Description**: Magnetic compass heading
- **Example**: `45.0`, `180.0`, `270.5`
- **Notes**: 0-360 range, magnetic north

#### compass_true_deg
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Degrees (°)
- **Description**: True compass heading (adjusted for declination)
- **Example**: `50.0`, `185.0`
- **Notes**: 0-360 range, true north

---

### Additional Metadata Fields

#### data_type
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Type of data/reading
- **Example**: `"weather"`, `"environmental"`
- **Notes**: From CSV metadata

#### record_name
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Name of record in device
- **Example**: `"Range Session 1"`
- **Notes**: From CSV metadata

#### start_time
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Start time of recording session
- **Example**: `"2024-01-15 10:00:00"`
- **Notes**: From CSV metadata

#### duration
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Duration of recording session
- **Example**: `"01:30:00"`, `"30 minutes"`
- **Notes**: From CSV metadata

#### location_description
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Text description of location
- **Example**: `"North Range"`, `"Home"`
- **Notes**: User-entered or from device

#### location_address
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Physical address
- **Example**: `"123 Main St, City, State"`
- **Notes**: From device GPS or manual entry

#### location_coordinates
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: GPS coordinates
- **Example**: `"40.7128,-74.0060"` (lat,lon)
- **Notes**: From device GPS

#### notes
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Additional notes/comments
- **Example**: `"Windy conditions"`
- **Notes**: User-entered

---

## WeatherMeasurement Class Methods

### from_supabase_record()

Create a `WeatherMeasurement` from a Supabase database record.

**Signature**:
```python
@classmethod
def from_supabase_record(cls, record: dict) -> WeatherMeasurement
```

**Parameters**:
- `record` (dict): Dictionary from Supabase query result

**Returns**:
- `WeatherMeasurement`: Fully typed measurement instance

**Example**:
```python
record = {
    "id": "measurement-123",
    "user_id": "user-123",
    "weather_source_id": "source-123",
    "measurement_timestamp": "2024-01-15T10:00:00",
    "temperature_c": 22.5,
    "relative_humidity_pct": 65.0,
    ...
}

measurement = WeatherMeasurement.from_supabase_record(record)
```

**Notes**:
- Automatically converts timestamp strings to datetime objects
- Handles missing optional fields (sets to None)

---

### from_supabase_records()

Batch convert multiple Supabase records to `WeatherMeasurement` instances.

**Signature**:
```python
@classmethod
def from_supabase_records(cls, records: List[dict]) -> List[WeatherMeasurement]
```

**Parameters**:
- `records` (List[dict]): List of dictionaries from Supabase

**Returns**:
- `List[WeatherMeasurement]`: List of typed measurement instances

**Example**:
```python
records = [record1, record2, record3]
measurements = WeatherMeasurement.from_supabase_records(records)
```

---

## WeatherMeasurement Properties

### has_wind_data()

Check if measurement contains any wind-related data.

**Signature**:
```python
def has_wind_data(self) -> bool
```

**Returns**:
- `bool`: True if any wind field is populated

**Checks**:
- `wind_speed_mps`
- `crosswind_mps`
- `headwind_mps`
- `compass_magnetic_deg`
- `compass_true_deg`

**Example**:
```python
measurement = WeatherMeasurement(
    wind_speed_mps=3.5,
    compass_magnetic_deg=45.0,
    ...
)

if measurement.has_wind_data():
    print(f"Wind: {measurement.wind_speed_mps} m/s")
    print(f"Direction: {measurement.compass_magnetic_deg}°")
```

---

### has_location_data()

Check if measurement contains any location-related data.

**Signature**:
```python
def has_location_data(self) -> bool
```

**Returns**:
- `bool`: True if any location field is populated

**Checks**:
- `location_description`
- `location_address`
- `location_coordinates`

**Example**:
```python
measurement = WeatherMeasurement(
    location_description="North Range",
    location_coordinates="40.7128,-74.0060",
    ...
)

if measurement.has_location_data():
    print(f"Location: {measurement.location_description}")
    print(f"Coordinates: {measurement.location_coordinates}")
```

---

## Unit Conventions

### Metric (Internal Storage)

**All measurements stored in metric**:
- Temperature: Celsius (°C)
- Pressure: Hectopascals (hPa)
- Altitude: Meters (m)
- Wind Speed: Meters per second (m/s)
- Humidity: Percent (%)
- Direction: Degrees (°)

### Display Conversion

UI may convert for display based on user preference:
- Temperature: °C ↔ °F
- Pressure: hPa ↔ inHg ↔ mmHg
- Altitude: m ↔ ft
- Wind speed: m/s ↔ mph ↔ km/h ↔ knots
- Humidity: always % (no conversion)
- Direction: always ° (no conversion)

**Example conversions**:
```python
# Stored internally (metric)
measurement.temperature_c = 22.5  # Celsius
measurement.barometric_pressure_hpa = 1013.25  # Hectopascals
measurement.wind_speed_mps = 3.5  # Meters per second

# Display to user (if imperial preferred)
temp_f = measurement.temperature_c * 9/5 + 32  # 72.5°F
pressure_inhg = measurement.barometric_pressure_hpa * 0.02953  # 29.92 inHg
wind_mph = measurement.wind_speed_mps * 2.237  # 7.8 mph
```

---

## Field Validation

### Required Field Constraints

```python
# These must always be provided
id: str  # Non-empty UUID
user_id: str  # Non-empty user ID
weather_source_id: str  # Valid source UUID
measurement_timestamp: datetime  # Valid timestamp
uploaded_at: datetime  # Valid timestamp
```

### Optional Field Defaults

All weather measurement fields default to `None` if not provided. This allows:
- Partial data recording (e.g., temperature only)
- Different devices with different capabilities
- Manual entry with limited data

---

## Usage Example

### Complete Measurement Creation

```python
from weather.models import WeatherMeasurement
from datetime import datetime

# Create comprehensive measurement
measurement = WeatherMeasurement(
    id="measurement-123",
    user_id="user-123",
    weather_source_id="source-123",
    measurement_timestamp=datetime(2024, 1, 15, 10, 0, 0),
    uploaded_at=datetime(2024, 1, 15, 14, 30, 0),
    # Temperature
    temperature_c=22.5,
    dew_point_c=15.5,
    heat_index_c=24.0,
    # Humidity
    relative_humidity_pct=65.0,
    # Pressure
    barometric_pressure_hpa=1013.25,
    station_pressure_hpa=980.5,
    # Altitude
    altitude_m=500.0,
    density_altitude_m=650.0,
    # Wind
    wind_speed_mps=3.5,
    crosswind_mps=2.5,
    headwind_mps=1.5,
    compass_magnetic_deg=45.0,
    compass_true_deg=50.0,
    # Location
    location_description="North Range",
    location_coordinates="40.7128,-74.0060",
)

# Access fields
print(f"Temperature: {measurement.temperature_c}°C")
print(f"Pressure: {measurement.barometric_pressure_hpa} hPa")
print(f"Wind: {measurement.wind_speed_mps} m/s at {measurement.compass_magnetic_deg}°")

# Check for data
if measurement.has_wind_data():
    print(f"Crosswind: {measurement.crosswind_mps} m/s")

if measurement.has_location_data():
    print(f"Location: {measurement.location_description}")
```

---

## Next Steps

- [API Reference](api-reference.md) - Methods for working with weather data
- [Examples](examples.md) - Common usage patterns
- [Module README](README.md) - Overview and integration

---

**Model Version**: 1.0
**Location**: `weather/models.py`
**Database Tables**: `weather_source`, `weather_measurements`