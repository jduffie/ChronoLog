# DOPE Module Examples

## Overview

This document provides pseudocode examples showing common usage patterns for the DOPE module API.

DOPE is the convergence point - it aggregates data from chronograph, cartridges (with bullets), rifles, weather, and ranges into unified ballistic profiles.

All examples assume you have initialized the API:

```python
from dope import DopeAPI

api = DopeAPI(supabase_client)
```

---

## Creating DOPE Sessions

### Example 1: Basic Session Creation

Create a DOPE session from existing source data.

```python
# User has already:
# - Uploaded chronograph session (velocity data)
# - Created rifle in rifles module
# - Selected range/location

session_data = {
    "session_name": "308 Win @ 100m - Morning Session",
    "chrono_session_id": "chrono-uuid",     # Required - velocity source
    "cartridge_id": "cartridge-uuid",        # Required - includes bullet via FK
    "rifle_id": "rifle-uuid",                # Required - firearm config
    "range_submission_id": "range-uuid",     # Required - location
    "weather_source_id": "weather-uuid",     # Optional - environmental data
    "notes": "Excellent conditions, testing new load"
}

# Create session (auto-creates measurements from chronograph)
session = api.create_session(session_data, user_id, auto_create_measurements=True)

# Session now has complete denormalized data from 6+ tables
print(f"Created: {session.display_name}")
print(f"  ID: {session.id}")
print(f"  Rifle: {session.rifle_name} ({session.rifle_barrel_length_cm}cm barrel)")
print(f"  Cartridge: {session.cartridge_make} {session.cartridge_model}")
print(f"  Bullet: {session.bullet_make} {session.bullet_model} {session.bullet_weight}gr")
print(f"  Bore Diameter: {session.bore_diameter_land_mm}mm")  # MANDATORY field
print(f"  Range: {session.range_name} at {session.range_distance_m}m")
print(f"  Time: {session.start_time} to {session.end_time}")
print(f"  Velocity: {session.speed_mps_avg}±{session.speed_mps_std_dev} m/s")
print(f"  Weather: {session.temperature_c_median}°C")
```

**Notes**:
- `start_time` and `end_time` automatically pulled from chronograph session
- Velocity statistics calculated from chronograph measurements
- Measurements automatically created from chronograph data
- All denormalized data available immediately

---

### Example 2: Session Creation Without Weather

Create session when no weather data is available.

```python
session_data = {
    "session_name": "Load Development - No Weather",
    "chrono_session_id": "chrono-uuid",
    "cartridge_id": "cartridge-uuid",
    "rifle_id": "rifle-uuid",
    "range_submission_id": "range-uuid",
    # weather_source_id is optional - omit if no weather data
    "notes": "Indoor range, no environmental logging"
}

session = api.create_session(session_data, user_id)

# Session created without weather data
print(f"Created: {session.session_name}")
print(f"  Weather data: {session.temperature_c_median}")  # None
```

---

### Example 3: Creating Session with Manual Measurements

Create session but add measurements manually instead of auto-copying.

```python
session_data = {
    "session_name": "Custom Measurement Session",
    "chrono_session_id": "chrono-uuid",
    "cartridge_id": "cartridge-uuid",
    "rifle_id": "rifle-uuid",
    "range_submission_id": "range-uuid"
}

# Don't auto-create measurements
session = api.create_session(session_data, user_id, auto_create_measurements=False)

# Manually add measurements with custom data
for shot_num in range(1, 11):
    measurement_data = {
        "dope_session_id": session.id,
        "shot_number": shot_num,
        "speed_mps": 792.5 + (shot_num * 0.5),  # Varying velocities
        "temperature_c": 21.0,
        "cold_bore": "yes" if shot_num == 1 else "no"
    }

    measurement = api.create_measurement(measurement_data, user_id)
    print(f"Created shot #{measurement.shot_number}")
```

---

## Querying DOPE Sessions

### Example 4: Get All Sessions

Retrieve all sessions for a user.

```python
sessions = api.get_sessions_for_user(user_id)

print(f"Total sessions: {len(sessions)}")

for session in sessions:
    print(f"\n{session.session_name}")
    print(f"  Date: {session.datetime_local}")
    print(f"  Cartridge: {session.cartridge_display}")
    print(f"  Bullet: {session.bullet_display}")
    print(f"  Rifle: {session.rifle_name}")
    print(f"  Avg Velocity: {session.speed_mps_avg} m/s")
    print(f"  Location: {session.range_name}")

# Sessions ordered by created_at desc (newest first)
```

---

### Example 5: Get Specific Session

Retrieve a single session by ID.

```python
session_id = "123e4567-..."

session = api.get_session_by_id(session_id, user_id)

if session:
    print(f"Session: {session.display_name}")
    print(f"\nRifle Configuration:")
    print(f"  Name: {session.rifle_name}")
    print(f"  Barrel Length: {session.rifle_barrel_length_cm}cm")
    print(f"  Twist Rate: 1:{session.rifle_barrel_twist_in_per_rev}")

    print(f"\nCartridge & Bullet:")
    print(f"  Cartridge: {session.cartridge_make} {session.cartridge_model}")
    print(f"  Type: {session.cartridge_type}")
    print(f"  Bullet: {session.bullet_make} {session.bullet_model}")
    print(f"  Weight: {session.bullet_weight}gr")
    print(f"  BC (G7): {session.ballistic_coefficient_g7}")
    print(f"  Bore Diameter: {session.bore_diameter_land_mm}mm")

    print(f"\nBallistics:")
    print(f"  Velocity: {session.speed_mps_avg}±{session.speed_mps_std_dev} m/s")
    print(f"  Range: {session.speed_mps_min}-{session.speed_mps_max} m/s")

    print(f"\nEnvironment:")
    print(f"  Temperature: {session.temperature_c_median}°C")
    print(f"  Humidity: {session.relative_humidity_pct_median}%")
    print(f"  Pressure: {session.barometric_pressure_hpa_median} hPa")
    print(f"  Wind: {session.wind_speed_mps_median} m/s @ {session.wind_direction_deg_median}°")

    print(f"\nLocation:")
    print(f"  Range: {session.range_name}")
    print(f"  Distance: {session.range_distance_m}m")
    print(f"  Coordinates: {session.lat}, {session.lon}")
    print(f"  Map: {session.location_hyperlink}")
else:
    print("Session not found or access denied")
```

---

## Searching and Filtering

### Example 6: Text Search

Search sessions by text across multiple fields.

```python
# Search for sessions with "Sierra 168"
search_results = api.search_sessions(user_id, "Sierra 168")

print(f"Found {len(search_results)} sessions matching 'Sierra 168'")

for session in search_results:
    print(f"  {session.session_name}: {session.bullet_make} {session.bullet_model} {session.bullet_weight}gr")

# Search in specific fields only
custom_results = api.search_sessions(
    user_id,
    "MatchKing",
    search_fields=["bullet_model", "notes"]
)

print(f"\nFound {len(custom_results)} sessions with 'MatchKing' in bullet_model or notes")
```

---

### Example 7: Filtered Search by Cartridge Type

Find all sessions for a specific cartridge type.

```python
from dope.filters import DopeSessionFilter

# Filter by cartridge type
filters = DopeSessionFilter(
    cartridge_type="308 Winchester"
)

sessions_308 = api.filter_sessions(user_id, filters)

print(f"Found {len(sessions_308)} sessions with 308 Winchester")

for session in sessions_308:
    print(f"  {session.session_name}")
    print(f"    {session.bullet_make} {session.bullet_model} {session.bullet_weight}gr")
    print(f"    Avg: {session.speed_mps_avg} m/s")
```

---

### Example 8: Complex Multi-Criteria Filtering

Filter by multiple criteria.

```python
from dope.filters import DopeSessionFilter

# Complex filter: 308 Win, Sierra bullets, 168-180gr, good weather
filters = DopeSessionFilter(
    cartridge_type="308 Winchester",
    bullet_make="Sierra",
    bullet_weight_range=(168, 180),           # Grains
    temperature_range=(15.0, 25.0),           # Celsius
    humidity_range=(30.0, 70.0),              # Percentage
    wind_speed_range=(0.0, 3.0),              # m/s (light wind only)
    distance_range=(100.0, 300.0)             # Meters
)

filtered_sessions = api.filter_sessions(user_id, filters)

print(f"Found {len(filtered_sessions)} sessions matching all criteria")

for session in filtered_sessions:
    print(f"\n{session.session_name}")
    print(f"  Bullet: {session.bullet_make} {session.bullet_model} {session.bullet_weight}gr")
    print(f"  Velocity: {session.speed_mps_avg}±{session.speed_mps_std_dev} m/s")
    print(f"  Weather: {session.temperature_c_median}°C, {session.wind_speed_mps_median} m/s")
    print(f"  Distance: {session.range_distance_m}m")
```

---

### Example 9: Date Range Filtering

Find sessions within a date range.

```python
from datetime import datetime, timedelta
from dope.filters import DopeSessionFilter

# Get sessions from last 30 days
thirty_days_ago = datetime.now() - timedelta(days=30)
filters = DopeSessionFilter(
    date_from=thirty_days_ago
)

recent_sessions = api.filter_sessions(user_id, filters)

print(f"Sessions in last 30 days: {len(recent_sessions)}")

# Get sessions from specific date range
filters = DopeSessionFilter(
    date_from=datetime(2025, 1, 1),
    date_to=datetime(2025, 3, 31)
)

q1_sessions = api.filter_sessions(user_id, filters)

print(f"Q1 2025 sessions: {len(q1_sessions)}")
```

---

## Working with Measurements

### Example 10: Get Session Measurements

Retrieve all measurements for a session.

```python
measurements = api.get_measurements_for_dope_session(session_id, user_id)

print(f"Session has {len(measurements)} shots")
print(f"\nShot Data:")

for m in measurements:
    print(f"\nShot #{m.shot_number}:")
    print(f"  Time: {m.datetime_shot}")
    print(f"  Velocity: {m.speed_mps} m/s")
    print(f"  Energy: {m.ke_j} J")
    print(f"  Power Factor: {m.power_factor_kgms}")

    if m.has_environmental_data():
        print(f"  Environment: {m.environmental_display}")

    if m.has_targeting_data():
        print(f"  Targeting: Az {m.azimuth_deg}°, El {m.elevation_angle_deg}°")

    if m.shot_notes:
        print(f"  Notes: {m.shot_notes}")
```

---

### Example 11: Create Individual Measurement

Add a single measurement to a session.

```python
measurement_data = {
    "dope_session_id": session_id,
    "shot_number": 11,
    "datetime_shot": datetime.now(),
    "speed_mps": 795.2,
    "ke_j": 3478.5,
    "temperature_c": 22.5,
    "pressure_hpa": 1015.0,
    "humidity_pct": 60.0,
    "clean_bore": "no",
    "cold_bore": "no",
    "distance_m": 100.0,
    "elevation_adjustment": "0.0",
    "windage_adjustment": "0.0",
    "shot_notes": "Good shot, center group"
}

measurement = api.create_measurement(measurement_data, user_id)

print(f"Created shot #{measurement.shot_number}")
print(f"  Velocity: {measurement.speed_mps} m/s")
print(f"  {measurement.environmental_display}")
```

---

### Example 12: Update Measurement with Notes

Add or update notes for a shot.

```python
measurement_id = "meas-uuid"

update_data = {
    "shot_notes": "Flyer - wind gust caught during trigger press"
}

measurement = api.update_measurement(measurement_id, update_data, user_id)

if measurement:
    print(f"Updated shot #{measurement.shot_number}")
    print(f"  New notes: {measurement.shot_notes}")
```

---

## Updating Sessions

### Example 13: Update Session Notes

Add notes to a session after shooting.

```python
update_data = {
    "notes": "Windy conditions in afternoon, groups opened up. Consider sheltered position next time."
}

session = api.update_session(session_id, update_data, user_id)

if session:
    print(f"Updated: {session.session_name}")
    print(f"  Notes: {session.notes}")
```

---

### Example 14: Change Session Weather Source

Update the weather source for a session.

```python
# Switch to different weather source
update_data = {
    "weather_source_id": "new-weather-uuid"
}

session = api.update_session(session_id, update_data, user_id)

if session:
    print(f"Updated weather source to: {session.weather_source_name}")
    # Note: Median weather values were automatically cleared
    # They'll need to be recalculated from the new weather source
```

---

## UI Helper Methods

### Example 15: Populate Edit Form Dropdowns

Get all dropdown options for editing a session.

```python
# Get all dropdown options in one call
options = api.get_edit_dropdown_options(user_id)

# Populate rifle dropdown
print("Rifles:")
for rifle in options['rifles']:
    print(f"  {rifle['id']}: {rifle['name']}")

# Populate cartridge dropdown
print("\nCartridges:")
for cartridge in options['cartridges']:
    print(f"  {cartridge['id']}: {cartridge['name']}")

# Populate chronograph sessions dropdown
print("\nChronograph Sessions:")
for chrono in options['chrono_sessions']:
    print(f"  {chrono['id']}: {chrono['name']}")

# Populate weather sources dropdown
print("\nWeather Sources:")
for weather in options['weather_sources']:
    print(f"  {weather['id']}: {weather['name']}")

# Populate ranges dropdown
print("\nRanges:")
for range_option in options['ranges']:
    print(f"  {range_option['id']}: {range_option['name']}")
```

---

### Example 16: Get Unique Values for Filters

Populate filter dropdowns with user's actual data.

```python
# Get unique cartridge types from user's sessions
cartridge_types = api.get_unique_values(user_id, "cartridge_type")

print("Cartridge Types (from your sessions):")
for ct in cartridge_types:
    print(f"  [ ] {ct}")

# Result:
# [ ] 223 Remington
# [ ] 308 Winchester
# [ ] 6.5 Creedmoor

# Get unique bullet makes
bullet_makes = api.get_unique_values(user_id, "bullet_make")

print("\nBullet Manufacturers:")
for bm in bullet_makes:
    print(f"  [ ] {bm}")

# Get unique rifle names
rifle_names = api.get_unique_values(user_id, "rifle_name")

print("\nRifles:")
for rn in rifle_names:
    print(f"  [ ] {rn}")
```

---

## Analytics and Statistics

### Example 17: Session Statistics

Get aggregate statistics across all sessions.

```python
stats = api.get_session_statistics(user_id)

print("DOPE Session Statistics:")
print(f"  Total sessions: {stats['total_sessions']}")
print(f"  Total shots: {stats['total_measurements']}")
print(f"  Unique rifles: {stats['unique_rifles']}")
print(f"  Unique cartridges: {stats['unique_cartridges']}")

if stats.get('date_range'):
    print(f"\nDate Range:")
    print(f"  First session: {stats['date_range']['first']}")
    print(f"  Latest session: {stats['date_range']['last']}")

# Use for dashboard display
display_dashboard_metrics(stats)
```

---

## Deleting Sessions

### Example 18: Delete Single Session

Delete a session and all its measurements.

```python
deleted = api.delete_session(session_id, user_id)

if deleted:
    print("Session deleted successfully")
    print("  All measurements also deleted (cascade)")
else:
    print("Session not found or access denied")
```

**Notes**:
- Deletes session and all measurements (cascade)
- Does NOT delete source data (chronograph, rifle, weather, range)
- No undo - deletion is permanent

---

### Example 19: Bulk Delete Sessions

Delete multiple sessions efficiently.

```python
# Select sessions to delete
session_ids_to_delete = [
    "session-id-1",
    "session-id-2",
    "session-id-3",
    "session-id-4"
]

result = api.delete_sessions_bulk(session_ids_to_delete, user_id)

print(f"Bulk delete results:")
print(f"  Requested: {len(session_ids_to_delete)}")
print(f"  Deleted: {result['deleted_count']}")

if result['failed_ids']:
    print(f"  Failed: {len(result['failed_ids'])}")
    for failed_id in result['failed_ids']:
        print(f"    - {failed_id}")
```

---

## Integration with Source Modules

### Example 20: Creating Complete Workflow

Complete workflow from chronograph upload to DOPE session.

```python
from chronograph import ChronographAPI
from rifles import RifleAPI
from dope import DopeAPI

chrono_api = ChronographAPI(supabase_client)
rifle_api = RifleAPI(supabase_client)
dope_api = DopeAPI(supabase_client)

# Step 1: User uploads chronograph file
chrono_file_path = "garmin_session.xlsx"
chrono_session = chrono_api.import_garmin_file(chrono_file_path, user_id)

print(f"Chronograph session created: {chrono_session.id}")
print(f"  Shots: {len(chrono_session.measurements)}")
print(f"  Avg Velocity: {chrono_session.avg_velocity_mps} m/s")

# Step 2: User selects existing rifle
rifles = rifle_api.get_rifles_for_user(user_id)
selected_rifle = rifles[0]  # User selects from UI

# Step 3: User selects cartridge (from global catalog)
# cartridge_id comes from UI selection

# Step 4: User selects range
# range_id comes from UI selection

# Step 5: Create DOPE session aggregating all data
dope_session_data = {
    "session_name": f"{selected_rifle.name} - {chrono_session.session_name}",
    "chrono_session_id": chrono_session.id,
    "cartridge_id": selected_cartridge_id,
    "rifle_id": selected_rifle.id,
    "range_submission_id": selected_range_id,
    "notes": "Auto-created from chronograph upload"
}

dope_session = dope_api.create_session(dope_session_data, user_id)

print(f"\nDOPE session created: {dope_session.id}")
print(f"  Name: {dope_session.session_name}")
print(f"  Rifle: {dope_session.rifle_name}")
print(f"  Cartridge: {dope_session.cartridge_type}")
print(f"  Bullet: {dope_session.bullet_make} {dope_session.bullet_model} {dope_session.bullet_weight}gr")
print(f"  Bore Diameter: {dope_session.bore_diameter_land_mm}mm")
print(f"  Velocity: {dope_session.speed_mps_avg}±{dope_session.speed_mps_std_dev} m/s")
print(f"  Measurements: {len(dope_api.get_measurements_for_dope_session(dope_session.id, user_id))}")
```

---

### Example 21: Accessing Denormalized Data

Show how denormalized data simplifies access.

```python
# Get session
session = api.get_session_by_id(session_id, user_id)

# All data flattened - no nested object navigation
# Instead of: session.cartridge.bullet.bore_diameter_land_mm
# You have:   session.bore_diameter_land_mm

print("Direct field access (no nested objects):")
print(f"  Session: {session.session_name}")
print(f"  Rifle: {session.rifle_name} ({session.rifle_barrel_length_cm}cm)")
print(f"  Cartridge: {session.cartridge_make} {session.cartridge_model}")
print(f"  Type: {session.cartridge_type}")
print(f"  Bullet: {session.bullet_make} {session.bullet_model}")
print(f"  Weight: {session.bullet_weight}gr")
print(f"  Bore: {session.bore_diameter_land_mm}mm")  # MANDATORY field
print(f"  BC (G7): {session.ballistic_coefficient_g7}")
print(f"  Range: {session.range_name} @ {session.range_distance_m}m")
print(f"  Weather: {session.temperature_c_median}°C")

# All from single session object - no additional queries needed
```

---

## Load Development Analysis

### Example 22: Compare Multiple Loads

Compare different bullet weights for load development.

```python
from dope.filters import DopeSessionFilter

# Get all 308 Win sessions
filters = DopeSessionFilter(cartridge_type="308 Winchester")
all_308_sessions = api.filter_sessions(user_id, filters)

# Group by bullet weight
sessions_by_weight = {}
for session in all_308_sessions:
    weight = session.bullet_weight
    if weight not in sessions_by_weight:
        sessions_by_weight[weight] = []
    sessions_by_weight[weight].append(session)

# Compare results
print("Load Development Results (308 Winchester):")
for weight in sorted(sessions_by_weight.keys()):
    sessions = sessions_by_weight[weight]
    avg_velocities = [s.speed_mps_avg for s in sessions if s.speed_mps_avg]
    avg_sds = [s.speed_mps_std_dev for s in sessions if s.speed_mps_std_dev]

    if avg_velocities:
        mean_velocity = sum(avg_velocities) / len(avg_velocities)
        mean_sd = sum(avg_sds) / len(avg_sds) if avg_sds else 0

        print(f"\n{weight}gr bullets ({len(sessions)} sessions):")
        print(f"  Avg Velocity: {mean_velocity:.1f} m/s")
        print(f"  Avg SD: {mean_sd:.2f} m/s")
        print(f"  Sessions:")
        for s in sessions:
            print(f"    - {s.session_name}: {s.speed_mps_avg} m/s")
```

---

### Example 23: Environmental Impact Analysis

Analyze how temperature affects velocity.

```python
from dope.filters import DopeSessionFilter

# Get all sessions for a specific load
filters = DopeSessionFilter(
    cartridge_type="308 Winchester",
    bullet_make="Sierra",
    bullet_weight_range=(168, 168)  # Exact weight
)

sessions = api.filter_sessions(user_id, filters)

# Group by temperature ranges
temp_ranges = {
    "Cold (0-10°C)": (0, 10),
    "Cool (10-20°C)": (10, 20),
    "Moderate (20-30°C)": (20, 30),
    "Warm (30-40°C)": (30, 40)
}

print("Temperature vs. Velocity Analysis (Sierra 168gr):")

for range_name, (min_temp, max_temp) in temp_ranges.items():
    range_sessions = [
        s for s in sessions
        if s.temperature_c_median and min_temp <= s.temperature_c_median < max_temp
    ]

    if range_sessions:
        velocities = [s.speed_mps_avg for s in range_sessions if s.speed_mps_avg]
        if velocities:
            avg_velocity = sum(velocities) / len(velocities)
            print(f"\n{range_name}:")
            print(f"  Sessions: {len(range_sessions)}")
            print(f"  Avg Velocity: {avg_velocity:.1f} m/s")
```

---

## Error Handling

### Example 24: Handle Not Found Gracefully

Handle cases where session doesn't exist.

```python
session_id = user_provided_session_id()

session = api.get_session_by_id(session_id, user_id)

if not session:
    display_error("Session not found or you don't have access.")
    return

# Continue with session data
process_session(session)
```

---

### Example 25: Handle Database Errors

Handle database connection issues.

```python
try:
    sessions = api.get_sessions_for_user(user_id)
    display_sessions(sessions)

except Exception as e:
    log_error(f"Failed to load DOPE sessions: {e}")
    display_error("Unable to load sessions. Please try again later.")
```

---

### Example 26: Validate Before Creation

Validate data before creating session.

```python
# Validate required fields
required_fields = [
    "session_name",
    "chrono_session_id",
    "cartridge_id",
    "rifle_id",
    "range_submission_id"
]

session_data = get_user_input()

missing = [field for field in required_fields if not session_data.get(field)]

if missing:
    display_error(f"Missing required fields: {', '.join(missing)}")
    return

# Validate user owns referenced resources
try:
    # Check if rifle belongs to user
    rifle = rifle_api.get_rifle_by_id(session_data['rifle_id'], user_id)
    if not rifle:
        display_error("Selected rifle not found")
        return

    # Create session
    session = api.create_session(session_data, user_id)
    display_success(f"Session created: {session.display_name}")

except ValueError as e:
    display_error(f"Validation error: {e}")
except Exception as e:
    log_error(f"Creation failed: {e}")
    display_error("Failed to create session. Please try again.")
```

---

## Next Steps

- [API Reference](api-reference.md) - Complete API documentation
- [Models](models.md) - Data model specifications (60+ fields!)
- [Module README](README.md) - Overview and integration

---

**Examples Version**: 1.0
**Last Updated**: 2025-10-19

**Important Notes**:
- All examples use pseudocode (not actual implementation)
- All ballistic data is metric
- `bore_diameter_land_mm` is MANDATORY (NOT NULL) in all DOPE sessions
- DOPE is the convergence point - only module that couples with others