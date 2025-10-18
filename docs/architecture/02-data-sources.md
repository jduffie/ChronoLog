# Data Source Modules

## Overview

ChronoLog's architecture is built on six independent data source modules that feed into the DOPE system. Each module manages a specific domain of ballistic data and provides a clean API for access.

## The Six Data Sources

### 1. Chronograph Module

**Purpose**: Import and manage velocity measurements from chronograph devices

**What it provides**:
- Chronograph sessions (collections of shots from a single device upload)
- Individual shot measurements (velocity, energy, power factor)
- Device-specific import adapters (Garmin Xero, etc.)
- Statistical calculations (mean, SD, ES, high/low)

**Key entities**:
- `ChronographSession`: Session metadata, statistics, file references
- `ChronographMeasurement`: Individual shot data
- `ChronographSource`: Device information

**Data ownership**:
- Raw velocity data from devices
- Shot-by-shot measurements
- Upload file references (Supabase Storage)

**Used by DOPE**: DOPE sessions link to chronograph sessions to access velocity data

---

### 2. Bullets Module

**Purpose**: Manage bullet specifications and ballistic coefficients

**What it provides**:
- Bullet catalog (manufacturer, model, weight)
- Ballistic data (BC G1/G7, sectional density)
- Physical specifications (diameter, length)
- Twist rate recommendations

**Key entities**:
- `BulletModel`: Complete bullet specification

**Data ownership**:
- Bullet specifications (weight, diameter, BC)
- Manufacturer and model information
- Ballistic coefficients for trajectory calculations

**Access model**:
- Admin-maintained catalog (populated manually, not via UI)
- Read-only to all users
- Users never select bullets directly; bullets are accessed via cartridge FK

**Used by DOPE**: DOPE sessions reference cartridges, which include bullet data via FK join

**Special notes**:
- All internal data is metric (grains converted at import/display edges)

---

### 3. Cartridges Module

**Purpose**: Manage cartridge configurations (bullet + case combination)

**What it provides**:
- Cartridge catalog (make, model, type)
- Bullet associations (which bullet is loaded)
- SAAMI specifications and references
- Cartridge type taxonomy

**Key entities**:
- `CartridgeModel`: Cartridge with joined bullet data
- `CartridgeTypeModel`: Cartridge type lookup (e.g., "308 Winchester")

**Data ownership**:
- Cartridge make and model
- Bullet selection for each cartridge (FK to bullets)
- Cartridge type classifications

**Access model**:
- Admin-maintained catalog (populated manually, not via UI)
- Read-only to all users
- Users select from available cartridges when creating DOPE sessions

**Used by DOPE**: DOPE sessions specify which cartridge was used, bringing in both cartridge and bullet data via FK joins

**Special notes**:
- Foreign key to bullets module creates rich joined data
- Each cartridge is pre-configured with a specific bullet

---

### 4. Rifles Module

**Purpose**: Manage rifle configurations and specifications

**What it provides**:
- Rifle catalog (name, cartridge type compatibility)
- Barrel specifications (length, twist rate)
- Optics configuration (scope, sight offset)
- Trigger information

**Key entities**:
- `Rifle`: Complete rifle specification

**Data ownership**:
- Rifle identification and naming
- Barrel characteristics (critical for ballistics)
- Optics setup (for trajectory calculations)

**Used by DOPE**: DOPE sessions specify which rifle was used

**Special notes**:
- Barrel twist rate affects bullet stabilization
- Sight offset affects trajectory calculations
- All user-specific (no global rifles)

---

### 5. Weather Module

**Purpose**: Import and manage environmental conditions

**What it provides**:
- Weather measurements (temp, humidity, pressure, wind)
- Device/source tracking (Kestrel, etc.)
- Time-series weather data
- Device-specific import adapters

**Key entities**:
- `WeatherSource`: Weather meter/device information
- `WeatherMeasurement`: Individual environmental readings

**Data ownership**:
- Environmental measurements (all metric internally)
- Weather device information
- Upload file references

**Used by DOPE**: DOPE sessions optionally link to weather measurements based on timestamp proximity

**Special notes**:
- All measurements stored in metric (Celsius, hPa, m/s)
- Kestrel device adapter handles imperial-to-metric conversion
- Weather association to DOPE can be automatic (by timestamp) or manual

---

### 6. Mapping Module

**Purpose**: Manage shooting range locations and geographic data

**What it provides**:
- Range catalog (public and user-submitted)
- Geographic coordinates
- Range submission and approval workflows
- Distance and location data

**Key entities**:
- Range models (various, complex structure)

**Data ownership**:
- Range locations and names
- Geographic coordinates
- Range metadata (public/private, approval status)

**Used by DOPE**: DOPE sessions specify range and shooting distance

**Special notes**:
- **Currently undergoing future refactoring** - API patterns may change
- More complex than other modules (submission workflows, admin approval)
- For now, DOPE interacts with mapping's existing interface

---

## Module Independence

Each data source module is **independently usable**:

- **Bullets** can be managed without any other module
- **Chronograph** sessions can be imported and analyzed standalone
- **Weather** data can be collected and viewed independently
- **Rifles** and **Cartridges** can be cataloged separately

This independence ensures:
1. **Simpler testing**: Each module can be tested in isolation
2. **Flexible usage**: Users can use subsets of features
3. **Clearer boundaries**: Each module has a single responsibility
4. **Easier maintenance**: Changes in one module don't cascade to others

## Module Relationships

While modules are independent, they have **optional relationships**:

```
Cartridges ──[FK]──> Bullets
    │
    │ (referenced by)
    ↓
DOPE Sessions
    │
    ├──[FK]──> Chronograph Sessions
    ├──[FK]──> Rifles
    ├──[FK]──> Weather Measurements (optional)
    └──[FK]──> Ranges
```

**Key points**:
- Only **DOPE** has dependencies on other modules
- **Cartridges** depends on **Bullets** (FK relationship)
- All other source modules are fully independent
- Relationships are one-way: sources don't know about DOPE

## Common Patterns Across Modules

All data source modules follow consistent patterns:

1. **Service Layer**: `ModuleService` class for database operations
2. **Model Classes**: Dataclasses with `from_supabase_record()` methods
3. **User Isolation**: User-owned modules filter by `user_id`; admin-owned modules (bullets, cartridges) are globally readable
4. **Metric System**: Internal data in metric, conversion at edges
5. **Streamlit UI**: Separate UI components (`*_tab.py` files)

See [Common Patterns](../integration/common-patterns.md) for implementation details.

## Data Ownership Summary

**Admin-Owned (Global, Read-Only to Users)**:
- Bullets
- Cartridges

**User-Owned (Private, user_id Filtered)**:
- Chronograph sessions and measurements
- Rifles
- Weather sources and measurements
- Ranges (with some public/shared ranges)
- DOPE sessions and measurements

## Next Steps

To understand how these modules work together, see:
- [Data Flow Patterns](03-data-flow.md)
- [Common Implementation Patterns](../integration/common-patterns.md)

For module-specific details, see individual module documentation:
- [Chronograph Module](../modules/chronograph/README.md)
- [Bullets Module](../modules/bullets/README.md)
- [Cartridges Module](../modules/cartridges/README.md)
- [Rifles Module](../modules/rifles/README.md)
- [Weather Module](../modules/weather/README.md)
- [Mapping Module](../modules/mapping/README.md)