-- Reset all tables: delete data, drop tables, and recreate with latest schema
-- Run this in Supabase SQL Editor

-- Delete all data first (respecting foreign key constraints)
DELETE FROM measurements;
DELETE FROM sessions;
DELETE FROM weather_measurements;

-- Drop all tables with CASCADE to handle any remaining dependencies
DROP TABLE IF EXISTS measurements CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS weather_measurements CASCADE;

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

-- Create weather_measurements table for Kestrel weather data
CREATE TABLE weather_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT NOT NULL,
    device_name TEXT,
    device_model TEXT,
    serial_number TEXT NOT NULL,
    measurement_timestamp TIMESTAMPTZ NOT NULL,
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
    
    -- Unique constraint on device_name + serial_number + timestamp
    UNIQUE(device_name, serial_number, measurement_timestamp)
);

-- Create indexes for better performance
CREATE INDEX idx_sessions_user_email ON sessions(user_email);
CREATE INDEX idx_sessions_uploaded_at ON sessions(uploaded_at);
CREATE INDEX idx_measurements_session_id ON measurements(session_id);
CREATE INDEX idx_measurements_shot_number ON measurements(shot_number);
CREATE INDEX idx_measurements_datetime_local ON measurements(datetime_local);
CREATE INDEX idx_weather_measurements_user_email ON weather_measurements(user_email);
CREATE INDEX idx_weather_measurements_device_serial_timestamp ON weather_measurements(device_name, serial_number, measurement_timestamp);
CREATE INDEX idx_weather_measurements_timestamp ON weather_measurements(measurement_timestamp);

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