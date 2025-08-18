# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```



### Testing Supabase Configuration

The application requires a Supabase service role key. Set it as an environment variable:
```bash
export SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

source venv/bin/activate
python verify_supabase.py
```

If using 1Password CLI (as documented in README):
```bash
# op account add --address https://my.1password.com --email johnduffie91@gmail.com

eval $(op signin)
export SUPABASE_SERVICE_ROLE_KEY=$(op item get "Supabase - ChronoLog" --vault "Private" --field "service_role secret")

source venv/bin/activate
python verify_supabase.py
```
### Running the Application
```bash
# Run the main Streamlit app
streamlit run ChronoLog.py
```

### Testing Commands

**IMPORTANT**: All tests must pass before committing code. Run both unit and integration tests:

```bash
# Run all unit tests
source venv/bin/activate
python run_all_tests.py

# Run integration tests
python run_integration_tests.py

# Both test suites must pass before any commit
```

### Commit Requirements

Before committing any code changes:
1. **Run all tests** - Both unit and integration tests must pass
2. **Verify functionality** - Test the specific features you modified
3. **Check for breaking changes** - Ensure existing functionality still works
4. **Only commit if all tests pass** - Never commit code with failing tests

## Architecture Overview

### Core Components
- **app.py**: Main Streamlit application with Auth0 Google authentication and file upload functionality
- **verify_supabase.py**: Utility script to test Supabase database and storage connectivity
- **.streamlit/secrets.toml**: Configuration file containing Auth0 and Supabase credentials

### Authentication Flow
- Uses Auth0 for Google OAuth authentication
- Redirects to authorize endpoint, processes auth code, retrieves user info
- User session maintained in Streamlit session state

### Data Flow
1. User uploads Garmin Xero Chronograph Excel files through Streamlit interface
2. Files are stored in Supabase Storage under user's email directory
3. Excel data is parsed and structured into:
   - **sessions** table: metadata (bullet type, grain, timestamps, file paths)
   - **measurements** table: individual shot data (speed, energy, power factor, etc.)

### Database Schema
The application uses a comprehensive Supabase database with the following tables and views:

#### Core Tables
- **users**: User profiles and authentication data
- **chrono_sessions**: Chronograph session metadata
- **chrono_measurements**: Individual shot measurements from chronograph
- **dope_sessions**: DOPE (Data On Previous Engagement) session data
- **dope_measurements**: Individual DOPE measurements with ballistic adjustments
- **weather_source**: Weather measurement device configurations
- **weather_measurements**: Environmental conditions data
- **rifles**: User rifle configurations and specifications
- **bullets**: Bullet specifications and ballistic data
- **ranges**: Approved public shooting ranges (admin-managed)
- **ranges_submissions**: User-submitted range data pending approval

#### Cartridge System Tables
- **factory_cartridge_specs**: Factory cartridge specifications (admin-managed)
- **factory_cartridge_lots**: Factory cartridge lot tracking
- **custom_cartridge_specs**: User-defined custom cartridge loads
- **custom_cartridge_lots**: Custom cartridge lot tracking
- **cartridges**: User cartridge inventory linking factory/custom specs

#### Legacy Tables
- **measurements**: Legacy measurements table (replaced by chrono_measurements)

#### Views
- **cartridge_details**: Unified view combining factory/custom cartridge specs with bullet data

#### Detailed Table Schemas

**users**
- id (text, PK): Auth0 user identifier
- email (text, NOT NULL): User email address
- name (text, NOT NULL): User display name
- username (text, NOT NULL): Unique username (3-30 chars, alphanumeric)
- state (text, NOT NULL): User's state/province
- country (text, NOT NULL): User's country
- unit_system (text, NOT NULL): 'Imperial' or 'Metric'
- profile_complete (boolean): Profile completion status
- picture (text): Profile image URL
- roles (text[], DEFAULT ['user']): User roles (user, admin)
- created_at (timestamptz): Account creation timestamp
- updated_at (timestamptz): Last profile update

**chrono_sessions**
- id (uuid, PK): Session identifier
- user_id (text, NOT NULL): Auth0 user identifier
- tab_name (text, NOT NULL): UI tab identifier
- bullet_type (text, NOT NULL): Bullet type/model
- bullet_grain (numeric): Bullet weight in grains
- datetime_local (timestamptz, NOT NULL): Session timestamp
- uploaded_at (timestamptz): File upload timestamp
- file_path (text): Original file path
- shot_count (integer): Number of shots in session
- avg_speed_fps (numeric): Average velocity
- std_dev_fps (numeric): Standard deviation
- min_speed_fps (numeric): Minimum velocity
- max_speed_fps (numeric): Maximum velocity
- created_at (timestamptz): Record creation

**chrono_measurements**
- id (uuid, PK): Measurement identifier
- user_id (text, NOT NULL): Auth0 user identifier
- chrono_session_id (uuid, FK): Parent session
- shot_number (integer, NOT NULL): Shot sequence number
- speed_fps (numeric, NOT NULL): Velocity in feet per second
- delta_avg_fps (numeric): Deviation from average
- ke_ft_lb (numeric): Kinetic energy in foot-pounds
- power_factor (numeric): Power factor calculation
- datetime_local (timestamptz): Shot timestamp
- clean_bore (boolean): Clean bore indicator
- cold_bore (boolean): Cold bore indicator
- shot_notes (text): Shot-specific notes

**dope_sessions**
- id (uuid, PK): DOPE session identifier
- user_id (text, NOT NULL): Auth0 user identifier
- session_name (text): Descriptive session name
- chrono_session_id (uuid, FK): Linked chronograph session
- range_submission_id (uuid, FK): Associated range
- weather_source_id (uuid, FK): Weather data source
- rifle_id (uuid, FK): Rifle configuration
- cartridge_type (text): 'factory' or 'custom'
- cartridge_spec_id (uuid): Reference to cartridge spec
- cartridge_lot_number (text): Lot identifier
- range_name (text): Range name
- distance_m (real): Target distance in meters
- notes (text): Session notes
- status (text): Session status
- created_at (timestamptz): Session creation
- updated_at (timestamptz): Last modification

**dope_measurements**
- id (uuid, PK): DOPE measurement identifier
- dope_session_id (uuid, FK, NOT NULL): Parent session
- user_id (text, NOT NULL): Auth0 user identifier
- shot_number (integer): Shot sequence
- datetime_shot (timestamptz): Shot timestamp
- speed_fps (real): Chronograph velocity
- ke_ft_lb (real): Kinetic energy
- power_factor (real): Power factor
- azimuth_deg (real): Azimuth angle
- elevation_angle_deg (real): Elevation angle
- temperature_f (real): Temperature in Fahrenheit
- pressure_inhg (real): Barometric pressure
- humidity_pct (real): Relative humidity percentage
- clean_bore (text): Clean bore status
- cold_bore (text): Cold bore status
- shot_notes (text): Shot annotations
- distance (text): User-specified distance
- elevation_adjustment (text): Elevation correction
- windage_adjustment (text): Windage correction
- created_at (timestamptz): Record creation
- updated_at (timestamptz): Last update

**weather_source**
- id (uuid, PK): Weather source identifier
- user_id (text, NOT NULL): Auth0 user identifier
- name (text, NOT NULL): Device name
- source_type (text, DEFAULT 'meter'): Source type
- make (text): Manufacturer
- device_name (text): Device model name
- model (text): Model number
- serial_number (text): Serial number
- created_at (timestamptz): Registration date
- updated_at (timestamptz): Last update

**weather_measurements**
- id (uuid, PK): Weather measurement identifier
- user_id (text, NOT NULL): Auth0 user identifier
- weather_source_id (uuid, FK): Source device
- measurement_timestamp (timestamptz, NOT NULL): Measurement time
- uploaded_at (timestamptz): Upload timestamp
- file_path (text): Source file path
- temperature_f (real): Temperature (°F)
- wet_bulb_temp_f (real): Wet bulb temperature
- relative_humidity_pct (real): Humidity percentage
- barometric_pressure_inhg (real): Pressure (inHg)
- altitude_ft (real): Altitude (feet)
- station_pressure_inhg (real): Station pressure
- wind_speed_mph (real): Wind speed
- heat_index_f (real): Heat index
- dew_point_f (real): Dew point
- density_altitude_ft (real): Density altitude
- crosswind_mph (real): Crosswind component
- headwind_mph (real): Headwind component
- compass_magnetic_deg (real): Magnetic bearing
- compass_true_deg (real): True bearing
- wind_chill_f (real): Wind chill
- data_type (text): Data record type
- record_name (text): Record identifier
- start_time (text): Session start
- duration (text): Session duration
- location_description (text): Location description
- location_address (text): Address
- location_coordinates (text): GPS coordinates
- notes (text): Additional notes

**rifles**
- id (uuid, PK): Rifle identifier
- user_id (text, NOT NULL): Auth0 user identifier
- name (text, NOT NULL): Rifle name/model
- barrel_twist_ratio (text): Twist rate (e.g., "1:8")
- barrel_length (text): Barrel length
- sight_offset (text): Sight height offset
- trigger (text): Trigger specifications
- scope (text): Scope details
- created_at (timestamptz): Registration date
- updated_at (timestamptz): Last modification

**bullets**
- id (uuid, PK): Bullet identifier
- user_id (text, NOT NULL): Bullet owner
- manufacturer (text, NOT NULL): Bullet manufacturer
- model (text, NOT NULL): Bullet model
- weight_grains (integer, NOT NULL): Weight in grains
- bullet_diameter_groove_mm (double precision, NOT NULL): Groove diameter
- bore_diameter_land_mm (double precision, NOT NULL): Land diameter
- bullet_length_mm (double precision): Length in millimeters
- ballistic_coefficient_g1 (double precision): G1 BC
- ballistic_coefficient_g7 (double precision): G7 BC
- sectional_density (double precision): Sectional density
- min_req_twist_rate_in_per_rev (double precision): Minimum twist rate
- pref_twist_rate_in_per_rev (double precision): Preferred twist rate
- data_source_name (text): Name or description of the data source
- data_source_url (text): URL or reference to the original data source

**factory_cartridge_specs**
- id (uuid, PK): Factory cartridge spec identifier
- user_id (text, NOT NULL): Spec creator (admin)
- make (text, NOT NULL): Cartridge manufacturer
- model (text, NOT NULL): Cartridge model
- bullet_id (uuid, FK, NOT NULL): Associated bullet
- cartridge_type (text): Cartridge type designation

**custom_cartridge_specs**
- id (uuid, PK): Custom cartridge spec identifier
- user_id (text, NOT NULL): Spec owner
- name (text, NOT NULL): Load name
- cartridge (text, NOT NULL): Cartridge case type
- bullet_id (uuid, FK, NOT NULL): Bullet selection
- powder (text): Powder type
- powder_charge_gr (numeric): Powder charge in grains
- casing_make (text): Case manufacturer
- casing_notes (text): Case preparation notes
- primer (text): Primer type
- coal_mm (double precision): Cartridge overall length
- velocity_fps (integer): Expected velocity
- pressure_notes (text): Pressure observations
- notes (text): Load development notes
- cartridge_type (text): Type designation

**ranges**
- id (uuid, PK): Range identifier
- user_id (text, NOT NULL): Auth0 user identifier
- range_name (text, NOT NULL): Range name
- range_description (text): Range description
- start_lat (numeric, NOT NULL): Firing position latitude
- start_lon (numeric, NOT NULL): Firing position longitude
- start_altitude_m (numeric): Firing position altitude
- end_lat (numeric, NOT NULL): Target latitude
- end_lon (numeric, NOT NULL): Target longitude
- end_altitude_m (numeric): Target altitude
- distance_m (numeric): Range distance
- azimuth_deg (numeric): Bearing angle
- elevation_angle_deg (numeric): Elevation angle
- address_geojson (jsonb): Geocoded address data
- display_name (text): Display name
- submitted_at (timestamptz): Submission timestamp
- created_at (timestamptz): Record creation

**ranges_submissions**
- id (uuid, PK): Range submission identifier
- user_id (text, NOT NULL): Auth0 user identifier
- range_name (text, NOT NULL): Proposed range name
- range_description (text): Range description
- start_lat (numeric, NOT NULL): Firing position latitude
- start_lon (numeric, NOT NULL): Firing position longitude
- start_altitude_m (numeric): Firing position altitude
- end_lat (numeric, NOT NULL): Target latitude
- end_lon (numeric, NOT NULL): Target longitude
- end_altitude_m (numeric): Target altitude
- distance_m (numeric): Range distance
- azimuth_deg (numeric): Bearing angle
- elevation_angle_deg (numeric): Elevation angle
- address_geojson (jsonb): Geocoded address data
- display_name (text): Display name
- status (text, DEFAULT 'Under Review'): Review status
- review_reason (text): Admin review notes
- submitted_at (timestamptz): Submission time
- created_at (timestamptz): Record creation

**cartridge_details** (VIEW)
- spec_id (uuid): Cartridge specification ID
- source (text): 'factory' or 'custom'
- cartridge_type (text): Cartridge type designation
- manufacturer (text): Cartridge manufacturer
- model (text): Cartridge model
- bullet_id (uuid): Associated bullet ID
- bullet_name (text): Computed bullet name
- bullet_manufacturer (text): Bullet manufacturer
- bullet_model (text): Bullet model
- bullet_weight_grains (integer): Bullet weight
- bullet_diameter_groove_mm (double precision): Groove diameter
- bore_diameter_land_mm (double precision): Land diameter
- bullet_length_mm (double precision): Bullet length
- ballistic_coefficient_g1 (double precision): G1 BC
- ballistic_coefficient_g7 (double precision): G7 BC
- sectional_density (double precision): Sectional density
- min_req_twist_rate_in_per_rev (double precision): Minimum twist rate
- pref_twist_rate_in_per_rev (double precision): Preferred twist rate

### External Dependencies
- **Streamlit**: Web framework for the application interface
- **Supabase**: Backend-as-a-Service for database and file storage
- **Auth0**: Authentication service for Google OAuth
- **pandas/openpyxl**: Excel file processing
- **requests**: HTTP client for Auth0 API calls

### File Processing
- Parses Garmin Xero Excel files with bullet metadata in first row
- Extracts bullet type and grain weight from comma-separated values
- Processes measurement data starting from row 2
- Handles optional fields like Clean Bore, Cold Bore, and Shot Notes

## Key Development Patterns

### Service Layer Pattern
All database operations go through service classes:
```python
from feature.service import FeatureService
service = FeatureService(supabase_client)
results = service.get_data_for_user(user_email)
```

### Model Classes
Use dataclasses for data entities with Supabase integration:
```python
@dataclass
class FeatureModel:
    @classmethod
    def from_supabase_record(cls, record: dict):
        # Convert Supabase record to model instance
```

### User Isolation
All database queries must filter by `user_email` for data isolation:
```python
.eq("user_email", user_email)
```

### Testing Patterns
- Mock Supabase client in tests
- Use `unittest.mock` for external dependencies
- Follow naming convention: `test_*.py`
- Include both unit and integration tests

### Import Structure
Add root directory to path for module imports:
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### Database Schema Maintenance
**IMPORTANT**: Whenever table schemas are modified (adding columns, changing types, creating new tables, etc.), the Database Schema section in this CLAUDE.md file MUST be updated to reflect the changes. This ensures documentation stays current and accurate for development work.
- to memorize


# Next Steps

- Update bullets table.  
  - Today, it uses an id that is monotonically increasing.  
  - Instead, I want it to use a UUID.  Be sure to address the foreign key references and to migrate existing data
- Create a bullets_types table.  It will have one column:
  - bore_diameter_land_mm - a float value
- Create a cartridge_types table.  The columns are:
  - cartridge_type - text string
  - bore_diameter_land_mm - a float value
- Update factory_cartridge_specs table. Today, the 'cartridge_type' column is a text string and all values are null. I want it to be an enumeration.  
  - The possible values are derived from the cartridge_type column in the cartridge_types table. 
- Update the View and Create tab on the factory cartridges page to include cartridge_type
    - need to ensure the create and filtering logic respect the 1 to 1 relationship between cartridge_type and bore_diameter_land_mm
- to memorize