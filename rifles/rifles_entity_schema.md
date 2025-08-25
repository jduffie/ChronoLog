# Rifles Entity Schema

## Entity: Rifle

### Properties

| Property Name      | Data Type                | Nullable | Default           | Notes                                              |
|--------------------|--------------------------|----------|-------------------|----------------------------------------------------|
| name               | text                     | NO       | null              | Rifle name/model                                   |
| cartridge_type     | cartridge_type (enum)    | NO       | null              | Primary cartridge type this rifle is chambered for |
| barrel_twist_ratio | text                     | YES      | null              | Twist rate (e.g., "1:8")                           |
| barrel_length      | text                     | YES      | null              | Barrel length                                      |
| sight_offset       | text                     | YES      | null              | Sight height offset                                |
| trigger            | text                     | YES      | null              | Trigger specifications                             |
| scope              | text                     | YES      | null              | Scope details                                      |



### Relationships
This entity is referenced by:
- `dope_sessions.rifle_id` - Links DOPE sessions to specific rifle configurations
