# cartridge_types Table Schema

## CREATE TABLE Statement

```sql
CREATE TABLE public.cartridge_types (
  name text PRIMARY KEY NOT NULL,
  bore_diameter_land_mm double precision,
  -- SAAMI Basic Identification
  saami_name text,
  saami_category text CHECK (saami_category IN ('CENTERFIRE RIFLE', 'CENTERFIRE P&R', 'SHOTSHELL', 'RIMFIRE')),
  
  -- SAAMI Dimensional Specifications (Imperial)
  saami_case_length_in double precision,
  saami_cartridge_overall_length_in double precision,
  saami_bore_diameter_in double precision,
  saami_groove_diameter_in double precision,
  saami_bullet_diameter_in double precision,
  saami_case_head_diameter_in double precision,
  saami_neck_diameter_in double precision,
  saami_shoulder_diameter_in double precision,
  saami_rim_diameter_in double precision,
  saami_rim_thickness_in double precision,
  
  -- SAAMI Dimensional Specifications (Metric)
  saami_case_length_mm double precision,
  saami_cartridge_overall_length_mm double precision,
  saami_bore_diameter_mm double precision,
  saami_groove_diameter_mm double precision,
  saami_bullet_diameter_mm double precision,
  saami_case_head_diameter_mm double precision,
  saami_neck_diameter_mm double precision,
  saami_shoulder_diameter_mm double precision,
  saami_rim_diameter_mm double precision,
  saami_rim_thickness_mm double precision,
  
  -- SAAMI Pressure Limits & Performance Data
  saami_max_avg_pressure_psi integer,
  saami_max_avg_pressure_cup integer,
  saami_max_avg_pressure_bar integer,
  saami_max_avg_pressure_mpa double precision,
  saami_test_barrel_length_in double precision,
  saami_test_barrel_length_mm double precision,
  saami_reference_velocity_fps integer,
  saami_reference_velocity_ms double precision,
  saami_reference_bullet_weight_gr integer,
  saami_reference_bullet_weight_g double precision,
  
  -- SAAMI Safety and Interchangeability Parameters
  saami_headspace_go_gauge_in double precision,
  saami_headspace_go_gauge_mm double precision,
  saami_headspace_no_go_gauge_in double precision,
  saami_headspace_no_go_gauge_mm double precision,
  saami_chamber_throat_diameter_in double precision,
  saami_chamber_throat_diameter_mm double precision,
  saami_chamber_throat_length_in double precision,
  saami_chamber_throat_length_mm double precision,
  saami_rifling_twist_rate text,
  saami_rifling_groove_count integer,
  
  -- SAAMI Metadata
  saami_standard_reference text,
  saami_approved_date date,
  saami_last_revised_date date,
  saami_source_url text
);
```

## Table Description

### Core Identification
| Column Name               | Data Type          | Nullable | Default | Description                                                                |
|---------------------------|--------------------|----------|---------|----------------------------------------------------------------------------|
| **name**                  | text               | NO       | -       | Primary key, cartridge type name (e.g., "6mm Creedmoor", "308 Winchester") |
| **bore_diameter_land_mm** | double precision   | YES      | -       | Bore diameter across the lands in millimeters                              |

### SAAMI Basic Identification
| Column Name        | Data Type | Nullable | Default | Description                                                             |
|--------------------|-----------|----------|---------|-------------------------------------------------------------------------|
| **saami_name**     | text      | YES      | -       | Official SAAMI cartridge name                                           |
| **saami_category** | text      | YES      | -       | SAAMI category: CENTERFIRE RIFLE, CENTERFIRE P&R, SHOTSHELL, or RIMFIRE |

### SAAMI Dimensional Specifications (Imperial Units)
| Column Name                           | Data Type        | Nullable | Default | Description |
|---------------------------------------|------------------|----------|---------|-------------|
| **saami_case_length_in**              | double precision | YES      | -       | Maximum case length in inches |
| **saami_cartridge_overall_length_in** | double precision | YES      | -       | Cartridge overall length (COAL) in inches |
| **saami_bore_diameter_in**            | double precision | YES      | -       | Bore diameter (across lands) in inches |
| **saami_groove_diameter_in**          | double precision | YES      | -       | Groove diameter in inches |
| **saami_bullet_diameter_in**          | double precision | YES      | -       | Bullet diameter in inches |
| **saami_case_head_diameter_in**       | double precision | YES      | -       | Case head diameter in inches |
| **saami_neck_diameter_in**            | double precision | YES      | -       | Case neck diameter in inches |
| **saami_shoulder_diameter_in**        | double precision | YES      | -       | Case shoulder diameter in inches |
| **saami_rim_diameter_in**             | double precision | YES      | -       | Case rim diameter in inches |
| **saami_rim_thickness_in**            | double precision | YES      | -       | Case rim thickness in inches |

### SAAMI Dimensional Specifications (Metric Units)
| Column Name                           | Data Type        | Nullable | Default | Description                                    |
|---------------------------------------|------------------|----------|---------|------------------------------------------------|
| **saami_case_length_mm**              | double precision | YES      | -       | Maximum case length in millimeters             |
| **saami_cartridge_overall_length_mm** | double precision | YES      | -       | Cartridge overall length (COAL) in millimeters |
| **saami_bore_diameter_mm**            | double precision | YES      | -       | Bore diameter (across lands) in millimeters    |
| **saami_groove_diameter_mm**          | double precision | YES      | -       | Groove diameter in millimeters                 |
| **saami_bullet_diameter_mm**          | double precision | YES      | -       | Bullet diameter in millimeters                 |
| **saami_case_head_diameter_mm**       | double precision | YES      | -       | Case head diameter in millimeters              |
| **saami_neck_diameter_mm**            | double precision | YES      | -       | Case neck diameter in millimeters              |
| **saami_shoulder_diameter_mm**        | double precision | YES      | -       | Case shoulder diameter in millimeters          |
| **saami_rim_diameter_mm**             | double precision | YES      | -       | Case rim diameter in millimeters               |
| **saami_rim_thickness_mm**            | double precision | YES      | -       | Case rim thickness in millimeters              |

### SAAMI Pressure Limits & Performance Data
| Column Name                          | Data Type        | Nullable | Default | Description                                          |
|--------------------------------------|------------------|----------|---------|------------------------------------------------------|
| **saami_max_avg_pressure_psi**       | integer          | YES      | -       | Maximum average pressure in PSI                      |
| **saami_max_avg_pressure_cup**       | integer          | YES      | -       | Maximum average pressure in Copper Units of Pressure |
| **saami_max_avg_pressure_bar**       | integer          | YES      | -       | Maximum average pressure in bar                      |
| **saami_max_avg_pressure_mpa**       | double precision | YES      | -       | Maximum average pressure in MPa                      |
| **saami_test_barrel_length_in**      | double precision | YES      | -       | Test barrel length in inches                         |
| **saami_test_barrel_length_mm**      | double precision | YES      | -       | Test barrel length in millimeters                    |
| **saami_reference_velocity_fps**     | integer          | YES      | -       | Reference velocity in feet per second                |
| **saami_reference_velocity_ms**      | double precision | YES      | -       | Reference velocity in meters per second              |
| **saami_reference_bullet_weight_gr** | integer          | YES      | -       | Reference bullet weight in grains                    |
| **saami_reference_bullet_weight_g**  | double precision | YES      | -       | Reference bullet weight in grams                     |

### SAAMI Safety and Interchangeability Parameters
| Column Name                          | Data Type        | Nullable | Default | Description                                    |
|--------------------------------------|------------------|----------|---------|------------------------------------------------|
| **saami_headspace_go_gauge_in**      | double precision | YES      | -       | Headspace GO gauge dimension in inches         |
| **saami_headspace_go_gauge_mm**      | double precision | YES      | -       | Headspace GO gauge dimension in millimeters    |
| **saami_headspace_no_go_gauge_in**   | double precision | YES      | -       | Headspace NO-GO gauge dimension in inches      |
| **saami_headspace_no_go_gauge_mm**   | double precision | YES      | -       | Headspace NO-GO gauge dimension in millimeters |
| **saami_chamber_throat_diameter_in** | double precision | YES      | -       | Chamber throat diameter in inches              |
| **saami_chamber_throat_diameter_mm** | double precision | YES      | -       | Chamber throat diameter in millimeters         |
| **saami_chamber_throat_length_in**   | double precision | YES      | -       | Chamber throat length in inches                |
| **saami_chamber_throat_length_mm**   | double precision | YES      | -       | Chamber throat length in millimeters           |
| **saami_rifling_twist_rate**         | text             | YES      | -       | Rifling twist rate (e.g., "1:8", "1:10")       |
| **saami_rifling_groove_count**       | integer          | YES      | -       | Number of rifling grooves                      |

### SAAMI Metadata
| Column Name                  | Data Type  | Nullable | Default | Description                                                        |
|------------------------------|------------|----------|---------|--------------------------------------------------------------------|
| **saami_standard_reference** | text       | YES      | -       | SAAMI standard reference (e.g., "SAAMI Z299.4-2025")               |
| **saami_approved_date**      | date       | YES      | -       | Date cartridge was approved by SAAMI                               |
| **saami_last_revised_date**  | date       | YES      | -       | Date SAAMI specifications were last revised                        |
| **saami_source_url**         | text       | YES      | -       | Semicolon-separated list of source URLs used to collect SAAMI data |

## Purpose and Context

The `cartridge_types` table serves as a comprehensive repository for standardized cartridge type names and their complete SAAMI (Sporting Arms and Ammunition Manufacturers' Institute) technical specifications. This table ensures data consistency across the application and provides detailed ballistic and dimensional data for cartridges.

## Key Features

1. **SAAMI Compliance**: Contains complete SAAMI specifications for dimensional data, pressure limits, and safety parameters
2. **Dual Unit System**: Provides both imperial and metric measurements for international compatibility
3. **Source Traceability**: Documents all sources used to collect SAAMI data for verification and updates
4. **Comprehensive Coverage**: Supports all SAAMI cartridge categories (centerfire rifle, centerfire pistol & revolver, shotshell, rimfire)
5. **Data Integrity**: Enforces referential integrity through foreign key relationships and check constraints

## SAAMI Categories

- **CENTERFIRE RIFLE**: High-powered rifle cartridges (e.g., 6.5mm Creedmoor, 308 Winchester)
- **CENTERFIRE P&R**: Pistol and revolver cartridges (e.g., 9mm Luger, .45 ACP)
- **SHOTSHELL**: Shotgun cartridges (e.g., 12 gauge, 20 gauge)
- **RIMFIRE**: Rimfire cartridges (e.g., .22 LR, 17 HMR)

## Referenced By

This table is referenced by:
- `cartridges.cartridge_type` - Foreign key relationship with ON DELETE RESTRICT
- Various ballistic calculation and cartridge selection components throughout the application

## Maintenance

SAAMI specifications are maintained using:
- Manual updates from official SAAMI publications
- Automated maintenance script at `/cartridges/datasets/maintainence/update_saami_specs.py`
- Source URL tracking for verification and updates