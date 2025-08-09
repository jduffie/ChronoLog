# Custom Cartridge Lots Table Schema

This document describes the structure of the `custom_cartridge_lots` table in the Supabase database.

## Table: `custom_cartridge_lots`

The custom_cartridge_lots table stores specific manufacturing lot information for custom cartridge specifications, enabling tracking of individual batches of handloaded ammunition.

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| **id** | integer | NO | nextval('custom_cartridge_lots_id_seq'::regclass) | Primary key (auto-increment) |
| **user_id** | text | NO | null | Foreign key to users table |
| **custom_spec_id** | integer | NO | null | Foreign key to custom_cartridge_specs table |
| **lot_number** | text | NO | null | User-defined lot number or batch identifier |
| **mfg_date** | date | YES | null | Manufacturing/loading date |
| **notes** | text | YES | null | User notes about this specific lot |

### Required Fields

- `id` - Primary key (auto-generated)
- `user_id` - User ownership/isolation
- `custom_spec_id` - Reference to the custom cartridge specification
- `lot_number` - User-defined lot number or batch identifier

### Optional Fields

- `mfg_date` - Date the lot was loaded/manufactured
- `notes` - Free-form notes about lot performance, testing results, storage, etc.

### Relationships

- **User Isolation**: Each custom cartridge lot is owned by a specific user via `user_id`
- **Specification Reference**: Links to `custom_cartridge_specs.id` to specify which custom load this lot represents
- **Used In**: Referenced by `cartridge_details` view for lot tracking

### Constraints

Based on the table structure, this table likely has:
- Primary key constraint on `id`
- Foreign key constraint on `user_id` referencing `users.id`
- Foreign key constraint on `custom_spec_id` referencing `custom_cartridge_specs.id`
- Possibly unique constraint on `(user_id, custom_spec_id, lot_number)` to prevent duplicate lot entries

### Design Notes

- **Handload Tracking**: Enables tracking of specific handloaded batches
- **Load Development**: Users can track performance of different load iterations
- **Testing Documentation**: Notes field allows detailed recording of test results
- **Batch Management**: Helps organize handloaded ammunition by batches
- **User-Defined Lots**: Lot numbers are completely user-controlled (unlike factory lots)

### Example Usage

```sql
-- Insert a new custom cartridge lot
INSERT INTO custom_cartridge_lots (
    user_id, custom_spec_id, lot_number, mfg_date, notes
) VALUES (
    'user123', 15, 'Load-001-V1', '2023-08-15', 
    'Initial load test - 0.75 MOA @ 100yd, SD 8.2fps, ES 22fps'
);

-- Query lots for a specific custom cartridge
SELECT ccl.*, ccs.name, ccs.cartridge
FROM custom_cartridge_lots ccl
JOIN custom_cartridge_specs ccs ON ccs.id = ccl.custom_spec_id
WHERE ccl.user_id = 'user123' AND ccl.custom_spec_id = 15
ORDER BY ccl.mfg_date DESC;

-- Find best performing lots based on notes
SELECT ccl.lot_number, ccs.name, ccl.notes
FROM custom_cartridge_lots ccl
JOIN custom_cartridge_specs ccs ON ccs.id = ccl.custom_spec_id
WHERE ccl.user_id = 'user123' 
AND ccl.notes ILIKE '%MOA%'
ORDER BY ccl.mfg_date DESC;

-- Track load development progression
SELECT ccl.lot_number, ccl.mfg_date, ccs.powder_charge_gr, ccl.notes
FROM custom_cartridge_lots ccl
JOIN custom_cartridge_specs ccs ON ccs.id = ccl.custom_spec_id
WHERE ccl.user_id = 'user123' AND ccs.name = 'My 6.5CM Load'
ORDER BY ccl.mfg_date;
```

### Integration with Views

This table is used in the `cartridge_details` view to provide lot information alongside custom cartridge specifications:

```sql
-- Part of cartridge_details view showing custom lot integration
SELECT c.id AS spec_id,
    'custom'::text AS source,
    c.cartridge_type,
    NULL::text AS manufacturer,
    c.name AS model,
    c.bullet_id,
    -- ... bullet details ...
    cl.id AS lot_id,
    cl.lot_number,
    cl.mfg_date,
    cl.notes AS lot_notes
FROM custom_cartridge_specs c
LEFT JOIN bullets b ON b.id = c.bullet_id
LEFT JOIN custom_cartridge_lots cl ON cl.custom_spec_id = c.id AND cl.user_id = c.user_id;
```

### Typical Workflow

1. User develops a custom load specification in `custom_cartridge_specs`
2. User loads ammunition and creates lot records in `custom_cartridge_lots`
3. User tests loads and records performance data in the `notes` field
4. User iterates on load development, creating new lots for variations
5. Historical lot data guides future load development decisions

### Use Cases

- **Load Development**: Track iterations of load recipes during development
- **Performance Testing**: Record chronograph data, accuracy results, pressure signs
- **Batch Tracking**: Organize handloaded ammunition by loading sessions
- **Component Lot Correlation**: Track which component lots were used in each load
- **Seasonal Testing**: Record how loads perform in different conditions
- **Load Book Maintenance**: Digital record of handloading activities

### Custom vs Factory Lots

Unlike factory lots which track purchased ammunition:
- **User-Controlled**: Lot numbers are defined by the user
- **Load Development Focus**: Designed for tracking handload variations
- **Detailed Notes**: Emphasis on recording test data and observations
- **Iterative Process**: Supports multiple lots per specification for development
- **Component Tracking**: Can record details about specific components used