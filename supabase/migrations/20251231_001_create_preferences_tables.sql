-- Migration: Create User Preferences Tables
-- Date: 2024-12-31
-- Description: Creates tables for user dietary preferences, allergies, and excluded/preferred ingredients
-- Also adds portions_count column to users table

-- =============================================================================
-- Step 1: Create ENUM types for dietary preferences and allergies
-- =============================================================================

-- Create dietary_type enum
CREATE TYPE dietary_type AS ENUM (
    'vegetarian',
    'vegan',
    'no_pork',
    'no_beef',
    'pescetarian',
    'halal',
    'kosher'
);

-- Create allergy_type enum
CREATE TYPE allergy_type AS ENUM (
    'gluten',
    'lactose',
    'tree_nuts',
    'peanuts',
    'eggs',
    'fish',
    'shellfish',
    'soy',
    'sesame',
    'mustard',
    'celery'
);

-- =============================================================================
-- Step 2: Create user_dietary_preferences table
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_dietary_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    dietary_type dietary_type NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint: one dietary preference per user per type
    CONSTRAINT unique_user_dietary_preference UNIQUE (user_id, dietary_type)
);

-- Create index on user_id for faster lookups
CREATE INDEX idx_user_dietary_preferences_user_id
    ON user_dietary_preferences(user_id);

-- =============================================================================
-- Step 3: Create user_allergies table
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_allergies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    allergy_type allergy_type NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint: one allergy per user per type
    CONSTRAINT unique_user_allergy UNIQUE (user_id, allergy_type)
);

-- Create index on user_id for faster lookups
CREATE INDEX idx_user_allergies_user_id
    ON user_allergies(user_id);

-- =============================================================================
-- Step 4: Create user_excluded_ingredients table
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_excluded_ingredients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    ingredient_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint: one ingredient name per user (normalized)
    CONSTRAINT unique_user_excluded_ingredient UNIQUE (user_id, ingredient_name),

    -- Constraint: ingredient name must not be empty
    CONSTRAINT ingredient_name_not_empty CHECK (LENGTH(TRIM(ingredient_name)) > 0)
);

-- Create index on user_id for faster lookups
CREATE INDEX idx_user_excluded_ingredients_user_id
    ON user_excluded_ingredients(user_id);

-- =============================================================================
-- Step 5: Create user_preferred_ingredients table
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_preferred_ingredients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    ingredient_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint: one ingredient name per user (normalized)
    CONSTRAINT unique_user_preferred_ingredient UNIQUE (user_id, ingredient_name),

    -- Constraint: ingredient name must not be empty
    CONSTRAINT preferred_ingredient_name_not_empty CHECK (LENGTH(TRIM(ingredient_name)) > 0)
);

-- Create index on user_id for faster lookups
CREATE INDEX idx_user_preferred_ingredients_user_id
    ON user_preferred_ingredients(user_id);

-- =============================================================================
-- Step 6: Add portions_count column to users table (via profiles or user_settings)
-- Note: If using Supabase auth, we need a separate profiles table
-- =============================================================================

-- Create user_settings table for portions_count
-- This approach is preferred as we don't modify auth.users directly
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    portions_count INTEGER NOT NULL DEFAULT 2,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint: one settings record per user
    CONSTRAINT unique_user_settings UNIQUE (user_id),

    -- Constraint: portions_count must be between 1 and 20
    CONSTRAINT portions_count_range CHECK (portions_count >= 1 AND portions_count <= 20)
);

-- Create index on user_id for faster lookups
CREATE INDEX idx_user_settings_user_id
    ON user_settings(user_id);

-- =============================================================================
-- Step 7: Create trigger to update updated_at on user_settings
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_settings_updated_at
    BEFORE UPDATE ON user_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Step 8: Enable Row Level Security (RLS) on all tables
-- =============================================================================

-- Enable RLS
ALTER TABLE user_dietary_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_allergies ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_excluded_ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferred_ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- Step 9: Create RLS Policies - Users can only access their own data
-- =============================================================================

-- Policies for user_dietary_preferences
CREATE POLICY "Users can view their own dietary preferences"
    ON user_dietary_preferences
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own dietary preferences"
    ON user_dietary_preferences
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own dietary preferences"
    ON user_dietary_preferences
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own dietary preferences"
    ON user_dietary_preferences
    FOR DELETE
    USING (auth.uid() = user_id);

-- Policies for user_allergies
CREATE POLICY "Users can view their own allergies"
    ON user_allergies
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own allergies"
    ON user_allergies
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own allergies"
    ON user_allergies
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own allergies"
    ON user_allergies
    FOR DELETE
    USING (auth.uid() = user_id);

-- Policies for user_excluded_ingredients
CREATE POLICY "Users can view their own excluded ingredients"
    ON user_excluded_ingredients
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own excluded ingredients"
    ON user_excluded_ingredients
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own excluded ingredients"
    ON user_excluded_ingredients
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own excluded ingredients"
    ON user_excluded_ingredients
    FOR DELETE
    USING (auth.uid() = user_id);

-- Policies for user_preferred_ingredients
CREATE POLICY "Users can view their own preferred ingredients"
    ON user_preferred_ingredients
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own preferred ingredients"
    ON user_preferred_ingredients
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own preferred ingredients"
    ON user_preferred_ingredients
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own preferred ingredients"
    ON user_preferred_ingredients
    FOR DELETE
    USING (auth.uid() = user_id);

-- Policies for user_settings
CREATE POLICY "Users can view their own settings"
    ON user_settings
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own settings"
    ON user_settings
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own settings"
    ON user_settings
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own settings"
    ON user_settings
    FOR DELETE
    USING (auth.uid() = user_id);

-- =============================================================================
-- Rollback script (save for future use)
-- =============================================================================
-- To rollback this migration, run:
--
-- DROP POLICY IF EXISTS "Users can delete their own settings" ON user_settings;
-- DROP POLICY IF EXISTS "Users can update their own settings" ON user_settings;
-- DROP POLICY IF EXISTS "Users can insert their own settings" ON user_settings;
-- DROP POLICY IF EXISTS "Users can view their own settings" ON user_settings;
-- DROP POLICY IF EXISTS "Users can delete their own preferred ingredients" ON user_preferred_ingredients;
-- DROP POLICY IF EXISTS "Users can update their own preferred ingredients" ON user_preferred_ingredients;
-- DROP POLICY IF EXISTS "Users can insert their own preferred ingredients" ON user_preferred_ingredients;
-- DROP POLICY IF EXISTS "Users can view their own preferred ingredients" ON user_preferred_ingredients;
-- DROP POLICY IF EXISTS "Users can delete their own excluded ingredients" ON user_excluded_ingredients;
-- DROP POLICY IF EXISTS "Users can update their own excluded ingredients" ON user_excluded_ingredients;
-- DROP POLICY IF EXISTS "Users can insert their own excluded ingredients" ON user_excluded_ingredients;
-- DROP POLICY IF EXISTS "Users can view their own excluded ingredients" ON user_excluded_ingredients;
-- DROP POLICY IF EXISTS "Users can delete their own allergies" ON user_allergies;
-- DROP POLICY IF EXISTS "Users can update their own allergies" ON user_allergies;
-- DROP POLICY IF EXISTS "Users can insert their own allergies" ON user_allergies;
-- DROP POLICY IF EXISTS "Users can view their own allergies" ON user_allergies;
-- DROP POLICY IF EXISTS "Users can delete their own dietary preferences" ON user_dietary_preferences;
-- DROP POLICY IF EXISTS "Users can update their own dietary preferences" ON user_dietary_preferences;
-- DROP POLICY IF EXISTS "Users can insert their own dietary preferences" ON user_dietary_preferences;
-- DROP POLICY IF EXISTS "Users can view their own dietary preferences" ON user_dietary_preferences;
-- DROP TRIGGER IF EXISTS update_user_settings_updated_at ON user_settings;
-- DROP FUNCTION IF EXISTS update_updated_at_column();
-- DROP TABLE IF EXISTS user_settings;
-- DROP TABLE IF EXISTS user_preferred_ingredients;
-- DROP TABLE IF EXISTS user_excluded_ingredients;
-- DROP TABLE IF EXISTS user_allergies;
-- DROP TABLE IF EXISTS user_dietary_preferences;
-- DROP TYPE IF EXISTS allergy_type;
-- DROP TYPE IF EXISTS dietary_type;
