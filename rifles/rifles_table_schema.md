# Rifles Table Schema

```sql
create table public.rifles (
id uuid not null default gen_random_uuid (),
name text not null,
barrel_twist_ratio text null,
barrel_length text null,
sight_offset text null,
trigger text null,
scope text null,
created_at timestamp with time zone null default now(),
updated_at timestamp with time zone null default now(),
user_id text not null,
cartridge_type public.cartridge_type not null,
constraint rifles_pkey primary key (id)
) TABLESPACE pg_default;

create index IF not exists idx_rifles_created_at on public.rifles using btree (created_at) TABLESPACE pg_default;

create index IF not exists idx_rifles_name on public.rifles using btree (name) TABLESPACE pg_default;

```

## Table: rifles

### Columns

| Column Name        | Data Type                  | Data Source | Nullable   | Default           | Notes                                   |
|--------------------|----------------------------|-------------|------------|-------------------|-----------------------------------------|
| id                 | uuid                       | foo         | NO         | gen_random_uuid() | Primary key                             |
| user_id            | text                       |             | NO         | null              | Auth0 user identifier                   |
| name               | text                       |             | NO         | null              | Rifle name/model                        |
| barrel_twist_ratio | text                       |             | YES        | null              | Twist rate (e.g., "1:8")                |
| barrel_length      | text                       |             | YES        | null              | Barrel length                           |
| sight_offset       | text                       |             | YES        | null              | Sight height offset                     |
| trigger            | text                       |             | YES        | null              | Trigger specifications                  |
| scope              | text                       |             | YES        | null              | Scope details                           |
| cartridge_type     | text                       |             | cartridges | null              | Type of cartridge from cartridge_types  |
| created_at         | timestamp with time zone   |             | YES        | now()             | Registration date                       |
| updated_at         | timestamp with time zone   |             | YES        | now()             | Last modification                       |



### Primary Key
- `id` (uuid)

### Foreign Key References
This table is referenced by:
- `dope_sessions.rifle_id`

### Indexes
- Primary key index on `id`
- User data isolation: All queries should filter by `user_id`

### Notes
- Uses UUID as primary key with automatic generation
- All user data must be isolated by `user_id`
- Name is the only required field besides user_id and id
- All specification fields are optional text fields
- Timestamps are automatically managed for creation and updates