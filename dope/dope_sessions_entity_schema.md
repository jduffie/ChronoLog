
# dope_sessions Entity Schema

## Table Description

| **Column Name**               | **Data Type**            | Data Source        | **Nullable** | **Default** | **Description**                                                                                                                                                                               |   |
|-------------------------------|--------------------------|--------------------|--------------|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| sectional_density             | text                     | bullets            | YES          | \-          | from bullet table                                                                                                                                                                             |   |
| ballistic_coefficient_g1      | text                     | bullets            | YES          | \-          | from bullet table                                                                                                                                                                             |   |
| ballistic_coefficient_g7      | text                     | bullets            | YES          | \-          | from bullet table                                                                                                                                                                             |   |
| bullet_diameter_groove_mm     | text                     | bullets            | YES          | \-          | from bullet table                                                                                                                                                                             |   |
| bullet_weight                 | text                     | bullets            | NO           | \-          | from bullet table                                                                                                                                                                             |   |
| bore_diameter_land_mm         | text                     | bullets            | NO           | \-          | from bullet table                                                                                                                                                                             |   |
| bullet_model                  | text                     | bullets            | NO           | \-          | from bullet table                                                                                                                                                                             |   |
| bullet_length_mm              | text                     | bullets            | YES          | \-          | from bullet table                                                                                                                                                                             |   |
| bullet_make                   | text                     | bullets            | NO           | \-          | from bullet table                                                                                                                                                                             |   |
| cartridge_type                | text                     | cartridges         | NO           | \-          | Type of cartridge from cartridge_types lookup table (e.g., '6mm Creedmoor', '22 LR', '308 Winchester')                                                                                        |   |
| cartridge_make                | text                     | cartridges         | NO           | \-          | Cartridge manufacturer from cartridges table                                                                                                                                                  |   |
| cartridge_model               | text                     | cartridges         | NO           | \-          | Cartridge model from cartridges table                                                                                                                                                         |   |
| session_name                  | text                     | chrono_sessions    | NO           | \-          | Descriptive name for the DOPE session                                                                                                                                                         |   |
| range_submission_id           | uuid                     | dope_sessions      | YES          | \-          | Foreign key to ranges_submissions table                                                                                                                                                       |   |
| wind_speed_2_kmh              | numeric(4,1)             | dope_sessions      | YES          | \-          | Wind speed measurement 2 in km/h with 1 decimal place<br/><br/>value is either computed from weather_measurements (using median value for the time window) or is entered manually by the user |   |
| status                        | text                     | dope_sessions      | YES          | 'active'    | Session status<br/><br/>provided by the user when session created                                                                                                                             |   |
| notes                         | text                     | dope_sessions      | YES          | \-          | Session notes and observations<br/><br/>provided by the user when session created                                                                                                             |   |
| cartridge_lot_number          | text                     | dope_sessions      | YES          | \-          | Cartridge lot identifier<br/><br/>provided by the user when session created                                                                                                                   |   |
| temperature_c                 | numeric(3,1)             | dope_sessions      | YES          | \-          | Temperature in Celsius with 1 decimal place<br/><br/>value is either computed from weather_measurements (using median value for the time window) or is entered manually by the user           |   |
| cartridge_id                  | uuid                     | dope_sessions      | YES          | \-          | Foreign key to cartridges table - provided by the user when session created                                                                                                                   |   |
| datetime_local                | timestamp with time zone | chrono_sessions    | NO           |             | datetime_local from the chrono_sessions table                                                                                                                                                 |   |
| relative_humidity_pct         | numeric(5,2)             | dope_sessions      | YES          | \-          | Relative humidity percentage with 2 decimal places<br/><br/>value is either computed from weather_measurements (using median value for the time window) or is entered manually by the user    |   |
| weather_source_id             | uuid                     | dope_sessions      |              |             | provided by the user when session created IF user is using external weather source like a kestrel                                                                                             |   |
| chrono_session_id             | uuid                     | dope_sessions      | YES          | \-          | Foreign key to chrono_sessions table                                                                                                                                                          |   |
| wind_speed_1_kmh              | numeric(4,1)             | dope_sessions      | YES          | \-          | Wind speed measurement 1 in km/h with 1 decimal place<br/><br/>value is either computed from weather_measurements (using median value for the time window) or is entered manually by the user |   |
| rifle_id                      | uuid                     | dope_sessions      |              |             | Foreign key to rifles table                                                                                                                                                                   |   |
| wind_direction_deg            | numeric(5,1)             | dope_sessions      | YES          | \-          | Wind direction in degrees with 1 decimal place<br/><br/>value is either computed from weather_measurements (using median value for the time window) or is entered manually by the user        |   |
| barometric_pressure_inhg      | numeric(6,2)             | dope_sessions      | YES          | \-          | Barometric pressure in inHg with 2 decimal places<br/><br/>value is either computed from weather_measurements (using median value for the time window) or is entered manually by the user     |   |
| start_lon                     | numeric(10,6)            | ranges_submissions | YES          | \-          | Firing position longitude from ranges_submissions                                                                                                                                             |   |
| range_name                    | text                     | ranges_submissions | YES          | \-          | Name of the shooting range from ranges_submissions table                                                                                                                                      |   |
| start_altitude_m              | numeric(8,2)             | ranges_submissions | YES          | \-          | Firing position altitude in meters from ranges_submissions                                                                                                                                    |   |
| start_lat                     | numeric(10,6)            | ranges_submissions | YES          | \-          | Firing position latitude from ranges_submissions                                                                                                                                              |   |
| elevation_angle_deg           | numeric(6,2)             | ranges_submissions | YES          | \-          | Elevation angle in degrees from ranges_submissions                                                                                                                                            |   |
| distance_m                    | real                     | ranges_submissions | YES          | \-          | Target distance in meters from ranges_submissions                                                                                                                                             |   |
| azimuth_deg                   | numeric(6,2)             | ranges_submissions | YES          | \-          | Bearing angle in degrees from ranges_submissions                                                                                                                                              |   |
| rifle_name                    | text                     | rifles             | NO           | \-          | from rifles table                                                                                                                                                                             |   |
| rifle_barrel_length_cm        | real                     | rifles             | YES          | \-          | from rifles table                                                                                                                                                                             |   |
| rifle_barrel_twist_in_per_rev | real                     | rifles             | YES          | \-          | from rifles table                                                                                                                                                                             |   |
| weather_source_name           | text                     |                    | YES          | \-          | name from weather_source table                                                                                                                                                                |   |

## Foreign Key Relationships

The table has the following foreign key relationships:

- **chrono_sessions(id)** - Links to chronograph session data for velocity measurements
- **ranges_submissions(id)** - Links to shooting range information and location data
- **weather_source(id)** - Links to weather measurement devices (optional)
- **rifles(id)** - Links to rifle configuration data including barrel specifications
- **cartridges(id)** - Links to cartridge specifications from the unified cartridges table

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

## Cartridge Data Integration

Cartridge information is now sourced from the unified `cartridges` table, which supports both factory and custom cartridge specifications:

- **Cartridge Type**: References the `cartridge_types` lookup table for standardized cartridge caliber/type names (e.g., "6mm Creedmoor", "308 Winchester", "22 LR")
- **Cartridge Make/Model**: Stored directly in the cartridges table for manufacturer and product identification
- **Global vs User-Owned**: The cartridges table supports both global (admin-managed) and user-specific cartridge records

This design provides flexibility for users to reference standard factory cartridges or create custom cartridge specifications while maintaining data consistency through the cartridge_types lookup table.