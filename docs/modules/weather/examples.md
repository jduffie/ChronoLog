# Weather Module Examples

## Overview

This document provides pseudocode examples showing common usage patterns for the weather module API.

All examples assume you have initialized the API:

```python
from weather import WeatherAPI

api = WeatherAPI(supabase_client)
user_id = "user-123"  # Current user's ID
```

---

## Weather Source Management

### Example 1: Create a Weather Source

Create a new weather source (meter/device).

```python
# Create a basic source with minimal info
source_data = {
    "name": "My Kestrel"
}

source = api.create_source(source_data, user_id)
print(f"Created source: {source.id}")
print(f"Display: {source.display_name()}")
# Output: "My Kestrel"
```

---

### Example 2: Create Source with Full Device Info

Create a source with complete device information.

```python
# Create source with full device details
source_data = {
    "name": "Range Kestrel",
    "device_name": "Kestrel 5700",
    "make": "Kestrel",
    "model": "5700 Elite",
    "serial_number": "K123456"
}

source = api.create_source(source_data, user_id)

print(source.short_display())
# Output: "Range Kestrel - Kestrel 5700 Elite (S/N: K123456)"
```

---

### Example 3: List All Sources

Display all weather sources for a user.

```python
# Get all sources
sources = api.get_all_sources(user_id)

print(f"Total sources: {len(sources)}")

for source in sources:
    print(f"\n{source.name}")
    print(f"  Device: {source.device_display()}")
    print(f"  Created: {source.created_at}")
```

---

### Example 4: Update a Source

Update source information.

```python
# Get source
source = api.get_source_by_id("source-123", user_id)

if source:
    # Update name and add make
    updates = {
        "name": "Competition Kestrel",
        "make": "Kestrel"
    }

    updated = api.update_source(source.id, updates, user_id)
    print(f"Updated: {updated.name}")
```

---

### Example 5: Delete a Source

Delete a source and all its measurements.

```python
source_id = "source-123"

# Confirm deletion
if confirm_deletion():
    success = api.delete_source(source_id, user_id)
    if success:
        print("Source and all measurements deleted")
```

---

## CSV Import Patterns

### Example 6: Import Weather Data from CSV

Import Kestrel CSV export with device identification.

```python
import csv
from datetime import datetime

# Read Kestrel CSV export
with open("kestrel_export.csv") as f:
    reader = csv.DictReader(f)

    # First row typically contains device metadata
    metadata_row = next(reader)
    device_name = metadata_row.get("Device Name", "Kestrel")
    device_model = metadata_row.get("Model", "")
    serial_number = metadata_row.get("Serial Number", "")

    # Create or get existing source
    source = api.create_or_get_source_from_device_info(
        user_id,
        device_name,
        device_model,
        serial_number
    )

    print(f"Using source: {source.short_display()}")

    # Parse and batch measurements
    measurements_data = []

    for row in reader:
        # Convert timestamp
        timestamp = datetime.strptime(
            row["Timestamp"],
            "%Y-%m-%d %H:%M:%S"
        ).isoformat()

        # Build measurement data (metric units)
        measurement = {
            "weather_source_id": source.id,
            "measurement_timestamp": timestamp,
            "temperature_c": float(row["Temperature"]) if row["Temperature"] else None,
            "relative_humidity_pct": float(row["Humidity"]) if row["Humidity"] else None,
            "barometric_pressure_hpa": float(row["Pressure"]) if row["Pressure"] else None,
            "wind_speed_mps": float(row["Wind Speed"]) if row["Wind Speed"] else None,
            "file_path": "kestrel_export.csv"
        }

        measurements_data.append(measurement)

    # Batch create measurements
    measurements = api.create_measurements_batch(measurements_data, user_id)
    print(f"Imported {len(measurements)} measurements")
```

---

### Example 7: Prevent Duplicate Imports

Check for existing measurements before importing.

```python
# During CSV import
for row in csv_rows:
    timestamp = parse_timestamp(row["Timestamp"])

    # Check if measurement already exists
    exists = api.measurement_exists(
        user_id,
        source.id,
        timestamp
    )

    if not exists:
        # Safe to import
        measurement_data = build_measurement_data(row)
        measurements_to_import.append(measurement_data)
    else:
        print(f"Skipping duplicate: {timestamp}")

# Import only new measurements
if measurements_to_import:
    api.create_measurements_batch(measurements_to_import, user_id)
```

---

## Creating Measurements

### Example 8: Create Single Measurement

Record a single weather reading.

```python
from datetime import datetime

measurement_data = {
    "weather_source_id": source.id,
    "measurement_timestamp": datetime.now().isoformat(),
    "temperature_c": 22.5,
    "relative_humidity_pct": 65.0,
    "barometric_pressure_hpa": 1013.25,
    "wind_speed_mps": 3.5,
    "density_altitude_m": 500.0
}

measurement = api.create_measurement(measurement_data, user_id)

print(f"Recorded at: {measurement.measurement_timestamp}")
print(f"Temperature: {measurement.temperature_c}°C")
print(f"Pressure: {measurement.barometric_pressure_hpa} hPa")
```

---

### Example 9: Create Measurement with Wind Data

Record detailed wind measurements.

```python
measurement_data = {
    "weather_source_id": source.id,
    "measurement_timestamp": "2024-01-15T10:00:00",
    "temperature_c": 18.0,
    "barometric_pressure_hpa": 1015.0,
    # Wind data
    "wind_speed_mps": 5.5,
    "crosswind_mps": 3.2,  # Right to left
    "headwind_mps": -1.5,  # Tailwind
    "compass_magnetic_deg": 270.0,
    "compass_true_deg": 275.0
}

measurement = api.create_measurement(measurement_data, user_id)

if measurement.has_wind_data():
    print(f"Wind: {measurement.wind_speed_mps} m/s")
    print(f"Crosswind: {measurement.crosswind_mps} m/s")
    print(f"Direction: {measurement.compass_magnetic_deg}°")
```

---

### Example 10: Batch Create Measurements

Create multiple measurements efficiently.

```python
# Collect readings over time
batch_data = [
    {
        "weather_source_id": source.id,
        "measurement_timestamp": "2024-01-15T10:00:00",
        "temperature_c": 22.5,
        "barometric_pressure_hpa": 1013.25
    },
    {
        "weather_source_id": source.id,
        "measurement_timestamp": "2024-01-15T10:05:00",
        "temperature_c": 22.6,
        "barometric_pressure_hpa": 1013.20
    },
    {
        "weather_source_id": source.id,
        "measurement_timestamp": "2024-01-15T10:10:00",
        "temperature_c": 22.8,
        "barometric_pressure_hpa": 1013.15
    },
]

# Create all at once
measurements = api.create_measurements_batch(batch_data, user_id)
print(f"Created {len(measurements)} measurements")
```

---

## Querying Measurements

### Example 11: Get All Measurements for a Source

Retrieve all measurements from a specific source.

```python
source_id = "source-123"

measurements = api.get_measurements_for_source(source_id, user_id)

print(f"Total measurements: {len(measurements)}")

# Display first 10
for m in measurements[:10]:
    print(f"{m.measurement_timestamp}: {m.temperature_c}°C")
```

---

### Example 12: Get Recent Measurements

Get the most recent measurements across all sources.

```python
# Get last 20 measurements
recent = api.get_all_measurements(user_id, limit=20)

print("Recent weather readings:")
for m in recent:
    source = api.get_source_by_id(m.weather_source_id, user_id)
    print(f"{m.measurement_timestamp} ({source.name}):")
    print(f"  Temp: {m.temperature_c}°C")
    print(f"  Pressure: {m.barometric_pressure_hpa} hPa")
```

---

### Example 13: Filter by Date Range

Query measurements for a specific time period.

```python
# Get January 2024 measurements
measurements = api.filter_measurements(
    user_id,
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59"
)

print(f"January measurements: {len(measurements)}")

# Calculate averages
temps = [m.temperature_c for m in measurements if m.temperature_c]
avg_temp = sum(temps) / len(temps) if temps else 0

print(f"Average temperature: {avg_temp:.1f}°C")
```

---

### Example 14: Filter by Source and Date

Combine filters for specific queries.

```python
# Get measurements from specific source during competition
measurements = api.filter_measurements(
    user_id,
    source_id="source-123",
    start_date="2024-01-15T08:00:00",
    end_date="2024-01-15T18:00:00"
)

print(f"Competition day measurements: {len(measurements)}")

# Find conditions during shooting
for m in measurements:
    if m.has_wind_data():
        print(f"{m.measurement_timestamp}:")
        print(f"  Wind: {m.wind_speed_mps} m/s")
        print(f"  Crosswind: {m.crosswind_mps} m/s")
```

---

## Data Analysis

### Example 15: Calculate Weather Statistics

Analyze weather conditions over time.

```python
measurements = api.filter_measurements(
    user_id,
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59"
)

# Extract values
temps = [m.temperature_c for m in measurements if m.temperature_c]
pressures = [m.barometric_pressure_hpa for m in measurements if m.barometric_pressure_hpa]
humidity = [m.relative_humidity_pct for m in measurements if m.relative_humidity_pct]

# Calculate statistics
print("January Weather Statistics:")
print(f"  Temperature:")
print(f"    Average: {sum(temps)/len(temps):.1f}°C")
print(f"    Min: {min(temps):.1f}°C")
print(f"    Max: {max(temps):.1f}°C")
print(f"  Pressure:")
print(f"    Average: {sum(pressures)/len(pressures):.1f} hPa")
print(f"  Humidity:")
print(f"    Average: {sum(humidity)/len(humidity):.1f}%")
```

---

### Example 16: Find Ideal Shooting Conditions

Identify measurements with favorable conditions.

```python
measurements = api.get_all_measurements(user_id, limit=100)

ideal_conditions = []

for m in measurements:
    # Check for ideal conditions
    temp_ok = m.temperature_c and 15 <= m.temperature_c <= 25
    wind_ok = m.wind_speed_mps and m.wind_speed_mps < 5.0
    pressure_ok = m.barometric_pressure_hpa and m.barometric_pressure_hpa > 1010

    if temp_ok and wind_ok and pressure_ok:
        ideal_conditions.append(m)

print(f"Found {len(ideal_conditions)} measurements with ideal conditions:")
for m in ideal_conditions[:5]:
    print(f"\n{m.measurement_timestamp}:")
    print(f"  Temperature: {m.temperature_c}°C")
    print(f"  Wind: {m.wind_speed_mps} m/s")
    print(f"  Pressure: {m.barometric_pressure_hpa} hPa")
```

---

## Integration with Other Modules

### Example 17: Link Weather to Chronograph Session

Associate weather data with shooting sessions.

```python
from chronograph import ChronographAPI

chrono_api = ChronographAPI(supabase_client)

# Get chronograph session
session = chrono_api.get_session_by_id("session-123", user_id)

# Get weather at time of session
weather_measurements = api.filter_measurements(
    user_id,
    start_date=session.start_time,
    end_date=session.end_time
)

if weather_measurements:
    # Use first measurement (closest to session start)
    weather = weather_measurements[0]

    print(f"Session: {session.display_name}")
    print(f"Weather conditions:")
    print(f"  Temperature: {weather.temperature_c}°C")
    print(f"  Pressure: {weather.barometric_pressure_hpa} hPa")
    print(f"  Density Altitude: {weather.density_altitude_m}m")

    # Use for ballistic calculations
    apply_weather_to_ballistics(session, weather)
```

---

### Example 18: Current Conditions for Ballistic Calculator

Get most recent weather for trajectory calculations.

```python
# Get most recent measurement
recent = api.get_all_measurements(user_id, limit=1)

if recent:
    current_weather = recent[0]

    # Extract conditions for ballistic calculator
    conditions = {
        "temperature_c": current_weather.temperature_c,
        "pressure_hpa": current_weather.barometric_pressure_hpa,
        "humidity_pct": current_weather.relative_humidity_pct,
        "altitude_m": current_weather.altitude_m,
        "density_altitude_m": current_weather.density_altitude_m
    }

    # Apply to trajectory calculation
    trajectory = calculate_trajectory(
        bullet_bc=0.243,
        muzzle_velocity_mps=800,
        **conditions
    )
else:
    print("No weather data available - using standard atmosphere")
    # Use standard atmosphere defaults
```

---

## Display Formatting

### Example 19: Format for Weather Dashboard

Display weather data in a dashboard UI.

```python
sources = api.get_all_sources(user_id)

for source in sources:
    # Get latest measurement
    measurements = api.get_measurements_for_source(source.id, user_id)
    if not measurements:
        continue

    latest = measurements[-1]  # Most recent

    # Format for display
    print(f"\n{source.name}")
    print(f"  Device: {source.device_display()}")
    print(f"  Last reading: {latest.measurement_timestamp}")

    if latest.temperature_c:
        print(f"  Temperature: {latest.temperature_c}°C")

    if latest.barometric_pressure_hpa:
        print(f"  Pressure: {latest.barometric_pressure_hpa} hPa")

    if latest.has_wind_data():
        print(f"  Wind: {latest.wind_speed_mps} m/s at {latest.compass_magnetic_deg}°")

    if latest.relative_humidity_pct:
        print(f"  Humidity: {latest.relative_humidity_pct}%")
```

---

### Example 20: Convert to Imperial for Display

Convert metric measurements to imperial for user display.

```python
measurement = api.get_all_measurements(user_id, limit=1)[0]

# Get user preference
user_prefers_imperial = get_user_preference()

if user_prefers_imperial:
    # Convert to imperial
    temp_f = measurement.temperature_c * 9/5 + 32
    pressure_inhg = measurement.barometric_pressure_hpa * 0.02953
    wind_mph = measurement.wind_speed_mps * 2.237
    altitude_ft = measurement.altitude_m * 3.281

    print(f"Temperature: {temp_f:.1f}°F")
    print(f"Pressure: {pressure_inhg:.2f} inHg")
    print(f"Wind: {wind_mph:.1f} mph")
    print(f"Altitude: {altitude_ft:.0f} ft")
else:
    # Display metric (stored format)
    print(f"Temperature: {measurement.temperature_c:.1f}°C")
    print(f"Pressure: {measurement.barometric_pressure_hpa:.1f} hPa")
    print(f"Wind: {measurement.wind_speed_mps:.1f} m/s")
    print(f"Altitude: {measurement.altitude_m:.0f} m")
```

---

## UI Dropdowns

### Example 21: Source Selection Dropdown

Populate dropdown with user's sources.

```python
sources = api.get_all_sources(user_id)

# Create dropdown options
dropdown_options = []
for source in sources:
    dropdown_options.append({
        "label": source.short_display(),
        "value": source.id
    })

# Display in UI
selected_source_id = display_dropdown(
    "Select Weather Source:",
    dropdown_options
)

# Get selected source
selected = api.get_source_by_id(selected_source_id, user_id)
```

---

### Example 22: Date Range Picker

Allow user to select date range for querying.

```python
# UI date range picker
start_date = user_select_date("Start Date")
end_date = user_select_date("End Date")

# Convert to ISO format
start_iso = start_date.isoformat()
end_iso = end_date.isoformat()

# Query measurements
measurements = api.filter_measurements(
    user_id,
    start_date=start_iso,
    end_date=end_iso
)

# Display results
display_measurements_table(measurements)
```

---

## Error Handling

### Example 23: Handle Missing Source

Handle case where source doesn't exist.

```python
source_id = user_provided_source_id()

source = api.get_source_by_id(source_id, user_id)

if not source:
    display_error("Weather source not found. It may have been deleted.")
    return

# Continue with source data
process_source(source)
```

---

### Example 24: Handle Database Errors

Handle database connection issues gracefully.

```python
try:
    sources = api.get_all_sources(user_id)
    display_sources(sources)

except Exception as e:
    log_error(f"Failed to load weather sources: {e}")
    display_error("Unable to load weather data. Please try again.")
```

---

### Example 25: Validate Measurement Data

Validate data before creating measurement.

```python
def validate_measurement_data(data):
    """Validate measurement data before creation"""

    # Check required fields
    if not data.get("weather_source_id"):
        raise ValueError("weather_source_id is required")

    if not data.get("measurement_timestamp"):
        raise ValueError("measurement_timestamp is required")

    # Validate ranges
    if data.get("temperature_c"):
        temp = data["temperature_c"]
        if temp < -50 or temp > 60:
            raise ValueError(f"Temperature {temp}°C out of valid range")

    if data.get("relative_humidity_pct"):
        humidity = data["relative_humidity_pct"]
        if humidity < 0 or humidity > 100:
            raise ValueError(f"Humidity {humidity}% out of valid range")

    if data.get("barometric_pressure_hpa"):
        pressure = data["barometric_pressure_hpa"]
        if pressure < 800 or pressure > 1100:
            raise ValueError(f"Pressure {pressure} hPa out of valid range")

    return True

# Use validation
try:
    validate_measurement_data(measurement_data)
    measurement = api.create_measurement(measurement_data, user_id)
except ValueError as e:
    display_error(f"Invalid data: {e}")
```

---

## Next Steps

- [API Reference](api-reference.md) - Complete API documentation
- [Models](models.md) - Data model specifications
- [Module README](README.md) - Overview and integration

---

**Examples Version**: 1.0
**Last Updated**: 2025-10-19