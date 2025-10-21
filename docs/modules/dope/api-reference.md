# DOPE API Reference

## Overview

The DOPE API provides type-safe access to ballistic session management and measurement tracking. This API follows the `DopeAPIProtocol` defined in `dope/protocols.py`.

All API methods are UI-agnostic and return strongly-typed `DopeSessionModel` and `DopeMeasurementModel` instances.

DOPE is the convergence point - it aggregates data from chronograph, cartridges (with bullets), rifles, weather, and ranges into unified sessions.

## API Contract

```python
from dope.protocols import DopeAPIProtocol
from dope.models import DopeSessionModel, DopeMeasurementModel
from dope.filters import DopeSessionFilter
```

The `DopeAPIProtocol` defines the complete API contract that all implementations must follow.

---

## Session Management

### get_sessions_for_user()

Get all DOPE sessions for a specific user with joined data from all source modules.

**Signature**:
```python
def get_sessions_for_user(self, user_id: str) -> List[DopeSessionModel]
```

**Parameters**:
- `user_id` (str): Auth0 user ID to filter sessions

**Returns**:
- `List[DopeSessionModel]`: List of sessions ordered by created_at desc
- Empty list if no sessions found
- Each session contains denormalized data from 6+ tables

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = DopeAPI(supabase_client)
sessions = api.get_sessions_for_user("auth0|123456")

print(f"Total sessions: {len(sessions)}")

for session in sessions:
    print(f"{session.session_name}")
    print(f"  Cartridge: {session.cartridge_make} {session.cartridge_model}")
    print(f"  Bullet: {session.bullet_make} {session.bullet_model} {session.bullet_weight}gr")
    print(f"  Rifle: {session.rifle_name}")
    print(f"  Avg Velocity: {session.speed_mps_avg} m/s")
```

**Notes**:
- Performs complex 6-table JOIN for complete data
- Returns denormalized sessions for performance
- All user-owned data is user_id filtered for security
- Admin data (bullets, cartridges) is globally accessible

---

### get_session_by_id()

Get a specific DOPE session by ID with complete joined data.

**Signature**:
```python
def get_session_by_id(
    self, session_id: str, user_id: str
) -> Optional[DopeSessionModel]
```

**Parameters**:
- `session_id` (str): UUID of the DOPE session
- `user_id` (str): Auth0 user ID (security check)

**Returns**:
- `DopeSessionModel`: Session if found and owned by user
- `None`: If session not found or not owned by user

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = DopeAPI(supabase_client)
session = api.get_session_by_id("123e4567-...", "auth0|123456")

if session:
    print(f"Session: {session.display_name}")
    print(f"Rifle: {session.rifle_name} ({session.rifle_barrel_length_cm}cm barrel)")
    print(f"Range: {session.range_name} at {session.range_distance_m}m")
    print(f"Weather: {session.temperature_c_median}°C")
else:
    print("Session not found or access denied")
```

**Notes**:
- Returns `None` rather than raising exception if not found
- Security enforced: user must own the session
- Complete denormalized data from all sources

---

### create_session()

Create a new DOPE session with automatic measurement creation from chronograph data.

**Signature**:
```python
def create_session(
    self,
    session_data: Dict[str, Any],
    user_id: str,
    auto_create_measurements: bool = True
) -> DopeSessionModel
```

**Parameters**:
- `session_data` (Dict[str, Any]): Session fields (metric units)
- `user_id` (str): Auth0 user ID (owner of session)
- `auto_create_measurements` (bool): If True, copy chronograph measurements to DOPE measurements

**Required fields in session_data**:
- `session_name` (str): Name of the session
- `cartridge_id` (str): FK to cartridges table
- `rifle_id` (str): FK to rifles table (user-owned)
- `chrono_session_id` (str): FK to chrono_sessions table (user-owned)
- `range_submission_id` (str): FK to ranges_submissions table

**Optional fields**:
- `weather_source_id` (str): FK to weather_source table (user-owned)
- `notes` (str): Session notes

**Returns**:
- `DopeSessionModel`: Created session with generated ID and joined data

**Raises**:
- `ValueError`: If required fields missing or invalid
- `Exception`: If creation fails
- `Exception`: If user doesn't own referenced resources

**Example**:
```python
api = DopeAPI(supabase_client)

session_data = {
    "session_name": "308 Win @ 100m - Morning Session",
    "chrono_session_id": "chrono-uuid",
    "cartridge_id": "cartridge-uuid",
    "rifle_id": "rifle-uuid",
    "range_submission_id": "range-uuid",
    "weather_source_id": "weather-uuid",  # Optional
    "notes": "Testing new load, excellent conditions"
}

session = api.create_session(session_data, "auth0|123456")

print(f"Created session: {session.id}")
print(f"Start time: {session.start_time}")
print(f"End time: {session.end_time}")
print(f"Velocity stats: {session.speed_mps_avg}±{session.speed_mps_std_dev} m/s")
```

**Notes**:
- `start_time` and `end_time` automatically pulled from chronograph session
- Velocity statistics (min/max/avg/SD) calculated from chronograph measurements
- If `auto_create_measurements=True`, chronograph measurements are copied to dope_measurements
- Validates user ownership of rifle, chronograph session, weather source
- Cartridge and bullet data joined automatically (admin-owned, global)

---

### update_session()

Update an existing DOPE session.

**Signature**:
```python
def update_session(
    self,
    session_id: str,
    session_data: Dict[str, Any],
    user_id: str
) -> Optional[DopeSessionModel]
```

**Parameters**:
- `session_id` (str): UUID of session to update
- `session_data` (Dict[str, Any]): Fields to update (metric units)
- `user_id` (str): Auth0 user ID (security check)

**Returns**:
- `DopeSessionModel`: Updated session if successful
- `None`: If session not found or not owned by user

**Raises**:
- `Exception`: If update fails

**Example**:
```python
api = DopeAPI(supabase_client)

update_data = {
    "notes": "Windy conditions, groups opened up",
    "weather_source_id": "new-weather-uuid"
}

session = api.update_session(session_id, update_data, "auth0|123456")

if session:
    print(f"Updated: {session.session_name}")
else:
    print("Session not found or access denied")
```

**Notes**:
- Can update any field except `id`, `user_id`, `created_at`
- `start_time` and `end_time` cannot be manually updated (derived from chronograph)
- If `chrono_session_id` is updated, timestamps are automatically recalculated
- If `weather_source_id` is changed, all median weather values are cleared
- Partial updates supported

---

### delete_session()

Delete a DOPE session and all its measurements.

**Signature**:
```python
def delete_session(self, session_id: str, user_id: str) -> bool
```

**Parameters**:
- `session_id` (str): UUID of session to delete
- `user_id` (str): Auth0 user ID (security check)

**Returns**:
- `bool`: True if deleted, False if not found or not owned

**Raises**:
- `Exception`: If delete fails

**Example**:
```python
api = DopeAPI(supabase_client)

deleted = api.delete_session(session_id, "auth0|123456")

if deleted:
    print("Session deleted successfully")
else:
    print("Session not found or access denied")
```

**Notes**:
- Cascade deletes all dope_measurements for this session
- Does NOT delete source data (chronograph, rifle, weather, range)
- No undo - deletion is permanent
- User must own the session

---

### delete_sessions_bulk()

Delete multiple DOPE sessions in bulk operation.

**Signature**:
```python
def delete_sessions_bulk(
    self, session_ids: List[str], user_id: str
) -> Dict[str, Any]
```

**Parameters**:
- `session_ids` (List[str]): List of session UUIDs to delete
- `user_id` (str): Auth0 user ID (security check)

**Returns**:
- `Dict[str, Any]` with keys:
  - `deleted_count` (int): Number of sessions successfully deleted
  - `failed_ids` (List[str]): IDs that failed to delete

**Raises**:
- `Exception`: If bulk delete fails

**Example**:
```python
api = DopeAPI(supabase_client)

session_ids = ["id1", "id2", "id3", "id4"]
result = api.delete_sessions_bulk(session_ids, "auth0|123456")

print(f"Deleted: {result['deleted_count']} sessions")
if result['failed_ids']:
    print(f"Failed: {result['failed_ids']}")
```

**Notes**:
- More efficient than calling `delete_session()` in a loop
- Partial success possible (some succeed, some fail)
- Cascade deletes all measurements for deleted sessions
- Only deletes sessions owned by user

---

## Session Querying & Filtering

### search_sessions()

Search DOPE sessions by text across multiple fields.

**Signature**:
```python
def search_sessions(
    self,
    user_id: str,
    search_term: str,
    search_fields: Optional[List[str]] = None
) -> List[DopeSessionModel]
```

**Parameters**:
- `user_id` (str): Auth0 user ID to filter sessions
- `search_term` (str): Text to search for (case-insensitive)
- `search_fields` (Optional[List[str]]): Field names to search in

**Default search fields**:
- `session_name`
- `notes`
- `cartridge_make`
- `cartridge_model`
- `bullet_make`
- `bullet_model`
- `rifle_name`
- `range_name`

**Returns**:
- `List[DopeSessionModel]`: Matching sessions
- Empty list if no matches

**Raises**:
- `Exception`: If search fails

**Example**:
```python
api = DopeAPI(supabase_client)

# Search for sessions with "Sierra 168"
sessions = api.search_sessions("auth0|123456", "Sierra 168")

for session in sessions:
    print(f"{session.session_name}: {session.bullet_make} {session.bullet_model}")

# Search specific fields only
custom_sessions = api.search_sessions(
    "auth0|123456",
    "MatchKing",
    search_fields=["bullet_model", "notes"]
)
```

**Notes**:
- Case-insensitive search
- Searches across denormalized joined data
- Partial matching (substring search)
- Useful for quick filtering in UI

---

### filter_sessions()

Filter DOPE sessions by multiple criteria using structured filters.

**Signature**:
```python
def filter_sessions(
    self,
    user_id: str,
    filters: DopeSessionFilter
) -> List[DopeSessionModel]
```

**Parameters**:
- `user_id` (str): Auth0 user ID to filter sessions
- `filters` (DopeSessionFilter): Filter criteria instance

**Returns**:
- `List[DopeSessionModel]`: Filtered sessions
- Empty list if no matches

**Raises**:
- `Exception`: If filtering fails

**Example**:
```python
from dope.filters import DopeSessionFilter

api = DopeAPI(supabase_client)

# Create filter criteria
filters = DopeSessionFilter(
    cartridge_type="308 Winchester",
    bullet_make="Sierra",
    bullet_weight_range=(168, 180),
    temperature_range=(15.0, 25.0),  # Celsius
    distance_range=(100.0, 300.0)    # Meters
)

sessions = api.filter_sessions("auth0|123456", filters)

print(f"Found {len(sessions)} matching sessions")
```

**Available filter fields**:
- `cartridge_type` (str): Exact cartridge type
- `cartridge_make` (str): Exact cartridge make
- `bullet_make` (str): Exact bullet manufacturer
- `bullet_weight_range` (tuple): Min/max weight in grains
- `rifle_name` (str): Exact rifle name
- `range_name` (str): Exact range name
- `distance_range` (tuple): Min/max distance in meters
- `temperature_range` (tuple): Min/max temp in Celsius
- `humidity_range` (tuple): Min/max humidity percentage
- `wind_speed_range` (tuple): Min/max wind in m/s
- `date_from` (datetime): Start date
- `date_to` (datetime): End date

**Notes**:
- Multiple filters combined with AND logic
- Range filters are inclusive
- String filters are exact match (not fuzzy)
- Use "Not Defined" for fields with no value

---

### get_unique_values()

Get unique values for a specific field across user's sessions.

**Signature**:
```python
def get_unique_values(self, user_id: str, field_name: str) -> List[str]
```

**Parameters**:
- `user_id` (str): Auth0 user ID to filter sessions
- `field_name` (str): Name of field to get unique values for

**Supported field names**:
- `cartridge_type`
- `cartridge_make`
- `cartridge_model`
- `bullet_make`
- `bullet_model`
- `rifle_name`
- `range_name`
- `weather_source_name`

**Returns**:
- `List[str]`: Sorted list of unique values
- Empty list if none found

**Raises**:
- `ValueError`: If field_name is invalid
- `Exception`: If query fails

**Example**:
```python
api = DopeAPI(supabase_client)

# Get unique cartridge types for dropdown
cartridge_types = api.get_unique_values("auth0|123456", "cartridge_type")

for ct in cartridge_types:
    print(f"Option: {ct}")

# Result: ['223 Remington', '308 Winchester', '6.5 Creedmoor']
```

**Notes**:
- Useful for populating UI dropdowns and filters
- Only includes values from user's sessions
- Results are sorted alphabetically
- Excludes empty/null values

---

### get_session_statistics()

Get aggregate statistics across all user's DOPE sessions.

**Signature**:
```python
def get_session_statistics(self, user_id: str) -> Dict[str, Any]
```

**Parameters**:
- `user_id` (str): Auth0 user ID to filter sessions

**Returns**:
- `Dict[str, Any]` with statistics including:
  - `total_sessions` (int)
  - `total_measurements` (int)
  - `unique_rifles` (int)
  - `unique_cartridges` (int)
  - `date_range` (Dict[str, datetime]): First and last session dates
  - Additional aggregate stats

**Raises**:
- `Exception`: If statistics calculation fails

**Example**:
```python
api = DopeAPI(supabase_client)
stats = api.get_session_statistics("auth0|123456")

print(f"Total sessions: {stats['total_sessions']}")
print(f"Total shots: {stats['total_measurements']}")
print(f"Unique rifles: {stats['unique_rifles']}")
print(f"Unique cartridges: {stats['unique_cartridges']}")
print(f"Date range: {stats['date_range']}")
```

**Notes**:
- Provides overview metrics for dashboard
- Useful for analytics and reporting
- All stats scoped to user

---

## Measurement Management

### get_measurements_for_dope_session()

Get all measurements (individual shots) for a specific DOPE session.

**Signature**:
```python
def get_measurements_for_dope_session(
    self, dope_session_id: str, user_id: str
) -> List[DopeMeasurementModel]
```

**Parameters**:
- `dope_session_id` (str): UUID of the DOPE session
- `user_id` (str): Auth0 user ID (security check)

**Returns**:
- `List[DopeMeasurementModel]`: List of measurements ordered by shot_number
- Empty list if no measurements found

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = DopeAPI(supabase_client)
measurements = api.get_measurements_for_dope_session(session_id, "auth0|123456")

print(f"Total shots: {len(measurements)}")

for m in measurements:
    print(f"Shot #{m.shot_number}:")
    print(f"  Velocity: {m.speed_mps} m/s")
    print(f"  Energy: {m.ke_j} J")
    print(f"  Temp: {m.temperature_c}°C")
    if m.shot_notes:
        print(f"  Notes: {m.shot_notes}")
```

**Notes**:
- Measurements are ordered by shot_number
- Includes ballistic, environmental, and targeting data
- User must own the parent session

---

### create_measurement()

Create a new DOPE measurement (individual shot).

**Signature**:
```python
def create_measurement(
    self, measurement_data: Dict[str, Any], user_id: str
) -> DopeMeasurementModel
```

**Parameters**:
- `measurement_data` (Dict[str, Any]): Measurement fields (metric units)
- `user_id` (str): Auth0 user ID (security check)

**Required fields**:
- `dope_session_id` (str): FK to dope_sessions

**Optional fields** (all metric):
- `shot_number` (int)
- `datetime_shot` (datetime)
- `speed_mps` (float): Velocity in m/s
- `ke_j` (float): Kinetic energy in Joules
- `power_factor_kgms` (float): Power factor in kg⋅m/s
- `azimuth_deg` (float)
- `elevation_angle_deg` (float)
- `temperature_c` (float)
- `pressure_hpa` (float): Barometric pressure in hPa
- `humidity_pct` (float)
- `clean_bore` (str): "yes"/"no"
- `cold_bore` (str): "yes"/"no"
- `distance_m` (float)
- `elevation_adjustment` (str)
- `windage_adjustment` (str)
- `shot_notes` (str)

**Returns**:
- `DopeMeasurementModel`: Created measurement with generated ID

**Raises**:
- `ValueError`: If required fields missing or invalid
- `Exception`: If creation fails

**Example**:
```python
api = DopeAPI(supabase_client)

measurement_data = {
    "dope_session_id": "session-uuid",
    "shot_number": 1,
    "speed_mps": 792.5,
    "ke_j": 3456.7,
    "temperature_c": 21.0,
    "pressure_hpa": 1013.25,
    "humidity_pct": 65.0,
    "cold_bore": "yes",
    "shot_notes": "First shot of the day"
}

measurement = api.create_measurement(measurement_data, "auth0|123456")

print(f"Created measurement: {measurement.id}")
```

**Notes**:
- All ballistic data in metric units
- User must own the parent session
- Optional fields can be null

---

### update_measurement()

Update an existing DOPE measurement.

**Signature**:
```python
def update_measurement(
    self,
    measurement_id: str,
    measurement_data: Dict[str, Any],
    user_id: str
) -> Optional[DopeMeasurementModel]
```

**Parameters**:
- `measurement_id` (str): UUID of measurement to update
- `measurement_data` (Dict[str, Any]): Fields to update (metric units)
- `user_id` (str): Auth0 user ID (security check)

**Returns**:
- `DopeMeasurementModel`: Updated measurement if successful
- `None`: If measurement not found or not owned

**Raises**:
- `Exception`: If update fails

**Example**:
```python
api = DopeAPI(supabase_client)

update_data = {
    "shot_notes": "Flyer - wind gust during trigger press",
    "temperature_c": 22.0  # Updated temperature reading
}

measurement = api.update_measurement(meas_id, update_data, "auth0|123456")

if measurement:
    print(f"Updated shot #{measurement.shot_number}")
```

**Notes**:
- Partial updates supported
- User must own the parent session
- Can update any field except `id`, `user_id`, `created_at`

---

### delete_measurement()

Delete a DOPE measurement.

**Signature**:
```python
def delete_measurement(self, measurement_id: str, user_id: str) -> bool
```

**Parameters**:
- `measurement_id` (str): UUID of measurement to delete
- `user_id` (str): Auth0 user ID (security check)

**Returns**:
- `bool`: True if deleted, False if not found or not owned

**Raises**:
- `Exception`: If delete fails

**Example**:
```python
api = DopeAPI(supabase_client)

deleted = api.delete_measurement(meas_id, "auth0|123456")

if deleted:
    print("Measurement deleted")
else:
    print("Measurement not found or access denied")
```

**Notes**:
- User must own the parent session
- No undo - deletion is permanent

---

## UI Helper Methods

### get_edit_dropdown_options()

Get all dropdown options needed for editing a DOPE session.

**Signature**:
```python
def get_edit_dropdown_options(
    self, user_id: str
) -> Dict[str, List[Dict[str, Any]]]
```

**Parameters**:
- `user_id` (str): Auth0 user ID to filter user-owned data

**Returns**:
- `Dict[str, List[Dict[str, Any]]]` with keys:
  - `rifles`: List of user's rifles
  - `cartridges`: List of global cartridges
  - `chrono_sessions`: List of user's chronograph sessions
  - `weather_sources`: List of user's weather sources
  - `ranges`: List of available ranges

Each list contains dicts with:
- `id` (str): UUID for the option
- `name` (str): Display name

**Raises**:
- `Exception`: If query fails

**Example**:
```python
api = DopeAPI(supabase_client)
options = api.get_edit_dropdown_options("auth0|123456")

# Populate rifle dropdown
for rifle in options['rifles']:
    add_dropdown_option(rifle['id'], rifle['name'])

# Populate cartridge dropdown
for cartridge in options['cartridges']:
    add_dropdown_option(cartridge['id'], cartridge['name'])

# Populate chronograph sessions dropdown
for chrono in options['chrono_sessions']:
    add_dropdown_option(chrono['id'], chrono['name'])
```

**Notes**:
- Single call gets all options (efficient)
- User-owned data filtered by user_id
- Admin data (cartridges) globally available
- Useful for populating edit forms

---

## Type Safety

All API methods use type hints for compile-time checking:

```python
# IDE autocomplete works
api = DopeAPI(supabase_client)
session = api.get_session_by_id(session_id, user_id)

if session:
    # Type checker knows session is DopeSessionModel
    name = session.session_name  # ✓ Valid
    bullet = session.bullet_make  # ✓ Valid
    rifle = session.rifle_name  # ✓ Valid
    invalid = session.nonexistent  # ✗ Type error

# Return types are enforced
sessions: List[DopeSessionModel] = api.get_sessions_for_user(user_id)  # ✓ Correct
sessions: List[dict] = api.get_sessions_for_user(user_id)  # ✗ Type error
```

---

## Error Handling

All API methods follow consistent error handling:

**Returns None** (not found, no error):
- `get_session_by_id()` returns `None` if session not found

**Returns empty list** (no matches, no error):
- `get_sessions_for_user()` returns `[]` if no sessions
- `filter_sessions()` returns `[]` if no matches
- `search_sessions()` returns `[]` if no matches
- `get_measurements_for_dope_session()` returns `[]` if no measurements

**Raises Exception** (actual errors):
- Database connection failures
- Invalid parameters
- Permission denied (user doesn't own resource)
- Constraint violations (FK violations, etc.)

**Example**:
```python
api = DopeAPI(supabase_client)

# Handle not found gracefully
session = api.get_session_by_id("nonexistent-id", user_id)
if not session:
    print("Session not found")  # Not an error

# Handle actual errors
try:
    sessions = api.get_sessions_for_user(user_id)
    process_sessions(sessions)
except Exception as e:
    log_error(f"Database error: {e}")
    display_error("Unable to load sessions. Please try again.")
```

---

## Next Steps

- [Models Documentation](models.md) - Detailed field specifications
- [Examples](examples.md) - Common usage patterns
- [Module README](README.md) - Overview and integration

---

**API Version**: 1.0
**Protocol**: `dope.protocols.DopeAPIProtocol`
**Implementation**: `dope.api.DopeAPI`