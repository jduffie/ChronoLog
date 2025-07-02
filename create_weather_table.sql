-- Create weather_measurements table for Kestrel weather data
CREATE TABLE IF NOT EXISTS weather_measurements (
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
    
    -- Unique constraint on serial_number + timestamp
    UNIQUE(serial_number, measurement_timestamp)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_weather_measurements_user_email ON weather_measurements(user_email);
CREATE INDEX IF NOT EXISTS idx_weather_measurements_serial_timestamp ON weather_measurements(serial_number, measurement_timestamp);
CREATE INDEX IF NOT EXISTS idx_weather_measurements_timestamp ON weather_measurements(measurement_timestamp);

-- Add RLS policy for user data isolation
ALTER TABLE weather_measurements ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own weather data
CREATE POLICY weather_measurements_user_policy ON weather_measurements
    FOR ALL USING (user_email = auth.jwt() ->> 'email');

-- Policy: Users can insert their own weather data  
CREATE POLICY weather_measurements_insert_policy ON weather_measurements
    FOR INSERT WITH CHECK (user_email = auth.jwt() ->> 'email');