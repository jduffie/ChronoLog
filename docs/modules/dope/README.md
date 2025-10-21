# DOPE Module

## Overview

The DOPE (Data On Previous Engagement) module is THE MOST IMPORTANT module in ChronoLog - it is the convergence point where all data source modules come together to create comprehensive ballistic profiles.

DOPE is unique because it is the **ONLY module allowed to couple with other modules**. While all other modules are independent, DOPE aggregates data from chronograph, rifles, cartridges (with bullets), weather, and ranges to create rich, denormalized sessions for ballistic analysis.

## Purpose

The DOPE module enables shooters to:

1. **Aggregate ballistic data** from multiple independent sources into unified sessions
2. **Create complete shooting profiles** combining velocity, rifle, cartridge, bullet, weather, and location
3. **Analyze performance patterns** across different equipment and conditions
4. **Track historical data** for load development and accuracy improvement
5. **Make informed decisions** about equipment, loads, and environmental factors

## What is DOPE?

**DOPE** = "Data On Previous Engagement"

A DOPE session represents a complete ballistic data point that aggregates:

- **Chronograph data**: Velocity measurements from shooting sessions
- **Cartridge information**: The specific cartridge used (with bullet specs via FK)
- **Rifle details**: Firearm configuration (barrel length, twist rate, optics)
- **Weather conditions**: Environmental factors (temperature, humidity, pressure, wind)
- **Range information**: Location, distance, and geometry
- **Shot measurements**: Individual shot data with environmental conditions

## The Convergence Architecture

DOPE follows a **convergent architecture** pattern - it is the only module that depends on others:

```
Independent Data Sources          DOPE (Convergent Point)
├── Chronograph                ┌─────────────────────┐
├── Bullets                    │                     │
├── Cartridges       ────────> │   DOPE Session      │
├── Rifles                     │  (denormalized)     │
├── Weather                    │                     │
└── Ranges                     └─────────────────────┘
```

### Key Architectural Principles

1. **Data sources are independent**: Each source module (chronograph, bullets, etc.) operates standalone
2. **DOPE is dependent**: DOPE requires and integrates data from multiple sources
3. **One-way coupling**: Data sources know nothing about DOPE; DOPE imports from all sources
4. **Single source of truth**: Each data element is owned by one source module
5. **Denormalized data**: DOPE sessions contain joined data for performance and convenience

## Data Ownership

### Admin-Owned (Global, Read-Only to Users)
- **Bullets**: Referenced via cartridges
- **Cartridges**: Selected when creating DOPE sessions

### User-Owned (Private, user_id Filtered)
- **DOPE sessions**: The aggregated ballistic profiles
- **DOPE measurements**: Individual shot data with environmental conditions
- **Chronograph sessions**: Source of velocity data (referenced by DOPE)
- **Rifles**: Firearm configurations (referenced by DOPE)
- **Weather sources/measurements**: Environmental data (referenced by DOPE)
- **Ranges**: Shooting locations (referenced by DOPE)

## Key Entities

### DopeSessionModel

Represents a complete DOPE session with denormalized data from all source modules.

**Includes 60+ fields** from joined tables:
- Core session data (name, dates, notes)
- Chronograph statistics (min/max/avg/SD velocity)
- Rifle specifications (name, barrel length, twist rate)
- Cartridge details (make, model, type, lot number)
- Bullet specifications (make, model, weight, BC, sectional density)
- Weather medians (temperature, humidity, pressure, wind)
- Range information (name, distance, location, geometry)

All ballistic data is stored in **metric units** internally.

### DopeMeasurementModel

Represents individual shot measurements with environmental conditions.

**Includes**:
- Shot data (shot number, timestamp)
- Ballistic data (velocity, kinetic energy, power factor)
- Environmental conditions (temperature, pressure, humidity)
- Bore conditions (clean bore, cold bore)
- Targeting data (distance, elevation, windage adjustments)
- Notes

### DopeSessionFilter

Helper class for filtering DOPE sessions by multiple criteria.

**Supports filtering by**:
- Cartridge type, make
- Bullet make, weight
- Rifle name
- Range name, distance
- Environmental conditions (temperature, humidity, wind)
- Date range

## Module Structure

```
dope/
├── models.py              # DopeSessionModel, DopeMeasurementModel
├── service.py             # DopeService (complex JOINs and business logic)
├── filters.py             # DopeSessionFilter (session filtering)
├── protocols.py           # DopeAPIProtocol (type contract)
├── api.py                 # DopeAPI facade (public interface)
├── __init__.py            # Module exports
├── view_tab.py            # Streamlit UI for viewing sessions
├── create_edit_tab.py     # Streamlit UI for creating/editing sessions
├── test_dope.py           # Unit tests
└── test_dope_integration.py  # Integration tests
```

## API

See [API Reference](api-reference.md) for detailed API documentation.

**Session management**:
- `get_sessions_for_user(user_id)` - Get all sessions with joined data
- `get_session_by_id(session_id, user_id)` - Get specific session
- `create_session(session_data, user_id)` - Create new session
- `update_session(session_id, session_data, user_id)` - Update session
- `delete_session(session_id, user_id)` - Delete session
- `delete_sessions_bulk(session_ids, user_id)` - Bulk delete

**Querying and filtering**:
- `search_sessions(user_id, search_term)` - Text search across fields
- `filter_sessions(user_id, filters)` - Multi-criteria filtering
- `get_unique_values(user_id, field_name)` - Get unique values for dropdowns
- `get_session_statistics(user_id)` - Aggregate statistics

**Measurement management**:
- `get_measurements_for_dope_session(dope_session_id, user_id)` - Get shot data
- `create_measurement(measurement_data, user_id)` - Create measurement
- `update_measurement(measurement_id, measurement_data, user_id)` - Update measurement
- `delete_measurement(measurement_id, user_id)` - Delete measurement

**UI helpers**:
- `get_edit_dropdown_options(user_id)` - Get all dropdown options for editing

## Usage

### Creating a DOPE Session

```python
from dope import DopeAPI

# Initialize API
api = DopeAPI(supabase_client)

# Create session from chronograph data
session_data = {
    "session_name": "308 Win @ 100m - Morning Session",
    "chrono_session_id": "chrono-uuid",  # Required - links to velocity data
    "cartridge_id": "cartridge-uuid",     # Required - brings in bullet specs
    "rifle_id": "rifle-uuid",             # Required - firearm configuration
    "range_submission_id": "range-uuid",  # Required - location and distance
    "weather_source_id": "weather-uuid",  # Optional - environmental data
    "notes": "Excellent conditions, testing new load"
}

session = api.create_session(session_data, user_id)

# Session now has complete joined data
print(session.display_name)
print(f"Bullet: {session.bullet_make} {session.bullet_model} {session.bullet_weight}gr")
print(f"Rifle: {session.rifle_name}")
print(f"Avg Velocity: {session.speed_mps_avg} m/s")
```

### Querying DOPE Sessions

```python
# Get all sessions
sessions = api.get_sessions_for_user(user_id)

# Filter sessions
from dope.filters import DopeSessionFilter

filters = DopeSessionFilter(
    cartridge_type="308 Winchester",
    bullet_make="Sierra",
    temperature_range=(15.0, 25.0)  # Celsius
)
filtered = api.filter_sessions(user_id, filters)

# Search sessions
search_results = api.search_sessions(user_id, "MatchKing")
```

### Accessing Measurements

```python
# Get measurements for a session
measurements = api.get_measurements_for_dope_session(session_id, user_id)

for m in measurements:
    print(f"Shot #{m.shot_number}: {m.speed_mps} m/s at {m.temperature_c}°C")
```

## Integration with Source Modules

DOPE integrates with all source modules through:

### Foreign Key Relationships

```
dope_sessions table
├── chrono_session_id → chronograph_sessions (velocity data)
├── cartridge_id → cartridges (brings in bullet via FK)
├── rifle_id → rifles (firearm specs)
├── weather_source_id → weather_source (environmental data)
└── range_submission_id → ranges_submissions (location)
```

### Service Layer Calls

DOPE service calls source module services:
- `ChronographService` - for time windows and measurement stats
- `CartridgeService` - for cartridge/bullet data
- `RifleService` - for rifle specifications
- `WeatherService` - for environmental measurements
- `SubmissionModel` - for range information

### Typed Composite Models

DOPE uses typed models from source modules:
- `BulletModel` (from bullets.models)
- `CartridgeModel` (from cartridges.models)
- `Rifle` (from rifles.models)
- `ChronographSession` (from chronograph.models)
- `WeatherMeasurement` (from weather.models)

## Data Flow

### Creating a DOPE Session

1. User selects **chronograph session** (source of velocity measurements)
2. User selects **cartridge** (which includes bullet via FK)
3. User selects **rifle** used
4. System optionally associates **weather data** (by timestamp or manual)
5. User selects **range** and shooting distance
6. DOPE service validates all references and user ownership
7. Session created with FKs to all sources
8. Chronograph measurements are copied to DOPE measurements
9. Session returned with complete joined data

### Querying DOPE Sessions

When retrieving sessions, DOPE service performs complex JOINs across:
- `dope_sessions` (core data)
- `cartridges` (cartridge details)
- `bullets` (via cartridge FK - ballistic specs)
- `rifles` (rifle configuration)
- `chrono_sessions` (chronograph metadata)
- `weather_source` (weather device/source)
- `ranges_submissions` (location and geometry)

Result: Rich `DopeSessionModel` instances with 60+ fields of denormalized data.

## Why DOPE is Central

DOPE represents the **integration layer** of ChronoLog:

1. **End goal**: All other modules exist to feed data into DOPE sessions
2. **Enables analysis**: By combining disparate data, DOPE unlocks pattern recognition
3. **User-facing**: Most user workflows culminate in creating or viewing DOPE sessions
4. **Drives requirements**: DOPE's needs inform what data source modules must provide
5. **Permanent record**: While chronograph sessions may be ephemeral, DOPE sessions are permanent ballistic profiles

## DOPE vs. Chronograph

**Chronograph sessions** are:
- Raw device output (direct from Garmin Xero, etc.)
- Device-centric (one upload = one session)
- Minimal context (just velocity measurements)
- May be deleted after DOPE creation

**DOPE sessions** are:
- Curated ballistic profiles
- Context-rich (rifle, cartridge, weather, location)
- Permanent record for analysis
- User-centric (organized by shooting scenarios)

## Data Model

See [Models Documentation](models.md) for complete field specifications.

**Metric Units** (internal storage):
- Velocity: meters per second (m/s)
- Energy: Joules (J)
- Temperature: Celsius (°C)
- Pressure: hectopascals (hPa)
- Distance: meters (m)
- Length: millimeters (mm)
- Wind speed: meters per second (m/s)

**Display Units**:
- UI may convert based on user preference
- Units shown in column headers, not in values

## Testing

```bash
# Set up credentials for integration tests
export SUPABASE_SERVICE_ROLE_KEY=$(op item get "Supabase - ChronoLog" --vault "Private" --fields "service role secret")
source venv/bin/activate

# Run DOPE unit tests
python -m pytest dope/test_dope.py -v

# Run DOPE integration tests (requires real Supabase)
python -m pytest dope/test_dope_integration.py -v -m integration

# Test specific functionality
python -m pytest dope/test_dope.py::test_create_session -v
```

## Examples

See [Examples](examples.md) for common usage patterns and pseudocode.

## Performance Considerations

### Complex JOINs

DOPE queries perform 6-table JOINs to construct denormalized sessions. This is intentional for:
- **Performance**: Single query vs. N+1 queries
- **Type safety**: Strongly-typed composite models
- **Convenience**: All data available in one model

### Denormalized Storage

DOPE sessions store denormalized data (cartridge name, bullet specs, etc.) to:
- Reduce JOINs on read-heavy operations
- Preserve historical data (if source data changes)
- Enable fast filtering and searching

## Future Enhancements

Potential future features:
- **Analytics engine**: Trend analysis across sessions
- **Load development**: Automatic load recommendations
- **Ballistic calculator integration**: Drop tables and trajectory
- **Export capabilities**: CSV, PDF reports
- **Session comparison**: Side-by-side analysis

## Next Steps

- [API Reference](api-reference.md) - Detailed API documentation
- [Models](models.md) - Data model specifications (60+ fields!)
- [Examples](examples.md) - Usage examples and patterns
- [Architecture Docs](../../architecture/01-dope-system.md) - DOPE system architecture

## Related Documentation

- [Architecture: DOPE System](../../architecture/01-dope-system.md)
- [Architecture: Data Sources](../../architecture/02-data-sources.md)
- [Architecture: Data Flow](../../architecture/03-data-flow.md)

---

**Module Type**: Convergence Point (Aggregator)
**Dependencies**: Chronograph, Bullets, Cartridges, Rifles, Weather, Ranges
**Used By**: UI, Analytics, Reporting
**Status**: Stable