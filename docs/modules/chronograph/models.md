# Chronograph Models Documentation

## Overview

The chronograph module uses three dataclass models:
- `ChronographSource`: Represents a chronograph device
- `ChronographSession`: Represents a shooting session with statistics
- `ChronographMeasurement`: Represents an individual shot measurement

All field values use **metric units** internally, following ChronoLog's metric system philosophy.

---

## ChronographSource

Dataclass representing a chronograph device (e.g., Garmin Xero, LabRadar).

**Location**: `chronograph/chronograph_source_models.py`

### Class Definition

```python
@dataclass
class ChronographSource:
    """Entity representing a chronograph device"""
    # ... fields ...
```

---

## Fields

### Identity Fields

#### id
- **Type**: `str`
- **Required**: Yes
- **Description**: UUID of the chronograph source
- **Example**: `"123e4567-e89b-12d3-a456-426614174000"`
- **Notes**: Auto-generated on creation

#### user_id
- **Type**: `str`
- **Required**: Yes
- **Description**: User ID of the owner
- **Example**: `"auth0|507f1f77bcf86cd799439011"`
- **Notes**: For user isolation - only owner can access this source

---

### Core Specification Fields

#### name
- **Type**: `str`
- **Required**: Yes
- **Description**: User-defined name for the chronograph source
- **Example**: `"My Garmin Xero"`, `"Range Chronograph"`
- **Notes**: Used for display and identification

#### source_type
- **Type**: `str`
- **Required**: No (default: "chronograph")
- **Description**: Type of chronograph source
- **Example**: `"chronograph"`, `"radar"`
- **Notes**: Reserved for future use; currently defaults to "chronograph"

---

### Device Information Fields

#### device_name
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Device name from CSV/import
- **Example**: `"Garmin Xero C1"`, `"LabRadar"`
- **Notes**: Often populated automatically during CSV import

#### make
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Manufacturer name
- **Example**: `"Garmin"`, `"LabRadar"`, `"MagnetoSpeed"`
- **Notes**: Used for device identification and display

#### model
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Device model number
- **Example**: `"Xero C1"`, `"XeroA1i"`, `"V3"`
- **Notes**: Specific model designation

#### serial_number
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Device serial number
- **Example**: `"G123456"`, `"LR789012"`
- **Notes**: Used for unique device identification during imports

---

### Metadata Fields

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

## Instance Methods

### display_name()

Get a user-friendly display name for the source.

**Signature**:
```python
def display_name(self) -> str
```

**Returns**:
- `str`: The source name

**Example**:
```python
source = ChronographSource(
    id="source-123",
    user_id="user-123",
    name="My Garmin Xero"
)

print(source.display_name())
# "My Garmin Xero"
```

---

### device_display()

Get a formatted device description with make, model, and serial number.

**Signature**:
```python
def device_display(self) -> str
```

**Returns**:
- `str`: Formatted device information

**Format**:
- If make and model: `"{make} {model}"`
- If only device_name: `"{device_name}"`
- If only model: `"{model}"`
- Otherwise: `"Unknown Device"`
- Appends serial number if available: `" (S/N: {serial_number})"`

**Examples**:
```python
source1 = ChronographSource(
    name="My Garmin",
    make="Garmin",
    model="Xero C1",
    serial_number="G123456"
)
print(source1.device_display())
# "Garmin Xero C1 (S/N: G123456)"

source2 = ChronographSource(
    name="My Device",
    device_name="Garmin Xero"
)
print(source2.device_display())
# "Garmin Xero"

source3 = ChronographSource(
    name="My Source",
    model="Xero C1"
)
print(source3.device_display())
# "Xero C1"
```

---

### short_display()

Get a short display combining name and device info for dropdowns/lists.

**Signature**:
```python
def short_display(self) -> str
```

**Returns**:
- `str`: Combined name and device info

**Format**: `"{name} - {device_display()}"`

**Example**:
```python
source = ChronographSource(
    name="My Garmin",
    make="Garmin",
    model="Xero C1",
    serial_number="G123456"
)

print(source.short_display())
# "My Garmin - Garmin Xero C1 (S/N: G123456)"
```

---

## Class Methods

### from_supabase_record()

Create a `ChronographSource` from a Supabase database record.

**Signature**:
```python
@classmethod
def from_supabase_record(cls, record: dict) -> ChronographSource
```

**Parameters**:
- `record` (dict): Dictionary from Supabase query result

**Returns**:
- `ChronographSource`: Fully typed source instance

**Example**:
```python
record = {
    "id": "source-123",
    "user_id": "user-123",
    "name": "My Garmin",
    "make": "Garmin",
    "model": "Xero C1",
    "serial_number": "G123456",
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-15T10:00:00"
}

source = ChronographSource.from_supabase_record(record)
```

---

### from_supabase_records()

Batch convert multiple Supabase records to `ChronographSource` instances.

**Signature**:
```python
@classmethod
def from_supabase_records(cls, records: List[dict]) -> List[ChronographSource]
```

**Parameters**:
- `records` (List[dict]): List of dictionaries from Supabase

**Returns**:
- `List[ChronographSource]`: List of typed source instances

**Example**:
```python
records = [record1, record2, record3]
sources = ChronographSource.from_supabase_records(records)
```

---

## ChronographSession

Dataclass representing a shooting session with calculated statistics.

**Location**: `chronograph/chronograph_session_models.py`

### Class Definition

```python
@dataclass
class ChronographSession:
    """Entity representing a chronograph session"""
    # ... fields ...
```

---

## Fields

### Identity Fields

#### id
- **Type**: `str`
- **Required**: Yes
- **Description**: UUID of the session
- **Example**: `"session-123"`
- **Notes**: Auto-generated on creation

#### user_id
- **Type**: `str`
- **Required**: Yes
- **Description**: User ID of the owner
- **Example**: `"auth0|user123"`
- **Notes**: For user isolation

---

### Core Session Fields

#### tab_name
- **Type**: `str`
- **Required**: Yes
- **Description**: Bullet type identifier (e.g., from Excel tab name)
- **Example**: `"168gr HPBT"`, `"175gr SMK"`, `"140gr ELD-M"`
- **Notes**: Used for filtering and grouping sessions

#### session_name
- **Type**: `str`
- **Required**: Yes
- **Description**: User-defined session name
- **Example**: `"Range Day 1"`, `"Load Development"`, `"Velocity Test"`
- **Notes**: Descriptive name for the session

#### datetime_local
- **Type**: `datetime`
- **Required**: Yes
- **Description**: When the session occurred (local time)
- **Example**: `datetime(2024, 1, 15, 10, 0, 0)`
- **Notes**: Used for filtering and sorting sessions

#### uploaded_at
- **Type**: `datetime`
- **Required**: Yes
- **Description**: When the session was uploaded to database
- **Example**: `datetime(2024, 1, 15, 10, 30, 0)`
- **Notes**: Auto-generated on creation

---

### Optional Session Fields

#### file_path
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: Path to the imported CSV/Excel file
- **Example**: `"user-123/garmin_xero_2024-01-15.csv"`
- **Notes**: Stored in Supabase Storage

#### chronograph_source_id
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: UUID of the chronograph source (device)
- **Example**: `"source-123"`
- **Notes**: Links session to specific chronograph device

#### created_at
- **Type**: `Optional[datetime]`
- **Required**: No
- **Description**: When session record was created
- **Example**: `datetime(2024, 1, 15, 10, 30, 0)`
- **Notes**: Auto-generated on creation

---

### Statistics Fields (Auto-calculated)

#### shot_count
- **Type**: `int`
- **Required**: No (default: 0)
- **Description**: Number of shots in the session
- **Example**: `10`, `20`, `5`
- **Notes**: Calculated from measurements

#### avg_speed_mps
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Meters per second (m/s)
- **Description**: Average velocity
- **Example**: `792.5`
- **Notes**: Mean of all shot velocities (metric)

#### std_dev_mps
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Meters per second (m/s)
- **Description**: Standard deviation of velocities
- **Example**: `1.2`
- **Notes**: Measure of velocity consistency

#### min_speed_mps
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Meters per second (m/s)
- **Description**: Minimum velocity in session
- **Example**: `790.5`
- **Notes**: Slowest shot

#### max_speed_mps
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Meters per second (m/s)
- **Description**: Maximum velocity in session
- **Example**: `794.5`
- **Notes**: Fastest shot

---

## Instance Methods

### display_name()

Get a display-friendly name for the session.

**Signature**:
```python
def display_name(self) -> str
```

**Returns**:
- `str`: Formatted display name

**Format**: `"{tab_name} - {datetime in YYYY-MM-DD HH:MM}"`

**Example**:
```python
session = ChronographSession(
    tab_name="168gr HPBT",
    datetime_local=datetime(2024, 1, 15, 10, 0, 0)
)

print(session.display_name())
# "168gr HPBT - 2024-01-15 10:00"
```

---

### bullet_display()

Get a display-friendly bullet description.

**Signature**:
```python
def bullet_display(self) -> str
```

**Returns**:
- `str`: Session name or "Unknown Session"

**Example**:
```python
session = ChronographSession(
    session_name="Range Day 1"
)

print(session.bullet_display())
# "Range Day 1"
```

---

### has_measurements()

Check if this session has any measurements.

**Signature**:
```python
def has_measurements(self) -> bool
```

**Returns**:
- `bool`: True if shot_count > 0

**Example**:
```python
session = ChronographSession(shot_count=10)
print(session.has_measurements())  # True

empty_session = ChronographSession(shot_count=0)
print(empty_session.has_measurements())  # False
```

---

### file_name()

Get just the filename from the file path.

**Signature**:
```python
def file_name(self) -> str
```

**Returns**:
- `str`: Filename or "N/A"

**Example**:
```python
session = ChronographSession(
    file_path="user-123/garmin_xero_2024-01-15.csv"
)

print(session.file_name())
# "garmin_xero_2024-01-15.csv"
```

---

## Class Methods

### from_supabase_record()

Create a `ChronographSession` from a Supabase database record.

**Signature**:
```python
@classmethod
def from_supabase_record(cls, record: dict) -> ChronographSession
```

**Parameters**:
- `record` (dict): Dictionary from Supabase query result

**Returns**:
- `ChronographSession`: Fully typed session instance

**Example**:
```python
record = {
    "id": "session-123",
    "user_id": "user-123",
    "tab_name": "168gr HPBT",
    "session_name": "Range Day 1",
    "datetime_local": "2024-01-15T10:00:00",
    "uploaded_at": "2024-01-15T10:30:00",
    "shot_count": 10,
    "avg_speed_mps": 792.5,
    "std_dev_mps": 1.2
}

session = ChronographSession.from_supabase_record(record)
```

---

### from_supabase_records()

Batch convert multiple Supabase records to `ChronographSession` instances.

**Signature**:
```python
@classmethod
def from_supabase_records(cls, records: List[dict]) -> List[ChronographSession]
```

**Parameters**:
- `records` (List[dict]): List of dictionaries from Supabase

**Returns**:
- `List[ChronographSession]`: List of typed session instances

---

## ChronographMeasurement

Dataclass representing a single shot measurement.

**Location**: `chronograph/chronograph_session_models.py`

### Class Definition

```python
@dataclass
class ChronographMeasurement:
    """Entity representing a single chronograph measurement"""
    # ... fields ...
```

---

## Fields

### Identity Fields

#### id
- **Type**: `str`
- **Required**: Yes
- **Description**: UUID of the measurement
- **Example**: `"measurement-123"`
- **Notes**: Auto-generated on creation

#### user_id
- **Type**: `str`
- **Required**: Yes
- **Description**: User ID of the owner
- **Example**: `"auth0|user123"`
- **Notes**: For user isolation

#### chrono_session_id
- **Type**: `str`
- **Required**: Yes
- **Description**: UUID of the parent session
- **Example**: `"session-123"`
- **Notes**: Foreign key to chrono_sessions table

---

### Shot Identification Fields

#### shot_number
- **Type**: `int`
- **Required**: Yes
- **Description**: Shot sequence number within session
- **Example**: `1`, `2`, `3`, `10`
- **Notes**: Used for ordering measurements

#### datetime_local
- **Type**: `datetime`
- **Required**: Yes
- **Description**: When the shot was taken (local time)
- **Example**: `datetime(2024, 1, 15, 10, 0, 0)`
- **Notes**: Precise timestamp for each shot

---

### Velocity Fields (Metric)

#### speed_mps
- **Type**: `float`
- **Required**: Yes
- **Unit**: Meters per second (m/s)
- **Description**: Projectile velocity
- **Example**: `792.5` (approximately 2600 fps)
- **Notes**: **Always metric** - stored and used in m/s, not fps

#### delta_avg_mps
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Meters per second (m/s)
- **Description**: Difference from session average velocity
- **Example**: `+1.5`, `-0.8`
- **Notes**: Can be positive or negative

---

### Energy Fields (Metric)

#### ke_j
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Joules (J)
- **Description**: Kinetic energy of the projectile
- **Example**: `3500.0` (approximately 2580 ft-lbs)
- **Notes**: **Always metric** - stored in joules, not ft-lbs

#### power_factor_kgms
- **Type**: `Optional[float]`
- **Required**: No
- **Unit**: Kilogram-meters per second (kg*m/s)
- **Description**: Power factor (bullet weight * velocity)
- **Example**: `42.5`
- **Notes**: **Always metric** - not traditional grain*fps power factor

---

### Shot Condition Flags

#### clean_bore
- **Type**: `Optional[bool]`
- **Required**: No
- **Description**: Shot taken with clean (freshly cleaned) bore
- **Example**: `True`, `False`, `None`
- **Notes**: First shot after cleaning

#### cold_bore
- **Type**: `Optional[bool]`
- **Required**: No
- **Description**: Shot taken with cold (not warmed up) bore
- **Example**: `True`, `False`, `None`
- **Notes**: First shot of the day or after cooling

---

### Notes Field

#### shot_notes
- **Type**: `Optional[str]`
- **Required**: No
- **Description**: User notes for this specific shot
- **Example**: `"Flyer - flinched"`, `"Good trigger pull"`, `"Wind gust"`
- **Notes**: Free-form text for shot-specific observations

---

## Class Methods

### from_supabase_record()

Create a `ChronographMeasurement` from a Supabase database record.

**Signature**:
```python
@classmethod
def from_supabase_record(cls, record: dict) -> ChronographMeasurement
```

**Parameters**:
- `record` (dict): Dictionary from Supabase query result

**Returns**:
- `ChronographMeasurement`: Fully typed measurement instance

**Example**:
```python
record = {
    "id": "measurement-123",
    "user_id": "user-123",
    "chrono_session_id": "session-123",
    "shot_number": 1,
    "speed_mps": 792.5,
    "datetime_local": "2024-01-15T10:00:00",
    "ke_j": 3500.0,
    "power_factor_kgms": 42.5,
    "cold_bore": True
}

measurement = ChronographMeasurement.from_supabase_record(record)
```

---

### from_supabase_records()

Batch convert multiple Supabase records to `ChronographMeasurement` instances.

**Signature**:
```python
@classmethod
def from_supabase_records(cls, records: List[dict]) -> List[ChronographMeasurement]
```

**Parameters**:
- `records` (List[dict]): List of dictionaries from Supabase

**Returns**:
- `List[ChronographMeasurement]`: List of typed measurement instances

---

## Unit Conventions

### Metric (Internal Storage)

**Always metric**:
- Velocity: meters per second (m/s) - NOT fps
- Energy: joules (J) - NOT ft-lbs
- Power factor: kg*m/s - NOT grain*fps
- All calculations in metric

### Display Conversion

UI may convert for display based on user preference:
- Velocity: m/s ↔ fps (1 m/s = 3.28084 fps)
- Energy: joules ↔ ft-lbs (1 J = 0.737562 ft-lbs)
- Power factor: may show traditional grain*fps equivalent

**Example conversions**:
```python
# Internal storage (metric)
speed_mps = 792.5  # m/s

# Display conversion (if user prefers imperial)
speed_fps = speed_mps * 3.28084  # 2600 fps

# Always store metric
measurement = ChronographMeasurement(
    speed_mps=792.5  # m/s, not fps
)
```

---

## Field Validation

### Required Field Constraints

```python
# ChronographSource - required
id: str  # Non-empty UUID
user_id: str  # Non-empty user ID
name: str  # Non-empty name

# ChronographSession - required
id: str  # Non-empty UUID
user_id: str  # Non-empty user ID
tab_name: str  # Non-empty bullet type
session_name: str  # Non-empty session name
datetime_local: datetime  # Valid datetime
uploaded_at: datetime  # Valid datetime

# ChronographMeasurement - required
id: str  # Non-empty UUID
user_id: str  # Non-empty user ID
chrono_session_id: str  # Non-empty session UUID
shot_number: int  # > 0
speed_mps: float  # > 0 (velocity in m/s)
datetime_local: datetime  # Valid datetime
```

### Optional Field Defaults

```python
# ChronographSource - optional
device_name: Optional[str] = None
make: Optional[str] = None
model: Optional[str] = None
serial_number: Optional[str] = None
created_at: Optional[datetime] = None
updated_at: Optional[datetime] = None

# ChronographSession - optional
file_path: Optional[str] = None
chronograph_source_id: Optional[str] = None
shot_count: int = 0
avg_speed_mps: Optional[float] = None
std_dev_mps: Optional[float] = None
min_speed_mps: Optional[float] = None
max_speed_mps: Optional[float] = None
created_at: Optional[datetime] = None

# ChronographMeasurement - optional
delta_avg_mps: Optional[float] = None
ke_j: Optional[float] = None
power_factor_kgms: Optional[float] = None
clean_bore: Optional[bool] = None
cold_bore: Optional[bool] = None
shot_notes: Optional[str] = None
```

---

## Usage Examples

### Complete Source Creation

```python
from chronograph.chronograph_source_models import ChronographSource

source = ChronographSource(
    id="source-123",
    user_id="auth0|user123",
    name="My Garmin Xero",
    source_type="chronograph",
    device_name="Garmin Xero C1",
    make="Garmin",
    model="Xero C1",
    serial_number="G123456",
    created_at=datetime.now(),
    updated_at=datetime.now()
)

print(source.display_name())
# "My Garmin Xero"

print(source.device_display())
# "Garmin Xero C1 (S/N: G123456)"

print(source.short_display())
# "My Garmin Xero - Garmin Xero C1 (S/N: G123456)"
```

---

### Complete Session Creation

```python
from chronograph.chronograph_session_models import ChronographSession

session = ChronographSession(
    id="session-123",
    user_id="auth0|user123",
    tab_name="168gr HPBT",
    session_name="Range Day 1",
    datetime_local=datetime(2024, 1, 15, 10, 0, 0),
    uploaded_at=datetime(2024, 1, 15, 10, 30, 0),
    file_path="user-123/garmin_xero_2024-01-15.csv",
    chronograph_source_id="source-123",
    shot_count=10,
    avg_speed_mps=792.5,
    std_dev_mps=1.2,
    min_speed_mps=790.5,
    max_speed_mps=794.5,
    created_at=datetime.now()
)

print(session.display_name())
# "168gr HPBT - 2024-01-15 10:00"

print(f"Average: {session.avg_speed_mps} m/s")
# "Average: 792.5 m/s"

print(f"SD: {session.std_dev_mps} m/s")
# "SD: 1.2 m/s"

print(f"ES: {session.max_speed_mps - session.min_speed_mps} m/s")
# "ES: 4.0 m/s"
```

---

### Complete Measurement Creation

```python
from chronograph.chronograph_session_models import ChronographMeasurement

measurement = ChronographMeasurement(
    id="measurement-123",
    user_id="auth0|user123",
    chrono_session_id="session-123",
    shot_number=1,
    speed_mps=792.5,  # m/s (NOT fps)
    datetime_local=datetime(2024, 1, 15, 10, 0, 0),
    delta_avg_mps=0.0,
    ke_j=3500.0,  # joules (NOT ft-lbs)
    power_factor_kgms=42.5,  # kg*m/s (NOT grain*fps)
    clean_bore=False,
    cold_bore=True,
    shot_notes="Good shot, slight crosswind"
)

print(f"Shot {measurement.shot_number}: {measurement.speed_mps} m/s")
# "Shot 1: 792.5 m/s"

print(f"Energy: {measurement.ke_j} J")
# "Energy: 3500.0 J"
```

---

## Next Steps

- [API Reference](api-reference.md) - Methods for working with chronograph data
- [Examples](examples.md) - Common usage patterns
- [Module README](README.md) - Overview and integration

---

**Model Version**: 1.0
**Location**: `chronograph/chronograph_source_models.py`, `chronograph/chronograph_session_models.py`
**Database Tables**: `chronograph_sources`, `chrono_sessions`, `chrono_measurements`