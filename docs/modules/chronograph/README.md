# Chronograph Module

Complete chronograph data management for ChronoLog including chronograph sources (devices), sessions (shooting sessions), and measurements (individual shots).

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Models](#models)
- [Integration](#integration)

## Overview

The Chronograph module provides comprehensive chronograph data management:

- **Chronograph Sources**: Manage chronograph devices (Garmin Xero, etc.)
- **Sessions**: Track shooting sessions with statistics
- **Measurements**: Store and retrieve individual shot data
- **CSV Import**: Import data from chronograph device CSV exports
- **Statistics**: Calculate session statistics (avg, std dev, ES, CV)
- **Filtering**: Query sessions by bullet type, date range

### Key Features

- User-scoped sources, sessions, and measurements
- Automatic session statistics calculation
- Device identification from CSV metadata
- Automatic timestamp and ID generation
- Batch measurement creation with statistics updates
- Type-safe API with protocol definitions

## Quick Start

```python
from chronograph import ChronographAPI
from supabase import create_client

# Initialize
supabase = create_client(url, key)
chrono_api = ChronographAPI(supabase)

# Create a chronograph source
source = chrono_api.create_source(
    {
        "name": "My Garmin Xero",
        "make": "Garmin",
        "model": "Xero C1",
        "serial_number": "G123456"
    },
    user_id
)

# Create a session
session = chrono_api.create_session(
    {
        "tab_name": "168gr HPBT",
        "session_name": "Range Day 1",
        "datetime_local": "2024-01-15T10:00:00",
        "chronograph_source_id": source.id
    },
    user_id
)

# Create measurements
batch_data = [
    {
        "chrono_session_id": session.id,
        "shot_number": 1,
        "speed_mps": 792.5,
        "datetime_local": "2024-01-15T10:00:00"
    },
    {
        "chrono_session_id": session.id,
        "shot_number": 2,
        "speed_mps": 794.2,
        "datetime_local": "2024-01-15T10:00:05"
    }
]
measurements = chrono_api.create_measurements_batch(batch_data, user_id)

# Get session statistics
stats = chrono_api.calculate_session_statistics(session.id, user_id)
print(f"Average: {stats['avg_speed_mps']} m/s")
print(f"Std Dev: {stats['std_dev_mps']} m/s")
print(f"ES: {stats['extreme_spread_mps']} m/s")
```

## Architecture

### Components

```
chronograph/
├── __init__.py                     # Module exports
├── client_api.py                   # ChronographAPI facade (internal use)
├── api.py                          # FastAPI REST API (external use)
├── protocols.py                    # ChronographAPIProtocol
├── chronograph_source_models.py    # ChronographSource
├── chronograph_session_models.py   # ChronographSession, ChronographMeasurement
├── service.py                      # ChronographService (database layer)
└── test_chronograph.py             # Unit tests
```

### Layer Pattern

1. **Protocol Layer** (`protocols.py`): Type-safe API contract
2. **API Layers**:
   - **Client API** (`client_api.py`): Internal synchronous API for application use
   - **REST API** (`api.py`): External FastAPI endpoints for web services
3. **Service Layer** (`service.py`): Database operations and business logic
4. **Model Layer**: Domain entities (sources, sessions, measurements)

### Data Flow

```
UI/Controller
    ↓
ChronographAPI (client_api.py)
    ↓
ChronographService (service.py)
    ↓
Supabase Database
```

## API Reference

### Chronograph Source Operations

#### get_all_sources(user_id: str) → List[ChronographSource]

Get all chronograph sources for a user.

```python
sources = chrono_api.get_all_sources(user_id)
for source in sources:
    print(f"{source.name}: {source.device_display()}")
```

#### create_source(source_data: dict, user_id: str) → ChronographSource

Create a new chronograph source.

```python
source = chrono_api.create_source(
    {
        "name": "My Garmin",
        "make": "Garmin",
        "model": "Xero C1",
        "serial_number": "G123456"
    },
    user_id
)
```

#### update_source(source_id: str, updates: dict, user_id: str) → ChronographSource

Update an existing chronograph source.

```python
updated = chrono_api.update_source(
    source_id,
    {"name": "Updated Garmin", "make": "Garmin"},
    user_id
)
```

#### delete_source(source_id: str, user_id: str) → bool

Delete a chronograph source.

```python
success = chrono_api.delete_source(source_id, user_id)
```

### Session Operations

#### get_all_sessions(user_id: str) → List[ChronographSession]

Get all chronograph sessions for a user.

```python
sessions = chrono_api.get_all_sessions(user_id)
for session in sessions:
    print(f"{session.display_name()}: {session.shot_count} shots")
```

#### get_session_by_id(session_id: str, user_id: str) → Optional[ChronographSession]

Get a specific session by ID.

```python
session = chrono_api.get_session_by_id(session_id, user_id)
if session:
    print(f"Average: {session.avg_speed_mps} m/s")
```

#### filter_sessions(...) → List[ChronographSession]

Query sessions with filters.

```python
sessions = chrono_api.filter_sessions(
    user_id,
    bullet_type="168gr HPBT",
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59"
)
```

#### create_session(session_data: dict, user_id: str) → ChronographSession

Create a new chronograph session.

```python
session = chrono_api.create_session(
    {
        "tab_name": "168gr HPBT",
        "session_name": "Range Day 1",
        "datetime_local": "2024-01-15T10:00:00",
        "chronograph_source_id": source_id
    },
    user_id
)
```

### Measurement Operations

#### get_measurements_for_session(session_id: str, user_id: str) → List[ChronographMeasurement]

Get all measurements for a session.

```python
measurements = chrono_api.get_measurements_for_session(session_id, user_id)
for m in measurements:
    print(f"Shot {m.shot_number}: {m.speed_mps} m/s")
```

#### create_measurement(measurement_data: dict, user_id: str) → ChronographMeasurement

Create a single measurement.

```python
measurement = chrono_api.create_measurement(
    {
        "chrono_session_id": session_id,
        "shot_number": 1,
        "speed_mps": 792.5,
        "datetime_local": "2024-01-15T10:00:00",
        "ke_j": 3500.0,
        "power_factor_kgms": 42.5
    },
    user_id
)
```

#### create_measurements_batch(measurements_data: List[dict], user_id: str) → List[ChronographMeasurement]

Create multiple measurements efficiently and update session statistics.

```python
batch = [
    {
        "chrono_session_id": session_id,
        "shot_number": 1,
        "speed_mps": 792.5,
        "datetime_local": "2024-01-15T10:00:00"
    },
    {
        "chrono_session_id": session_id,
        "shot_number": 2,
        "speed_mps": 794.2,
        "datetime_local": "2024-01-15T10:00:05"
    }
]
measurements = chrono_api.create_measurements_batch(batch, user_id)
```

### Statistics Operations

#### calculate_session_statistics(session_id: str, user_id: str) → dict

Calculate statistics for a session.

```python
stats = chrono_api.calculate_session_statistics(session_id, user_id)
print(f"Shot Count: {stats['shot_count']}")
print(f"Average: {stats['avg_speed_mps']} m/s")
print(f"Std Dev: {stats['std_dev_mps']} m/s")
print(f"Min: {stats['min_speed_mps']} m/s")
print(f"Max: {stats['max_speed_mps']} m/s")
print(f"ES: {stats['extreme_spread_mps']} m/s")
print(f"CV: {stats['coefficient_of_variation']}%")
```

#### get_unique_bullet_types(user_id: str) → List[str]

Get all unique bullet types used by a user.

```python
bullet_types = chrono_api.get_unique_bullet_types(user_id)
print(bullet_types)  # ['168gr HPBT', '175gr SMK', '140gr ELD-M']
```

## Models

### ChronographSource

Represents a chronograph device.

**Required Fields:**
- `id`: UUID
- `user_id`: Owner ID
- `name`: User-defined name

**Optional Fields:**
- `device_name`: Device name from CSV
- `make`: Manufacturer (e.g., "Garmin")
- `model`: Model number (e.g., "Xero C1")
- `serial_number`: Device serial number

**Display Methods:**
- `display_name()`: Returns source name
- `device_display()`: Formatted device info with serial number
- `short_display()`: Combined name and device info

### ChronographSession

Represents a shooting session with statistics.

**Required Fields:**
- `id`: UUID
- `user_id`: Owner ID
- `tab_name`: Bullet type identifier (e.g., "168gr HPBT")
- `session_name`: User-defined session name
- `datetime_local`: Session date/time
- `uploaded_at`: When uploaded to database

**Optional Fields:**
- `file_path`: Path to imported CSV file
- `chronograph_source_id`: Associated chronograph device

**Statistics Fields (auto-calculated):**
- `shot_count`: Number of shots
- `avg_speed_mps`: Average velocity (m/s)
- `std_dev_mps`: Standard deviation (m/s)
- `min_speed_mps`: Minimum velocity
- `max_speed_mps`: Maximum velocity
- `extreme_spread_mps`: Max - Min velocity
- `coefficient_of_variation`: (std_dev / avg) * 100

**Display Methods:**
- `display_name()`: Returns session name
- `full_display()`: Session name with bullet type

### ChronographMeasurement

Represents a single shot measurement.

**Required Fields:**
- `id`: UUID
- `user_id`: Owner ID
- `chrono_session_id`: Associated session ID
- `shot_number`: Shot sequence number
- `speed_mps`: Velocity in meters per second
- `datetime_local`: When shot was taken
- `uploaded_at`: When uploaded to database

**Optional Metric Fields:**
- `ke_j`: Kinetic energy (joules)
- `power_factor_kgms`: Power factor (kg*m/s)
- `clean_bore`: Boolean flag for clean bore shot
- `cold_bore`: Boolean flag for cold bore shot
- `shot_notes`: User notes for this shot

## Integration

### With Bullets Module

Link chronograph sessions to specific bullet loads:

```python
from chronograph import ChronographAPI
from bullets import BulletsAPI

# Get bullet info
bullet = bullets_api.get_bullet_by_id(bullet_id, user_id)

# Create session for this bullet
session = chrono_api.create_session(
    {
        "tab_name": f"{bullet.weight_grains}gr {bullet.name}",
        "session_name": "Velocity Testing",
        "datetime_local": datetime.now().isoformat()
    },
    user_id
)
```

### With Weather Module

Combine chronograph data with environmental conditions:

```python
from chronograph import ChronographAPI
from weather import WeatherAPI

# Get session
session = chrono_api.get_session_by_id(session_id, user_id)

# Get weather at time of session
weather_measurements = weather_api.filter_measurements(
    user_id,
    start_date=session.datetime_local,
    end_date=session.datetime_local
)
```

### With Rifles Module

Link sessions to specific rifles:

```python
from chronograph import ChronographAPI
from rifles import RiflesAPI

# Get rifle
rifle = rifles_api.get_rifle_by_id(rifle_id, user_id)

# Get sessions for this rifle
sessions = chrono_api.filter_sessions(
    user_id,
    bullet_type=f"{rifle.chambering}"
)
```

### CSV Import Pattern

Chronograph data is typically imported from CSV files exported by chronograph devices:

```python
import csv

# Parse CSV from chronograph
with open("garmin_xero_export.csv") as f:
    reader = csv.DictReader(f)
    metadata = next(reader)  # First row contains metadata

    # Create or get source
    source_id = chrono_api.create_or_get_source_from_device_info(
        user_id,
        metadata.get("Device Name"),
        metadata.get("Model"),
        metadata.get("Serial Number")
    )

    # Create session
    session = chrono_api.create_session(
        {
            "tab_name": metadata.get("Bullet Type"),
            "session_name": metadata.get("Session Name"),
            "datetime_local": metadata.get("Timestamp"),
            "chronograph_source_id": source_id
        },
        user_id
    )

    # Batch create measurements
    measurements_data = []
    for row in reader:
        measurements_data.append({
            "chrono_session_id": session.id,
            "shot_number": int(row["Shot"]),
            "speed_mps": float(row["Velocity"]),
            "datetime_local": row["Timestamp"],
            "ke_j": float(row.get("Energy", 0)) if row.get("Energy") else None,
        })

    measurements = chrono_api.create_measurements_batch(
        measurements_data,
        user_id
    )

    # Statistics are automatically calculated
    updated_session = chrono_api.get_session_by_id(session.id, user_id)
    print(f"Average: {updated_session.avg_speed_mps} m/s")
```

## Database Schema

### chronograph_source Table

```sql
CREATE TABLE chronograph_source (
    id UUID PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    device_name TEXT,
    make TEXT,
    model TEXT,
    serial_number TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### chronograph_sessions Table

```sql
CREATE TABLE chronograph_sessions (
    id UUID PRIMARY KEY,
    user_id TEXT NOT NULL,
    tab_name TEXT NOT NULL,
    session_name TEXT,
    datetime_local TIMESTAMP NOT NULL,
    uploaded_at TIMESTAMP NOT NULL,
    file_path TEXT,
    chronograph_source_id UUID REFERENCES chronograph_source(id),
    -- Statistics (auto-calculated)
    shot_count INTEGER,
    avg_speed_mps REAL,
    std_dev_mps REAL,
    min_speed_mps REAL,
    max_speed_mps REAL,
    extreme_spread_mps REAL,
    coefficient_of_variation REAL
);
```

### chronograph_measurements Table

```sql
CREATE TABLE chronograph_measurements (
    id UUID PRIMARY KEY,
    user_id TEXT NOT NULL,
    chrono_session_id UUID REFERENCES chronograph_sessions(id) ON DELETE CASCADE,
    shot_number INTEGER NOT NULL,
    speed_mps REAL NOT NULL,
    datetime_local TIMESTAMP NOT NULL,
    uploaded_at TIMESTAMP NOT NULL,
    ke_j REAL,
    power_factor_kgms REAL,
    clean_bore BOOLEAN,
    cold_bore BOOLEAN,
    shot_notes TEXT
);
```

## Testing

The chronograph module includes 36 unit tests covering:

- Model creation and display methods
- Source CRUD operations
- Session CRUD operations with statistics
- Measurement CRUD operations
- Batch operations with statistics updates
- Filtering and querying
- Error handling
- Device identification logic

Run tests:

```bash
python -m pytest chronograph/test_chronograph.py -v
```

## See Also

- [Models Reference](./models.md) - Detailed model documentation
- [API Reference](./api-reference.md) - Complete API documentation
- [Examples](./examples.md) - Practical usage examples