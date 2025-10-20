# Chronograph Module Examples

## Overview

This document provides pseudocode examples showing common usage patterns for the chronograph module API.

All examples assume you have initialized the API:

```python
from chronograph import ChronographAPI

api = ChronographAPI(supabase_client)
```

---

## Managing Chronograph Sources

### Example 1: Create a Chronograph Source

Create a new chronograph device entry.

```python
# Create a chronograph source
source_data = {
    "name": "My Garmin Xero",
    "make": "Garmin",
    "model": "Xero C1",
    "serial_number": "G123456"
}

source = api.create_source(source_data, user_id)

print(f"Created: {source.display_name()}")
# "My Garmin Xero"

print(f"Device: {source.device_display()}")
# "Garmin Xero C1 (S/N: G123456)"
```

---

### Example 2: List All Sources

Get all chronograph devices for a user.

```python
# Get all sources
sources = api.get_all_sources(user_id)

print(f"You have {len(sources)} chronograph(s):")
for source in sources:
    print(f"  {source.short_display()}")
    # My Garmin Xero - Garmin Xero C1 (S/N: G123456)
    # Range LabRadar - LabRadar (S/N: LR789012)
```

---

### Example 3: Update a Source

Update chronograph source information.

```python
# Get source
source = api.get_source_by_id(source_id, user_id)

# Update name
updates = {
    "name": "Competition Garmin",
    "make": "Garmin"
}

updated_source = api.update_source(source_id, updates, user_id)
print(f"Updated: {updated_source.name}")
# "Competition Garmin"
```

---

### Example 4: Delete a Source

Remove a chronograph source and all its data.

```python
# Confirm deletion
if user_confirms_deletion():
    success = api.delete_source(source_id, user_id)
    if success:
        print("Source and all sessions/measurements deleted")
```

---

## Creating Sessions

### Example 5: Create a Session

Create a new chronograph session.

```python
# Create session
session_data = {
    "tab_name": "168gr HPBT",
    "session_name": "Range Day 1",
    "datetime_local": "2024-01-15T10:00:00",
    "chronograph_source_id": source_id
}

session = api.create_session(session_data, user_id)

print(f"Created: {session.display_name()}")
# "168gr HPBT - 2024-01-15 10:00"
```

---

### Example 6: Check if Session Exists

Prevent duplicate sessions during import.

```python
# Check before creating
exists = api.session_exists(
    user_id,
    "168gr HPBT",
    "2024-01-15T10:00:00"
)

if exists:
    print("Session already exists, skipping import")
else:
    # Safe to create
    session = api.create_session(session_data, user_id)
    print("Created new session")
```

---

## Adding Measurements

### Example 7: Add Single Measurement

Add a single shot to a session.

```python
# Create single measurement
measurement_data = {
    "chrono_session_id": session_id,
    "shot_number": 1,
    "speed_mps": 792.5,  # m/s (NOT fps)
    "datetime_local": "2024-01-15T10:00:00",
    "ke_j": 3500.0,  # joules (NOT ft-lbs)
    "cold_bore": True
}

measurement = api.create_measurement(measurement_data, user_id)
print(f"Shot {measurement.shot_number}: {measurement.speed_mps} m/s")
# "Shot 1: 792.5 m/s"
```

---

### Example 8: Batch Add Measurements

Add multiple shots efficiently and auto-update statistics.

```python
# Create batch of measurements
batch_data = [
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
    },
    {
        "chrono_session_id": session_id,
        "shot_number": 3,
        "speed_mps": 791.8,
        "datetime_local": "2024-01-15T10:00:10"
    },
    {
        "chrono_session_id": session_id,
        "shot_number": 4,
        "speed_mps": 793.0,
        "datetime_local": "2024-01-15T10:00:15"
    },
    {
        "chrono_session_id": session_id,
        "shot_number": 5,
        "speed_mps": 792.0,
        "datetime_local": "2024-01-15T10:00:20"
    }
]

measurements = api.create_measurements_batch(batch_data, user_id)
print(f"Added {len(measurements)} shots")
# "Added 5 shots"

# Statistics are automatically updated
session = api.get_session_by_id(session_id, user_id)
print(f"Average: {session.avg_speed_mps} m/s")
print(f"SD: {session.std_dev_mps} m/s")
# "Average: 792.7 m/s"
# "SD: 0.9 m/s"
```

---

## Viewing Sessions and Data

### Example 9: List All Sessions

Get all sessions for a user.

```python
# Get all sessions
sessions = api.get_all_sessions(user_id)

print(f"Total sessions: {len(sessions)}")

for session in sessions:
    print(f"{session.display_name()}")
    print(f"  Shots: {session.shot_count}")
    print(f"  Average: {session.avg_speed_mps} m/s")
    print(f"  SD: {session.std_dev_mps} m/s")
    # 168gr HPBT - 2024-01-15 10:00
    #   Shots: 10
    #   Average: 792.5 m/s
    #   SD: 1.2 m/s
```

---

### Example 10: Filter Sessions by Bullet Type

Get all sessions for a specific bullet load.

```python
# Filter by bullet type
sessions = api.filter_sessions(
    user_id,
    bullet_type="168gr HPBT"
)

print(f"Found {len(sessions)} sessions for 168gr HPBT:")
for session in sessions:
    print(f"  {session.datetime_local.strftime('%Y-%m-%d')}: {session.shot_count} shots")
    # 2024-01-15: 10 shots
    # 2024-01-10: 15 shots
```

---

### Example 11: Filter Sessions by Date Range

Get sessions within a date range.

```python
# Get January 2024 sessions
sessions = api.filter_sessions(
    user_id,
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59"
)

print(f"January 2024: {len(sessions)} sessions")

for session in sessions:
    print(f"  {session.display_name()}: {session.shot_count} shots")
```

---

### Example 12: Combined Filters

Filter by both bullet type and date range.

```python
# Get 168gr HPBT sessions from January 2024
sessions = api.filter_sessions(
    user_id,
    bullet_type="168gr HPBT",
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59"
)

print(f"168gr HPBT sessions in January 2024: {len(sessions)}")
```

---

### Example 13: Get Measurements for Session

View all shots in a session.

```python
# Get session
session = api.get_session_by_id(session_id, user_id)

# Get measurements
measurements = api.get_measurements_for_session(session_id, user_id)

print(f"{session.display_name()}")
print(f"Shots: {len(measurements)}")
print()

for m in measurements:
    print(f"Shot {m.shot_number}: {m.speed_mps} m/s", end="")
    if m.cold_bore:
        print(" (cold bore)", end="")
    if m.clean_bore:
        print(" (clean bore)", end="")
    if m.shot_notes:
        print(f" - {m.shot_notes}", end="")
    print()

# Example output:
# 168gr HPBT - 2024-01-15 10:00
# Shots: 5
#
# Shot 1: 792.5 m/s (cold bore)
# Shot 2: 794.2 m/s
# Shot 3: 791.8 m/s - Slight wind gust
# Shot 4: 793.0 m/s
# Shot 5: 792.0 m/s
```

---

## Statistics and Analysis

### Example 14: Calculate Session Statistics

Get detailed statistics for a session.

```python
# Get statistics
stats = api.calculate_session_statistics(session_id, user_id)

print(f"Session Statistics:")
print(f"  Shot Count: {stats['shot_count']}")
print(f"  Average: {stats['avg_speed_mps']:.1f} m/s")
print(f"  Std Dev: {stats['std_dev_mps']:.2f} m/s")
print(f"  Min: {stats['min_speed_mps']:.1f} m/s")
print(f"  Max: {stats['max_speed_mps']:.1f} m/s")
print(f"  ES: {stats['extreme_spread_mps']:.1f} m/s")
print(f"  CV: {stats['coefficient_of_variation']:.2f}%")

# Example output:
# Session Statistics:
#   Shot Count: 10
#   Average: 792.5 m/s
#   Std Dev: 1.20 m/s
#   Min: 790.5 m/s
#   Max: 794.5 m/s
#   ES: 4.0 m/s
#   CV: 0.15%
```

---

### Example 15: Compare Multiple Sessions

Compare statistics across different sessions.

```python
# Get sessions for a bullet type
sessions = api.filter_sessions(user_id, bullet_type="168gr HPBT")

print("Session Comparison:")
print(f"{'Date':<12} {'Shots':<6} {'Avg (m/s)':<10} {'SD (m/s)':<9} {'ES (m/s)':<9}")
print("-" * 60)

for session in sessions:
    date = session.datetime_local.strftime('%Y-%m-%d')
    shots = session.shot_count
    avg = session.avg_speed_mps or 0
    sd = session.std_dev_mps or 0
    es = (session.max_speed_mps - session.min_speed_mps) if session.max_speed_mps else 0

    print(f"{date:<12} {shots:<6} {avg:<10.1f} {sd:<9.2f} {es:<9.1f}")

# Example output:
# Session Comparison:
# Date         Shots  Avg (m/s)  SD (m/s)  ES (m/s)
# ------------------------------------------------------------
# 2024-01-15   10     792.5      1.20      4.0
# 2024-01-10   15     793.2      0.95      3.5
# 2024-01-05   12     791.8      1.45      5.2
```

---

## UI Helpers

### Example 16: Populate Bullet Type Dropdown

Get unique bullet types for filtering UI.

```python
# Get unique bullet types
bullet_types = api.get_unique_bullet_types(user_id)

# Create dropdown options
dropdown_options = ["All"] + bullet_types

for option in dropdown_options:
    display_dropdown_option(option)

# Example output:
# [ ] All
# [ ] 140gr ELD-M
# [ ] 168gr HPBT
# [ ] 175gr SMK
```

---

### Example 17: Recent Sessions Widget

Show recent chronograph activity.

```python
# Get recent sessions (last 7 days)
start, end = api.get_time_window(user_id, days=7)

sessions = api.filter_sessions(
    user_id,
    start_date=start.isoformat(),
    end_date=end.isoformat()
)

print(f"Recent Activity (Last 7 Days):")
print(f"Total Sessions: {len(sessions)}")
print(f"Total Shots: {sum(s.shot_count for s in sessions)}")
print()

for session in sessions[:5]:  # Show top 5
    print(f"  {session.display_name()}")
    print(f"    {session.shot_count} shots, avg {session.avg_speed_mps:.1f} m/s")
```

---

## CSV Import Pattern

### Example 18: Import Garmin Xero CSV

Complete CSV import workflow.

```python
import csv
import uuid
from datetime import datetime

# Parse CSV file
with open("garmin_xero_export.csv") as f:
    reader = csv.DictReader(f)

    # First row may contain metadata
    first_row = next(reader)
    device_name = first_row.get("Device Name", "Garmin Xero")
    device_model = first_row.get("Model", "Unknown")
    serial_number = first_row.get("Serial Number", "Unknown")

    # Create or get chronograph source
    source = api.create_or_get_source_from_device_info(
        user_id,
        device_name,
        device_model,
        serial_number
    )

    # Extract session metadata
    bullet_type = first_row.get("Bullet Type", "Unknown Load")
    session_name = first_row.get("Session Name", "Imported Session")
    session_date = first_row.get("Session Date", datetime.now().isoformat())

    # Check if session exists
    if not api.session_exists(user_id, bullet_type, session_date):
        # Create session
        session_data = {
            "tab_name": bullet_type,
            "session_name": session_name,
            "datetime_local": session_date,
            "chronograph_source_id": source.id,
            "file_path": f"{user_id}/garmin_xero_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }

        session = api.create_session(session_data, user_id)

        # Parse measurements
        measurements_data = []
        shot_num = 1

        # Process first row if it's a measurement
        if first_row.get("Velocity"):
            measurements_data.append({
                "chrono_session_id": session.id,
                "shot_number": shot_num,
                "speed_mps": float(first_row["Velocity"]),
                "datetime_local": first_row.get("Timestamp", session_date),
                "ke_j": float(first_row["Energy"]) if first_row.get("Energy") else None
            })
            shot_num += 1

        # Process remaining rows
        for row in reader:
            if row.get("Velocity"):
                measurements_data.append({
                    "chrono_session_id": session.id,
                    "shot_number": shot_num,
                    "speed_mps": float(row["Velocity"]),
                    "datetime_local": row.get("Timestamp", session_date),
                    "ke_j": float(row["Energy"]) if row.get("Energy") else None
                })
                shot_num += 1

        # Batch create measurements
        measurements = api.create_measurements_batch(measurements_data, user_id)

        print(f"Import Complete:")
        print(f"  Session: {session.display_name()}")
        print(f"  Source: {source.short_display()}")
        print(f"  Shots Imported: {len(measurements)}")

        # Get updated session with statistics
        updated_session = api.get_session_by_id(session.id, user_id)
        print(f"  Average: {updated_session.avg_speed_mps:.1f} m/s")
        print(f"  SD: {updated_session.std_dev_mps:.2f} m/s")
    else:
        print("Session already exists, skipping import")
```

---

## Unit Conversion (Display Only)

### Example 19: Display Imperial Units

Convert metric to imperial for display (if user prefers).

```python
# Get session with metric data
session = api.get_session_by_id(session_id, user_id)

# All data is stored in metric
avg_mps = session.avg_speed_mps  # 792.5 m/s
sd_mps = session.std_dev_mps      # 1.2 m/s

# Convert for display if user prefers imperial
user_prefers_imperial = get_user_preference()

if user_prefers_imperial:
    avg_fps = avg_mps * 3.28084  # 2600 fps
    sd_fps = sd_mps * 3.28084     # 3.9 fps

    print(f"Average: {avg_fps:.0f} fps ({avg_mps:.1f} m/s)")
    print(f"SD: {sd_fps:.1f} fps ({sd_mps:.2f} m/s)")
    # "Average: 2600 fps (792.5 m/s)"
    # "SD: 3.9 fps (1.20 m/s)"
else:
    print(f"Average: {avg_mps:.1f} m/s")
    print(f"SD: {sd_mps:.2f} m/s")
    # "Average: 792.5 m/s"
    # "SD: 1.20 m/s"
```

---

### Example 20: Energy Conversion

Convert kinetic energy for display.

```python
# Get measurement with metric energy
measurement = api.get_measurements_for_session(session_id, user_id)[0]

# Energy stored in joules
ke_j = measurement.ke_j  # 3500 J

# Convert for display if user prefers imperial
if user_prefers_imperial:
    ke_ftlbs = ke_j * 0.737562  # 2581 ft-lbs

    print(f"Energy: {ke_ftlbs:.0f} ft-lbs ({ke_j:.0f} J)")
    # "Energy: 2581 ft-lbs (3500 J)"
else:
    print(f"Energy: {ke_j:.0f} J")
    # "Energy: 3500 J"
```

---

## Integration Examples

### Example 21: Link to Weather Data

Combine chronograph data with weather conditions.

```python
from chronograph import ChronographAPI
from weather import WeatherAPI

chrono_api = ChronographAPI(supabase_client)
weather_api = WeatherAPI(supabase_client)

# Get chronograph session
session = chrono_api.get_session_by_id(session_id, user_id)

# Get weather at time of session (using time window from chrono module)
time_window = chrono_api.get_time_window(user_id, session_id, buffer_minutes=30)

if time_window:
    start_time, end_time = time_window

    weather_measurements = weather_api.filter_measurements(
        user_id,
        start_date=start_time.isoformat(),
        end_date=end_time.isoformat()
    )

    if weather_measurements:
        # Use closest weather measurement
        weather = weather_measurements[0]

        print(f"Session: {session.display_name()}")
        print(f"  Average: {session.avg_speed_mps:.1f} m/s")
        print(f"  Temperature: {weather.temperature_c:.1f}°C")
        print(f"  Pressure: {weather.barometric_pressure_hpa:.1f} hPa")
        print(f"  Humidity: {weather.relative_humidity_pct:.0f}%")
```

---

### Example 22: Link to Bullet Data

Display session with bullet information.

```python
from chronograph import ChronographAPI
from bullets import BulletsAPI

chrono_api = ChronographAPI(supabase_client)
bullets_api = BulletsAPI(supabase_client)

# Get session
session = chrono_api.get_session_by_id(session_id, user_id)

# Parse bullet info from tab_name
# Assuming tab_name like "168gr HPBT"
bullet_weight = 168  # Parsed from tab_name

# Find matching bullets
bullets = bullets_api.filter_bullets(weight_grains=bullet_weight)

if bullets:
    bullet = bullets[0]  # Use first match

    print(f"Session: {session.display_name()}")
    print(f"  Bullet: {bullet.display_name}")
    print(f"  BC (G7): {bullet.ballistic_coefficient_g7}")
    print(f"  Average Velocity: {session.avg_speed_mps:.1f} m/s")
```

---

## Error Handling

### Example 23: Handle Not Found

Handle cases where session doesn't exist.

```python
session_id = user_provided_session_id()

session = api.get_session_by_id(session_id, user_id)

if not session:
    display_error("Session not found or access denied")
    return

# Continue with session data
process_session(session)
```

---

### Example 24: Handle Database Errors

Handle database connection issues.

```python
try:
    sessions = api.get_all_sessions(user_id)
    display_sessions(sessions)

except Exception as e:
    log_error(f"Failed to load sessions: {e}")
    display_error("Unable to load chronograph sessions. Please try again.")
```

---

## Next Steps

- [API Reference](api-reference.md) - Complete API documentation
- [Models](models.md) - Data model specifications
- [Module README](README.md) - Overview and integration

---

**Examples Version**: 1.0
**Last Updated**: 2025-10-19
