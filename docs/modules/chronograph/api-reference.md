# Chronograph API Reference

## Overview

The Chronograph API provides type-safe access to chronograph sources (devices), sessions (shooting sessions), and measurements (individual shots). This API follows the `ChronographAPIProtocol` defined in `chronograph/protocols.py`.

All API methods are UI-agnostic and return strongly-typed `ChronographSource`, `ChronographSession`, and `ChronographMeasurement` instances.

## API Contract

```python
from chronograph.protocols import ChronographAPIProtocol
from chronograph.chronograph_source_models import ChronographSource
from chronograph.chronograph_session_models import ChronographSession, ChronographMeasurement
```

The `ChronographAPIProtocol` defines the complete API contract that all implementations must follow.

---

## Chronograph Source Operations

These methods manage chronograph sources (devices) for individual users.

### get_all_sources()

Get all chronograph sources for a user.

**Signature**:
```python
def get_all_sources(self, user_id: str) -> List[ChronographSource]
```

**Parameters**:
- `user_id` (str): User identifier

**Returns**:
- `List[ChronographSource]`: List of all sources owned by user, ordered by name
- Empty list if no sources found

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = ChronographAPI(supabase_client)
sources = api.get_all_sources("user-123")

for source in sources:
    print(source.display_name())
    # My Garmin Xero
    # Range Chronograph
```

**Notes**:
- Results are user-scoped (only returns sources owned by user)
- Ordered alphabetically by name for consistent display
- Returns empty list, not error, if user has no sources

---

### get_source_by_id()

Get a specific chronograph source by its UUID.

**Signature**:
```python
def get_source_by_id(
    self, source_id: str, user_id: str
) -> Optional[ChronographSource]
```

**Parameters**:
- `source_id` (str): Chronograph source UUID
- `user_id` (str): User identifier (for access control)

**Returns**:
- `ChronographSource`: Source if found and owned by user
- `None`: If source not found or not owned by user

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = ChronographAPI(supabase_client)
source = api.get_source_by_id("source-123", "user-123")

if source:
    print(source.device_display())
    # Garmin Xero C1 (S/N: G123456)
else:
    print("Source not found or access denied")
```

**Notes**:
- Returns `None` rather than raising exception if not found
- Enforces user isolation (only returns if owned by user)
- User must own the source to retrieve it

---

### get_source_by_name()

Get a chronograph source by name.

**Signature**:
```python
def get_source_by_name(
    self, user_id: str, name: str
) -> Optional[ChronographSource]
```

**Parameters**:
- `user_id` (str): User identifier
- `name` (str): Source name to search for (exact match, case-sensitive)

**Returns**:
- `ChronographSource`: Source if found
- `None`: If no source with that name exists for user

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = ChronographAPI(supabase_client)
source = api.get_source_by_name("user-123", "My Garmin Xero")

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

Create a new chronograph source with auto-generated ID and timestamps.

**Signature**:
```python
def create_source(
    self, source_data: dict, user_id: str
) -> ChronographSource
```

**Parameters**:
- `source_data` (dict): Dictionary containing source information (see below)
- `user_id` (str): User identifier

**Required fields**:
- `name` (str): User-defined name for the source

**Optional fields**:
- `device_name` (str): Device name from CSV/import
- `make` (str): Manufacturer (e.g., "Garmin")
- `model` (str): Model number (e.g., "Xero C1")
- `serial_number` (str): Device serial number

**Returns**:
- `ChronographSource`: Created source with generated ID and timestamps

**Raises**:
- `Exception`: If creation fails

**Example**:
```python
api = ChronographAPI(supabase_client)

source_data = {
    "name": "My Garmin",
    "device_name": "Garmin Xero",
    "make": "Garmin",
    "model": "Xero C1",
    "serial_number": "G123456"
}

source = api.create_source(source_data, "user-123")
print(f"Created source: {source.id}")
print(source.short_display())
# My Garmin - Garmin Xero C1 (S/N: G123456)
```

**Notes**:
- ID is auto-generated (UUID)
- Timestamps (created_at, updated_at) are auto-generated
- source_type defaults to "chronograph"
- All device fields are optional (can create minimal source with just name)

---

### update_source()

Update an existing chronograph source with auto-updated timestamp.

**Signature**:
```python
def update_source(
    self, source_id: str, updates: dict, user_id: str
) -> ChronographSource
```

**Parameters**:
- `source_id` (str): Chronograph source UUID
- `updates` (dict): Dictionary of fields to update
- `user_id` (str): User identifier (for access control)

**Returns**:
- `ChronographSource`: Updated source

**Raises**:
- `Exception`: If source not found or not owned by user
- `Exception`: If update fails

**Example**:
```python
api = ChronographAPI(supabase_client)

updates = {
    "name": "Range Garmin",
    "make": "Garmin"
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

Delete a chronograph source and all its sessions/measurements.

**Signature**:
```python
def delete_source(self, source_id: str, user_id: str) -> bool
```

**Parameters**:
- `source_id` (str): Chronograph source UUID
- `user_id` (str): User identifier (for access control)

**Returns**:
- `bool`: True if deleted successfully

**Raises**:
- `Exception`: If deletion fails

**Example**:
```python
api = ChronographAPI(supabase_client)

success = api.delete_source("source-123", "user-123")
if success:
    print("Source and all associated data deleted")
```

**Notes**:
- Cascades to delete all associated sessions and measurements
- No undo - deletion is permanent
- User must own source to delete it
- Returns True even if source didn't exist (idempotent)

---

## Session Operations

These methods manage chronograph sessions (shooting sessions) for individual users.

### get_all_sessions()

Get all chronograph sessions for a user.

**Signature**:
```python
def get_all_sessions(self, user_id: str) -> List[ChronographSession]
```

**Parameters**:
- `user_id` (str): User identifier

**Returns**:
- `List[ChronographSession]`: List of all sessions, ordered by date descending
- Empty list if no sessions found

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = ChronographAPI(supabase_client)
sessions = api.get_all_sessions("user-123")

for session in sessions:
    print(session.display_name())
    # 168gr HPBT - 2024-01-15 10:00
    # 175gr SMK - 2024-01-14 14:30
```

**Notes**:
- Results are user-scoped (only returns sessions owned by user)
- Ordered by datetime_local descending (newest first)
- Returns empty list, not error, if user has no sessions

---

### get_session_by_id()

Get a specific chronograph session by its UUID.

**Signature**:
```python
def get_session_by_id(
    self, session_id: str, user_id: str
) -> Optional[ChronographSession]
```

**Parameters**:
- `session_id` (str): Session UUID
- `user_id` (str): User identifier (for access control)

**Returns**:
- `ChronographSession`: Session if found and owned by user
- `None`: If session not found or not owned by user

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = ChronographAPI(supabase_client)
session = api.get_session_by_id("session-123", "user-123")

if session:
    print(f"Shots: {session.shot_count}")
    print(f"Average: {session.avg_speed_mps} m/s")
    print(f"SD: {session.std_dev_mps} m/s")
else:
    print("Session not found or access denied")
```

**Notes**:
- Returns `None` rather than raising exception if not found
- Enforces user isolation (only returns if owned by user)
- Includes calculated statistics (avg, std_dev, etc.)

---

### filter_sessions()

Get filtered chronograph sessions.

**Signature**:
```python
def filter_sessions(
    self,
    user_id: str,
    bullet_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[ChronographSession]
```

**Parameters**:
- `user_id` (str): User identifier
- `bullet_type` (Optional[str]): Filter by bullet type (tab_name)
- `start_date` (Optional[str]): Start date filter (ISO format)
- `end_date` (Optional[str]): End date filter (ISO format)

**Returns**:
- `List[ChronographSession]`: Filtered sessions, ordered by date descending
- Empty list if no matches

**Raises**:
- `Exception`: If database query fails

**Examples**:
```python
api = ChronographAPI(supabase_client)

# Filter by bullet type
sessions = api.filter_sessions(
    "user-123",
    bullet_type="168gr HPBT"
)

# Filter by date range
january_sessions = api.filter_sessions(
    "user-123",
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59"
)

# Combined filters
specific = api.filter_sessions(
    "user-123",
    bullet_type="168gr HPBT",
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59"
)

# No filters (all sessions)
all_sessions = api.filter_sessions("user-123")
```

**Notes**:
- All filter parameters are optional
- Multiple filters are combined with AND logic
- Date filters use ISO 8601 format
- Results ordered by datetime_local descending (newest first)
- bullet_type filters on tab_name field

---

### create_session()

Create a new chronograph session with auto-generated ID.

**Signature**:
```python
def create_session(
    self, session_data: dict, user_id: str
) -> ChronographSession
```

**Parameters**:
- `session_data` (dict): Dictionary containing session information (see below)
- `user_id` (str): User identifier

**Required fields**:
- `tab_name` (str): Bullet type identifier (e.g., "168gr HPBT")
- `session_name` (str): User-defined session name
- `datetime_local` (str): Session date/time (ISO format)

**Optional fields**:
- `file_path` (str): Path to imported CSV file
- `chronograph_source_id` (str): Associated chronograph device UUID

**Returns**:
- `ChronographSession`: Created session with generated ID

**Raises**:
- `Exception`: If creation fails

**Example**:
```python
api = ChronographAPI(supabase_client)

session_data = {
    "tab_name": "168gr HPBT",
    "session_name": "Range Day 1",
    "datetime_local": "2024-01-15T10:00:00",
    "chronograph_source_id": "source-123"
}

session = api.create_session(session_data, "user-123")
print(f"Created session: {session.id}")
print(session.display_name())
# 168gr HPBT - 2024-01-15 10:00
```

**Notes**:
- ID is auto-generated (UUID)
- uploaded_at timestamp is auto-generated
- Statistics fields (shot_count, avg_speed_mps, etc.) start at 0/None
- Statistics are calculated when measurements are added
- chronograph_source_id is optional but recommended

---

### session_exists()

Check if a session already exists.

**Signature**:
```python
def session_exists(
    self, user_id: str, tab_name: str, datetime_local: str
) -> bool
```

**Parameters**:
- `user_id` (str): User identifier
- `tab_name` (str): Tab name to check
- `datetime_local` (str): Datetime to check (ISO format)

**Returns**:
- `bool`: True if session exists, False otherwise

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = ChronographAPI(supabase_client)

exists = api.session_exists(
    "user-123",
    "168gr HPBT",
    "2024-01-15T10:00:00"
)

if not exists:
    # Safe to create session
    session = api.create_session(session_data, user_id)
else:
    print("Session already exists, skipping")
```

**Notes**:
- Useful for preventing duplicate imports
- Checks user_id, tab_name, and datetime_local together
- Called before creating sessions during CSV import
- Fast check (uses database index)

---

## Measurement Operations

These methods manage chronograph measurements (individual shots) for individual users.

### get_measurements_for_session()

Get all measurements for a specific session.

**Signature**:
```python
def get_measurements_for_session(
    self, session_id: str, user_id: str
) -> List[ChronographMeasurement]
```

**Parameters**:
- `session_id` (str): Session UUID
- `user_id` (str): User identifier (for access control)

**Returns**:
- `List[ChronographMeasurement]`: All measurements for session, ordered by shot number
- Empty list if no measurements found

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = ChronographAPI(supabase_client)

measurements = api.get_measurements_for_session(
    "session-123", "user-123"
)

for m in measurements:
    print(f"Shot {m.shot_number}: {m.speed_mps} m/s")
    # Shot 1: 792.5 m/s
    # Shot 2: 794.2 m/s
```

**Notes**:
- Results ordered by shot_number ascending
- User must own the session
- Returns empty list if no measurements, not an error
- All velocities in meters per second (metric)

---

### create_measurement()

Create a new chronograph measurement with auto-generated ID.

**Signature**:
```python
def create_measurement(
    self, measurement_data: dict, user_id: str
) -> ChronographMeasurement
```

**Parameters**:
- `measurement_data` (dict): Dictionary containing measurement data (see below)
- `user_id` (str): User identifier

**Required fields**:
- `chrono_session_id` (str): Session UUID
- `shot_number` (int): Shot sequence number
- `speed_mps` (float): Velocity in meters per second
- `datetime_local` (str): When shot was taken (ISO format)

**Optional fields (all metric units)**:
- `delta_avg_mps` (float): Difference from average velocity
- `ke_j` (float): Kinetic energy (joules)
- `power_factor_kgms` (float): Power factor (kg*m/s)
- `clean_bore` (bool): Clean bore shot flag
- `cold_bore` (bool): Cold bore shot flag
- `shot_notes` (str): User notes for this shot

**Returns**:
- `ChronographMeasurement`: Created measurement with generated ID

**Raises**:
- `Exception`: If creation fails
- `Exception`: If session doesn't exist or not owned by user

**Example**:
```python
api = ChronographAPI(supabase_client)

measurement_data = {
    "chrono_session_id": "session-123",
    "shot_number": 1,
    "speed_mps": 792.5,
    "datetime_local": "2024-01-15T10:00:00",
    "ke_j": 3500.0,
    "power_factor_kgms": 42.5,
    "cold_bore": True
}

measurement = api.create_measurement(measurement_data, "user-123")
print(f"Created measurement: {measurement.id}")
print(f"Velocity: {measurement.speed_mps} m/s")
```

**Notes**:
- ID is auto-generated (UUID)
- All energy/velocity measurements in metric units
- User must own the session
- Does NOT automatically update session statistics (use batch method for that)

---

### create_measurements_batch()

Create multiple chronograph measurements in a single batch and update session statistics.

**Signature**:
```python
def create_measurements_batch(
    self, measurements_data: List[dict], user_id: str
) -> List[ChronographMeasurement]
```

**Parameters**:
- `measurements_data` (List[dict]): List of measurement data dictionaries
- `user_id` (str): User identifier

**Returns**:
- `List[ChronographMeasurement]`: List of created measurements

**Raises**:
- `Exception`: If batch creation fails

**Example**:
```python
api = ChronographAPI(supabase_client)

batch_data = [
    {
        "chrono_session_id": "session-123",
        "shot_number": 1,
        "speed_mps": 792.5,
        "datetime_local": "2024-01-15T10:00:00"
    },
    {
        "chrono_session_id": "session-123",
        "shot_number": 2,
        "speed_mps": 794.2,
        "datetime_local": "2024-01-15T10:00:05"
    },
    {
        "chrono_session_id": "session-123",
        "shot_number": 3,
        "speed_mps": 791.8,
        "datetime_local": "2024-01-15T10:00:10"
    }
]

measurements = api.create_measurements_batch(batch_data, "user-123")
print(f"Created {len(measurements)} measurements")

# Session statistics are automatically updated
session = api.get_session_by_id("session-123", "user-123")
print(f"Average: {session.avg_speed_mps} m/s")
print(f"SD: {session.std_dev_mps} m/s")
```

**Notes**:
- More efficient than creating measurements one at a time
- Automatically updates session statistics for all affected sessions
- IDs are auto-generated for each measurement
- Typical use: CSV import with many measurements
- Handles multiple sessions in one batch (updates statistics for each)

---

## Statistics Operations

These methods calculate and retrieve statistics for chronograph sessions.

### calculate_session_statistics()

Calculate statistics for a session.

**Signature**:
```python
def calculate_session_statistics(
    self, session_id: str, user_id: str
) -> dict
```

**Parameters**:
- `session_id` (str): Session UUID
- `user_id` (str): User identifier (for access control)

**Returns**:
- `dict`: Dictionary with statistics:
  - `shot_count` (int): Number of shots
  - `avg_speed_mps` (float): Average velocity
  - `std_dev_mps` (float): Standard deviation
  - `min_speed_mps` (float): Minimum velocity
  - `max_speed_mps` (float): Maximum velocity
  - `extreme_spread_mps` (float): Max - Min velocity
  - `coefficient_of_variation` (float): (std_dev / avg) * 100

**Raises**:
- `Exception`: If session not found or calculation fails

**Example**:
```python
api = ChronographAPI(supabase_client)

stats = api.calculate_session_statistics("session-123", "user-123")

print(f"Shot Count: {stats['shot_count']}")
print(f"Average: {stats['avg_speed_mps']} m/s")
print(f"Std Dev: {stats['std_dev_mps']} m/s")
print(f"Min: {stats['min_speed_mps']} m/s")
print(f"Max: {stats['max_speed_mps']} m/s")
print(f"ES: {stats['extreme_spread_mps']} m/s")
print(f"CV: {stats['coefficient_of_variation']}%")

# Example output:
# Shot Count: 10
# Average: 792.5 m/s
# Std Dev: 1.2 m/s
# Min: 790.5 m/s
# Max: 794.5 m/s
# ES: 4.0 m/s
# CV: 0.15%
```

**Notes**:
- All velocities in meters per second (metric)
- Coefficient of variation is percentage (0-100)
- Returns 0 for statistics if session has no measurements
- User must own the session

---

### get_unique_bullet_types()

Get a list of unique bullet types used by the user.

**Signature**:
```python
def get_unique_bullet_types(self, user_id: str) -> List[str]
```

**Parameters**:
- `user_id` (str): User identifier

**Returns**:
- `List[str]`: Sorted list of unique bullet type strings (from session tab_name)

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = ChronographAPI(supabase_client)

bullet_types = api.get_unique_bullet_types("user-123")
print(bullet_types)
# ['140gr ELD-M', '168gr HPBT', '175gr SMK']

# Use in UI dropdown
for bullet_type in bullet_types:
    display_dropdown_option(bullet_type)
```

**Notes**:
- Useful for populating UI dropdowns and filters
- Results are sorted alphabetically
- Includes only bullet types that have sessions
- Derives from tab_name field in sessions

---

### get_time_window()

Get a time window for recent sessions.

**Signature**:
```python
def get_time_window(
    self, user_id: str, days: int = 30
) -> Tuple[datetime, datetime]
```

**Parameters**:
- `user_id` (str): User identifier
- `days` (int): Number of days to look back (default: 30)

**Returns**:
- `Tuple[datetime, datetime]`: (start_datetime, end_datetime)

**Raises**:
- `Exception`: If database query fails

**Example**:
```python
api = ChronographAPI(supabase_client)

# Get sessions from last 7 days
start, end = api.get_time_window("user-123", days=7)

sessions = api.filter_sessions(
    "user-123",
    start_date=start.isoformat(),
    end_date=end.isoformat()
)

print(f"Sessions from {start} to {end}: {len(sessions)}")
```

**Notes**:
- Returns current datetime as end, current datetime - days as start
- Useful for "recent activity" queries
- Can be used with filter_sessions() for time-based filtering

---

## Type Safety

All API methods use type hints for compile-time checking:

```python
# IDE autocomplete works
api = ChronographAPI(supabase_client)
session = api.get_session_by_id("session-123", "user-123")

if session:
    # Type checker knows session is ChronographSession
    shots = session.shot_count  # Valid
    avg = session.avg_speed_mps  # Valid
    invalid = session.nonexistent_field  # Type error

# Return types are enforced
sessions: List[ChronographSession] = api.get_all_sessions("user-123")  # Correct
sessions: List[dict] = api.get_all_sessions("user-123")  # Type error
```

---

## Error Handling

All API methods follow consistent error handling:

**Returns None** (not found, no error):
- `get_source_by_id()` returns `None` if source not found or not owned
- `get_source_by_name()` returns `None` if no source with that name
- `get_session_by_id()` returns `None` if session not found or not owned

**Returns empty list** (no matches, no error):
- `get_all_sources()` returns `[]` if user has no sources
- `get_all_sessions()` returns `[]` if user has no sessions
- `get_measurements_for_session()` returns `[]` if no measurements
- `filter_sessions()` returns `[]` if no matches

**Raises Exception** (actual errors):
- Database connection failures
- Invalid parameters
- Access control violations (wrong user_id)
- Constraint violations (FK violations)

**Example**:
```python
api = ChronographAPI(supabase_client)

# Handle not found gracefully
session = api.get_session_by_id("nonexistent-id", "user-123")
if not session:
    print("Session not found")  # Not an error

# Handle actual errors
try:
    sessions = api.get_all_sessions("user-123")
except Exception as e:
    print(f"Database error: {e}")  # Actual error
```

---

## User Isolation

All operations enforce user isolation:

- Sources are user-scoped (can only access own sources)
- Sessions are user-scoped (can only access own sessions)
- Measurements are user-scoped (can only access own measurements)
- All methods require user_id parameter for access control
- Queries automatically filter by user_id

**Example**:
```python
# User A creates a session
session_a = api.create_session({...}, "user-a")

# User B cannot access User A's session
session = api.get_session_by_id(session_a.id, "user-b")
# Returns None (access denied)

# User B can create their own session with same bullet type
session_b = api.create_session({...}, "user-b")
# Different session, same bullet type - OK
```

---

## Next Steps

- [Models Documentation](models.md) - Detailed field specifications
- [Examples](examples.md) - Common usage patterns
- [Module README](README.md) - Overview and integration

---

**API Version**: 1.0
**Protocol**: `chronograph.protocols.ChronographAPIProtocol`
**Implementation**: `chronograph.client_api.ChronographAPI`
