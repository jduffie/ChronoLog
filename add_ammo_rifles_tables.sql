-- Add ammo and rifles tables to existing database
-- Run this in Supabase SQL Editor

-- ========================================
-- AMMO TABLE OPERATIONS
-- ========================================

-- Create ammo table for ammunition metadata
CREATE TABLE IF NOT EXISTS ammo (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT NOT NULL,

    make TEXT NOT NULL,        -- Manufacturer/brand (Hornady)
    model TEXT NOT NULL,       -- Model (ELD-M)
    caliber TEXT NOT NULL,     -- Caliber (6.5cm)
    weight TEXT NOT NULL,      -- Weight (147gr)

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint to prevent duplicate ammo per user
    UNIQUE(user_email, make, model, caliber, weight)
);

-- Create ammo indexes
CREATE INDEX IF NOT EXISTS idx_ammo_user_email ON ammo(user_email);
CREATE INDEX IF NOT EXISTS idx_ammo_make ON ammo(make);
CREATE INDEX IF NOT EXISTS idx_ammo_caliber ON ammo(caliber);
CREATE INDEX IF NOT EXISTS idx_ammo_created_at ON ammo(created_at);

-- Enable RLS on ammo table
ALTER TABLE ammo ENABLE ROW LEVEL SECURITY;

-- Create ammo RLS policies
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'ammo' AND policyname = 'ammo_user_policy'
    ) THEN
        CREATE POLICY ammo_user_policy ON ammo
            FOR ALL USING (user_email = auth.jwt() ->> 'email');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'ammo' AND policyname = 'ammo_insert_policy'
    ) THEN
        CREATE POLICY ammo_insert_policy ON ammo
            FOR INSERT WITH CHECK (user_email = auth.jwt() ->> 'email');
    END IF;
END $$;

-- ========================================
-- RIFLES TABLE OPERATIONS
-- ========================================

-- Create rifles table for rifle metadata
CREATE TABLE IF NOT EXISTS rifles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email TEXT NOT NULL,

    name TEXT NOT NULL,                    -- User-defined rifle name
    barrel_twist_ratio TEXT,               -- Barrel twist ratio (e.g., "1:8", "1:10")
    barrel_length TEXT,                    -- Barrel length (e.g., "24 inches", "20\"")
    sight_offset TEXT,                     -- Sight offset/height (e.g., "1.5 inches", "38mm")
    trigger TEXT,                          -- Trigger information (e.g., "Timney 2-stage", "Stock trigger")
    scope TEXT,                            -- Scope information (e.g., "Vortex Viper PST 5-25x50")

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint to prevent duplicate rifle names per user
    UNIQUE(user_email, name)
);

-- Create rifles indexes
CREATE INDEX IF NOT EXISTS idx_rifles_user_email ON rifles(user_email);
CREATE INDEX IF NOT EXISTS idx_rifles_name ON rifles(name);
CREATE INDEX IF NOT EXISTS idx_rifles_created_at ON rifles(created_at);

-- Enable RLS on rifles table
ALTER TABLE rifles ENABLE ROW LEVEL SECURITY;

-- Create rifles RLS policies
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'rifles' AND policyname = 'rifles_user_policy'
    ) THEN
        CREATE POLICY rifles_user_policy ON rifles
            FOR ALL USING (user_email = auth.jwt() ->> 'email');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'rifles' AND policyname = 'rifles_insert_policy'
    ) THEN
        CREATE POLICY rifles_insert_policy ON rifles
            FOR INSERT WITH CHECK (user_email = auth.jwt() ->> 'email');
    END IF;
END $$;

-- ========================================
-- VERIFICATION
-- ========================================

-- Verify tables were created successfully
DO $$
BEGIN
    -- Check if ammo table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ammo') THEN
        RAISE NOTICE 'SUCCESS: ammo table created successfully';
    ELSE
        RAISE EXCEPTION 'ERROR: ammo table was not created';
    END IF;
    
    -- Check if rifles table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'rifles') THEN
        RAISE NOTICE 'SUCCESS: rifles table created successfully';
    ELSE
        RAISE EXCEPTION 'ERROR: rifles table was not created';
    END IF;
END $$;