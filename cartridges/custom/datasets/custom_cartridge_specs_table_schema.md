# Custom Cartridge Specs Table Schema

This document describes the structure of the `custom_cartridge_specs` table in the Supabase database.

## Table: `custom_cartridge_specs`

The custom_cartridge_specs table stores specifications for custom handloaded ammunition cartridges, including load data and component information.

### Columns

| Column               | Type                  | Nullable | Default                                            | Description                                                         |
|----------------------|-----------------------|----------|----------------------------------------------------|---------------------------------------------------------------------|
| **id**               | integer               | NO       | nextval('custom_cartridge_specs_id_seq'::regclass) | Primary key (auto-increment)                                        |
| **user_id**          | text                  | NO       | null                                               | Foreign key to users table                                          |
| **name**             | text                  | NO       | null                                               | User-defined name for the load                                      |
| **cartridge**        | text                  | NO       | null                                               | Cartridge designation (e.g., "6.5 Creedmoor", ".308 Winchester")    |
| **bullet_id**        | integer               | NO       | null                                               | Foreign key to bullets table                                        |
| **powder**           | text                  | YES      | null                                               | Powder type/brand                                                   |
| **powder_charge_gr** | numeric               | YES      | null                                               | Powder charge weight in grains                                      |
| **casing_make**      | text                  | YES      | null                                               | Brass case manufacturer                                             |
| **casing_notes**     | text                  | YES      | null                                               | Notes about case preparation, neck tension, etc.                    |
| **primer**           | text                  | YES      | null                                               | Primer type                                                         |
| **coal_mm**          | double precision      | YES      | null                                               | Cartridge Overall Length in millimeters                             |
| **velocity_fps**     | integer               | YES      | null                                               | Muzzle velocity in feet per second                                  |
| **pressure_notes**   | text                  | YES      | null                                               | Pressure observations, signs, testing notes                         |
| **notes**            | text                  | YES      | null                                               | General notes about the load                                        |
| **cartridge_type**   | cartridge_type (enum) | NO       | null                                               | Enumerated cartridge type (e.g., '6mm Creedmoor', '308 Winchester') |

### Required Fields

- `id` - Primary key (auto-generated)
- `user_id` - User ownership/isolation
- `name` - User-defined load name (e.g., "My 6.5CM Hunting Load")
- `cartridge` - Cartridge designation
- `bullet_id` - Reference to the bullet used in this load

### Optional Fields

- `powder` - Powder type (e.g., "H4350", "Varget")
- `powder_charge_gr` - Powder charge in grains
- `casing_make` - Brass manufacturer (e.g., "Lapua", "Federal")
- `casing_notes` - Case preparation details
- `primer` - Primer specification (e.g., "CCI BR-2", "Federal 210M")
- `coal_mm` - Cartridge Overall Length
- `velocity_fps` - Expected/measured velocity
- `pressure_notes` - Pressure testing observations
- `notes` - General load notes
- `cartridge_type` - Enumerated cartridge type for consistency across the system

### Relationships

- **User Isolation**: Each custom cartridge spec is owned by a specific user via `user_id`
- **Bullet Reference**: Links to `bullets.id` to specify which bullet is used
- **Referenced By**:
  - `custom_cartridge_lots.custom_spec_id`
  - Used in `cartridge_details` view

### Constraints

Based on the table structure, this table likely has:
- Primary key constraint on `id`
- Foreign key constraint on `user_id` referencing `users.id`
- Foreign key constraint on `bullet_id` referencing `bullets.id`
- Possibly unique constraint on `(user_id, name)` to prevent duplicate load names

### Design Notes

- **Complete Load Data**: Captures all aspects of a handload recipe
- **Flexible Components**: All component fields are optional for partial loads
- **User-Friendly Names**: Users can name loads descriptively
- **Performance Tracking**: Velocity and pressure fields for load characterization
- **Development Support**: Notes fields support load development process

### Example Usage

```sql
-- Insert a new custom cartridge specification
INSERT INTO custom_cartridge_specs (
    user_id, name, cartridge, bullet_id, powder, powder_charge_gr,
    casing_make, primer, coal_mm, velocity_fps, notes
) VALUES (
    'user123', 'Match Load 6.5CM', '6.5 Creedmoor', 42, 'H4350', 41.2,
    'Lapua', 'CCI BR-2', 72.4, 2710, 'Excellent accuracy load - 0.4 MOA'
);

-- Query custom loads with bullet details
SELECT ccs.*, b.manufacturer as bullet_manufacturer, b.model as bullet_model, b.weight_grains
FROM custom_cartridge_specs ccs
JOIN bullets b ON b.id = ccs.bullet_id
WHERE ccs.user_id = 'user123'
ORDER BY ccs.cartridge, ccs.name;

-- Find loads using specific powder
SELECT ccs.name, ccs.cartridge, ccs.powder_charge_gr, ccs.velocity_fps
FROM custom_cartridge_specs ccs
WHERE ccs.user_id = 'user123' AND ccs.powder = 'H4350'
ORDER BY ccs.powder_charge_gr;

-- Search loads by performance
SELECT ccs.name, ccs.cartridge, ccs.velocity_fps, ccs.notes
FROM custom_cartridge_specs ccs
WHERE ccs.user_id = 'user123' 
AND ccs.velocity_fps > 2700
ORDER BY ccs.velocity_fps DESC;
```

### Integration with Views

This table is used in the `cartridge_details` view to provide a unified interface with factory cartridges:

```sql
-- Part of cartridge_details view for custom cartridges
SELECT c.id AS spec_id,
    'custom'::text AS source,
    c.cartridge_type,
    NULL::text AS manufacturer,
    c.name AS model,
    c.bullet_id,
    -- ... bullet details joined from bullets table
FROM custom_cartridge_specs c
LEFT JOIN bullets b ON b.id = c.bullet_id;
```

### Load Development Workflow

1. **Initial Specification**: User creates basic load with bullet and cartridge
2. **Component Selection**: Add powder, primer, brass specifications
3. **Load Development**: Iterate on powder charges and seating depth
4. **Performance Testing**: Record velocity and accuracy data
5. **Lot Tracking**: Create lots in `custom_cartridge_lots` for specific batches
6. **Refinement**: Update specifications based on testing results

### Component Data Management

#### Powder Information
- **Type**: Specific powder brand and model
- **Charge**: Weight in grains (typically 2-3 decimal precision)
- **Pressure Notes**: Signs of pressure, chronograph data correlation

#### Case Information
- **Make**: Manufacturer for quality/consistency tracking
- **Preparation**: Details about sizing, trimming, annealing
- **Neck Tension**: Critical for consistency

#### Primer Selection
- **Type**: Large/small rifle, magnum, benchrest variants
- **Performance**: Impact on ignition consistency and accuracy

#### Cartridge Overall Length
- **COAL**: Critical dimension affecting pressure and accuracy
- **Seating Depth**: Relationship to lands for optimal accuracy

### Use Cases

- **Load Recipe Storage**: Digital load book for handloaders
- **Component Tracking**: Record which components work well together
- **Performance Database**: Build library of tested loads
- **Safety Documentation**: Pressure signs and safe charge weights
- **Accuracy Development**: Track loads that shoot well in specific rifles
- **Seasonal Adjustments**: Different loads for different conditions