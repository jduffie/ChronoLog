# DOPE Database Table to Model Comparison Analysis

This document analyzes the alignment between the DOPE database tables and their corresponding Python models, identifying any fields that exist in the models but not in the database tables, or vice versa.

## Analysis Date
Generated: 2025-09-22

## Table 1: `dope_sessions` vs `DopeSessionModel`

### Database Table Fields (`dope_sessions`)
The following fields exist in the `dope_sessions` table:

| Field Name | Data Type | Notes |
|------------|-----------|--------|
| `id` | uuid | Primary key |
| `session_name` | text | Required |
| `created_at` | timestamptz | Auto-generated |
| `updated_at` | timestamptz | Auto-generated |
| `chrono_session_id` | uuid | Foreign key, nullable, unique |
| `range_submission_id` | uuid | Foreign key, nullable |
| `weather_source_id` | uuid | Foreign key, nullable |
| `range_name` | text | Nullable |
| `range_distance_m` | real | Nullable |
| `notes` | text | Nullable |
| `rifle_id` | uuid | Foreign key, required |
| `cartridge_lot_number` | text | Nullable |
| `user_id` | text | Required |
| `cartridge_id` | uuid | Foreign key, required |
| `start_time` | timestamptz | Required |
| `end_time` | timestamptz | Required |
| `bullet_id` | uuid | Foreign key, required |
| `temperature_c_median` | real | Nullable |
| `relative_humidity_pct_median` | real | Nullable |
| `wind_speed_mps_median` | real | Nullable |
| `wind_direction_deg_median` | real | Nullable |
| `lat` | real | Nullable |
| `lon` | real | Nullable |
| `start_altitude` | real | Nullable |
| `azimuth_deg` | real | Nullable |
| `elevation_angle_deg` | real | Nullable |
| `location_hyperlink` | text | Nullable |
| `barometric_pressure_hpa_median` | real | Nullable |
| `wind_speed_2_mps_median` | real | Nullable |

### Model Fields (`DopeSessionModel`)
The following fields exist in the `DopeSessionModel` class:

| Field Name | Type | Notes |
|------------|------|--------|
| `id` | Optional[str] | Model field |
| `user_id` | Optional[str] | Model field |
| `session_name` | str | Model field |
| `datetime_local` | Optional[datetime] | **NOT IN DATABASE** |
| `cartridge_id` | Optional[str] | Model field |
| `bullet_id` | Optional[str] | Model field |
| `chrono_session_id` | Optional[str] | Model field |
| `range_submission_id` | Optional[str] | Model field |
| `weather_source_id` | Optional[str] | Model field |
| `rifle_id` | Optional[str] | Model field |
| `start_time` | datetime | Model field |
| `end_time` | datetime | Model field |
| `range_name` | Optional[str] | Model field |
| `range_distance_m` | Optional[float] | Model field |
| `notes` | Optional[str] | Model field |
| `lat` | Optional[float] | Model field |
| `lon` | Optional[float] | Model field |
| `start_altitude` | Optional[float] | Model field |
| `azimuth_deg` | Optional[float] | Model field |
| `elevation_angle_deg` | Optional[float] | Model field |
| `location_hyperlink` | Optional[str] | Model field |
| `rifle_name` | str | **NOT IN DATABASE** - Joined from `rifles` table |
| `rifle_barrel_length_cm` | Optional[float] | **NOT IN DATABASE** - Joined from `rifles` table |
| `rifle_barrel_twist_in_per_rev` | Optional[float] | **NOT IN DATABASE** - Joined from `rifles` table |
| `cartridge_make` | str | **NOT IN DATABASE** - Joined from `cartridges` table |
| `cartridge_model` | str | **NOT IN DATABASE** - Joined from `cartridges` table |
| `cartridge_type` | str | **NOT IN DATABASE** - Joined from `cartridges` table |
| `cartridge_lot_number` | Optional[str] | Model field |
| `bullet_make` | str | **NOT IN DATABASE** - Joined from `bullets` table |
| `bullet_model` | str | **NOT IN DATABASE** - Joined from `bullets` table |
| `bullet_weight` | str | **NOT IN DATABASE** - Joined from `bullets` table |
| `bullet_length_mm` | Optional[str] | **NOT IN DATABASE** - Joined from `bullets` table |
| `ballistic_coefficient_g1` | Optional[str] | **NOT IN DATABASE** - Joined from `bullets` table |
| `ballistic_coefficient_g7` | Optional[str] | **NOT IN DATABASE** - Joined from `bullets` table |
| `sectional_density` | Optional[str] | **NOT IN DATABASE** - Joined from `bullets` table |
| `bullet_diameter_groove_mm` | Optional[str] | **NOT IN DATABASE** - Joined from `bullets` table |
| `bore_diameter_land_mm` | Optional[str] | **NOT IN DATABASE** - Joined from `bullets` table |
| `temperature_c_median` | Optional[float] | Model field |
| `relative_humidity_pct_median` | Optional[float] | Model field |
| `barometric_pressure_hpa_median` | Optional[float] | Model field |
| `wind_speed_mps_median` | Optional[float] | Model field |
| `wind_speed_2_mps_median` | Optional[float] | Model field |
| `wind_direction_deg_median` | Optional[float] | Model field |
| `weather_source_name` | Optional[str] | **NOT IN DATABASE** - Joined from `weather_source` table |
| `chrono_session_name` | Optional[str] | **NOT IN DATABASE** - Joined from `chrono_sessions` table |

### ⚠️ Fields in Model but NOT in Database Table:
1. **`datetime_local`** - Model has this field but it doesn't exist in `dope_sessions` table
2. **Rifle-related fields** (populated via JOIN with `rifles` table):
   - `rifle_name`
   - `rifle_barrel_length_cm`
   - `rifle_barrel_twist_in_per_rev`
3. **Cartridge-related fields** (populated via JOIN with `cartridges` table):
   - `cartridge_make`
   - `cartridge_model`
   - `cartridge_type`
4. **Bullet-related fields** (populated via JOIN with `bullets` table):
   - `bullet_make`
   - `bullet_model`
   - `bullet_weight`
   - `bullet_length_mm`
   - `ballistic_coefficient_g1`
   - `ballistic_coefficient_g7`
   - `sectional_density`
   - `bullet_diameter_groove_mm`
   - `bore_diameter_land_mm`
5. **Weather-related fields** (populated via JOIN with `weather_source` table):
   - `weather_source_name`
6. **Chronograph-related fields** (populated via JOIN with `chrono_sessions` table):
   - `chrono_session_name`

### ✅ Fields in Database but NOT in Model:
1. **`created_at`** - Database has this timestamp field but model doesn't include it
2. **`updated_at`** - Database has this timestamp field but model doesn't include it

---

## Table 2: `dope_measurements` vs `DopeMeasurementModel`

### Database Table Fields (`dope_measurements`)
The following fields exist in the `dope_measurements` table:

| Field Name | Data Type | Notes |
|------------|-----------|--------|
| `id` | uuid | Primary key |
| `dope_session_id` | uuid | Foreign key, required |
| `shot_number` | integer | Nullable |
| `datetime_shot` | timestamptz | Nullable |
| `azimuth_deg` | real | Nullable |
| `elevation_angle_deg` | real | Nullable |
| `humidity_pct` | real | Nullable |
| `clean_bore` | text | Nullable |
| `cold_bore` | text | Nullable |
| `shot_notes` | text | Nullable |
| `elevation_adjustment` | text | Nullable |
| `windage_adjustment` | text | Nullable |
| `created_at` | timestamptz | Auto-generated |
| `updated_at` | timestamptz | Auto-generated |
| `user_id` | text | Required |
| `speed_mps` | real | Nullable |
| `ke_j` | real | Nullable |
| `power_factor_kgms` | real | Nullable |
| `temperature_c` | real | Nullable |
| `pressure_hpa` | real | Nullable |
| `distance_m` | real | Nullable |

### Model Fields (`DopeMeasurementModel`)
The following fields exist in the `DopeMeasurementModel` class:

| Field Name | Type | Notes |
|------------|------|--------|
| `id` | Optional[str] | Model field |
| `dope_session_id` | str | Model field |
| `user_id` | str | Model field |
| `shot_number` | Optional[int] | Model field |
| `datetime_shot` | Optional[datetime] | Model field |
| `speed_mps` | Optional[float] | Model field |
| `ke_j` | Optional[float] | Model field |
| `power_factor_kgms` | Optional[float] | Model field |
| `azimuth_deg` | Optional[float] | Model field |
| `elevation_angle_deg` | Optional[float] | Model field |
| `temperature_c` | Optional[float] | Model field |
| `pressure_hpa` | Optional[float] | Model field |
| `humidity_pct` | Optional[float] | Model field |
| `clean_bore` | Optional[str] | Model field |
| `cold_bore` | Optional[str] | Model field |
| `distance_m` | Optional[float] | Model field |
| `elevation_adjustment` | Optional[float] | Model field |
| `windage_adjustment` | Optional[float] | Model field |
| `shot_notes` | Optional[str] | Model field |
| `created_at` | Optional[datetime] | Model field |
| `updated_at` | Optional[datetime] | Model field |

### ⚠️ Fields in Model but NOT in Database Table:
**NONE** - All model fields have corresponding database fields.

### ✅ Fields in Database but NOT in Model:
**NONE** - All database fields have corresponding model fields.

### ⚠️ Data Type Mismatches:
1. **`elevation_adjustment`**: Database stores as `text`, Model expects `Optional[float]`
2. **`windage_adjustment`**: Database stores as `text`, Model expects `Optional[float]`

---

## Summary and Recommendations

### ✅ What's Working Well:
1. **`dope_measurements` table and model are well-aligned** - All fields match between table and model
2. **Foreign key relationships are properly defined** in both tables
3. **Metric unit standardization** is consistently applied
4. **User isolation** via `user_id` is implemented in both tables

### ⚠️ Issues Identified:

#### For `dope_sessions`:
1. **Missing `datetime_local` field** in database table but present in model
2. **Missing timestamp fields** (`created_at`, `updated_at`) in model but present in database
3. **Joined fields dependency** - Model includes many fields that come from JOINs with other tables

#### For `dope_measurements`:
1. **Data type mismatches** for adjustment fields (text vs float)

### 📋 Recommended Actions:

#### High Priority:
1. **Add missing timestamp fields to DopeSessionModel**:
   ```python
   created_at: Optional[datetime] = None
   updated_at: Optional[datetime] = None
   ```

2. **Resolve adjustment field type mismatch** in `dope_measurements`:
   - Either change database columns to `real` type
   - Or update model to use `Optional[str]` type
   - Current implementation may cause conversion errors

#### Medium Priority:
3. **Remove or clarify `datetime_local` field** in DopeSessionModel since it doesn't exist in database

4. **Document JOIN dependencies** clearly in model docstrings to indicate which fields require database JOINs

#### Low Priority:
5. **Consider adding database constraints** for data validation where appropriate
6. **Review field naming consistency** between snake_case (database) and model conventions

### 💡 Architecture Notes:
- The extensive use of JOINs in DopeSessionModel suggests a denormalized read model approach
- Consider whether all joined fields are necessary or if some could be loaded on-demand
- The model serves as an aggregate entity combining data from multiple normalized tables

### 🔧 Data Integrity Considerations:
- Ensure all foreign key relationships remain valid
- Consider adding database-level checks for the adjustment field types
- Validate that metric unit conversions are handled consistently across the application