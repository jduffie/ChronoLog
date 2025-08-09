# Cartridge Details View Schema

This document describes the structure of the `cartridge_details` view in the Supabase database.

## View: `cartridge_details`

The cartridge_details view provides a unified interface for viewing both factory and custom cartridge specifications along with their associated bullet information. This view combines data from multiple tables to present a complete picture of cartridge specifications.

### Columns

| Column | Type | Nullable | Source Table | Description |
|--------|------|----------|--------------|-------------|
| **spec_id** | integer | YES | factory_cartridge_specs.id / custom_cartridge_specs.id | Primary key from either factory_cartridge_specs or custom_cartridge_specs |
| **source** | text | YES | Computed | Source type: 'factory' or 'custom' |
| **user_id** | text | YES | factory_cartridge_specs.user_id / custom_cartridge_specs.user_id | User ownership from cartridge spec tables |
| **cartridge_type** | text | YES | factory_cartridge_specs / custom_cartridge_specs | Cartridge type designation (e.g., "6.5 Creedmoor", ".308 Winchester") |
| **manufacturer** | text | YES | factory_cartridge_specs.make | Cartridge manufacturer (NULL for custom cartridges) |
| **model** | text | YES | factory_cartridge_specs.model / custom_cartridge_specs.name | Cartridge model/product name or custom name |
| **bullet_id** | integer | YES | factory_cartridge_specs / custom_cartridge_specs | Foreign key reference to bullets table |
| **bullet_name** | text | YES | Computed | Computed friendly bullet description from bullets fields |
| **bullet_manufacturer** | text | YES | bullets.manufacturer | Bullet manufacturer from bullets table |
| **bullet_model** | text | YES | bullets.model | Bullet model from bullets table |
| **bullet_weight_grains** | integer | YES | bullets.weight_grains | Bullet weight in grains |
| **bullet_diameter_groove_mm** | double precision | YES | bullets.bullet_diameter_groove_mm | Bullet diameter at groove in mm |
| **bore_diameter_land_mm** | double precision | YES | bullets.bore_diameter_land_mm | Bore diameter at land in mm |
| **bullet_length_mm** | double precision | YES | bullets.bullet_length_mm | Bullet length in mm |
| **ballistic_coefficient_g1** | double precision | YES | bullets.ballistic_coefficient_g1 | G1 ballistic coefficient |
| **ballistic_coefficient_g7** | double precision | YES | bullets.ballistic_coefficient_g7 | G7 ballistic coefficient |
| **sectional_density** | double precision | YES | bullets.sectional_density | Bullet sectional density |
| **min_req_twist_rate_in_per_rev** | double precision | YES | bullets.min_req_twist_rate_in_per_rev | Minimum required twist rate (in/rev) |
| **pref_twist_rate_in_per_rev** | double precision | YES | bullets.pref_twist_rate_in_per_rev | Preferred twist rate (in/rev) |

### View Definition

The view is constructed using a UNION ALL of factory and custom cartridge specifications:

```sql
-- Factory cartridge portion
SELECT f.id AS spec_id,
    'factory'::text AS source,
    f.user_id,
    f.cartridge_type,
    f.make AS manufacturer,
    f.model,
    f.bullet_id,
    concat_ws(' '::text, 
        COALESCE(NULLIF(TRIM(BOTH FROM concat_ws(' '::text, b.manufacturer, b.model)), ''::text), 'Unknown'::text), 
        concat_ws(' '::text, b.weight_grains::text, 'gr'), 
        concat_ws(' '::text, round(b.bore_diameter_land_mm::numeric, 3)::text, 'mm')
    ) AS bullet_name,
    b.manufacturer AS bullet_manufacturer,
    b.model AS bullet_model,
    b.weight_grains AS bullet_weight_grains,
    b.bullet_diameter_groove_mm,
    b.bore_diameter_land_mm,
    b.bullet_length_mm,
    b.ballistic_coefficient_g1,
    b.ballistic_coefficient_g7,
    b.sectional_density,
    b.min_req_twist_rate_in_per_rev,
    b.pref_twist_rate_in_per_rev
FROM factory_cartridge_specs f
LEFT JOIN bullets b ON b.id = f.bullet_id

UNION ALL

-- Custom cartridge portion
SELECT c.id AS spec_id,
    'custom'::text AS source,
    c.user_id,
    c.cartridge_type,
    NULL::text AS manufacturer,
    c.name AS model,
    c.bullet_id,
    concat_ws(' '::text, 
        COALESCE(NULLIF(TRIM(BOTH FROM concat_ws(' '::text, b.manufacturer, b.model)), ''::text), 'Unknown'::text), 
        concat_ws(' '::text, b.weight_grains::text, 'gr'), 
        concat_ws(' '::text, round(b.bore_diameter_land_mm::numeric, 3)::text, 'mm')
    ) AS bullet_name,
    b.manufacturer AS bullet_manufacturer,
    b.model AS bullet_model,
    b.weight_grains AS bullet_weight_grains,
    b.bullet_diameter_groove_mm,
    b.bore_diameter_land_mm,
    b.bullet_length_mm,
    b.ballistic_coefficient_g1,
    b.ballistic_coefficient_g7,
    b.sectional_density,
    b.min_req_twist_rate_in_per_rev,
    b.pref_twist_rate_in_per_rev
FROM custom_cartridge_specs c
LEFT JOIN bullets b ON b.id = c.bullet_id;
```

### Key Features

#### Unified Interface
- **Single Query Point**: Access both factory and custom cartridges through one view
- **Consistent Schema**: Same column structure regardless of cartridge source
- **Source Identification**: `source` column distinguishes between 'factory' and 'custom'

#### Computed Fields
- **bullet_name**: Human-friendly bullet description combining manufacturer, model, weight, and caliber
- **Standardized Nulls**: NULL values for fields not applicable to specific cartridge types

#### Data Relationships
- **Bullet Integration**: Complete bullet specifications joined from bullets table
- **User Isolation**: Inherits user filtering from underlying tables
- **Type Flexibility**: Supports both factory and custom cartridge specifications

### Usage Examples

```sql
-- Get all cartridges for a user (now simplified with user_id in view)
SELECT * FROM cartridge_details 
WHERE user_id = 'user123'
ORDER BY source, manufacturer, model;

-- Find cartridges by caliber
SELECT source, manufacturer, model, bullet_name
FROM cartridge_details
WHERE cartridge_type = '6.5 Creedmoor'
ORDER BY source, manufacturer, model;

-- Get cartridges using specific bullet weight
SELECT source, manufacturer, model, bullet_name
FROM cartridge_details
WHERE bullet_weight_grains = 147
ORDER BY source, manufacturer;

-- Find high BC bullets
SELECT DISTINCT bullet_name, ballistic_coefficient_g1, ballistic_coefficient_g7
FROM cartridge_details
WHERE ballistic_coefficient_g1 > 0.6 OR ballistic_coefficient_g7 > 0.3
ORDER BY ballistic_coefficient_g1 DESC;
```

### Application Integration

This view is primarily used by:
- **Cartridges Page**: Main data source for the view tab
- **Filtering**: Supports filtering by source, manufacturer, cartridge type, and bullet specifications
- **Export Functions**: Provides unified data for CSV exports
- **Detailed Views**: Source for expandable detail sections

### Design Benefits

1. **Simplified Queries**: Single query instead of complex UNION operations
2. **Consistent Interface**: Same schema for factory and custom cartridges
3. **Rich Data**: Includes complete bullet specifications
4. **Performance**: Pre-computed bullet_name field reduces client-side processing
5. **Flexibility**: Easy to extend with additional computed fields

### Performance Considerations

- **Indexing**: Performance depends on underlying table indexes
- **User Filtering**: Always filter by user_id on underlying tables
- **Bullet Joins**: LEFT JOIN ensures cartridges appear even with missing bullet data
- **Computed Fields**: bullet_name computation happens at query time

### Limitations

- **No Direct Updates**: Being a view, updates must be made to underlying tables
- **User Context**: Requires application-level user filtering
- **No Aggregation**: Individual cartridge records only, no summary statistics