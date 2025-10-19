# Weather Module

Complete weather data management for ChronoLog including weather sources (meters/devices) and measurements.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Models](#models)
- [Integration](#integration)

## Overview

The Weather module provides comprehensive weather data management:

- **Weather Sources**: Manage weather meters/devices (Kestrel, etc.)
- **Measurements**: Store and retrieve weather readings
- **CSV Import**: Import data from weather meter CSV exports
- **Filtering**: Query measurements by source, date range
- **Batch Operations**: Efficient bulk measurement creation

### Key Features

- User-scoped weather sources and measurements
- Device identification from CSV metadata
- Automatic timestamp and ID generation
- Comprehensive filtering capabilities
- Type-safe API with protocol definitions

## Quick Start

```python
from weather import WeatherAPI
from supabase import create_client

# Initialize
supabase = create_client(url, key)
weather_api = WeatherAPI(supabase)

# Create a weather source
source = weather_api.create_source(
    {
        "name": "My Kestrel",
        "device_name": "Kestrel 5700",
        "model": "5700 Elite",
        "serial_number": "K123456"
    },
    user_id
)

# Create a measurement
measurement = weather_api.create_measurement(
    {
        "weather_source_id": source.id,
        "measurement_timestamp": "2024-01-15T10:00:00",
        "temperature_c": 22.5,
        "relative_humidity_pct": 65.0,
        "barometric_pressure_hpa": 1013.25,
        "wind_speed_mps": 3.5
    },
    user_id
)

# Query measurements
measurements = weather_api.filter_measurements(
    user_id,
    source_id=source.id,
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59"
)
```

## Architecture

### Components

```
weather/
├── __init__.py          # Module exports
├── api.py               # WeatherAPI facade
├── protocols.py         # WeatherAPIProtocol
├── models.py            # WeatherSource, WeatherMeasurement
├── service.py           # WeatherService (database layer)
└── test_weather.py      # Unit tests
```

### Layer Pattern

1. **Protocol Layer** (`protocols.py`): Type-safe API contract
2. **API Layer** (`api.py`): Public interface with ID/timestamp generation
3. **Service Layer** (`service.py`): Database operations
4. **Model Layer** (`models.py`): Domain entities

### Data Flow

```
UI/Controller
    ↓
WeatherAPI (api.py)
    ↓
WeatherService (service.py)
    ↓
Supabase Database
```

## API Reference

### Weather Source Operations

#### get_all_sources(user_id: str) → List[WeatherSource]

Get all weather sources for a user.

```python
sources = weather_api.get_all_sources(user_id)
for source in sources:
    print(f"{source.name}: {source.device_display()}")
```

#### create_source(source_data: dict, user_id: str) → WeatherSource

Create a new weather source.

```python
source = weather_api.create_source(
    {
        "name": "My Kestrel",
        "model": "5700 Elite",
        "serial_number": "K123456"
    },
    user_id
)
```

#### update_source(source_id: str, updates: dict, user_id: str) → WeatherSource

Update an existing weather source.

```python
updated = weather_api.update_source(
    source_id,
    {"name": "Updated Kestrel", "make": "Kestrel"},
    user_id
)
```

#### delete_source(source_id: str, user_id: str) → bool

Delete a weather source and all its measurements.

```python
success = weather_api.delete_source(source_id, user_id)
```

### Weather Measurement Operations

#### create_measurement(measurement_data: dict, user_id: str) → WeatherMeasurement

Create a single weather measurement.

```python
measurement = weather_api.create_measurement(
    {
        "weather_source_id": source_id,
        "measurement_timestamp": "2024-01-15T10:00:00",
        "temperature_c": 22.5,
        "relative_humidity_pct": 65.0,
        "barometric_pressure_hpa": 1013.25
    },
    user_id
)
```

#### create_measurements_batch(measurements_data: List[dict], user_id: str) → List[WeatherMeasurement]

Create multiple measurements efficiently.

```python
batch = [
    {
        "weather_source_id": source_id,
        "measurement_timestamp": "2024-01-15T10:00:00",
        "temperature_c": 22.5
    },
    {
        "weather_source_id": source_id,
        "measurement_timestamp": "2024-01-15T10:01:00",
        "temperature_c": 22.6
    }
]
measurements = weather_api.create_measurements_batch(batch, user_id)
```

#### filter_measurements(...) → List[WeatherMeasurement]

Query measurements with filters.

```python
measurements = weather_api.filter_measurements(
    user_id,
    source_id=source_id,
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59"
)
```

## Models

### WeatherSource

Represents a weather meter/device.

**Required Fields:**
- `id`: UUID
- `user_id`: Owner ID
- `name`: User-defined name

**Optional Fields:**
- `device_name`: Device name from CSV
- `make`: Manufacturer (e.g., "Kestrel")
- `model`: Model number (e.g., "5700 Elite")
- `serial_number`: Device serial number

**Display Methods:**
- `display_name()`: Returns source name
- `device_display()`: Formatted device info with serial number
- `short_display()`: Combined name and device info

### WeatherMeasurement

Represents a single weather reading.

**Required Fields:**
- `id`: UUID
- `user_id`: Owner ID
- `weather_source_id`: Associated source ID
- `measurement_timestamp`: When reading was taken
- `uploaded_at`: When uploaded to database

**Metric Weather Fields (all Optional):**
- `temperature_c`: Temperature (Celsius)
- `wet_bulb_temp_c`: Wet bulb temperature
- `relative_humidity_pct`: Relative humidity (%)
- `barometric_pressure_hpa`: Barometric pressure (hPa)
- `station_pressure_hpa`: Station pressure (hPa)
- `altitude_m`: Altitude (meters)
- `density_altitude_m`: Density altitude (meters)
- `wind_speed_mps`: Wind speed (m/s)
- `crosswind_mps`: Crosswind component (m/s)
- `headwind_mps`: Headwind component (m/s)
- `compass_magnetic_deg`: Magnetic compass heading
- `compass_true_deg`: True compass heading
- `dew_point_c`: Dew point temperature
- `heat_index_c`: Heat index
- `wind_chill_c`: Wind chill

**Helper Methods:**
- `has_wind_data()`: Check if wind measurements present
- `has_location_data()`: Check if location data present

## Integration

### With Rifles Module

Weather data can be linked to shooting sessions for ballistic calculations:

```python
from weather import WeatherAPI
from rifles import RiflesAPI

# Get current weather
weather_measurements = weather_api.get_all_measurements(user_id, limit=1)
current_weather = weather_measurements[0] if weather_measurements else None

# Use with rifle data
rifle = rifles_api.get_rifle_by_id(rifle_id, user_id)
# Apply weather conditions to ballistic calculations
```

### With Chronograph Module

Combine chronograph data with environmental conditions:

```python
from weather import WeatherAPI
from chronograph import ChronographAPI

# Get weather at time of chronograph session
chrono_session = chrono_api.get_session_by_id(session_id, user_id)
weather_measurements = weather_api.filter_measurements(
    user_id,
    start_date=chrono_session.start_time,
    end_date=chrono_session.end_time
)
```

### CSV Import Pattern

Weather data is typically imported from CSV files exported by weather meters:

```python
import csv

# Parse CSV from weather meter
with open("kestrel_export.csv") as f:
    reader = csv.DictReader(f)
    device_info = next(reader)  # First row usually contains device info
    
    # Create or get source
    source = weather_api.create_or_get_source_from_device_info(
        user_id,
        device_info.get("Device Name"),
        device_info.get("Model"),
        device_info.get("Serial Number")
    )
    
    # Batch create measurements
    measurements_data = []
    for row in reader:
        measurements_data.append({
            "weather_source_id": source.id,
            "measurement_timestamp": row["Timestamp"],
            "temperature_c": float(row["Temperature"]),
            "relative_humidity_pct": float(row["Humidity"]),
            # ... other fields
        })
    
    measurements = weather_api.create_measurements_batch(
        measurements_data,
        user_id
    )
```

## Database Schema

### weather_source Table

```sql
CREATE TABLE weather_source (
    id UUID PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    source_type TEXT DEFAULT 'meter',
    device_name TEXT,
    make TEXT,
    model TEXT,
    serial_number TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### weather_measurements Table

```sql
CREATE TABLE weather_measurements (
    id UUID PRIMARY KEY,
    user_id TEXT NOT NULL,
    weather_source_id UUID REFERENCES weather_source(id) ON DELETE CASCADE,
    measurement_timestamp TIMESTAMP NOT NULL,
    uploaded_at TIMESTAMP NOT NULL,
    file_path TEXT,
    -- Metric weather fields
    temperature_c REAL,
    wet_bulb_temp_c REAL,
    relative_humidity_pct REAL,
    barometric_pressure_hpa REAL,
    altitude_m REAL,
    station_pressure_hpa REAL,
    wind_speed_mps REAL,
    heat_index_c REAL,
    dew_point_c REAL,
    density_altitude_m REAL,
    crosswind_mps REAL,
    headwind_mps REAL,
    compass_magnetic_deg REAL,
    compass_true_deg REAL,
    wind_chill_c REAL,
    -- Additional fields
    data_type TEXT,
    record_name TEXT,
    start_time TEXT,
    duration TEXT,
    location_description TEXT,
    location_address TEXT,
    location_coordinates TEXT,
    notes TEXT
);
```

## Testing

The weather module includes 33 unit tests covering:

- Model creation and display methods
- Service CRUD operations
- Batch operations
- Filtering and querying
- Error handling
- Device identification logic

Run tests:

```bash
python -m pytest weather/test_weather.py -v
```

## See Also

- [Models Reference](./models.md) - Detailed model documentation
- [API Reference](./api-reference.md) - Complete API documentation
- [Examples](./examples.md) - Practical usage examples
