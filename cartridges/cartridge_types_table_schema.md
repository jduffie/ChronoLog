# cartridge_types Table Schema

## CREATE TABLE Statement

```sql
CREATE TABLE public.cartridge_types (
  name text PRIMARY KEY
);
```

## Table Description

| Column Name | Data Type | Nullable | Default | Description                                    |
|-------------|-----------|----------|---------|------------------------------------------------|
| **name**    | text      | NO       | -       | Primary key, cartridge type name (e.g., "6mm Creedmoor", "308 Winchester") |

## Purpose and Context

The `cartridge_types` table serves as a lookup table for standardized cartridge type names. This table ensures data consistency across the application by providing a controlled vocabulary for cartridge types.

## Key Features

1. **Simple Lookup**: Contains only cartridge type names as the primary key
2. **Data Integrity**: Enforces referential integrity through foreign key relationships
3. **Standardization**: Provides consistent naming for cartridge types across the system

## Referenced By

This table is referenced by:
- `cartridges.cartridge_type` - Foreign key relationship with ON DELETE RESTRICT