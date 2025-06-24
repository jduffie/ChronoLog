-- Migration script to update locations table structure
-- Run this in Supabase SQL Editor

-- Step 1: Create locations_draft table for new location requests
CREATE TABLE IF NOT EXISTS locations_draft (
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

-- Step 2: Migrate existing PENDING locations to locations_draft
INSERT INTO locations_draft (user_email, name, altitude, azimuth, latitude, longitude, google_maps_link, created_at, updated_at)
SELECT user_email, name, altitude, azimuth, latitude, longitude, google_maps_link, created_at, updated_at
FROM locations 
WHERE status = 'PENDING';

-- Step 3: Remove PENDING locations from main locations table (keep only ACTIVE)
DELETE FROM locations WHERE status = 'PENDING';

-- Step 4: Remove status and user_email columns from locations table
ALTER TABLE locations DROP COLUMN IF EXISTS status;
ALTER TABLE locations DROP COLUMN IF EXISTS user_email;

-- Step 5: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_locations_draft_user_email ON locations_draft(user_email);
CREATE INDEX IF NOT EXISTS idx_locations_draft_name ON locations_draft(name);

-- Step 6: Remove old status index if it exists
DROP INDEX IF EXISTS idx_locations_status;