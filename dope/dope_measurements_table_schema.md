# dope_measurements Table Schema

## CREATE TABLE Statement

```sql
CREATE TABLE dope_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dope_session_id UUID NOT NULL REFERENCES dope_sessions(id),
    user_id TEXT NOT NULL,
    shot_number INTEGER NOT NULL,
    datetime_shot TIMESTAMPTZ NOT NULL,

    -- Ballistic measurements (metric only)
    speed_mps REAL NOT NULL,
    ke_j REAL,
    power_factor_kgms REAL,

    -- Environmental conditions (metric only)
    temperature_c REAL,
    pressure_hpa REAL,
    humidity_pct REAL,

    -- Targeting data
    distance_m REAL,
    elevation_adjustment REAL,
    windage_adjustment REAL,

    -- Bore conditions
    clean_bore TEXT,
    cold_bore TEXT,

    -- Notes and timestamps
    shot_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

## Recommended Indexes

```sql
CREATE INDEX idx_dope_measurements_user_id ON dope_measurements(user_id);
CREATE INDEX idx_dope_measurements_dope_session_id ON dope_measurements(dope_session_id);
CREATE INDEX idx_dope_measurements_session_shot ON dope_measurements(dope_session_id, shot_number);
CREATE INDEX idx_dope_measurements_datetime_shot ON dope_measurements(datetime_shot);
```

## Table Description

| Column Name              | Description                                              | Lineage                                   | Data Type                | Nullable | Default           |
|--------------------------|----------------------------------------------------------|-------------------------------------------|--------------------------|----------|-------------------|
| **id**                   | Primary key, auto-generated unique identifier            | Database auto-generated                   | uuid                     | NO       | gen_random_uuid() |
| **dope_session_id**      | Foreign key to dope_sessions table                       | Parent DOPE session                       | uuid                     | NO       | -                 |
| **user_id**              | Auth0 user identifier for data isolation                 | Auth0 authentication system               | text                     | NO       | -                 |
| **shot_number**          | Sequential shot number within the session                | Chronograph measurement                   | integer                  | NO       | -                 |
| **datetime_shot**        | Timestamp when the shot was fired                        | Chronograph measurement                   | timestamp with time zone | NO       | -                 |
| **speed_mps**            | Projectile velocity in meters per second                 | Chronograph measurement                   | real                     | NO       | -                 |
| **ke_j**                 | Kinetic energy in Joules                                 | Chronograph measurement                   | real                     | YES      | -                 |
| **power_factor_kgms**    | Power factor in kg⋅m/s                                   | Chronograph measurement                   | real                     | YES      | -                 |
| **temperature_c**        | Air temperature in Celsius                               | Weather source                            | real                     | YES      | -                 |
| **pressure_hpa**         | Barometric pressure in hectopascals                      | Weather source                            | real                     | YES      | -                 |
| **humidity_pct**         | Relative humidity as percentage (0-100)                  | Weather source                            | real                     | YES      | -                 |
| **distance_m**           | Target distance in meters                                | User input via UI                         | real                     | YES      | -                 |
| **elevation_adjustment** | Elevation scope adjustment                               | User input via UI                         | real                     | YES      | -                 |
| **windage_adjustment**   | Windage scope adjustment                                 | User input via UI                         | real                     | YES      | -                 |
| **clean_bore**           | Bore cleanliness indicator (yes/no/fouled)               | User input via UI                         | text                     | YES      | -                 |
| **cold_bore**            | Cold bore indicator (yes/no)                             | User input via UI                         | text                     | YES      | -                 |
| **shot_notes**           | Free-form notes about the specific shot                  | User input via UI                         | text                     | YES      | -                 |
| **created_at**           | Record creation timestamp                                | Database auto-generated                   | timestamp with time zone | YES      | now()             |
| **updated_at**           | Last modification timestamp                              | Database auto-generated on updates        | timestamp with time zone | YES      | now()             |

## Foreign Key Relationships

The table has the following foreign key relationships:

- **dope_sessions(id)** - Links to parent DOPE session containing session-level metadata and configuration

## Purpose and Context

The `dope_measurements` table stores individual shot measurement data within DOPE (Data On Previous Engagement) sessions. Each record represents a single projectile fired during a shooting session, capturing:

- Ballistic performance (velocity, energy, power factor)
- Environmental conditions (temperature, pressure, humidity)
- Targeting adjustments (elevation, windage, distance)
- Shot-specific metadata (bore condition, notes, timestamp)

Each measurement is linked to its parent DOPE session, which provides the context of rifle, cartridge, range, and overall session configuration.

## Key Features

1. **User Isolation**: The `user_id` field ensures data is properly isolated per user
2. **Metric-Only Storage**: All measurements are stored in metric units internally
3. **Flexible Data**: Most fields are nullable to accommodate varying data availability
4. **Shot Tracking**: Sequential shot numbering and timestamps for temporal analysis
5. **Environmental Context**: Captures conditions at the time of each shot for correlation analysis
6. **Parent Session Link**: All measurements are tied to a DOPE session for complete context
