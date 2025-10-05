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
    notes TEXT,
    rifle_id UUID NOT NULL REFERENCES rifles(id),
    cartridge_lot_number TEXT,
    user_id TEXT NOT NULL,
    cartridge_id UUID NOT NULL REFERENCES cartridges(id),
    bullet_id UUID NOT NULL REFERENCES bullets(id),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,

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

| Column Name                         | Description                                                  | Lineage                                    | Data Type                | Nullable | Default           |
|-------------------------------------|--------------------------------------------------------------|--------------------------------------------|--------------------------|----------|-------------------|
| **id**                              | Primary key, auto-generated unique identifier                | Database auto-generated                    | uuid                     | NO       | gen_random_uuid() |
| **session_name**                    | Descriptive name for the DOPE session                        | User input via UI                          | text                     | NO       | -                 |
| **created_at**                      | Record creation timestamp                                    | Database auto-generated                    | timestamp with time zone | NO       | now()             |
| **updated_at**                      | Last modification timestamp                                  | Database auto-generated on updates         | timestamp with time zone | NO       | now()             |
| **chrono_session_id**               | Foreign key to chrono_sessions table                         | User selection from chronograph sessions   | uuid                     | YES      | -                 |
| **range_submission_id**             | Foreign key to ranges_submissions table                      | User selection from range submissions      | uuid                     | YES      | -                 |
| **weather_source_id**               | Foreign key to weather_source table                          | User selection from weather sources        | uuid                     | YES      | -                 |
| **notes**                           | Session notes and observations                               | User input via UI                          | text                     | YES      | -                 |
| **rifle_id**                        | Foreign key to rifles table                                  | User selection from rifles                 | uuid                     | NO       | -                 |
| **cartridge_lot_number**            | Cartridge lot identifier                                     | User input via UI                          | text                     | YES      | -                 |
| **user_id**                         | Auth0 user identifier for data isolation                     | Auth0 authentication system                | text                     | NO       | -                 |
| **cartridge_id**                    | Foreign key to cartridges table                              | User selection from cartridges             | uuid                     | NO       | -                 |
| **bullet_id**                       | Foreign key to bullets table (required)                      | User selection from bullets                | uuid                     | NO       | -                 |
| **start_time**                      | Session start time from chronograph time window              | Chronograph session data (required)        | timestamp with time zone | NO       | -                 |
| **end_time**                        | Session end time from chronograph time window                | Chronograph session data (required)        | timestamp with time zone | NO       | -                 |
| **temperature_c_median**            | Median temperature in Celsius from weather association       | Weather source aggregation or user input   | real                     | YES      | -                 |
| **relative_humidity_pct_median**    | Median relative humidity percentage from weather association | Weather source aggregation or user input   | real                     | YES      | -                 |
| **barometric_pressure_inhg_median** | Median barometric pressure in inHg from weather association  | Weather source aggregation or user input   | real                     | YES      | -                 |
| **wind_speed_mps_median**           | Median wind speed in m/s from weather association            | Weather source aggregation or user input   | real                     | YES      | -                 |
| **wind_direction_deg_median**       | Median wind direction in degrees from weather association    | Weather source aggregation or user input   | real                     | YES      | -                 |

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