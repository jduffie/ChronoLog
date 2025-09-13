# dope_sessions Table Schema

## CREATE TABLE Statement

```sql
CREATE TABLE dope_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    chrono_session_id UUID REFERENCES chrono_sessions(id),
    range_submission_id UUID REFERENCES ranges_submissions(id),
    weather_source_id UUID REFERENCES weather_source(id),
    range_name TEXT,
    range_distance_m REAL,
    notes TEXT,
    rifle_id UUID NOT NULL REFERENCES rifles(id),
    cartridge_lot_number TEXT,
    user_id TEXT NOT NULL,
    cartridge_id UUID NOT NULL REFERENCES cartridges(id),
    bullet_id UUID NOT NULL REFERENCES bullets(id),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    
    -- Location and range geometry fields (from range data)
    lat REAL,
    lon REAL,
    start_altitude REAL,
    azimuth_deg REAL,
    elevation_angle_deg REAL,
    location_hyperlink TEXT,
    
    -- Median weather fields from weather association
    temperature_c_median REAL,
    relative_humidity_pct_median REAL,
    barometric_pressure_inhg_median REAL,
    wind_speed_mps_median REAL,
    wind_direction_deg_median REAL
);
```

## Recommended Indexes

```sql
CREATE INDEX idx_dope_sessions_user_id ON dope_sessions(user_id);
CREATE INDEX idx_dope_sessions_chrono_session_id ON dope_sessions(chrono_session_id);
CREATE INDEX idx_dope_sessions_range_submission_id ON dope_sessions(range_submission_id);
CREATE INDEX idx_dope_sessions_created_at ON dope_sessions(created_at DESC);
```

## Table Description

| Column Name                         | Data Type                | Nullable | Default           | Description                                                  |
|-------------------------------------|--------------------------|----------|-------------------|--------------------------------------------------------------|
| **id**                              | uuid                     | NO       | gen_random_uuid() | Primary key, auto-generated unique identifier                |
| **session_name**                    | text                     | NO       | -                 | Descriptive name for the DOPE session                        |
| **created_at**                      | timestamp with time zone | NO       | now()             | Record creation timestamp                                    |
| **updated_at**                      | timestamp with time zone | NO       | now()             | Last modification timestamp                                  |
| **chrono_session_id**               | uuid                     | YES      | -                 | Foreign key to chrono_sessions table                         |
| **range_submission_id**             | uuid                     | YES      | -                 | Foreign key to ranges_submissions table                      |
| **weather_source_id**               | uuid                     | YES      | -                 | Foreign key to weather_source table                          |
| **range_name**                      | text                     | YES      | -                 | Name of the shooting range                                   |
| **range_distance_m**                | real                     | YES      | -                 | Target distance in meters                                    |
| **notes**                           | text                     | YES      | -                 | Session notes and observations                               |
| **rifle_id**                        | uuid                     | NO       | -                 | Foreign key to rifles table                                  |
| **cartridge_lot_number**            | text                     | YES      | -                 | Cartridge lot identifier                                     |
| **user_id**                         | text                     | NO       | -                 | Auth0 user identifier for data isolation                     |
| **cartridge_id**                    | uuid                     | NO       | -                 | Foreign key to cartridges table                              |
| **bullet_id**                       | uuid                     | NO       | -                 | Foreign key to bullets table (required)                      |
| **start_time**                      | timestamp with time zone | NO       | -                 | Session start time from chronograph time window              |
| **end_time**                        | timestamp with time zone | NO       | -                 | Session end time from chronograph time window                |
| **lat**                             | real                     | YES      | -                 | Latitude from range data                                     |
| **lon**                             | real                     | YES      | -                 | Longitude from range data                                    |
| **start_altitude**                  | real                     | YES      | -                 | Starting altitude from range data                            |
| **azimuth_deg**                     | real                     | YES      | -                 | Azimuth angle in degrees from range data                     |
| **elevation_angle_deg**             | real                     | YES      | -                 | Elevation angle in degrees from range data                   |
| **location_hyperlink**              | text                     | YES      | -                 | Google Maps hyperlink for range location                     |
| **temperature_c_median**            | real                     | YES      | -                 | Median temperature in Celsius from weather association       |
| **relative_humidity_pct_median**    | real                     | YES      | -                 | Median relative humidity percentage from weather association |
| **barometric_pressure_inhg_median** | real                     | YES      | -                 | Median barometric pressure in inHg from weather association  |
| **wind_speed_mps_median**           | real                     | YES      | -                 | Median wind speed in m/s from weather association            |
| **wind_direction_deg_median**       | real                     | YES      | -                 | Median wind direction in degrees from weather association    |

## Foreign Key Relationships

The table has the following foreign key relationships:

- **chrono_sessions(id)** - Links to chronograph session data for velocity measurements
- **ranges_submissions(id)** - Links to shooting range information and location data
- **weather_source(id)** - Links to weather measurement devices (optional)
- **rifles(id)** - Links to rifle configuration data including barrel specifications
- **cartridges(id)** - Links to cartridge specifications
- **bullets(id)** - Links to bullet specifications (required for ballistic calculations)

## Purpose and Context

The `dope_sessions` table stores "Data On Previous Engagement" sessions, which are used for ballistic analysis and tracking shooting performance across different conditions. This table serves as the metadata container for DOPE sessions, connecting:

- Chronograph data (velocity measurements)
- Range information (distance, location, environmental factors)
- Weather conditions (both from linked weather sources and direct measurements)
- Rifle configurations
- Cartridge specifications

Each DOPE session represents a shooting event where ballistic performance is recorded and analyzed for future reference and trajectory calculations.

## Key Features

1. **User Isolation**: The `user_id` field ensures data is properly isolated per user
2. **Timestamps**: Both creation and update timestamps are automatically tracked
3. **Optional Relationships**: Many foreign key fields are nullable to accommodate varying data availability
4. **Comprehensive Context**: Links multiple aspects of shooting data for complete ballistic analysis
5. **Cartridge Integration**: Links to the unified cartridges table for both factory and custom specifications
6. **Weather Data**: Includes both linked weather source data and direct weather measurements for environmental tracking