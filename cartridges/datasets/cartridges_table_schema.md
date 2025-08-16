# Cartridges Table Schema

This document describes the structure of the `cartridges` table in the Supabase database.

## Table: `cartridges`

The cartridges table stores user's cartridge inventory, linking to either factory or custom cartridge specifications with batch tracking.

### Columns

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| **id** | integer | NO | nextval('cartridges_id_seq'::regclass) | Primary key (auto-increment) |
| **user_id** | text | NO | null | Foreign key to users table |
| **source** | text | NO | null | Source type: 'factory' or 'custom' |
| **batch_number** | text | NO | null | User-defined batch identifier |
| **factory_spec_id** | integer | YES | null | Foreign key to factory_cartridge_specs (when source = 'factory') |
| **custom_spec_id** | integer | YES | null | Foreign key to custom_cartridge_specs (when source = 'custom') |
| **created_at** | timestamp | NO | now() | Record creation timestamp |
| **notes** | text | YES | null | User notes about this batch |

### Required Fields

- `id` - Primary key (auto-generated)
- `user_id` - User ownership/isolation
- `source` - Must be either 'factory' or 'custom'
- `batch_number` - User-defined batch identifier (unique per user)

### Optional Fields

- `factory_spec_id` - Required when source = 'factory', NULL when source = 'custom'
- `custom_spec_id` - Required when source = 'custom', NULL when source = 'factory'
- `created_at` - Automatically set to current timestamp
- `notes` - Free-form notes about the batch

### Relationships

- **User Isolation**: Each cartridge record is owned by a specific user via `user_id`
- **Factory Specs**: Links to `factory_cartridge_specs.id` when source = 'factory'
- **Custom Specs**: Links to `custom_cartridge_specs.id` when source = 'custom'

### Constraints

The table should have these constraints:
- Primary key constraint on `id`
- Foreign key constraint on `user_id` referencing `users.id`
- Foreign key constraint on `factory_spec_id` referencing `factory_cartridge_specs.id`
- Foreign key constraint on `custom_spec_id` referencing `custom_cartridge_specs.id`
- Check constraint: `source IN ('factory', 'custom')`
- Check constraint: `(source = 'factory' AND factory_spec_id IS NOT NULL AND custom_spec_id IS NULL) OR (source = 'custom' AND custom_spec_id IS NOT NULL AND factory_spec_id IS NULL)`
- Unique constraint on `(user_id, batch_number)` to ensure unique batch numbers per user

### Design Notes

- **Flexible Source**: Supports both factory and custom cartridges through conditional foreign keys
- **Batch Tracking**: User-defined batch numbers for inventory organization
- **User Isolation**: All records are user-specific
- **Audit Trail**: Created timestamp for tracking when batches were added
- **Data Integrity**: Check constraints ensure proper source/foreign key relationships

### SQL Definition

```sql
CREATE TABLE cartridges (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    source TEXT NOT NULL CHECK (source IN ('factory', 'custom')),
    batch_number TEXT NOT NULL,
    factory_spec_id INTEGER,
    custom_spec_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    
    -- Foreign key constraints
    CONSTRAINT cartridges_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT cartridges_factory_spec_id_fkey FOREIGN KEY (factory_spec_id) REFERENCES factory_cartridge_specs(id),
    CONSTRAINT cartridges_custom_spec_id_fkey FOREIGN KEY (custom_spec_id) REFERENCES custom_cartridge_specs(id),
    
    -- Unique batch numbers per user
    CONSTRAINT cartridges_user_batch_unique UNIQUE (user_id, batch_number),
    
    -- Ensure proper source/foreign key relationship
    CONSTRAINT cartridges_source_fkey_check CHECK (
        (source = 'factory' AND factory_spec_id IS NOT NULL AND custom_spec_id IS NULL) OR
        (source = 'custom' AND custom_spec_id IS NOT NULL AND factory_spec_id IS NULL)
    )
);

-- Indexes for performance
CREATE INDEX idx_cartridges_user_id ON cartridges(user_id);
CREATE INDEX idx_cartridges_source ON cartridges(source);
CREATE INDEX idx_cartridges_factory_spec_id ON cartridges(factory_spec_id);
CREATE INDEX idx_cartridges_custom_spec_id ON cartridges(custom_spec_id);
```

### Example Usage

```sql
-- Insert a factory cartridge batch
INSERT INTO cartridges (user_id, source, batch_number, factory_spec_id, notes)
VALUES ('user123', 'factory', 'BATCH-001', 42, 'Excellent accuracy batch');

-- Insert a custom cartridge batch
INSERT INTO cartridges (user_id, source, batch_number, custom_spec_id, notes)
VALUES ('user123', 'custom', 'LOAD-V2-001', 15, 'Load development iteration 2');

-- Query all cartridges for a user
SELECT c.*, 
       CASE 
         WHEN c.source = 'factory' THEN fcs.make || ' ' || fcs.model
         WHEN c.source = 'custom' THEN ccs.name
       END as cartridge_name
FROM cartridges c
LEFT JOIN factory_cartridge_specs fcs ON c.factory_spec_id = fcs.id
LEFT JOIN custom_cartridge_specs ccs ON c.custom_spec_id = ccs.id
WHERE c.user_id = 'user123'
ORDER BY c.created_at DESC;

-- Find factory cartridges by manufacturer
SELECT c.*, fcs.make, fcs.model
FROM cartridges c
JOIN factory_cartridge_specs fcs ON c.factory_spec_id = fcs.id
WHERE c.user_id = 'user123' AND c.source = 'factory' AND fcs.make = 'Federal'
ORDER BY c.batch_number;
```

### Workflow Integration

This table supports the cartridge creation workflow:

1. **Source Selection**: User selects 'factory' or 'custom'
2. **Specification Selection**: User selects from appropriate spec table
3. **Batch Assignment**: User enters unique batch number
4. **Record Creation**: New cartridge record created with proper foreign keys
5. **Inventory Tracking**: Batch numbers allow organizing ammunition inventory

### Use Cases

- **Inventory Management**: Track different batches of ammunition
- **Performance Correlation**: Link shooting performance to specific batches
- **Purchase Tracking**: Record when ammunition was acquired
- **Load Development**: Track iterations of custom loads
- **Batch Testing**: Compare performance between different batches
- **Ammunition Allocation**: Organize ammo for different purposes (practice, competition, hunting)