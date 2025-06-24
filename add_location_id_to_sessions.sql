-- Add location_id column to sessions table
-- Run this in Supabase SQL Editor

ALTER TABLE sessions ADD COLUMN IF NOT EXISTS location_id UUID REFERENCES locations(id);

-- Add index for better performance
CREATE INDEX IF NOT EXISTS idx_sessions_location_id ON sessions(location_id);