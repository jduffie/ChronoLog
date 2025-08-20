# Bullets Table Schema

## Table: bullets

### Columns

| Column Name | Data Type | Nullable | Default | Notes |
|-------------|-----------|----------|---------|-------|
| id | uuid | NO | null | Primary key |
| user_id | text | NO | null | Auth0 user identifier |
| manufacturer | text | NO | null | Bullet manufacturer |
| model | text | NO | null | Bullet model |
| weight_grains | integer | NO | null | Weight in grains |
| bullet_diameter_groove_mm | double precision | NO | null | Groove diameter in millimeters |
| bore_diameter_land_mm | double precision | NO | null | Land diameter in millimeters |
| bullet_length_mm | double precision | YES | null | Length in millimeters |
| ballistic_coefficient_g1 | double precision | YES | null | G1 ballistic coefficient |
| ballistic_coefficient_g7 | double precision | YES | null | G7 ballistic coefficient |
| sectional_density | double precision | YES | null | Sectional density |
| min_req_twist_rate_in_per_rev | double precision | YES | null | Minimum required twist rate |
| pref_twist_rate_in_per_rev | double precision | YES | null | Preferred twist rate |
| data_source_name | text | YES | null | Name or description of the data source |
| data_source_url | text | YES | null | URL or reference to the original data source |

### Primary Key
- `id` (uuid)

### Foreign Key References
This table is referenced by:
- `factory_cartridge_specs.bullet_id`
- `custom_cartridge_specs.bullet_id`

### Indexes
- Primary key index on `id`
- User data isolation: All queries should filter by `user_id`

### Notes
- Currently uses UUID as primary key
- All user data must be isolated by `user_id`
- Manufacturer and model are required fields
- Weight in grains is required
- Diameter measurements are required in millimeters
- Ballistic data fields are optional
- Data source fields track origin of bullet specifications