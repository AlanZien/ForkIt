-- Migration: Create meal_slots table
-- Date: 2026-01-03
-- Feature: Weekly Meal Planning

-- Create meal_slots table
CREATE TABLE IF NOT EXISTS meal_slots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  meal_type VARCHAR(10) NOT NULL CHECK (meal_type IN ('dejeuner', 'diner')),
  recipe_id VARCHAR(20) NOT NULL,
  recipe_name VARCHAR(255) NOT NULL,
  recipe_thumbnail VARCHAR(500),
  portions INTEGER NOT NULL DEFAULT 2 CHECK (portions >= 1 AND portions <= 20),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Unique constraint: one recipe per slot (user + date + meal_type)
  CONSTRAINT uq_meal_slots_user_date_type UNIQUE(user_id, date, meal_type)
);

-- Index for week queries (user_id + date range)
CREATE INDEX IF NOT EXISTS idx_meal_slots_user_date ON meal_slots(user_id, date);

-- Index for recent recipes queries (user_id + recipe_id)
CREATE INDEX IF NOT EXISTS idx_meal_slots_user_recipe ON meal_slots(user_id, recipe_id);

-- Enable Row Level Security
ALTER TABLE meal_slots ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own meal slots"
  ON meal_slots FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own meal slots"
  ON meal_slots FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own meal slots"
  ON meal_slots FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own meal slots"
  ON meal_slots FOR DELETE
  USING (auth.uid() = user_id);

-- Create or replace function for auto-updating updated_at
CREATE OR REPLACE FUNCTION update_meal_slots_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS trigger_meal_slots_updated_at ON meal_slots;
CREATE TRIGGER trigger_meal_slots_updated_at
  BEFORE UPDATE ON meal_slots
  FOR EACH ROW
  EXECUTE FUNCTION update_meal_slots_updated_at();

-- Comment
COMMENT ON TABLE meal_slots IS 'Stores user weekly meal planning slots with recipe assignments';
COMMENT ON COLUMN meal_slots.meal_type IS 'Meal type: dejeuner (lunch) or diner (dinner)';
COMMENT ON COLUMN meal_slots.portions IS 'Number of portions for this meal (1-20)';
