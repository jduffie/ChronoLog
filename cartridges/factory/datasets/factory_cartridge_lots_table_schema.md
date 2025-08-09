# Factory Cartridge Lots Table Schema

This document describes the structure of the `factory_cartridge_lots` table in the Supabase database.

## Table: `factory_cartridge_lots`

The factory_cartridge_lots table stores specific manufacturing lot information for factory cartridge specifications, enabling tracking of individual batches of ammunition.

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| **id** | integer | NO | nextval('factory_cartridge_lots_id_seq'::regclass) | Primary key (auto-increment) |
| **user_id** | text | NO | null | Foreign key to users table |
| **factory_spec_id** | integer | NO | null | Foreign key to factory_cartridge_specs table |
| **lot_number** | text | NO | null | Manufacturing lot number |
| **mfg_date** | date | YES | null | Manufacturing date |
| **notes** | text | YES | null | User notes about this specific lot |

### Required Fields

- `id` - Primary key (auto-generated)
- `user_id` - User ownership/isolation
- `factory_spec_id` - Reference to the factory cartridge specification
- `lot_number` - Manufacturing lot number or batch identifier

### Optional Fields

- `mfg_date` - Date the lot was manufactured
- `notes` - Free-form notes about lot performance, storage, etc.

### Relationships

- **User Isolation**: Each factory cartridge lot is owned by a specific user via `user_id`
- **Specification Reference**: Links to `factory_cartridge_specs.id` to specify which cartridge spec this lot represents
- **Used In**: Referenced by `cartridge_details` view for lot tracking

### Constraints

Based on the table structure, this table likely has:
- Primary key constraint on `id`
- Foreign key constraint on `user_id` referencing `users.id`
- Foreign key constraint on `factory_spec_id` referencing `factory_cartridge_specs.id`
- Possibly unique constraint on `(user_id, factory_spec_id, lot_number)` to prevent duplicate lot entries

### Design Notes

- **Lot Tracking**: Enables tracking of specific manufacturing batches
- **Performance Monitoring**: Users can track how different lots perform
- **Inventory Management**: Helps manage ammunition inventory by lot
- **Quality Control**: Notes field allows tracking of lot-specific observations
- **Optional Details**: Manufacturing date is optional for cases where it's unknown

### Example Usage

```sql
-- Insert a new factory cartridge lot
INSERT INTO factory_cartridge_lots (
    user_id, factory_spec_id, lot_number, mfg_date, notes
) VALUES (
    'user123', 42, 'FC21334A', '2021-11-15', 'Excellent accuracy, consistent velocity'
);

-- Query lots for a specific factory cartridge
SELECT fcl.*, fcs.make, fcs.model
FROM factory_cartridge_lots fcl
JOIN factory_cartridge_specs fcs ON fcs.id = fcl.factory_spec_id
WHERE fcl.user_id = 'user123' AND fcl.factory_spec_id = 42
ORDER BY fcl.mfg_date DESC;

-- Find all lots with performance notes
SELECT fcl.lot_number, fcs.make, fcs.model, fcl.notes
FROM factory_cartridge_lots fcl
JOIN factory_cartridge_specs fcs ON fcs.id = fcl.factory_spec_id
WHERE fcl.user_id = 'user123' AND fcl.notes IS NOT NULL;

-- Track lots by manufacturing date
SELECT fcl.lot_number, fcl.mfg_date, fcs.make, fcs.model
FROM factory_cartridge_lots fcl
JOIN factory_cartridge_specs fcs ON fcs.id = fcl.factory_spec_id
WHERE fcl.user_id = 'user123' AND fcl.mfg_date >= '2021-01-01'
ORDER BY fcl.mfg_date;
```

### Integration with Views

This table is used in the `cartridge_details` view to provide lot information alongside cartridge specifications:

```sql
-- Part of cartridge_details view showing lot integration
SELECT f.id AS spec_id,
    'factory'::text AS source,
    f.cartridge_type,
    f.make AS manufacturer,
    f.model,
    f.bullet_id,
    -- ... bullet details ...
    fl.id AS lot_id,
    fl.lot_number,
    fl.mfg_date,
    fl.notes AS lot_notes
FROM factory_cartridge_specs f
LEFT JOIN bullets b ON b.id = f.bullet_id
LEFT JOIN factory_cartridge_lots fl ON fl.factory_spec_id = f.id AND fl.user_id = f.user_id;
```

### Typical Workflow

1. User creates a factory cartridge specification in `factory_cartridge_specs`
2. User purchases ammunition and records lot information in `factory_cartridge_lots`
3. User can track performance of specific lots through the `notes` field
4. Historical lot data helps with future ammunition purchases
5. Lot information appears in the unified `cartridge_details` view

### Use Cases

- **Performance Tracking**: Record which lots shoot better in specific rifles
- **Inventory Management**: Track remaining rounds from each lot
- **Quality Assurance**: Note lots with consistency issues
- **Purchase History**: Maintain record of when ammunition was acquired
- **Chronograph Data**: Link velocity/accuracy data to specific lots