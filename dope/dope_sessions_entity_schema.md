# dope_sessions Entity Schema

## Table Description

| Column Name                       | Data Type | Nullable | Default | Description                                                |
|-----------------------------------|-----------|----------|---------|------------------------------------------------------------|
| **session_name**                  | text | NO | - | Descriptive name for the DOPE session                      |
| **created_at**                    | timestamp with time zone | YES | now() | Record creation timestamp                                  |
| **chrono_session_id**             | uuid | YES | - | Foreign key to chrono_sessions table                       |
| **range_submission_id**           | uuid | YES | - | Foreign key to ranges_submissions table                    |
| **range_name**                    | text | YES | - | Name of the shooting range from ranges_submissions table   |
| **distance_m**                    | real | YES | - | Target distance in meters                                  |
| **notes**                         | text | YES | - | Session notes and observations                             |
| **status**                        | text | YES | 'active' | Session status                                             |
| **rifle_name**                    | uuid | NO | - | from rifles table                                          |
| **rifle_barrel_length_cm**        | uuid | YES | - | from rifles table                                          |
| **rifle_barrel_twist_in_per_rev** | uuid | YES | - | from rifles table                                          |
| **cartridge_make**                | text | NO | - | creator of the cartridge                                   |
| **cartridge_model**               | text | NO | - | model                                                      |
| **cartridge_type**                | text | NO | - | Type of cartridge ('6mm Creedmore', '22LR', etc)           |
| **cartridge_lot_number**          | text | YES | - | Cartridge lot identifier                                   |
| **bullet_make**                   | text | NO | - | from bullet table                                          |
| **bullet_model**                  | text | NO | - | from bullet table                                          |
| **bullet_weight**                 | text | NO | - | from bullet table                                          |
| **bullet_length_mm**              | text | YES | - | from bullet table                                          |
| **ballistic_coefficient_g1**      | text | YES | - | from bullet table                                          |
| **ballistic_coefficient_g7**      | text | YES | - | from bullet table                                          |
| **sectional_density**             | text | YES | - | from bullet table                                          |
| **bullet_diameter_groove_mm**     | text | YES | - | from bullet table                                          |
| **bore_diameter_land_mm**         | text | YES | - | from bullet table                                          |
| **weather_source_name**           | uuid | YES | - | name from weather_source table                             |
| **temperature_c**                 | numeric(3,1) | YES | - | Temperature in Celsius with 1 decimal place                |
| **relative_humidity_pct**         | numeric(5,2) | YES | - | Relative humidity percentage with 2 decimal places         |
| **barometric_pressure_inhg**      | numeric(6,2) | YES | - | Barometric pressure in inHg with 2 decimal places          |
| **wind_speed_1_kmh**              | numeric(4,1) | YES | - | Wind speed measurement 1 in km/h with 1 decimal place      |
| **wind_speed_2_kmh**              | numeric(4,1) | YES | - | Wind speed measurement 2 in km/h with 1 decimal place      |
| **wind_direction_deg**            | numeric(5,1) | YES | - | Wind direction in degrees with 1 decimal place             |
| **start_lat**                     | numeric(10,6) | YES | - | Firing position latitude from ranges_submissions           |
| **start_lon**                     | numeric(10,6) | YES | - | Firing position longitude from ranges_submissions          |
| **start_altitude_m**              | numeric(8,2) | YES | - | Firing position altitude in meters from ranges_submissions |
| **azimuth_deg**                   | numeric(6,2) | YES | - | Bearing angle in degrees from ranges_submissions           |
| **elevation_angle_deg**           | numeric(6,2) | YES | - | Elevation angle in degrees from ranges_submissions         |

## Foreign Key Relationships

The table has the following foreign key relationships:

- **chrono_sessions(id)** - Links to chronograph session data for velocity measurements
- **ranges_submissions(id)** - Links to shooting range information and location data
- **weather_source(id)** - Links to weather measurement devices (optional)
- **rifles(id)** - Links to rifle configuration data including barrel specifications

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
5. **Flexible Cartridge Tracking**: Supports both factory and custom cartridge specifications
6. **Weather Data**: Includes both linked weather source data and direct weather measurements for environmental tracking
