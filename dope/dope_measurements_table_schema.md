# dope_measurements Table Schema

## Table Description

The `dope_measurements` table stores individual shot measurement data within DOPE (Data On Previous Engagement) sessions. Each record represents a single projectile fired during a shooting session, capturing ballistic performance, environmental conditions, and targeting adjustments.

## Current Database Schema (Metric-Only, Post-Migration)

| **Column Name**              | **Data Type**            | **Nullable** | **Default**      | **Description**                                                                                                                                                                               |
|------------------------------|--------------------------|--------------|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| id                           | uuid                     | NO           | gen_random_uuid() | Primary key, auto-generated UUID                                                                                                                                                             |
| dope_session_id              | uuid                     | NO           | -                | Foreign key to dope_sessions table                                                                                                                                                           |
| user_id                      | text                     | NO           | -                | User identifier for data isolation and security                                                                                                                                               |
| shot_number                  | integer                  | YES          | -                | Sequential shot number within the session                                                                                                                                                     |
| datetime_shot                | timestamp with time zone | YES          | -                | Timestamp when the shot was fired                                                                                                                                                             |
| speed_mps                    | real                     | YES          | -                | **METRIC**: Projectile velocity in meters per second                                                                                                                                         |
| ke_j                         | real                     | YES          | -                | **METRIC**: Kinetic energy in Joules                                                                                                                                                         |
| power_factor_kgms            | real                     | YES          | -                | **METRIC**: Power factor in kg⋅m/s                                                                                                                                                           |
| azimuth_deg                  | real                     | YES          | -                | Horizontal bearing angle in degrees                                                                                                                                                           |
| elevation_angle_deg          | real                     | YES          | -                | Vertical elevation angle in degrees                                                                                                                                                           |
| temperature_c                | real                     | YES          | -                | **METRIC**: Air temperature in Celsius                                                                                                                                                       |
| pressure_hpa                 | real                     | YES          | -                | **METRIC**: Barometric pressure in hectopascals                                                                                                                                              |
| humidity_pct                 | real                     | YES          | -                | Relative humidity as percentage (0-100)                                                                                                                                                       |
| clean_bore                   | text                     | YES          | -                | Bore cleanliness indicator (text field)                                                                                                                                                      |
| cold_bore                    | text                     | YES          | -                | Cold bore indicator (text field)                                                                                                                                                             |
| distance                     | text                     | YES          | -                | **DEPRECATED**: Target distance as text field                                                                                                                                                |
| elevation_adjustment         | text                     | YES          | -                | **DEPRECATED**: Elevation scope adjustment as text field                                                                                                                                     |
| windage_adjustment           | text                     | YES          | -                | **DEPRECATED**: Windage scope adjustment as text field                                                                                                                                       |
| shot_notes                   | text                     | YES          | -                | Free-form notes about the specific shot                                                                                                                                                       |
| created_at                   | timestamp with time zone | YES          | now()            | Record creation timestamp                                                                                                                                                                     |
| updated_at                   | timestamp with time zone | YES          | now()            | Record last update timestamp                                                                                                                                                                  |

## Foreign Key Constraints

| **Constraint Name**                     | **Column**              | **References**                | **Description**                                                                                                                                                                               |
|-----------------------------------------|-------------------------|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| dope_measurements_dope_session_id_fkey  | dope_session_id         | dope_sessions(id)             | Links measurement to its parent DOPE session                                                                                                                                                 |

## Migration History

The table has been successfully migrated to metric-only storage. The following imperial columns were removed:

| **Removed Column**           | **Replaced By**          | **Migration Date**       | **Reason for Removal**                                                                                                                                                                        |
|------------------------------|--------------------------|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| speed_fps                    | speed_mps                | 2025-01-15               | Imperial velocity measurement - replaced by metric equivalent                                                                                                                                 |
| ke_ft_lb                     | ke_j                     | 2025-01-15               | Imperial energy measurement - replaced by metric equivalent                                                                                                                                   |
| power_factor                 | power_factor_kgms        | 2025-01-15               | Imperial power factor - replaced by metric equivalent                                                                                                                                         |
| temperature_f                | temperature_c            | 2025-01-15               | Imperial temperature measurement - replaced by metric equivalent                                                                                                                              |
| pressure_inhg                | pressure_hpa             | 2025-01-15               | Imperial pressure measurement - replaced by metric equivalent                                                                                                                                 |

## Future Schema Enhancements

The following improvements could be implemented for better data structure:

| **Column Name**              | **Data Type**            | **Nullable** | **Default**      | **Purpose**                                                                                                                                                                                   |
|------------------------------|--------------------------|--------------|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| distance_m                   | real                     | YES          | -                | **PROPOSED**: Target distance in meters (to replace text field)                                                                                                                              |
| elevation_adjustment_mrad    | real                     | YES          | -                | **PROPOSED**: Elevation adjustment in milliradians (to replace text field)                                                                                                                   |
| windage_adjustment_mrad      | real                     | YES          | -                | **PROPOSED**: Windage adjustment in milliradians (to replace text field)                                                                                                                     |

## Completed Migration

The metric-only migration has been successfully completed. The following migration was applied:

### Migration: `remove_imperial_columns_from_dope_measurements` (20250914111821)
```sql
-- Remove imperial columns that have been replaced by metric equivalents
ALTER TABLE dope_measurements
DROP COLUMN IF EXISTS speed_fps,
DROP COLUMN IF EXISTS ke_ft_lb,
DROP COLUMN IF EXISTS power_factor,
DROP COLUMN IF EXISTS temperature_f,
DROP COLUMN IF EXISTS pressure_inhg;
```

### Future Text Field Migration Strategy

For converting remaining text fields to structured numeric data:

#### Phase 1: Add Structured Columns
```sql
-- Add new structured columns for deprecated text fields
ALTER TABLE dope_measurements
ADD COLUMN distance_m real,
ADD COLUMN elevation_adjustment_mrad real,
ADD COLUMN windage_adjustment_mrad real;
```

#### Phase 2: Parse and Migrate Text Data
```sql
-- Migrate distance from text to metric
UPDATE dope_measurements
SET distance_m = CASE
    WHEN distance ~ '^[0-9]+\.?[0-9]*\s*y' THEN (CAST(regexp_replace(distance, '[^0-9.]', '', 'g') AS real) * 0.9144)
    WHEN distance ~ '^[0-9]+\.?[0-9]*\s*m' THEN CAST(regexp_replace(distance, '[^0-9.]', '', 'g') AS real)
    ELSE NULL
END
WHERE distance IS NOT NULL;

-- Similar conversions for scope adjustments (MOA to mrad, etc.)
```

#### Phase 3: Remove Legacy Text Columns
```sql
-- Remove deprecated text-based columns
ALTER TABLE dope_measurements
DROP COLUMN distance,
DROP COLUMN elevation_adjustment,
DROP COLUMN windage_adjustment;
```

## Data Integrity Constraints

### Current Constraints
- **Primary Key**: `id` (UUID, auto-generated)
- **Foreign Key**: `dope_session_id` references `dope_sessions(id)`
- **User Isolation**: All queries must filter by `user_id`

### Proposed Additional Constraints
```sql
-- Ensure shot numbers are positive when specified
ALTER TABLE dope_measurements 
ADD CONSTRAINT check_shot_number_positive 
CHECK (shot_number IS NULL OR shot_number > 0);

-- Ensure realistic velocity ranges (metric)
ALTER TABLE dope_measurements 
ADD CONSTRAINT check_speed_mps_range 
CHECK (speed_mps IS NULL OR (speed_mps >= 50 AND speed_mps <= 2000));

-- Ensure realistic temperature ranges
ALTER TABLE dope_measurements 
ADD CONSTRAINT check_temperature_c_range 
CHECK (temperature_c IS NULL OR (temperature_c >= -50 AND temperature_c <= 70));

-- Ensure realistic pressure ranges
ALTER TABLE dope_measurements 
ADD CONSTRAINT check_pressure_hpa_range 
CHECK (pressure_hpa IS NULL OR (pressure_hpa >= 800 AND pressure_hpa <= 1200));

-- Ensure realistic humidity ranges
ALTER TABLE dope_measurements 
ADD CONSTRAINT check_humidity_pct_range 
CHECK (humidity_pct IS NULL OR (humidity_pct >= 0 AND humidity_pct <= 100));
```

## Indexing Strategy

### Current Indexes
- **Primary Index**: `id` (automatic for primary key)
- **Foreign Key Index**: `dope_session_id` (automatic for foreign key)

### Proposed Additional Indexes
```sql
-- Index for user-based queries
CREATE INDEX idx_dope_measurements_user_id ON dope_measurements(user_id);

-- Composite index for session + shot number queries
CREATE INDEX idx_dope_measurements_session_shot ON dope_measurements(dope_session_id, shot_number);

-- Index for datetime-based queries
CREATE INDEX idx_dope_measurements_datetime_shot ON dope_measurements(datetime_shot);

-- Index for velocity-based analysis
CREATE INDEX idx_dope_measurements_speed_mps ON dope_measurements(speed_mps) WHERE speed_mps IS NOT NULL;
```

## Storage Considerations

### Data Types
- **Real vs Numeric**: Using `real` (float4) provides sufficient precision for ballistic measurements while conserving storage
- **UUID**: Uses 16 bytes per record but provides globally unique identifiers
- **Timestamps**: Include timezone information for accurate temporal tracking

### Storage Optimization
- **Nullable Columns**: Most measurement fields are nullable since not all data may be available for every shot
- **Text Fields**: Used for free-form data (notes, bore conditions) where structured data isn't feasible
- **Indexing**: Strategic indexing on commonly queried columns improves performance

## Security and Access Control

### Row Level Security (RLS)
```sql
-- Enable RLS on the table
ALTER TABLE dope_measurements ENABLE ROW LEVEL SECURITY;

-- Policy for user data isolation
CREATE POLICY dope_measurements_user_isolation ON dope_measurements
    FOR ALL USING (user_id = auth.uid()::text);
```

### API Access Patterns
- **All queries** must include `.eq("user_id", user_id)` filter
- **Session validation** should verify user owns the referenced dope_session
- **Batch operations** should validate all records belong to the authenticated user

## Performance Considerations

### Query Patterns
1. **Session-based queries**: Retrieving all measurements for a DOPE session
2. **Statistical analysis**: Aggregating velocity/energy data across measurements
3. **Environmental correlation**: Analyzing performance vs environmental conditions
4. **Temporal analysis**: Tracking performance changes over time

### Optimization Strategies
1. **Composite indexes** for multi-column queries
2. **Partial indexes** for non-null measurements
3. **Query planning** for complex analytical operations
4. **Connection pooling** for high-volume data ingestion

This schema design supports the transition to metric-only internal processing while maintaining compatibility during migration and providing optimized performance for ballistic analysis workflows.