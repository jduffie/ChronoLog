-- Add status column to locations table
-- Run this in Supabase SQL Editor

ALTER TABLE locations ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'ACTIVE';

-- Update existing locations to ACTIVE status
UPDATE locations SET status = 'ACTIVE' WHERE status IS NULL;

-- Add index for status column for better performance
CREATE INDEX IF NOT EXISTS idx_locations_status ON locations(status);