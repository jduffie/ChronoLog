# dope_sessions Table Schema

## CREATE TABLE Statement

```sql
CREATE TABLE dope_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_name TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    chrono_session_id UUID REFERENCES chrono_sessions(id),
    range_submission_id UUID REFERENCES ranges_submissions(id),
    weather_source_id UUID REFERENCES weather_source(id),
    range_name TEXT,
    distance_m REAL,
    notes TEXT,
    status TEXT DEFAULT 'active',
    rifle_id UUID REFERENCES rifles(id),

    cartridge_id UUID REFERENCES cartridges(id),
    cartridge_lot_number TEXT,
    user_id TEXT NOT NULL,
    temperature_c NUMERIC(3,1),
    relative_humidity_pct NUMERIC(5,2),
    barometric_pressure_inhg NUMERIC(6,2),
    wind_speed_1_kmh NUMERIC(4,1),
    wind_speed_2_kmh NUMERIC(4,1),
    wind_direction_deg NUMERIC(5,1)
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

| Column Name                  | Data Type                | Nullable | Default           | Description                                                                              |
|------------------------------|--------------------------|----------|-------------------|------------------------------------------------------------------------------------------|
| **id**                       | uuid                     | NO       | gen_random_uuid() | Primary key, auto-generated unique identifier                                            |
| **session_name**             | text                     | YES      | -                 | Descriptive name for the DOPE session                                                    |
| **created_at**               | timestamp with time zone | YES      | now()             | Record creation timestamp                                                                |
| **updated_at**               | timestamp with time zone | YES      | now()             | Last modification timestamp                                                              |
| **chrono_session_id**        | uuid                     | YES      | -                 | Foreign key to chrono_sessions table                                                     |
| **range_submission_id**      | uuid                     | YES      | -                 | Foreign key to ranges_submissions table                                                  |
| **weather_source_id**        | uuid                     | YES      | -                 | Foreign key to weather_source table                                                      |
| **range_name**               | text                     | YES      | -                 | Name of the shooting range                                                               |
| **distance_m**               | real                     | YES      | -                 | Target distance in meters                                                                |
| **notes**                    | text                     | YES      | -                 | Session notes and observations                                                           |
| **status**                   | text                     | YES      | 'active'          | Session status                                                                           |
| **rifle_id**                 | uuid                     | YES      | -                 | Foreign key to rifles table                                                              |
| **cartridge_id**             | uuid                     | YES      | -                 | Foreign key to cartridges table                                                          |
| **cartridge_lot_number**     | text                     | YES      | -                 | Cartridge lot identifier                                                                 |
| **user_id**                  | text                     | NO       | -                 | Auth0 user identifier for data isolation                                                 |
| **temperature_c**            | numeric(3,1)             | YES      | -                 | Temperature in Celsius with 1 decimal place                                              |
| **relative_humidity_pct**    | numeric(5,2)             | YES      | -                 | Relative humidity percentage with 2 decimal places                                       |
| **barometric_pressure_inhg** | numeric(6,2)             | YES      | -                 | Barometric pressure in inHg with 2 decimal places                                        |
| **wind_speed_1_kmh**         | numeric(4,1)             | YES      | -                 | Wind speed measurement 1 in km/h with 1 decimal place                                    |
| **wind_speed_2_kmh**         | numeric(4,1)             | YES      | -                 | Wind speed measurement 2 in km/h with 1 decimal place                                    |
| **wind_direction_deg**       | numeric(5,1)             | YES      | -                 | Wind direction in degrees with 1 decimal place                                           |

## Foreign Key Relationships

The table has the following foreign key relationships:

- **chrono_sessions(id)** - Links to chronograph session data for velocity measurements
- **ranges_submissions(id)** - Links to shooting range information and location data
- **weather_source(id)** - Links to weather measurement devices (optional)
- **rifles(id)** - Links to rifle configuration data including barrel specifications
- **cartridges(id)** - Links to cartridge specifications

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