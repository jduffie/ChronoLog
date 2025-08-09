# Bullets Table Schema

This document describes the structure of the `bullets` table in the Supabase database.

## Table: `bullets`

The bullets table stores bullet specifications and ballistic data for users.

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| **id** | integer | NO | nextval('bullets_id_seq'::regclass) | Primary key (auto-increment) |
| **user_id** | text | NO | null | Foreign key to users table |
| **manufacturer** | text | NO | null | Bullet manufacturer name |
| **model** | text | NO | null | Bullet model/type |
| **weight_grains** | integer | NO | null | Bullet weight in grains |
| **bullet_diameter_groove_mm** | double precision | NO | null | Bullet diameter at groove (mm) |
| **bore_diameter_land_mm** | double precision | NO | null | Bore diameter at land (mm) |
| **bullet_length_mm** | double precision | YES | null | Bullet length in millimeters |
| **ballistic_coefficient_g1** | double precision | YES | null | G1 ballistic coefficient |
| **ballistic_coefficient_g7** | double precision | YES | null | G7 ballistic coefficient |
| **sectional_density** | double precision | YES | null | Sectional density |
| **min_req_twist_rate_in_per_rev** | double precision | YES | null | Minimum required twist rate (in/rev) |
| **pref_twist_rate_in_per_rev** | double precision | YES | null | Preferred twist rate (in/rev) |

### Required Fields

- `id` - Primary key (auto-generated)
- `user_id` - User ownership/isolation
- `manufacturer` - Bullet manufacturer name
- `model` - Bullet model or type designation
- `weight_grains` - Bullet weight in grains
- `bullet_diameter_groove_mm` - Bullet diameter at the groove
- `bore_diameter_land_mm` - Bore diameter at the land

### Optional Fields

- `bullet_length_mm` - Physical bullet length
- `ballistic_coefficient_g1` - G1 ballistic coefficient for trajectory calculations
- `ballistic_coefficient_g7` - G7 ballistic coefficient for trajectory calculations
- `sectional_density` - Bullet sectional density (weight/diameter²)
- `min_req_twist_rate_in_per_rev` - Minimum required barrel twist rate
- `pref_twist_rate_in_per_rev` - Preferred barrel twist rate

### Relationships

- **User Isolation**: Each bullet record is owned by a specific user via `user_id`
- **Referenced By**: 
  - `factory_cartridge_specs.bullet_id`
  - `custom_cartridge_specs.bullet_id`

### Notes

- All precision measurements use millimeters for consistency
- Twist rates are specified in inches per revolution
- Optional ballistic fields allow for incomplete bullet data while maintaining core functionality
- The table supports both factory bullets with full specifications and custom/unknown bullets with minimal data

### Example Usage

```sql
-- Insert a new bullet with full specifications
INSERT INTO bullets (
    user_id, manufacturer, model, weight_grains,
    bullet_diameter_groove_mm, bore_diameter_land_mm,
    bullet_length_mm, ballistic_coefficient_g1,
    sectional_density, min_req_twist_rate_in_per_rev
) VALUES (
    'user123', 'Hornady', 'ELD-M', 147,
    6.500, 6.350, 33.5, 0.697,
    0.301, 8.0
);

-- Query bullets for a specific user
SELECT * FROM bullets 
WHERE user_id = 'user123' 
ORDER BY manufacturer, model, weight_grains;
```