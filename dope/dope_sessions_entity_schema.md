# dope_sessions Entity Schema

## Table Description

This entity represents a flattened view of DOPE session data with joined information from related tables.

| **Column Name**                     | **Data Type**            | Data Source        | **Nullable** | **Default**       | **Description**                                                                    |
|-------------------------------------|--------------------------|--------------------|--------------|--------------------|------------------------------------------------------------------------------------|
| **id**                              | uuid                     | dope_sessions      | NO           | gen_random_uuid()  | Primary key, auto-generated unique identifier                                      |
| **user_id**                         | text                     | dope_sessions      | NO           | -                  | Auth0 user identifier for data isolation                                           |
| **session_name**                    | text                     | dope_sessions      | NO           | -                  | Descriptive name for the DOPE session                                              |
| **start_time**                      | timestamp with time zone | dope_sessions      | NO           | -                  | Session start time from chronograph time window                                    |
| **end_time**                        | timestamp with time zone | dope_sessions      | NO           | -                  | Session end time from chronograph time window                                      |
| **chrono_session_id**               | uuid                     | dope_sessions      | NO           | -                  | Foreign key to chrono_sessions table (required)                                    |
| **range_submission_id**             | uuid                     | dope_sessions      | NO           | -                  | Foreign key to ranges_submissions table (required)                                 |
| **weather_source_id**               | uuid                     | dope_sessions      | YES          | -                  | Foreign key to weather_source table (optional)                                     |
| **rifle_id**                        | uuid                     | dope_sessions      | NO           | -                  | Foreign key to rifles table (required)                                             |
| **cartridge_id**                    | uuid                     | dope_sessions      | NO           | -                  | Foreign key to cartridges table (required)                                         |
| **bullet_id**                       | uuid                     | dope_sessions      | NO           | -                  | Foreign key to bullets table (required)                                            |
| **notes**                           | text                     | dope_sessions      | YES          | -                  | Session notes and observations                                                     |
| **cartridge_lot_number**            | text                     | dope_sessions      | YES          | -                  | Cartridge lot identifier                                                           |
| **temperature_c_median**            | real                     | dope_sessions      | YES          | -                  | Median temperature in Celsius from weather association                             |
| **relative_humidity_pct_median**    | real                     | dope_sessions      | YES          | -                  | Median relative humidity percentage from weather association                       |
| **barometric_pressure_inhg_median** | real                     | dope_sessions      | YES          | -                  | Median barometric pressure in inHg from weather association                        |
| **wind_speed_mps_median**           | real                     | dope_sessions      | YES          | -                  | Median wind speed in m/s from weather association                                  |
| **wind_direction_deg_median**       | real                     | dope_sessions      | YES          | -                  | Median wind direction in degrees from weather association                          |
| **speed_mps_min**                   | real                     | dope_sessions      | NO           | -                  | Minimum velocity in m/s from chronograph session                                   |
| **speed_mps_max**                   | real                     | dope_sessions      | NO           | -                  | Maximum velocity in m/s from chronograph session                                   |
| **speed_mps_avg**                   | real                     | dope_sessions      | NO           | -                  | Average velocity in m/s from chronograph session                                   |
| **speed_mps_std_dev**               | real                     | dope_sessions      | NO           | -                  | Standard deviation of velocity in m/s from chronograph session                     |
| **created_at**                      | timestamp with time zone | dope_sessions      | NO           | now()              | Record creation timestamp                                                          |
| **updated_at**                      | timestamp with time zone | dope_sessions      | NO           | now()              | Last modification timestamp                                                        |
| **datetime_local**                  | timestamp with time zone | chrono_sessions    | NO           | -                  | Session datetime from chronograph session                                          |
| **chrono_session_name**             | text                     | chrono_sessions    | YES          | -                  | Session name from chronograph session                                              |
| **cartridge_type**                  | text                     | cartridges         | NO           | -                  | Cartridge type (e.g., '6mm Creedmoor', '308 Winchester')                          |
| **cartridge_make**                  | text                     | cartridges         | NO           | -                  | Cartridge manufacturer                                                             |
| **cartridge_model**                 | text                     | cartridges         | NO           | -                  | Cartridge model                                                                    |
| **bullet_make**                     | text                     | bullets            | NO           | -                  | Bullet manufacturer                                                                |
| **bullet_model**                    | text                     | bullets            | NO           | -                  | Bullet model                                                                       |
| **bullet_weight**                   | text                     | bullets            | NO           | -                  | Bullet weight in grains                                                            |
| **bullet_length_mm**                | text                     | bullets            | YES          | -                  | Bullet length in millimeters                                                       |
| **ballistic_coefficient_g1**        | text                     | bullets            | YES          | -                  | G1 ballistic coefficient                                                           |
| **ballistic_coefficient_g7**        | text                     | bullets            | YES          | -                  | G7 ballistic coefficient                                                           |
| **sectional_density**               | text                     | bullets            | YES          | -                  | Sectional density                                                                  |
| **bullet_diameter_groove_mm**       | text                     | bullets            | YES          | -                  | Bullet diameter (groove) in millimeters                                            |
| **bore_diameter_land_mm**           | text                     | bullets            | NO           | -                  | Bore diameter (land) in millimeters                                                |
| **rifle_name**                      | text                     | rifles             | NO           | -                  | Rifle name                                                                         |
| **rifle_barrel_length_cm**          | real                     | rifles             | YES          | -                  | Barrel length in centimeters                                                       |
| **rifle_barrel_twist_in_per_rev**   | real                     | rifles             | YES          | -                  | Barrel twist rate in inches per revolution                                         |
| **range_name**                      | text                     | ranges_submissions | YES          | -                  | Name of the shooting range                                                         |
| **range_display_name**              | text                     | ranges_submissions | YES          | -                  | Display name for the range                                                         |
| **range_description**               | text                     | ranges_submissions | YES          | -                  | Range description                                                                  |
| **lat**                             | numeric(10,6)            | ranges_submissions | YES          | -                  | Firing position latitude (mapped from start_lat)                                   |
| **lon**                             | numeric(10,6)            | ranges_submissions | YES          | -                  | Firing position longitude (mapped from start_lon)                                  |
| **end_lat**                         | numeric(10,6)            | ranges_submissions | YES          | -                  | Target position latitude                                                           |
| **end_lon**                         | numeric(10,6)            | ranges_submissions | YES          | -                  | Target position longitude                                                          |
| **start_altitude**                  | numeric(8,2)             | ranges_submissions | YES          | -                  | Firing position altitude in meters (mapped from start_altitude_m)                  |
| **range_distance_m**                | real                     | ranges_submissions | YES          | -                  | Target distance in meters (mapped from distance_m)                                 |
| **azimuth_deg**                     | numeric(6,2)             | ranges_submissions | YES          | -                  | Bearing angle in degrees                                                           |
| **elevation_angle_deg**             | numeric(6,2)             | ranges_submissions | YES          | -                  | Elevation angle in degrees                                                         |
| **location_hyperlink**              | text                     | ranges_submissions | YES          | -                  | Google Maps URL with marker at firing position                                     |
| **weather_source_name**             | text                     | weather_source     | YES          | -                  | Name from weather_source table                                                     |

## Foreign Key Relationships

The entity includes joined data from the following tables:

- **chrono_sessions(id)** - Links to chronograph session data for velocity measurements (required)
- **ranges_submissions(id)** - Links to shooting range information and location data (required)
- **weather_source(id)** - Links to weather measurement devices (optional)
- **rifles(id)** - Links to rifle configuration data including barrel specifications (required)
- **cartridges(id)** - Links to cartridge specifications (required)
- **bullets(id)** - Links to bullet specifications for ballistic calculations (required)

## Purpose and Context

The `dope_sessions` entity represents a complete DOPE (Data On Previous Engagement) session with all related data flattened for easy access. This entity is used for:

- Displaying session information in the UI
- Ballistic analysis and trajectory calculations
- Performance tracking across different conditions
- Historical reference for shooting data

Each DOPE session captures:

- **Chronograph data**: Velocity measurements with min, max, average, and standard deviation
- **Range information**: Location, distance, bearing, and elevation data
- **Weather conditions**: Median environmental measurements from linked weather sources
- **Rifle configuration**: Barrel specifications and rifle details
- **Cartridge/Bullet data**: Complete ammunition specifications for ballistic calculations

## Key Features

1. **User Isolation**: The `user_id` field ensures data is properly isolated per user
2. **Required Core Data**: Chronograph session, range, rifle, cartridge, and bullet must be specified
3. **Velocity Statistics**: Min, max, average, and standard deviation computed from chronograph measurements
4. **Optional Weather Source**: Weather source link is optional to accommodate sessions without linked weather data
5. **Flattened Structure**: All related data is joined and accessible without additional queries
6. **Metric Units**: All measurements are stored in metric units (m/s, meters, Celsius, hPa)
7. **Comprehensive Context**: Complete ballistic and environmental data for trajectory analysis

## Data Lineage

The entity combines data from multiple sources:

- **Core Session Data**: From `dope_sessions` table (identifiers, notes, foreign keys, timestamps)
- **Velocity Statistics**: Aggregated from chronograph measurements during session creation
- **Weather Medians**: Aggregated from weather measurements within the session time window
- **Joined Reference Data**: From bullets, cartridges, rifles, ranges, and chronograph sessions