-- Reset all tables: delete data, drop tables, and recreate with latest schema
-- Run this in Supabase SQL Editor

-- Delete all data first (respecting foreign key constraints)
DELETE FROM dope_measurements;
DELETE FROM dope_sessions;
DELETE FROM measurements;
DELETE FROM sessions;
DELETE FROM weather_measurements;
DELETE FROM weather_source;
DELETE FROM chrono_measurements;
DELETE FROM chrono_sessions;
DELETE FROM ranges_submissions;
DELETE FROM ranges;

-- Drop all tables with CASCADE to handle any remaining dependencies
DROP TABLE IF EXISTS dope_measurements CASCADE;
DROP TABLE IF EXISTS dope_sessions CASCADE;
DROP TABLE IF EXISTS measurements CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS weather_measurements CASCADE;
DROP TABLE IF EXISTS weather_source CASCADE;
DROP TABLE IF EXISTS chrono_measurements CASCADE;
DROP TABLE IF EXISTS chrono_sessions CASCADE;
DROP TABLE IF EXISTS ranges_submissions CASCADE;
DROP TABLE IF EXISTS ranges CASCADE;

-- Create sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT NOT NULL,
    sheet_name TEXT NOT NULL,
    bullet_type TEXT NOT NULL,
    bullet_grain NUMERIC,
    session_timestamp TIMESTAMPTZ,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    file_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create measurements table with datetime_local
CREATE TABLE measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    shot_number INTEGER,
    speed_fps NUMERIC,
    delta_avg_fps NUMERIC,
    ke_ft_lb NUMERIC,
    power_factor NUMERIC,
    datetime_local TIMESTAMPTZ,
    clean_bore BOOLEAN,
    cold_bore BOOLEAN,
    shot_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create weather_source table for weather meter metadata
CREATE TABLE weather_source (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT NOT NULL,
    
    -- User-defined name for this weather meter
    name TEXT NOT NULL,
    
    -- Source type and make (user-selected)
    source_type TEXT NOT NULL DEFAULT 'meter',  -- 'meter' (future: 'api')
    make TEXT,           -- Manufacturer/brand (Kestrel)
    
    -- Optional device information (from CSV metadata)
    device_name TEXT,     -- Device name from CSV row 1
    model TEXT,          -- Device model from CSV row 2
    serial_number TEXT,  -- Serial number from CSV row 3
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicate weather sources per user
    UNIQUE(user_email, name)
);

-- Create weather_measurements table for Kestrel weather data
CREATE TABLE weather_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT NOT NULL,
    weather_source_id UUID REFERENCES weather_source(id) ON DELETE CASCADE,
    measurement_timestamp TIMESTAMPTZ NOT NULL,
    
    -- Import metadata
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    file_path TEXT,
    
    -- Weather measurement fields
    temperature_f REAL,
    wet_bulb_temp_f REAL,
    relative_humidity_pct REAL,
    barometric_pressure_inhg REAL,
    altitude_ft REAL,
    station_pressure_inhg REAL,
    wind_speed_mph REAL,
    heat_index_f REAL,
    dew_point_f REAL,
    density_altitude_ft REAL,
    crosswind_mph REAL,
    headwind_mph REAL,
    compass_magnetic_deg REAL,
    compass_true_deg REAL,
    wind_chill_f REAL,
    
    -- Additional fields
    data_type TEXT,
    record_name TEXT,
    start_time TEXT,
    duration TEXT,
    location_description TEXT,
    location_address TEXT,
    location_coordinates TEXT,
    notes TEXT,
    
    -- Unique constraint on source + timestamp to prevent duplicate measurements
    UNIQUE(user_email, weather_source_id, measurement_timestamp)
);

-- Create chrono_sessions table for session metadata from Excel tabs
CREATE TABLE chrono_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT NOT NULL,
    
    -- Session metadata from Excel file
    tab_name TEXT NOT NULL,  -- Sheet/tab name from Excel file
    bullet_type TEXT NOT NULL,  -- First part before comma in first row
    bullet_grain NUMERIC,  -- Grain weight from first row
    datetime_local TIMESTAMPTZ NOT NULL,  -- Full DATE value from Excel
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    file_path TEXT,
    
    -- Session summary statistics (can be computed from measurements)
    shot_count INTEGER DEFAULT 0,
    avg_speed_fps NUMERIC,
    std_dev_fps NUMERIC,
    min_speed_fps NUMERIC,
    max_speed_fps NUMERIC,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicate sessions
    UNIQUE(user_email, tab_name, datetime_local)
);

-- Create chrono_measurements table for Garmin Xero chronograph timeseries data
CREATE TABLE chrono_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT NOT NULL,
    
    -- Foreign key to chrono_sessions
    chrono_session_id UUID REFERENCES chrono_sessions(id) ON DELETE CASCADE,
    
    -- Timeseries measurement data from Excel rows
    shot_number INTEGER NOT NULL,  -- # column
    speed_fps NUMERIC NOT NULL,  -- Speed (FPS) column
    delta_avg_fps NUMERIC,  -- Δ AVG (FPS) column
    ke_ft_lb NUMERIC,  -- KE (FT-LB) column
    power_factor NUMERIC,  -- Power Factor column
    datetime_local TIMESTAMPTZ,  -- Computed: session_date + time_local
    
    -- Optional measurement flags
    clean_bore BOOLEAN,  -- Clean Bore column
    cold_bore BOOLEAN,  -- Cold Bore column
    shot_notes TEXT,  -- Shot Notes column
    
    -- Unique constraint to prevent duplicate measurements
    UNIQUE(user_email, chrono_session_id, shot_number, datetime_local)
);

-- Create ranges_submissions table for mapping data (pending approval)
CREATE TABLE ranges_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT NOT NULL,
    range_name TEXT NOT NULL,
    range_description TEXT,
    
    -- Geographic coordinates and measurements
    start_lat NUMERIC(10, 6) NOT NULL,
    start_lon NUMERIC(10, 6) NOT NULL,
    start_altitude_m NUMERIC(8, 2),
    end_lat NUMERIC(10, 6) NOT NULL,
    end_lon NUMERIC(10, 6) NOT NULL,
    end_altitude_m NUMERIC(8, 2),
    
    -- Calculated values
    distance_m NUMERIC(10, 2),
    azimuth_deg NUMERIC(6, 2),
    elevation_angle_deg NUMERIC(6, 2),
    
    -- Address information (stored as GeoJSON)
    address_geojson JSONB,
    display_name TEXT,
    
    -- Admin review fields
    status TEXT NOT NULL DEFAULT 'Under Review' CHECK (status IN ('Under Review', 'Accepted', 'Denied')),
    review_reason TEXT,
    
    -- Timestamps
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create ranges table for approved ranges (public)
CREATE TABLE ranges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT NOT NULL,
    range_name TEXT NOT NULL,
    range_description TEXT,
    
    -- Geographic coordinates and measurements
    start_lat NUMERIC(10, 6) NOT NULL,
    start_lon NUMERIC(10, 6) NOT NULL,
    start_altitude_m NUMERIC(8, 2),
    end_lat NUMERIC(10, 6) NOT NULL,
    end_lon NUMERIC(10, 6) NOT NULL,
    end_altitude_m NUMERIC(8, 2),
    
    -- Calculated values
    distance_m NUMERIC(10, 2),
    azimuth_deg NUMERIC(6, 2),
    elevation_angle_deg NUMERIC(6, 2),
    
    -- Address information (stored as GeoJSON)
    address_geojson JSONB,
    display_name TEXT,
    
    -- Timestamps
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create dope_sessions table for DOPE session metadata
CREATE TABLE dope_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT NOT NULL,
    
    -- Session metadata
    session_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Source data references
    chrono_session_id UUID REFERENCES chrono_sessions(id) ON DELETE SET NULL,
    range_submission_id UUID REFERENCES ranges_submissions(id) ON DELETE SET NULL,
    weather_source_id UUID REFERENCES weather_source(id) ON DELETE SET NULL,
    
    -- Session details from original sources
    bullet_type TEXT,
    bullet_grain INTEGER,
    range_name TEXT,
    distance_m REAL,
    
    -- User-editable session fields (for future use)
    caliber TEXT,
    manufacturer TEXT,
    model TEXT,
    grain INTEGER,
    rifle TEXT,
    
    -- Additional metadata
    notes TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    
    UNIQUE(user_email, session_name),
    UNIQUE(chrono_session_id)  -- Enforce 1-to-1 relationship with chronograph sessions
);

-- Create dope_measurements table for individual shot measurements and DOPE adjustments
CREATE TABLE dope_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dope_session_id UUID NOT NULL REFERENCES dope_sessions(id) ON DELETE CASCADE,
    user_email TEXT NOT NULL,
    
    -- Shot identification
    shot_number INTEGER,
    datetime_shot TIMESTAMPTZ,
    
    -- Source chronograph data (read-only)
    speed_fps REAL,
    ke_ft_lb REAL,
    power_factor REAL,
    
    -- Source range data (read-only)
    start_lat REAL,
    start_lon REAL,
    start_altitude_m REAL,
    azimuth_deg REAL,
    elevation_angle_deg REAL,
    
    -- Source weather data (read-only)
    temperature_f REAL,
    pressure_inhg REAL,
    humidity_pct REAL,
    
    -- User-editable DOPE data
    clean_bore TEXT,
    cold_bore TEXT,
    shot_notes TEXT,
    distance TEXT,  -- User-provided distance (may differ from range distance)
    elevation_adjustment TEXT,  -- Elevation adjustment in RADS or MOA
    windage_adjustment TEXT,  -- Windage adjustment in RADS or MOA
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(dope_session_id, shot_number)
);

-- Create indexes for better performance
CREATE INDEX idx_sessions_user_email ON sessions(user_email);
CREATE INDEX idx_sessions_uploaded_at ON sessions(uploaded_at);
CREATE INDEX idx_measurements_session_id ON measurements(session_id);
CREATE INDEX idx_measurements_shot_number ON measurements(shot_number);
CREATE INDEX idx_measurements_datetime_local ON measurements(datetime_local);
CREATE INDEX idx_weather_measurements_user_email ON weather_measurements(user_email);
CREATE INDEX idx_weather_measurements_source_timestamp ON weather_measurements(weather_source_id, measurement_timestamp);
CREATE INDEX idx_weather_measurements_timestamp ON weather_measurements(measurement_timestamp);
CREATE INDEX idx_weather_measurements_source_id ON weather_measurements(weather_source_id);
CREATE INDEX idx_weather_measurements_uploaded_at ON weather_measurements(uploaded_at);
CREATE INDEX idx_weather_source_user_email ON weather_source(user_email);
CREATE INDEX idx_weather_source_name ON weather_source(name);
CREATE INDEX idx_weather_source_serial_number ON weather_source(serial_number);
CREATE INDEX idx_chrono_measurements_user_email ON chrono_measurements(user_email);
CREATE INDEX idx_chrono_measurements_datetime_local ON chrono_measurements(datetime_local);
CREATE INDEX idx_chrono_measurements_shot_number ON chrono_measurements(shot_number);
CREATE INDEX idx_chrono_measurements_speed_fps ON chrono_measurements(speed_fps);
CREATE INDEX idx_chrono_measurements_session_id ON chrono_measurements(chrono_session_id);
CREATE INDEX idx_chrono_sessions_user_email ON chrono_sessions(user_email);
CREATE INDEX idx_chrono_sessions_tab_name ON chrono_sessions(tab_name);
CREATE INDEX idx_chrono_sessions_datetime_local ON chrono_sessions(datetime_local);
CREATE INDEX idx_chrono_sessions_bullet_type ON chrono_sessions(bullet_type);
CREATE INDEX idx_ranges_submissions_user_email ON ranges_submissions(user_email);
CREATE INDEX idx_ranges_submissions_range_name ON ranges_submissions(range_name);
CREATE INDEX idx_ranges_submissions_submitted_at ON ranges_submissions(submitted_at);
CREATE INDEX idx_ranges_submissions_status ON ranges_submissions(status);
CREATE INDEX idx_ranges_user_email ON ranges(user_email);
CREATE INDEX idx_ranges_range_name ON ranges(range_name);
CREATE INDEX idx_ranges_submitted_at ON ranges(submitted_at);
CREATE INDEX idx_dope_sessions_user_email ON dope_sessions(user_email);
CREATE INDEX idx_dope_sessions_session_name ON dope_sessions(session_name);
CREATE INDEX idx_dope_sessions_created_at ON dope_sessions(created_at);
CREATE INDEX idx_dope_sessions_chrono_session_id ON dope_sessions(chrono_session_id);
CREATE INDEX idx_dope_sessions_range_submission_id ON dope_sessions(range_submission_id);
CREATE INDEX idx_dope_measurements_dope_session_id ON dope_measurements(dope_session_id);
CREATE INDEX idx_dope_measurements_user_email ON dope_measurements(user_email);
CREATE INDEX idx_dope_measurements_shot_number ON dope_measurements(shot_number);
CREATE INDEX idx_dope_measurements_datetime_shot ON dope_measurements(datetime_shot);

-- Enable RLS on sessions table
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Sessions RLS policies
CREATE POLICY sessions_user_policy ON sessions
    FOR ALL USING (user_email = auth.jwt() ->> 'email');

CREATE POLICY sessions_insert_policy ON sessions
    FOR INSERT WITH CHECK (user_email = auth.jwt() ->> 'email');

-- Enable RLS on measurements table
ALTER TABLE measurements ENABLE ROW LEVEL SECURITY;

-- Measurements RLS policies
CREATE POLICY measurements_user_policy ON measurements
    FOR ALL USING (session_id IN (
        SELECT id FROM sessions WHERE user_email = auth.jwt() ->> 'email'
    ));

CREATE POLICY measurements_insert_policy ON measurements
    FOR INSERT WITH CHECK (session_id IN (
        SELECT id FROM sessions WHERE user_email = auth.jwt() ->> 'email'
    ));

-- Enable RLS on weather_measurements table
ALTER TABLE weather_measurements ENABLE ROW LEVEL SECURITY;

-- Weather measurements RLS policies
CREATE POLICY weather_measurements_user_policy ON weather_measurements
    FOR ALL USING (user_email = auth.jwt() ->> 'email');

CREATE POLICY weather_measurements_insert_policy ON weather_measurements
    FOR INSERT WITH CHECK (user_email = auth.jwt() ->> 'email');

-- Enable RLS on weather_source table
ALTER TABLE weather_source ENABLE ROW LEVEL SECURITY;

-- Weather source RLS policies
CREATE POLICY weather_source_user_policy ON weather_source
    FOR ALL USING (user_email = auth.jwt() ->> 'email');

CREATE POLICY weather_source_insert_policy ON weather_source
    FOR INSERT WITH CHECK (user_email = auth.jwt() ->> 'email');

-- Enable RLS on chrono_measurements table
ALTER TABLE chrono_measurements ENABLE ROW LEVEL SECURITY;

-- Chrono measurements RLS policies
CREATE POLICY chrono_measurements_user_policy ON chrono_measurements
    FOR ALL USING (user_email = auth.jwt() ->> 'email');

CREATE POLICY chrono_measurements_insert_policy ON chrono_measurements
    FOR INSERT WITH CHECK (user_email = auth.jwt() ->> 'email');

-- Enable RLS on chrono_sessions table
ALTER TABLE chrono_sessions ENABLE ROW LEVEL SECURITY;

-- Chrono session RLS policies
CREATE POLICY chrono_sessions_user_policy ON chrono_sessions
    FOR ALL USING (user_email = auth.jwt() ->> 'email');

CREATE POLICY chrono_sessions_insert_policy ON chrono_sessions
    FOR INSERT WITH CHECK (user_email = auth.jwt() ->> 'email');

-- Enable RLS on ranges_submissions table
ALTER TABLE ranges_submissions ENABLE ROW LEVEL SECURITY;

-- Ranges submissions RLS policies
CREATE POLICY ranges_submissions_user_policy ON ranges_submissions
    FOR ALL USING (user_email = auth.jwt() ->> 'email');

CREATE POLICY ranges_submissions_insert_policy ON ranges_submissions
    FOR INSERT WITH CHECK (user_email = auth.jwt() ->> 'email');

-- Admin policy for ranges_submissions (johnduffie91@gmail.com can see all)
CREATE POLICY ranges_submissions_admin_policy ON ranges_submissions
    FOR ALL USING (auth.jwt() ->> 'email' = 'johnduffie91@gmail.com');

-- Enable RLS on ranges table
ALTER TABLE ranges ENABLE ROW LEVEL SECURITY;

-- Ranges RLS policies (public read access, admin can insert)
CREATE POLICY ranges_public_read_policy ON ranges
    FOR SELECT USING (true);

CREATE POLICY ranges_admin_policy ON ranges
    FOR ALL USING (auth.jwt() ->> 'email' = 'johnduffie91@gmail.com');

-- Enable RLS on dope_sessions table
ALTER TABLE dope_sessions ENABLE ROW LEVEL SECURITY;

-- DOPE sessions RLS policies
CREATE POLICY dope_sessions_user_policy ON dope_sessions
    FOR ALL USING (user_email = auth.jwt() ->> 'email');

CREATE POLICY dope_sessions_insert_policy ON dope_sessions
    FOR INSERT WITH CHECK (user_email = auth.jwt() ->> 'email');

-- Enable RLS on dope_measurements table
ALTER TABLE dope_measurements ENABLE ROW LEVEL SECURITY;

-- DOPE measurements RLS policies
CREATE POLICY dope_measurements_user_policy ON dope_measurements
    FOR ALL USING (user_email = auth.jwt() ->> 'email');

CREATE POLICY dope_measurements_insert_policy ON dope_measurements
    FOR INSERT WITH CHECK (user_email = auth.jwt() ->> 'email');