# DOPE System: The Convergence Point

## Overview

DOPE (Data On Previous Engagement) is the central aggregation and analysis system in ChronoLog. It serves as the convergence point where all data source modules come together to create comprehensive ballistic profiles.

## Purpose

The DOPE system enables shooters to:

1. **Aggregate ballistic data** from multiple sources into unified sessions
2. **Track performance** across different rifles, cartridges, and environmental conditions
3. **Analyze patterns** to improve shooting accuracy and consistency
4. **Make informed decisions** about equipment and load development

## What is a DOPE Session?

A DOPE session represents a complete ballistic data point that combines:

- **Chronograph data**: Velocity measurements from shooting sessions
- **Cartridge information**: The specific cartridge and bullet combination used
- **Rifle details**: The firearm configuration (barrel length, twist rate, optics)
- **Weather conditions**: Environmental factors (temperature, humidity, pressure, wind)
- **Range information**: Location and distance
- **Shot data**: Individual measurements with statistical analysis

## Architecture Philosophy

DOPE follows a **convergent architecture** pattern:

```
Data Sources (Independent)          DOPE (Convergent)
├── Chronograph                  ┌─────────────────┐
├── Bullets                      │                 │
├── Cartridges         ────────> │  DOPE Session   │
├── Rifles                       │                 │
├── Weather                      └─────────────────┘
└── Ranges/Mapping
```

### Key Principles

1. **Data sources are independent**: Each source module (chronograph, bullets, etc.) operates independently and can be used standalone
2. **DOPE is dependent**: DOPE requires and integrates data from multiple sources
3. **Loose coupling**: Data sources know nothing about DOPE; DOPE knows about all sources
4. **Single source of truth**: Each data element is owned by one source module

## Data Flow

### Creating a DOPE Session

1. User selects a **chronograph session** (source of velocity data)
2. User specifies the **cartridge** (which includes bullet information via FK)
3. User specifies the **rifle** used
4. System optionally associates **weather data** if available for the timeframe
5. User specifies the **range** and shooting distance
6. System creates DOPE session with all joined data
7. Chronograph measurements are linked to the DOPE session

### Querying DOPE Data

When retrieving DOPE sessions, the system performs joins across:
- `dope_sessions` table (core session data)
- `cartridges` table (cartridge details)
- `bullets` table (bullet specifications via cartridge FK)
- `rifles` table (rifle configuration)
- `weather_measurements` table (environmental conditions)
- `ranges` table (location information)

This produces rich `DopeSessionModel` instances with complete context.

## Why DOPE is Central

DOPE represents the **integration layer** of ChronoLog:

- **It's the end goal**: All other modules exist to feed data into DOPE sessions
- **It enables analysis**: By combining disparate data, DOPE unlocks pattern recognition
- **It's user-facing**: Most user workflows culminate in creating or viewing DOPE sessions
- **It drives requirements**: DOPE's needs inform what data the source modules must provide

## DOPE vs. Chronograph

A common question: "Why separate DOPE from chronograph?"

**Chronograph sessions** are:
- Raw device output (direct from Garmin, etc.)
- Device-centric (one session = one device upload)
- Minimal context (just velocity measurements)
- Ephemeral (may be deleted after DOPE creation)

**DOPE sessions** are:
- Curated ballistic profiles
- Context-rich (rifle, cartridge, weather, location)
- Permanent record for analysis
- User-centric (organized by shooting scenarios)

## Module Responsibilities

### DOPE Module Owns:
- DOPE session metadata (date, notes, user associations)
- Relationships between sessions and source data
- Statistical aggregations across sessions
- Analytics and trend analysis
- Session filtering and search

### DOPE Module Does NOT Own:
- Bullet specifications (owned by bullets module)
- Rifle configurations (owned by rifles module)
- Weather measurements (owned by weather module)
- Chronograph raw data (owned by chronograph module)
- Range/location data (owned by mapping module)

## Integration Patterns

DOPE integrates with source modules through:

1. **Foreign key relationships**: DOPE sessions reference IDs from source tables
2. **Service layer calls**: DOPE service calls source module services for data
3. **Model composition**: `DopeSessionModel` composes models from other modules
4. **User isolation**: All joins respect `user_id` filtering for security

## Next Steps

To understand how DOPE integrates with each data source, see:
- [Data Sources Overview](02-data-sources.md)
- [Data Flow Patterns](03-data-flow.md)
- [DOPE Module Documentation](../modules/dope/README.md)
