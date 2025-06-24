-- ChronoLog Database Schema
-- Run this in Supabase SQL Editor

-- Drop existing tables if they exist
DROP TABLE IF EXISTS measurements CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS locations_draft CASCADE;
DROP TABLE IF EXISTS locations CASCADE;

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
    location_id UUID REFERENCES locations(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create measurements table
CREATE TABLE measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    shot_number INTEGER,
    speed_fps NUMERIC,
    delta_avg_fps NUMERIC,
    ke_ft_lb NUMERIC,
    power_factor NUMERIC,
    time_local TEXT,
    clean_bore BOOLEAN,
    cold_bore BOOLEAN,
    shot_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create locations table (global read access for all users)
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    altitude NUMERIC,
    azimuth NUMERIC,
    latitude NUMERIC(10, 8),
    longitude NUMERIC(11, 8),
    google_maps_link TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create locations_draft table for new location requests
CREATE TABLE locations_draft (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT NOT NULL,
    name TEXT NOT NULL,
    altitude NUMERIC,
    azimuth NUMERIC,
    latitude NUMERIC(10, 8),
    longitude NUMERIC(11, 8),
    google_maps_link TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_sessions_user_email ON sessions(user_email);
CREATE INDEX idx_sessions_uploaded_at ON sessions(uploaded_at);
CREATE INDEX idx_sessions_location_id ON sessions(location_id);
CREATE INDEX idx_measurements_session_id ON measurements(session_id);
CREATE INDEX idx_measurements_shot_number ON measurements(shot_number);
CREATE INDEX idx_locations_name ON locations(name);
CREATE INDEX idx_locations_draft_user_email ON locations_draft(user_email);
CREATE INDEX idx_locations_draft_name ON locations_draft(name);