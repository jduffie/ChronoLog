# Weather API Reference

## Overview

The Weather API provides type-safe access to weather sources (meters/devices) and measurements. This API follows the `WeatherAPIProtocol` defined in `weather/protocols.py`.

All API methods are UI-agnostic and return strongly-typed `WeatherSource` and `WeatherMeasurement` instances.

## API Contract

```python
from weather.protocols import WeatherAPIProtocol
from weather.models import WeatherSource, WeatherMeasurement
```

The `WeatherAPIProtocol` defines the complete API contract that all implementations must follow.

---

## Weather Source Operations

These methods manage weather sources (meters/devices) for individual users.

### get_all_sources()

Get all weather sources for a user.

**Signature**:
```python
def get_all_sources(self, user_id: str) -> List[WeatherSource]
```

**Parameters**:
- `user_id` (str): User identifier

**Returns**:
- `List[WeatherSource]`: List of all sources owned by user, ordered by name
- Empty list if no sources found

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = WeatherAPI(supabase_client)
sources = api.get_all_sources("user-123")

for source in sources:
    print(source.display_name())
    # My Kestrel
    # Range Meter
```

**Notes**:
- Results are user-scoped (only returns sources owned by user)
- Ordered alphabetically by name for consistent display
- Returns empty list, not error, if user has no sources

---

### get_source_by_id()

Get a specific weather source by its UUID.

**Signature**:
```python
def get_source_by_id(
    self, source_id: str, user_id: str
) -> Optional[WeatherSource]
```

**Parameters**:
- `source_id` (str): Weather source UUID
- `user_id` (str): User identifier (for access control)

**Returns**:
- `WeatherSource`: Source if found and owned by user
- `None`: If source not found or not owned by user

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = WeatherAPI(supabase_client)
source = api.get_source_by_id("source-123", "user-123")

if source:
    print(source.device_display())
    # Kestrel 5700 Elite (S/N: K123456)
else:
    print("Source not found or access denied")
```

**Notes**:
- Returns `None` rather than raising exception if not found
- Enforces user isolation (only returns if owned by user)
- User must own the source to retrieve it

---

### get_source_by_name()

Get a weather source by name.

**Signature**:
```python
def get_source_by_name(
    self, user_id: str, name: str
) -> Optional[WeatherSource]
```

**Parameters**:
- `user_id` (str): User identifier
- `name` (str): Source name to search for (exact match, case-sensitive)

**Returns**:
- `WeatherSource`: Source if found
- `None`: If no source with that name exists for user

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = WeatherAPI(supabase_client)
source = api.get_source_by_name("user-123", "My Kestrel")

if source:
    print(f"Found: {source.id}")
else:
    print("No source with that name")
```

**Notes**:
- Name matching is exact and case-sensitive
- Scoped to user (different users can have sources with same name)
- Useful for checking if name exists before creating source

---

### create_source()

Create a new weather source with auto-generated ID and timestamps.

**Signature**:
```python
def create_source(
    self, source_data: dict, user_id: str
) -> WeatherSource
```

**Parameters**:
- `source_data` (dict): Dictionary containing source information (see below)
- `user_id` (str): User identifier

**Required fields**:
- `name` (str): User-defined name for the source

**Optional fields**:
- `device_name` (str): Device name from CSV/import
- `make` (str): Manufacturer (e.g., "Kestrel")
- `model` (str): Model number (e.g., "5700 Elite")
- `serial_number` (str): Device serial number

**Returns**:
- `WeatherSource`: Created source with generated ID and timestamps

**Raises**:
- `Exception`: If creation fails

**Example**:
```python
api = WeatherAPI(supabase_client)

source_data = {
    "name": "My Kestrel",
    "device_name": "Kestrel 5700",
    "make": "Kestrel",
    "model": "5700 Elite",
    "serial_number": "K123456"
}

source = api.create_source(source_data, "user-123")
print(f"Created source: {source.id}")
print(source.short_display())
# My Kestrel - Kestrel 5700 Elite (S/N: K123456)
```

**Notes**:
- ID is auto-generated (UUID)
- Timestamps (created_at, updated_at) are auto-generated
- source_type defaults to "meter"
- All device fields are optional (can create minimal source with just name)

---

### update_source()

Update an existing weather source with auto-updated timestamp.

**Signature**:
```python
def update_source(
    self, source_id: str, updates: dict, user_id: str
) -> WeatherSource
```

**Parameters**:
- `source_id` (str): Weather source UUID
- `updates` (dict): Dictionary of fields to update
- `user_id` (str): User identifier (for access control)

**Returns**:
- `WeatherSource`: Updated source

**Raises**:
- `Exception`: If source not found or not owned by user
- `Exception`: If update fails

**Example**:
```python
api = WeatherAPI(supabase_client)

updates = {
    "name": "Range Kestrel",
    "make": "Kestrel"
}

source = api.update_source("source-123", updates, "user-123")
print(f"Updated: {source.name}")
```

**Notes**:
- updated_at timestamp is automatically set
- Partial updates supported (only update specified fields)
- User must own source to update it
- Cannot update id or user_id

---

### delete_source()

Delete a weather source and all its measurements.

**Signature**:
```python
def delete_source(self, source_id: str, user_id: str) -> bool
```

**Parameters**:
- `source_id` (str): Weather source UUID
- `user_id` (str): User identifier (for access control)

**Returns**:
- `bool`: True if deleted successfully

**Raises**:
- `Exception`: If deletion fails

**Example**:
```python
api = WeatherAPI(supabase_client)

success = api.delete_source("source-123", "user-123")
if success:
    print("Source and all measurements deleted")
```

**Notes**:
- Cascades to delete all associated measurements
- No undo - deletion is permanent
- User must own source to delete it
- Returns True even if source didn't exist (idempotent)

---

### create_or_get_source_from_device_info()

Create or retrieve existing weather source from device information.

**Signature**:
```python
def create_or_get_source_from_device_info(
    self,
    user_id: str,
    device_name: str,
    device_model: str,
    serial_number: str,
) -> WeatherSource
```

**Parameters**:
- `user_id` (str): User identifier
- `device_name` (str): Device name from CSV/import
- `device_model` (str): Device model from CSV/import
- `serial_number` (str): Device serial number from CSV/import

**Returns**:
- `WeatherSource`: Existing or newly created source

**Raises**:
- `Exception`: If creation/retrieval fails

**Example**:
```python
api = WeatherAPI(supabase_client)

# Called during CSV import
source = api.create_or_get_source_from_device_info(
    "user-123",
    "Kestrel 5700",
    "5700 Elite",
    "K123456"
)

print(f"Using source: {source.id}")
# Either found existing or created new
```

**Notes**:
- Intelligent device identification:
  1. First searches by serial_number
  2. If not found, searches by generated name
  3. If still not found, creates new source
- Generated name format: "{device_name} ({last_4_serial})"
- Prevents duplicate sources during repeated imports
- Updates device info if source exists but lacks details

---

## Weather Measurement Operations

These methods manage weather measurements for individual users.

### get_measurements_for_source()

Get all measurements for a specific weather source.

**Signature**:
```python
def get_measurements_for_source(
    self, source_id: str, user_id: str
) -> List[WeatherMeasurement]
```

**Parameters**:
- `source_id` (str): Weather source UUID
- `user_id` (str): User identifier (for access control)

**Returns**:
- `List[WeatherMeasurement]`: All measurements for source, ordered by timestamp
- Empty list if no measurements found

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = WeatherAPI(supabase_client)

measurements = api.get_measurements_for_source(
    "source-123", "user-123"
)

for m in measurements:
    print(f"{m.measurement_timestamp}: {m.temperature_c}°C")
    # 2024-01-15 10:00:00: 22.5°C
    # 2024-01-15 10:01:00: 22.6°C
```

**Notes**:
- Results are ordered chronologically by measurement_timestamp
- User must own the source
- Returns empty list if no measurements, not an error

---

### get_all_measurements()

Get all weather measurements for a user across all sources.

**Signature**:
```python
def get_all_measurements(
    self, user_id: str, limit: Optional[int] = None
) -> List[WeatherMeasurement]
```

**Parameters**:
- `user_id` (str): User identifier
- `limit` (Optional[int]): Maximum number of measurements to return

**Returns**:
- `List[WeatherMeasurement]`: All measurements for user, ordered by timestamp (desc)
- Empty list if no measurements found

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = WeatherAPI(supabase_client)

# Get last 100 measurements
recent = api.get_all_measurements("user-123", limit=100)

# Get all measurements (no limit)
all_measurements = api.get_all_measurements("user-123")
```

**Notes**:
- Results ordered by timestamp descending (newest first)
- Limit is optional (returns all if not specified)
- Useful for recent measurements or pagination

---

### filter_measurements()

Get filtered weather measurements with optional filters.

**Signature**:
```python
def filter_measurements(
    self,
    user_id: str,
    source_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[WeatherMeasurement]
```

**Parameters**:
- `user_id` (str): User identifier
- `source_id` (Optional[str]): Filter by specific source
- `start_date` (Optional[str]): Start date filter (ISO format)
- `end_date` (Optional[str]): End date filter (ISO format)

**Returns**:
- `List[WeatherMeasurement]`: Filtered measurements, ordered by timestamp (desc)
- Empty list if no matches

**Raises**:
- `Exception`: If database query fails

**Examples**:
```python
api = WeatherAPI(supabase_client)

# Filter by source
source_measurements = api.filter_measurements(
    "user-123",
    source_id="source-123"
)

# Filter by date range
january_measurements = api.filter_measurements(
    "user-123",
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59"
)

# Combined filters
specific = api.filter_measurements(
    "user-123",
    source_id="source-123",
    start_date="2024-01-15T00:00:00",
    end_date="2024-01-15T23:59:59"
)

# No filters (all measurements)
all_measurements = api.filter_measurements("user-123")
```

**Notes**:
- All filter parameters are optional
- Multiple filters are combined with AND logic
- Date filters use ISO 8601 format
- Results ordered by timestamp descending (newest first)

---

### create_measurement()

Create a new weather measurement with auto-generated ID and timestamp.

**Signature**:
```python
def create_measurement(
    self, measurement_data: dict, user_id: str
) -> WeatherMeasurement
```

**Parameters**:
- `measurement_data` (dict): Dictionary containing measurement data (see below)
- `user_id` (str): User identifier

**Required fields**:
- `weather_source_id` (str): UUID of weather source
- `measurement_timestamp` (str): ISO timestamp of when reading was taken

**Optional fields (all metric units)**:
- `temperature_c` (float): Temperature in Celsius
- `wet_bulb_temp_c` (float): Wet bulb temperature
- `relative_humidity_pct` (float): Relative humidity (%)
- `barometric_pressure_hpa` (float): Barometric pressure (hPa)
- `station_pressure_hpa` (float): Station pressure (hPa)
- `altitude_m` (float): Altitude (meters)
- `density_altitude_m` (float): Density altitude (meters)
- `wind_speed_mps` (float): Wind speed (m/s)
- `crosswind_mps` (float): Crosswind component (m/s)
- `headwind_mps` (float): Headwind component (m/s)
- `compass_magnetic_deg` (float): Magnetic heading (degrees)
- `compass_true_deg` (float): True heading (degrees)
- `dew_point_c` (float): Dew point temperature
- `heat_index_c` (float): Heat index
- `wind_chill_c` (float): Wind chill
- `file_path` (str): Path to source file
- Plus additional metadata fields (see models.md)

**Returns**:
- `WeatherMeasurement`: Created measurement with generated ID

**Raises**:
- `Exception`: If creation fails
- `Exception`: If source doesn't exist or not owned by user

**Example**:
```python
api = WeatherAPI(supabase_client)

measurement_data = {
    "weather_source_id": "source-123",
    "measurement_timestamp": "2024-01-15T10:00:00",
    "temperature_c": 22.5,
    "relative_humidity_pct": 65.0,
    "barometric_pressure_hpa": 1013.25,
    "wind_speed_mps": 3.5
}

measurement = api.create_measurement(measurement_data, "user-123")
print(f"Created measurement: {measurement.id}")
print(f"Temperature: {measurement.temperature_c}°C")
```

**Notes**:
- ID is auto-generated (UUID)
- uploaded_at timestamp is auto-generated
- All weather fields are optional (can record partial data)
- All measurements stored in metric units
- User must own the weather source

---

### create_measurements_batch()

Create multiple weather measurements in a single batch operation.

**Signature**:
```python
def create_measurements_batch(
    self, measurements_data: List[dict], user_id: str
) -> List[WeatherMeasurement]
```

**Parameters**:
- `measurements_data` (List[dict]): List of measurement data dictionaries
- `user_id` (str): User identifier

**Returns**:
- `List[WeatherMeasurement]`: List of created measurements

**Raises**:
- `Exception`: If batch creation fails

**Example**:
```python
api = WeatherAPI(supabase_client)

batch_data = [
    {
        "weather_source_id": "source-123",
        "measurement_timestamp": "2024-01-15T10:00:00",
        "temperature_c": 22.5,
        "barometric_pressure_hpa": 1013.25
    },
    {
        "weather_source_id": "source-123",
        "measurement_timestamp": "2024-01-15T10:01:00",
        "temperature_c": 22.6,
        "barometric_pressure_hpa": 1013.20
    },
    {
        "weather_source_id": "source-123",
        "measurement_timestamp": "2024-01-15T10:02:00",
        "temperature_c": 22.7,
        "barometric_pressure_hpa": 1013.18
    },
]

measurements = api.create_measurements_batch(batch_data, "user-123")
print(f"Created {len(measurements)} measurements")
```

**Notes**:
- More efficient than creating measurements one at a time
- All measurements use same uploaded_at timestamp
- IDs are auto-generated for each measurement
- Typical use: CSV import with many measurements
- All-or-nothing operation (transaction)

---

### measurement_exists()

Check if a measurement already exists for a source at a specific timestamp.

**Signature**:
```python
def measurement_exists(
    self, user_id: str, source_id: str, measurement_timestamp: str
) -> bool
```

**Parameters**:
- `user_id` (str): User identifier
- `source_id` (str): Weather source UUID
- `measurement_timestamp` (str): Timestamp to check (ISO format)

**Returns**:
- `bool`: True if measurement exists, False otherwise

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = WeatherAPI(supabase_client)

exists = api.measurement_exists(
    "user-123",
    "source-123",
    "2024-01-15T10:00:00"
)

if not exists:
    # Safe to create measurement
    api.create_measurement(measurement_data, user_id)
else:
    print("Measurement already exists, skipping")
```

**Notes**:
- Useful for preventing duplicate imports
- Checks user_id, source_id, and timestamp together
- Called before creating measurements during CSV import
- Fast check (uses database index)

---

## Type Safety

All API methods use type hints for compile-time checking:

```python
# IDE autocomplete works
api = WeatherAPI(supabase_client)
source = api.get_source_by_id("source-123", "user-123")

if source:
    # Type checker knows source is WeatherSource
    name = source.name  # ✓ Valid
    device = source.device_display()  # ✓ Valid
    invalid = source.nonexistent_field  # ✗ Type error

# Return types are enforced
sources: List[WeatherSource] = api.get_all_sources("user-123")  # ✓ Correct
sources: List[dict] = api.get_all_sources("user-123")  # ✗ Type error
```

---

## Error Handling

All API methods follow consistent error handling:

**Returns None** (not found, no error):
- `get_source_by_id()` returns `None` if source not found or not owned
- `get_source_by_name()` returns `None` if no source with that name

**Returns empty list** (no matches, no error):
- `get_all_sources()` returns `[]` if user has no sources
- `get_measurements_for_source()` returns `[]` if no measurements
- `filter_measurements()` returns `[]` if no matches

**Raises Exception** (actual errors):
- Database connection failures
- Invalid parameters
- Access control violations (wrong user_id)
- Constraint violations (FK violations)

**Example**:
```python
api = WeatherAPI(supabase_client)

# Handle not found gracefully
source = api.get_source_by_id("nonexistent-id", "user-123")
if not source:
    print("Source not found")  # Not an error

# Handle actual errors
try:
    sources = api.get_all_sources("user-123")
except Exception as e:
    print(f"Database error: {e}")  # Actual error
```

---

## User Isolation

All operations enforce user isolation:

- Sources are user-scoped (can only access own sources)
- Measurements are user-scoped (can only access own measurements)
- All methods require user_id parameter for access control
- Queries automatically filter by user_id

**Example**:
```python
# User A creates a source
source_a = api.create_source({"name": "My Meter"}, "user-a")

# User B cannot access User A's source
source = api.get_source_by_id(source_a.id, "user-b")
# Returns None (access denied)

# User B can create their own source with same name
source_b = api.create_source({"name": "My Meter"}, "user-b")
# Different source, same name - OK
```

---

## Next Steps

- [Models Documentation](models.md) - Detailed field specifications
- [Examples](examples.md) - Common usage patterns
- [Module README](README.md) - Overview and integration

---

**API Version**: 1.0
**Protocol**: `weather.protocols.WeatherAPIProtocol`
**Implementation**: `weather.api.WeatherAPI`