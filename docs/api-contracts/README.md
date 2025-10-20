# ChronoLog API Contracts

This directory contains the API contract specifications for all ChronoLog modules. Each module exposes a clean, type-safe API for accessing its functionality.

## Overview

ChronoLog uses Python Protocol classes to define API contracts. This approach provides:
- **Type safety**: Static type checking with mypy
- **Structural subtyping**: Any class implementing the protocol can be used
- **Clear interfaces**: Explicit contracts for module boundaries
- **Testability**: Easy to mock for unit tests

## Module APIs

### Data Source Modules (Independent)

These modules are fully independent and have no dependencies on other modules:

#### 1. Bullets API
- **Protocol**: `BulletsAPIProtocol` (bullets/protocols.py)
- **Implementation**: `BulletsAPI` (bullets/api.py)
- **Access Model**: Admin-owned, globally readable
- **Documentation**: [API Reference](../modules/bullets/api-reference.md)

**Key Methods**:
- `get_all_bullets()` - List all bullets
- `get_bullet_by_id(bullet_id)` - Get specific bullet
- `filter_bullets(manufacturer, bore_diameter_mm, weight_grains)` - Filter catalog
- `get_unique_manufacturers()` - Dropdown options
- Admin methods: `create_bullet()`, `update_bullet()`, `delete_bullet()`

#### 2. Cartridges API
- **Protocol**: `CartridgesAPIProtocol` (cartridges/protocols.py)
- **Implementation**: `CartridgesAPI` (cartridges/api.py)
- **Access Model**: Admin-owned, globally readable
- **Documentation**: [API Reference](../modules/cartridges/api-reference.md)

**Key Methods**:
- `get_all_cartridges()` - List all cartridges with bullet data
- `get_cartridge_by_id(cartridge_id)` - Get specific cartridge
- `filter_cartridges(make, cartridge_type_id)` - Filter catalog
- `get_unique_makes()` - Dropdown options
- Admin methods: `create_cartridge()`, `update_cartridge()`, `delete_cartridge()`

**Special Notes**:
- Cartridges have FK to bullets (includes joined bullet data)
- Each cartridge is pre-configured with a specific bullet

#### 3. Rifles API
- **Protocol**: `RiflesAPIProtocol` (rifles/protocols.py)
- **Implementation**: `RiflesAPI` (rifles/api.py)
- **Access Model**: User-owned (user_id required)
- **Documentation**: [API Reference](../modules/rifles/api-reference.md)

**Key Methods**:
- `get_all_rifles(user_id)` - List user's rifles
- `get_rifle_by_id(rifle_id, user_id)` - Get specific rifle
- `create_rifle(rifle_data, user_id)` - Create new rifle
- `update_rifle(rifle_id, rifle_data, user_id)` - Update rifle
- `delete_rifle(rifle_id, user_id)` - Delete rifle
- `filter_rifles(user_id, cartridge_type_id)` - Filter by cartridge type

#### 4. Weather API
- **Protocol**: `WeatherAPIProtocol` (weather/protocols.py)
- **Implementation**: `WeatherAPI` (weather/api.py)
- **Access Model**: User-owned (user_id required)
- **Documentation**: [API Reference](../modules/weather/api-reference.md)

**Key Methods**:
- Source Management:
  - `get_all_sources(user_id)` - List weather sources/devices
  - `create_source(source_data, user_id)` - Create weather source
  - `create_or_get_source_from_device_info()` - Smart device identification
- Measurement Management:
  - `get_measurements_for_source(source_id, user_id)` - Get measurements
  - `create_measurement(measurement_data, user_id)` - Single measurement
  - `create_measurements_batch(measurements, user_id)` - Batch CSV import
  - `filter_measurements(user_id, source_id, start_date, end_date)` - Query

**Special Notes**:
- Supports device adapters (Kestrel, etc.) for CSV import
- All measurements in metric (temperature_c, pressure_hpa, wind_speed_mps)
- Batch import for efficiency

#### 5. Chronograph API
- **Protocol**: `ChronographAPIProtocol` (chronograph/protocols.py)
- **Implementation**: `ChronographAPI` (chronograph/api.py)
- **Access Model**: User-owned (user_id required)
- **Documentation**: [API Reference](../modules/chronograph/api-reference.md)

**Key Methods**:
- Source Management:
  - `get_all_sources(user_id)` - List chronograph devices
  - `create_source(source_data, user_id)` - Create device
- Session Management:
  - `get_all_sessions(user_id)` - List sessions with statistics
  - `create_session(session_data, user_id)` - Create session
  - `get_session_statistics(session_id, user_id)` - Velocity stats
- Measurement Management:
  - `get_measurements_for_session(session_id, user_id)` - Shot data
  - `create_measurements_batch(session_id, measurements, user_id)` - Batch import

**Special Notes**:
- Supports device adapters (Garmin Xero, etc.) for CSV/Excel import
- Automatic statistics calculation (mean, SD, ES, high/low)
- All velocities in metric (speed_mps, not fps)

### Convergence Module (Couples with All Modules)

#### 6. DOPE API
- **Protocol**: `DopeAPIProtocol` (dope/protocols.py)
- **Implementation**: `DopeAPI` (dope/api.py)
- **Access Model**: User-owned (user_id required)
- **Documentation**: [API Reference](../modules/dope/api-reference.md)

**Key Methods**:
- Session Management:
  - `get_sessions_for_user(user_id)` - List all sessions with joined data
  - `get_session_by_id(session_id, user_id)` - Get session with full denormalized data
  - `create_session(session_data, user_id, auto_create_measurements)` - Create session
  - `update_session(session_id, session_data, user_id)` - Update session
  - `delete_session(session_id, user_id)` - Delete session and measurements
  - `delete_sessions_bulk(session_ids, user_id)` - Bulk delete
- Querying & Filtering:
  - `search_sessions(user_id, search_term, search_fields)` - Text search
  - `filter_sessions(user_id, filters)` - Multi-criteria filtering
  - `get_unique_values(user_id, field_name)` - Dropdown options
  - `get_session_statistics(user_id)` - Aggregate statistics
- Measurement Management:
  - `get_measurements_for_dope_session(dope_session_id, user_id)` - Shot data
  - `create_measurement(measurement_data, user_id)` - Create measurement
  - `update_measurement(measurement_id, measurement_data, user_id)` - Update
  - `delete_measurement(measurement_id, user_id)` - Delete
- UI Helpers:
  - `get_edit_dropdown_options(user_id)` - All dropdown options

**Special Notes**:
- **THE MOST IMPORTANT MODULE** - convergence point for all ballistic data
- Only module allowed to couple with others (aggregation layer)
- Performs complex JOINs across 6+ tables
- Returns denormalized data (60+ fields from cartridges, bullets, rifles, chronograph, weather, ranges)
- Automatic measurements creation from chronograph sessions
- Weather association via time window matching
- All metric units (m/s, J, °C, hPa, m, mm)

### Pending Refactoring

#### 7. Mapping API
- **Status**: Pending architectural refactor
- **Current State**: Existing interface via Range_Library and range_models
- **Documentation**: [Mapping Module Status](../modules/mapping/README.md)

**Planned API** (future):
- Range catalog management
- Geographic coordinates
- Range submission workflows
- User and public ranges

**Current Usage**:
- DOPE references ranges via `range_submission_id` FK to `ranges_submissions` table
- Will be refactored to follow standard module patterns in future phase

---

## API Usage Patterns

### Common Pattern: User-Owned Data

All user-owned modules (rifles, weather, chronograph, DOPE) follow this pattern:

```python
# Get user's data
from rifles.api import RiflesAPI

api = RiflesAPI(supabase_client)
rifles = api.get_all_rifles(user_id)

# Create new item
rifle_data = {
    "name": "Remington 700",
    "cartridge_type_id": "308-win-uuid",
    "barrel_length": 60.96,  # cm (metric!)
}
rifle = api.create_rifle(rifle_data, user_id)

# Update item
update_data = {"notes": "New scope installed"}
updated_rifle = api.update_rifle(rifle.id, update_data, user_id)
```

### Common Pattern: Admin-Owned Data

Admin-owned modules (bullets, cartridges) are globally readable:

```python
# All users can read
from bullets.api import BulletsAPI

api = BulletsAPI(supabase_client)
bullets = api.get_all_bullets()  # No user_id needed for read
sierra_168 = api.filter_bullets(manufacturer="Sierra", weight_grains=168)

# Only admin can write
if is_admin(user):
    bullet_data = {
        "manufacturer": "Sierra",
        "model": "MatchKing",
        "weight_grains": 168,
        # ... metric fields
    }
    bullet = api.create_bullet(bullet_data)
```

### Special Pattern: DOPE Aggregation

DOPE brings together all source modules:

```python
# DOPE creates denormalized views
from dope.api import DopeAPI

api = DopeAPI(supabase_client)

# Create session aggregating all sources
session_data = {
    "session_name": "308 Win Load Development",
    "cartridge_id": "cart-uuid",       # -> cartridges -> bullets
    "rifle_id": "rifle-uuid",          # -> rifles
    "chrono_session_id": "chrono-uuid", # -> chrono_sessions -> measurements
    "weather_source_id": "weather-uuid", # -> weather_source -> measurements
    "range_submission_id": "range-uuid", # -> ranges
}
session = api.create_session(session_data, user_id)

# Retrieve denormalized data (60+ fields from 6+ tables)
session = api.get_session_by_id(session.id, user_id)
print(session.rifle_name)           # From rifles table
print(session.cartridge_make)       # From cartridges table
print(session.bullet_make)          # From bullets table (via cartridges FK)
print(session.bore_diameter_land_mm) # From bullets (MANDATORY)
print(session.speed_mps_avg)        # From chrono_sessions statistics
print(session.temperature_c_median) # From weather measurements (median)
print(session.range_distance_m)     # From ranges_submissions
```

---

## Type Safety

All APIs use Python Protocol classes for type checking:

```python
from typing import Protocol
from bullets.protocols import BulletsAPIProtocol

def use_bullets_api(api: BulletsAPIProtocol):
    """Any class implementing BulletsAPIProtocol can be passed."""
    bullets = api.get_all_bullets()
    # Type checker validates method signatures
```

---

## Metric Units

**CRITICAL**: All internal storage and API operations use metric units:
- Velocity: m/s (not fps)
- Energy: Joules (not ft-lbs)
- Temperature: °C (not °F)
- Pressure: hPa (not inHg)
- Distance: meters (not yards)
- Length: mm/cm (not inches)

**Exception**: Bullet weights stored as grams but always displayed in grains (ballistics standard).

**Conversion**: Use device adapters for import and UI formatters for display.

---

## Module Independence

### Independent Modules (No Dependencies)
- Bullets
- Cartridges (depends only on bullets via FK)
- Rifles
- Weather
- Chronograph

**Rules**:
- No JOINs to other module tables
- Use batch loading APIs if cross-module data needed
- Fully testable in isolation

### Convergence Module (Explicit Coupling)
- DOPE

**Special Permissions**:
- Can import model classes from all source modules
- Can perform JOINs for performance
- Creates typed composite models (DopeSessionModel)
- Explicitly allowed to couple (it's the aggregator)

---

## Testing with Protocols

Protocols make testing easy:

```python
from typing import List
from bullets.protocols import BulletsAPIProtocol
from bullets.models import BulletModel

class MockBulletsAPI:
    """Test mock implementing BulletsAPIProtocol."""

    def get_all_bullets(self) -> List[BulletModel]:
        return [
            BulletModel(id="1", manufacturer="Sierra", model="MatchKing", weight_grains=168, ...)
        ]

    # Implement other protocol methods...

def test_feature():
    mock_api = MockBulletsAPI()
    # Use mock_api as BulletsAPIProtocol
    result = feature_using_bullets(mock_api)
    assert result is not None
```

---

## Next Steps

### For Developers

**Adding a new data source module**:
1. Follow pattern from bullets/rifles/weather/chronograph
2. Create `models.py` with dataclasses
3. Create `service.py` with user isolation
4. Define `protocols.py` with Python Protocol class
5. Implement `api.py` facade
6. Write documentation (README, api-reference, models, examples)

**Integrating with DOPE**:
1. Add FK in `dope_sessions` table
2. Add field to `DopeSessionModel`
3. Update `DopeService` JOIN queries
4. Update `_flatten_joined_record()` method
5. Document in DOPE module docs

### For AI Agents

When working with ChronoLog APIs:
1. Use API facades, not service classes directly
2. Always pass `user_id` for user-owned data
3. Use metric units for all data
4. Import model classes for type safety
5. DOPE is the only module that couples with others
6. Follow existing protocol patterns for new APIs

---

## Documentation Status

| Module | Protocol | API | README | API Ref | Models | Examples |
|--------|----------|-----|--------|---------|--------|----------|
| Bullets | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Cartridges | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Rifles | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Weather | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Chronograph | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DOPE | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Mapping | ⏳ | ⏳ | ✅ | ⏳ | ⏳ | ⏳ |

**Legend**: ✅ Complete | ⏳ Pending Refactor

---

**Last Updated**: 2025-10-19
**Phase**: Phase 2 (API Contracts) - Complete