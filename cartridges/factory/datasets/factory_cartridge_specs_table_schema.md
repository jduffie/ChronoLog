# Factory Cartridge Specs Table Schema

This document describes the structure of the `factory_cartridge_specs` table in the Supabase database.

## Table: `factory_cartridge_specs`

The factory_cartridge_specs table stores specifications for factory-manufactured ammunition cartridges.

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| **id** | integer | NO | nextval('factory_cartridge_specs_id_seq'::regclass) | Primary key (auto-increment) |
| **user_id** | text | NO | null | Foreign key to users table |
| **make** | text | NO | null | Cartridge manufacturer name |
| **model** | text | NO | null | Cartridge model/product name |
| **bullet_id** | integer | NO | null | Foreign key to bullets table |
| **cartridge_type** | text | YES | null | Cartridge type designation (e.g., "6.5 Creedmoor", ".308 Winchester") |

### Required Fields

- `id` - Primary key (auto-generated)
- `user_id` - User ownership/isolation
- `make` - Cartridge manufacturer (e.g., "Federal", "Hornady", "Winchester")
- `model` - Specific product model (e.g., "Gold Medal Match", "Precision Hunter")
- `bullet_id` - Reference to the bullet used in this cartridge

### Optional Fields

- `cartridge_type` - Standardized cartridge designation

### Relationships

- **User Isolation**: Each factory cartridge spec is owned by a specific user via `user_id`
- **Bullet Reference**: Links to `bullets.id` to specify which bullet is used
- **Referenced By**:
  - `factory_cartridge_lots.factory_spec_id`
  - Used in `cartridge_details` view

### Constraints

Based on the original schema file, this table likely has:
- Primary key constraint on `id`
- Foreign key constraint on `user_id` referencing `users.id`
- Foreign key constraint on `bullet_id` referencing `bullets.id`
- Unique constraint on `(user_id, make, model)` to prevent duplicate entries

### Design Notes

- **Factory Focus**: This table is specifically for factory-manufactured ammunition
- **Minimal Data**: Contains only basic identification and bullet reference
- **Bullet Separation**: Bullet specifications are stored in separate `bullets` table for reusability
- **User Isolation**: Each user maintains their own catalog of factory cartridges

### Example Usage

```sql
-- Insert a new factory cartridge specification
INSERT INTO factory_cartridge_specs (
    user_id, make, model, bullet_id, cartridge_type
) VALUES (
    'user123', 'Federal', 'Gold Medal Match', 42, '6.5 Creedmoor'
);

-- Query factory cartridges with bullet details
SELECT fcs.*, b.manufacturer as bullet_manufacturer, b.model as bullet_model, b.weight_grains
FROM factory_cartridge_specs fcs
JOIN bullets b ON b.id = fcs.bullet_id
WHERE fcs.user_id = 'user123'
ORDER BY fcs.make, fcs.model;

-- Find all cartridges using a specific bullet
SELECT fcs.make, fcs.model, fcs.cartridge_type
FROM factory_cartridge_specs fcs
WHERE fcs.bullet_id = 42 AND fcs.user_id = 'user123';
```

### Integration with Views

This table is used in the `cartridge_details` view to provide a unified interface for viewing both factory and custom cartridges:

```sql
-- Part of cartridge_details view for factory cartridges
SELECT f.id AS spec_id,
    'factory'::text AS source,
    f.cartridge_type,
    f.make AS manufacturer,
    f.model,
    f.bullet_id,
    -- ... bullet details joined from bullets table
FROM factory_cartridge_specs f
LEFT JOIN bullets b ON b.id = f.bullet_id;
```

### Typical Workflow

1. User adds bullets to their `bullets` table
2. User creates factory cartridge specs linking to those bullets
3. User can optionally track specific lots in `factory_cartridge_lots`
4. All data is unified in the `cartridge_details` view for display