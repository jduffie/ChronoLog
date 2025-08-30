# cartridges Table Schema

## CREATE TABLE Statement

```sql
create table public.cartridges (
  id uuid not null default gen_random_uuid (),
  owner_id text null,
  make text not null,
  model text not null,
  bullet_id uuid not null,
  cartridge_type text not null,
  data_source_name text null,
  data_source_link text null,
  cartridge_key text GENERATED ALWAYS as (
    (
      (
        (
          (
            ((lower(make) || '|'::text) || lower(model)) || '|'::text
          ) || lower(cartridge_type)
        ) || '|'::text
      ) || (bullet_id)::text
    )
  ) STORED null,
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  constraint cartridges_pkey primary key (id),
  constraint cartridges_bullet_id_fkey foreign KEY (bullet_id) references bullets (id) on delete RESTRICT,
  constraint fk_cartridge_type foreign KEY (cartridge_type) references cartridge_types (name) on delete RESTRICT,
  constraint chk_data_source_link_url check (
    (
      (data_source_link is null)
      or (data_source_link ~* '^[a-z][a-z0-9+.-]*://'::text)
    )
  )
) TABLESPACE pg_default;

create unique INDEX IF not exists uq_cartridges_global_key on public.cartridges using btree (cartridge_key) TABLESPACE pg_default
where
  (owner_id is null);

create unique INDEX IF not exists uq_cartridges_user_key on public.cartridges using btree (cartridge_key, owner_id) TABLESPACE pg_default
where
  (owner_id is not null);

create index IF not exists idx_cartridges_owner on public.cartridges using btree (owner_id) TABLESPACE pg_default;

create index IF not exists idx_cartridges_bullet on public.cartridges using btree (bullet_id) TABLESPACE pg_default;

create trigger trg_cartridges_touch BEFORE
update on cartridges for EACH row
execute FUNCTION touch_updated_at ();
```

## Recommended Indexes

```sql
-- "One global per key"
CREATE UNIQUE INDEX uq_cartridges_global_key
  ON public.cartridges (cartridge_key)
  WHERE owner_id IS NULL;

-- "One user row per key"
CREATE UNIQUE INDEX uq_cartridges_user_key
  ON public.cartridges (cartridge_key, owner_id)
  WHERE owner_id IS NOT NULL;

-- Helpful lookup indexes
CREATE INDEX idx_cartridges_owner ON public.cartridges(owner_id);
CREATE INDEX idx_cartridges_bullet ON public.cartridges(bullet_id);
```

## Triggers

```sql
-- Touch trigger for updated_at
CREATE OR REPLACE FUNCTION public.touch_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END $$;

CREATE TRIGGER trg_cartridges_touch
BEFORE UPDATE ON public.cartridges
FOR EACH ROW EXECUTE PROCEDURE public.touch_updated_at();
```

## Table Description

| Column Name          | Data Type                | Nullable | Default           | Description                                                                              |
|----------------------|--------------------------|----------|-------------------|------------------------------------------------------------------------------------------|
| **id**               | uuid                     | NO       | gen_random_uuid() | Primary key, auto-generated unique identifier                                            |
| **owner_id**         | text                     | YES      | -                 | Auth0 user identifier; NULL for global/admin rows, NOT NULL for user-owned rows          |
| **make**             | text                     | NO       | -                 | Cartridge manufacturer name                                                              |
| **model**            | text                     | NO       | -                 | Cartridge model name                                                                     |
| **bullet_id**        | uuid                     | NO       | -                 | Foreign key to bullets table                                                             |
| **cartridge_type**   | text                     | NO       | -                 | Foreign key to cartridge_types lookup table                                              |
| **data_source_name** | text                     | YES      | -                 | Name or description of the data source                                                   |
| **data_source_link** | text                     | YES      | -                 | URL reference to the original data source (validated by constraint)                      |
| **cartridge_key**    | text                     | NO       | generated         | Generated natural key combining make, model, cartridge_type, and bullet_id               |
| **created_at**       | timestamp with time zone | NO       | now()             | Record creation timestamp                                                                |
| **updated_at**       | timestamp with time zone | NO       | now()             | Last modification timestamp (auto-updated by trigger)                                    |

## Foreign Key Relationships

The table has the following foreign key relationships:

- **bullets(id)** - Links to bullet specifications with ON DELETE RESTRICT
- **cartridge_types(name)** - Links to cartridge type lookup table with ON DELETE RESTRICT

## Constraints

1. **chk_data_source_link_url**: Validates that data_source_link follows basic URL format (scheme://host...)

## Purpose and Context

The `cartridges` table stores cartridge specifications that combine manufacturer information, bullet data, and cartridge type classifications. This table supports both:

- **Global/Admin Records**: When `owner_id` IS NULL, these are system-wide cartridge specs visible to all users
- **User-Owned Records**: When `owner_id` IS NOT NULL, these are user-specific cartridge configurations

## Key Features

1. **Dual Ownership Model**: Supports both global admin-managed and user-specific cartridge records
2. **Generated Natural Key**: The `cartridge_key` provides a unique identifier based on the cartridge's characteristics
3. **Unique Constraints**: Ensures one global record per cartridge combination and one user record per combination
4. **Data Source Tracking**: Maintains provenance information for cartridge specifications
5. **Automatic Timestamps**: Creation and update timestamps are automatically managed
6. **URL Validation**: Data source links are validated for proper URL format

## Usage Patterns

- Global records (owner_id = NULL) represent standard factory cartridges managed by administrators
- User records (owner_id = user_id) represent custom user configurations or overrides
- The cartridge_key enables efficient duplicate detection and data consistency
- Foreign key relationships ensure data integrity with bullets and cartridge types