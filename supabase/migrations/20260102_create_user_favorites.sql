-- Migration: Create user_favorites table
-- Date: 2026-01-02
-- Feature: Recipe Favorites

-- Create user_favorites table
CREATE TABLE IF NOT EXISTS user_favorites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  recipe_id VARCHAR(20) NOT NULL,
  recipe_name VARCHAR(255) NOT NULL,
  recipe_thumbnail VARCHAR(500),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  CONSTRAINT unique_user_recipe UNIQUE(user_id, recipe_id)
);

-- Index for user queries
CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON user_favorites(user_id);

-- Enable Row Level Security
ALTER TABLE user_favorites ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own favorites"
  ON user_favorites FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own favorites"
  ON user_favorites FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own favorites"
  ON user_favorites FOR DELETE
  USING (auth.uid() = user_id);

-- Comment
COMMENT ON TABLE user_favorites IS 'Stores user favorite recipes from TheMealDB';
