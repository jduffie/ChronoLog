# Ranges Submissions Table Schema

## Table: ranges_submissions

### Columns

| Column Name | Data Type | Nullable | Default | Notes |
|-------------|-----------|----------|---------|-------|
| id | uuid | NO | gen_random_uuid() | Primary key |
| user_id | text | NO | null | Auth0 user identifier |
| range_name | text | NO | null | Proposed range name |
| range_description | text | YES | null | Range description |
| start_lat | numeric(10,6) | NO | null | Firing position latitude |
| start_lon | numeric(10,6) | NO | null | Firing position longitude |
| start_altitude_m | numeric(8,2) | YES | null | Firing position altitude in meters |
| end_lat | numeric(10,6) | NO | null | Target latitude |
| end_lon | numeric(10,6) | NO | null | Target longitude |
| end_altitude_m | numeric(8,2) | YES | null | Target altitude in meters |
| distance_m | numeric(10,2) | YES | null | Range distance in meters |
| azimuth_deg | numeric(6,2) | YES | null | Bearing angle in degrees |
| elevation_angle_deg | numeric(6,2) | YES | null | Elevation angle in degrees |
| address_geojson | jsonb | YES | null | Geocoded address data |
| display_name | text | YES | null | Display name |
| status | text | NO | 'Under Review' | Review status |
| review_reason | text | YES | null | Admin review notes |
| submitted_at | timestamp with time zone | YES | now() | Submission time |
| created_at | timestamp with time zone | YES | now() | Record creation |

### Primary Key
- `id` (uuid)

### Foreign Key References
This table is referenced by:
- `dope_sessions.range_submission_id`

### Indexes
- Primary key index on `id`
- User data isolation: All queries should filter by `user_id`

### Notes
- Uses UUID as primary key with automatic generation
- All user data must be isolated by `user_id`
- Range name is required for submissions
- Start and end coordinates are required with 6 decimal precision
- Status defaults to 'Under Review' for new submissions
- Altitude and calculated fields (distance, angles) are optional
- Address data stored as JSONB for flexible geocoding information
- Timestamps are automatically managed for submission and creation tracking