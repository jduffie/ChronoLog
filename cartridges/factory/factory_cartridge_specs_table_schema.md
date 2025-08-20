# Factory Cartridge Specs Table Schema

## Table: factory_cartridge_specs

### Columns

| Column Name      | Data Type  | Nullable | Default           | Notes                                        |
|------------------|------------|----------|-------------------|----------------------------------------------|
| id               | uuid       | NO       | gen_random_uuid() | Primary key                                  |
| user_id          | text       | NO       | null              | Auth0 user identifier                        |
| make             | text       | NO       | null              | Cartridge manufacturer                       |
| model            | text       | NO       | null              | Cartridge model                              |
| bullet_id        | uuid       | NO       | null              | Foreign key to bullets table                 |
| cartridge_type   | text       | YES      | null              | Cartridge type designation                   |
| data_source_name | text       | YES      | null              | Name or description of the data source       |
| data_source_link | text       | YES      | null              | URL or reference to the original data source |

### Primary Key
- `id` (uuid)

### Foreign Key References
- `bullet_id` references `bullets(id)`

This table is referenced by:
- `cartridge_details` view (via spec_id)

### Indexes
- Primary key index on `id`
- Foreign key index on `bullet_id`
- User data isolation: All queries should filter by `user_id`

### Notes
- Uses UUID as primary key with automatic generation
- All user data must be isolated by `user_id`
- Make, model, and bullet_id are required fields
- Cartridge type is currently nullable but may become an enumeration
- Data source fields track origin of cartridge specifications
- Links to bullets table for complete ballistic information