# Rifles Table Schema

## Table: rifles

### Columns

| Column Name | Data Type | Nullable | Default | Notes |
|-------------|-----------|----------|---------|-------|
| id | uuid | NO | gen_random_uuid() | Primary key |
| user_id | text | NO | null | Auth0 user identifier |
| name | text | NO | null | Rifle name/model |
| barrel_twist_ratio | text | YES | null | Twist rate (e.g., "1:8") |
| barrel_length | text | YES | null | Barrel length |
| sight_offset | text | YES | null | Sight height offset |
| trigger | text | YES | null | Trigger specifications |
| scope | text | YES | null | Scope details |
| created_at | timestamp with time zone | YES | now() | Registration date |
| updated_at | timestamp with time zone | YES | now() | Last modification |

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