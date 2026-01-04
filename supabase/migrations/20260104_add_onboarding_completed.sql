-- Migration: Add onboarding_completed column to user_settings table
-- Task 1.2: Add onboarding_completed boolean column (default: false)
-- This tracks whether a user has completed the post-registration profile setup wizard

-- Add the onboarding_completed column if it doesn't exist
ALTER TABLE user_settings
ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE;

-- Add a comment for documentation
COMMENT ON COLUMN user_settings.onboarding_completed IS
  'Tracks if user has completed the post-registration onboarding wizard';
