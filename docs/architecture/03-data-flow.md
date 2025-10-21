# Data Flow Patterns

## Overview

This document describes how data moves through the ChronoLog system, from initial import through source modules to DOPE aggregation and analysis.

## Core Data Flow Principles

1. **Source modules are entry points**: Data enters via chronograph, weather, or user-entered catalogs (rifles)
2. **Admin catalogs are pre-populated**: Bullets and cartridges are maintained by admin
3. **DOPE is the convergence point**: Rich analysis happens via typed JOINs (see [Design Decisions](06-design-decisions.md))
4. **User isolation at every step**: User-owned data respects user_id filtering
5. **Metric system internally**: Conversions happen only at import/export boundaries

## Typical User Workflows

### Workflow 1: Import Chronograph Data → Create DOPE Session

This is the most common workflow in ChronoLog.

**Step 1: Import Chronograph Session**
```
User uploads Garmin Excel file
    ↓
Chronograph module processes file
    ↓
Device adapter converts to metric (if needed)
    ↓
ChronographSession created (with metadata)
    ↓
ChronographMeasurement records created (shot-by-shot data)
    ↓
File stored in Supabase Storage
    ↓
Session and measurements saved to database (filtered by user_id)
```

**Step 2: Create DOPE Session from Chronograph Data**
```
User selects existing ChronographSession (from their own sessions)
    ↓
User specifies:
  - Cartridge (from admin-maintained global catalog)
    └─> Automatically brings in Bullet data via FK
  - Rifle (from user's rifle catalog)
  - Range and distance
  - Optional: Weather measurements (auto-associated by timestamp or manual)
    ↓
DOPE service validates:
  - ChronographSession belongs to user
  - Rifle belongs to user
  - Cartridge exists (globally available)
  - Weather (if specified) belongs to user
    ↓
DopeSession created with FKs to all sources
    ↓
Chronograph measurements linked to DOPE session
    ↓
DOPE session statistics calculated
```

**Result**: Rich ballistic profile combining velocity, rifle, cartridge, bullet specs, environmental conditions, and location.

---

### Workflow 2: Build User Catalog → Configure Equipment → Create DOPE

Users build their personal equipment catalog before shooting sessions.

**Step 1: Browse Admin Catalogs** (Read-Only)
```
User views available cartridges (admin-maintained)
    ↓
CartridgesAPI returns typed CartridgeModel instances
    ↓
Each cartridge includes nested BulletModel (via FK join)
    ↓
User notes which cartridges match their loads
```

**Step 2: Register Rifles** (User-Owned)
```
User creates rifle profile via UI
    ↓
RiflesAPI validates and creates Rifle model
    ↓
Rifle saved with barrel specs, optics, cartridge type
    ↓
Saved with user_id (private to user)
```

**Step 3: Import Weather** (User-Owned, Optional)
```
User uploads Kestrel or other weather data
    ↓
Weather module processes file (device adapter)
    ↓
WeatherSource and WeatherMeasurement records created
    ↓
Saved with user_id (private to user)
```

**Step 4: Use in DOPE Session**
```
DOPE UI queries:
  - RiflesAPI.get_rifles_for_user(user_id) → List[Rifle]
  - CartridgesAPI.get_all_cartridges() → List[CartridgeModel]
  - WeatherAPI.get_measurements_for_user(user_id) → List[WeatherMeasurement]
    ↓
User selects from dropdowns
    ↓
DOPE service creates session with typed references
```

---

### Workflow 3: DOPE Analytics and Queries

Once DOPE sessions exist, users analyze patterns.

**Query Flow (using typed composite models)**:
```
User requests DOPE sessions (with filters)
    ↓
DopeAPI.get_sessions_for_user(user_id)
    ↓
DopeService queries database with JOINs:
  - dope_sessions ⟕ cartridges (global, no user_id filter)
  - cartridges ⟕ bullets (global, no user_id filter)
  - dope_sessions ⟕ rifles (user_id filtered)
  - dope_sessions ⟕ chronograph_sessions (user_id filtered)
  - dope_sessions ⟕ weather_measurements (user_id filtered via source)
  - dope_sessions ⟕ ranges
    ↓
DopeService constructs typed DopeSessionModel instances:
  - Uses BulletModel.from_supabase_record() for bullet portion
  - Uses CartridgeModel for cartridge portion
  - Uses Rifle.from_supabase_record() for rifle portion
  - Uses ChronographSession.from_supabase_record() for chronograph portion
  - Uses WeatherMeasurement.from_supabase_record() for weather portion
    ↓
Returns List[DopeSessionModel] with full type safety
    ↓
UI can access: session.bullet.weight_grains, session.rifle.barrel_length_inches, etc.
```

**Analytics Flow**:
```
User requests statistics (e.g., "group by cartridge")
    ↓
DOPE analytics module aggregates across user's sessions
    ↓
Uses typed fields: session.cartridge.display_name, session.bullet.bc_g1
    ↓
Calculations performed (SD trends, velocity consistency, etc.)
    ↓
Results formatted for display
```

---

## Module-to-Module Communication Patterns

### Pattern 1: Independent Module (No Cross-Module Data)

**Example: Rifles Module**

```
User requests rifles
    ↓
RiflesAPI.get_rifles_for_user(user_id)
    ↓
RiflesService queries rifles table (user_id filtered)
    ↓
Returns List[Rifle] (no joins, fully independent)
```

**No coupling**: Rifles doesn't need data from other modules.

---

### Pattern 2: Independent Module with Batch Loading (Hypothetical)

**If chronograph needed to display cartridge info** (not current, but shows pattern):

```
User views chronograph sessions
    ↓
ChronographAPI.get_sessions_for_user(user_id)
    ↓
Returns List[ChronographSession] (no joins yet)
    ↓
UI layer (or presentation service) wants cartridge names
    ↓
Collect cartridge IDs: [s.cartridge_id for s in sessions if s.cartridge_id]
    ↓
CartridgesAPI.get_cartridges_by_ids(cartridge_ids)  # Batch operation
    ↓
UI manually combines: session + cartridge
```

**Light coupling**: Uses API (type-safe), not JOINs. Keeps modules independent.

---

### Pattern 3: DOPE Convergence (Typed JOINs)

**DOPE sessions with full context**:

```
User views DOPE sessions
    ↓
DopeAPI.get_sessions_for_user(user_id)
    ↓
DopeService performs complex JOIN (1 query)
    ↓
DopeService imports and uses:
  - BulletModel (from bullets.models)
  - CartridgeModel (from cartridges.models)
  - Rifle (from rifles.models)
  - ChronographSession (from chronograph.models)
  - WeatherMeasurement (from weather.models)
    ↓
Constructs DopeSessionModel with nested typed models
    ↓
Returns fully typed composite: List[DopeSessionModel]
```

**Explicit coupling**: DOPE imports from all modules, but coupling is one-way and typed.

See [Design Decisions](06-design-decisions.md) for detailed rationale.

---

## Database-Level Data Flow

### Foreign Key Relationships

```
bullets (admin-owned, global)
  ↑
  │ (FK: bullet_id)
  │
cartridges (admin-owned, global)
  ↑
  │ (FK: cartridge_id)
  │
dope_sessions (user-owned) ──[FK: chronograph_session_id]──> chronograph_sessions (user-owned)
  │                                                                   ↓
  ├──[FK: rifle_id]──> rifles (user-owned)              chronograph_measurements (user-owned)
  │
  ├──[FK: weather_measurement_id]──> weather_measurements (user-owned)
  │                                           ↑
  ├──[FK: range_id]──> ranges                │ (FK: source_id)
  │                                    weather_sources (user-owned)
  └──[1:N relationship]──> dope_measurements (user-owned)
```

### DOPE JOIN Pattern (Conceptual SQL)

```sql
-- DOPE performs this JOIN for performance
-- But uses typed models to parse results
SELECT
  ds.*,
  c.id as cartridge_id, c.make as cartridge_make, c.model as cartridge_model,
  b.id as bullet_id, b.manufacturer as bullet_manufacturer, b.weight_grains,
  r.id as rifle_id, r.name as rifle_name, r.barrel_length_inches,
  cs.id as chrono_id, cs.session_name as chrono_session_name,
  wm.id as weather_id, wm.temp_c, wm.humidity_pct
FROM dope_sessions ds
LEFT JOIN cartridges c ON ds.cartridge_id = c.id
  -- No user_id filter (global catalog)
LEFT JOIN bullets b ON c.bullet_id = b.id
  -- No user_id filter (global catalog)
LEFT JOIN rifles r ON ds.rifle_id = r.id
  AND r.user_id = :user_id -- User isolation
LEFT JOIN chronograph_sessions cs ON ds.chronograph_session_id = cs.id
  AND cs.user_id = :user_id -- User isolation
LEFT JOIN weather_measurements wm ON ds.weather_measurement_id = wm.id
  -- User isolation via weather_sources.user_id
WHERE ds.user_id = :user_id -- Primary user isolation
```

DOPE service then parses this result using:
- `BulletModel.from_supabase_record(bullet_fields)`
- `CartridgeModel(...)` with nested bullet
- `Rifle.from_supabase_record(rifle_fields)`
- `ChronographSession.from_supabase_record(chrono_fields)`
- `WeatherMeasurement.from_supabase_record(weather_fields)`

Result: Fully typed `DopeSessionModel` with type-safe access to all nested data.

---

## Unit Conversion Flow

### Import Path (Imperial → Metric)

```
User uploads file with imperial units
    ↓
Device adapter (Garmin, Kestrel, etc.) detects units
    ↓
Conversion applied BEFORE database storage:
  - fps → m/s
  - °F → °C
  - grains → grams (if needed)
  - inches → mm
    ↓
Metric data stored in database
    ↓
Model classes always work with metric
```

### Export/Display Path (Metric → Imperial, if user preference)

```
Database returns metric data
    ↓
Model instances created (metric internally)
    ↓
UI layer checks user preferences
    ↓
If user prefers imperial:
  Display formatters convert for presentation only
    ↓
Units shown in column headers: "Velocity (fps)", not in cell values
```

**Critical rule**: Models and services NEVER handle imperial units. Only:
- Device adapters (import): Imperial → Metric
- UI formatters (display): Metric → Imperial

---

## Access Control in Data Flow

### User-Owned Data Flow

**Example: Rifle Creation**
```
User creates rifle via UI
    ↓
RiflesAPI.create_rifle(rifle_data, user_id)
    ↓
RiflesService validates data
    ↓
Database INSERT with user_id column set
    ↓
Later queries: WHERE user_id = ?
    ↓
User can only access their own rifles
```

### Admin-Owned Data Flow

**Example: Cartridge Selection**
```
User creates DOPE session
    ↓
CartridgesAPI.get_all_cartridges()
    ↓
CartridgesService queries cartridges table (no user_id filter)
    ↓
Returns all cartridges (global catalog) with nested bullets
    ↓
UI displays dropdown
    ↓
User selects cartridge by ID
    ↓
DOPE session references cartridge_id (FK)
```

### Mixed Ownership in DOPE

```
DOPE Session (user-owned, user_id filtered)
├── Cartridge (admin-owned, global) ──> Bullet (admin-owned, global)
├── Rifle (user-owned, user_id filtered)
├── Chronograph Session (user-owned, user_id filtered)
├── Weather Measurement (user-owned, user_id filtered via source)
└── Range (varies: public/user-submitted)
```

DOPE service validates:
- User owns the DOPE session being created (`user_id` matches)
- User owns referenced user-owned resources (rifle, chronograph, weather)
- Admin resources (cartridges/bullets) exist and are valid
- All FK constraints are satisfied

---

## API Layer Data Flow (Future)

With the new API layer (Phase 3), the flow becomes:

```
UI/Client
    ↓
DopeAPI (facade, type-safe interface)
    ↓
DopeService (business logic, JOINs)
    ↓
Database (Supabase)
    ↓
DopeService constructs typed models
    ↓
DopeAPI returns typed models
    ↓
UI has full type safety
```

Benefits:
- Clear API contract (Protocol classes)
- Type checking at compile time
- Easy to mock for tests
- AI agents can understand interface

---

## Error Handling in Data Flow

### Validation Points

1. **Import validation**: Device adapters validate file format and data sanity
2. **API validation**: (Future) Protocol classes enforce type contracts at API boundary
3. **Service validation**: Services validate user_id ownership before operations
4. **Foreign key validation**: Database enforces referential integrity
5. **Model validation**: Model constructors validate data types

### User Isolation Enforcement

Different patterns for different ownership models:

**User-owned tables** (with user_id filtering):
```
chronograph_sessions: WHERE user_id = ?
rifles: WHERE user_id = ?
weather_sources: WHERE user_id = ?
weather_measurements: via weather_sources.user_id = ?
dope_sessions: WHERE user_id = ?
```

**Admin-owned tables** (no user filtering on reads):
```
bullets: No user_id column (global catalog)
cartridges: No user_id column (global catalog)
```

This ensures:
- User-owned data never leaks between users
- Admin data is appropriately shared with all users
- JOINs respect ownership boundaries

---

## Next Steps

To understand specific patterns:
- [User Isolation](04-user-isolation.md) - Security model details
- [Metric System](05-metric-system.md) - Unit handling philosophy
- [Design Decisions](06-design-decisions.md) - Typed composite models in detail
- [Common Patterns](../integration/common-patterns.md) - Implementation patterns
