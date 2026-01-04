-- Migration: Create personal recipes tables
-- Date: 2026-01-04
-- Feature: Personal Recipe Management

-- =============================================================================
-- Table: personal_recipes
-- Main table for user-created personal recipes
-- =============================================================================
CREATE TABLE IF NOT EXISTS personal_recipes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  image_url VARCHAR(500),
  servings INTEGER NOT NULL CHECK (servings >= 1 AND servings <= 20),
  prep_time_minutes INTEGER CHECK (prep_time_minutes >= 0),
  cook_time_minutes INTEGER CHECK (cook_time_minutes >= 0),
  tags TEXT[],
  source_recipe_id VARCHAR(20),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- Table: personal_recipe_ingredients
-- Stores structured ingredients for personal recipes
-- =============================================================================
CREATE TABLE IF NOT EXISTS personal_recipe_ingredients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recipe_id UUID NOT NULL REFERENCES personal_recipes(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  quantity NUMERIC NOT NULL,
  unit VARCHAR(50) NOT NULL,
  note VARCHAR(255),
  sort_order INTEGER NOT NULL,

  -- Ensure unique ordering per recipe
  CONSTRAINT uq_recipe_ingredient_order UNIQUE(recipe_id, sort_order)
);

-- =============================================================================
-- Table: personal_recipe_steps
-- Stores instruction steps for personal recipes
-- =============================================================================
CREATE TABLE IF NOT EXISTS personal_recipe_steps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recipe_id UUID NOT NULL REFERENCES personal_recipes(id) ON DELETE CASCADE,
  step_number INTEGER NOT NULL,
  instruction TEXT NOT NULL,

  -- Ensure unique step numbering per recipe
  CONSTRAINT uq_recipe_step_number UNIQUE(recipe_id, step_number)
);

-- =============================================================================
-- Indexes for Performance
-- =============================================================================

-- Index for querying user's recipes
CREATE INDEX IF NOT EXISTS idx_personal_recipes_user_id
  ON personal_recipes(user_id);

-- Index for searching by title within user's recipes
CREATE INDEX IF NOT EXISTS idx_personal_recipes_user_title
  ON personal_recipes(user_id, title);

-- Index for querying ingredients by recipe
CREATE INDEX IF NOT EXISTS idx_personal_recipe_ingredients_recipe
  ON personal_recipe_ingredients(recipe_id);

-- Index for querying steps by recipe
CREATE INDEX IF NOT EXISTS idx_personal_recipe_steps_recipe
  ON personal_recipe_steps(recipe_id);

-- =============================================================================
-- Row Level Security (RLS)
-- =============================================================================

-- Enable RLS on all tables
ALTER TABLE personal_recipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE personal_recipe_ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE personal_recipe_steps ENABLE ROW LEVEL SECURITY;

-- -----------------------------------------------------------------------------
-- RLS Policies for personal_recipes
-- -----------------------------------------------------------------------------
CREATE POLICY "Users can view own personal recipes"
  ON personal_recipes FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own personal recipes"
  ON personal_recipes FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own personal recipes"
  ON personal_recipes FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own personal recipes"
  ON personal_recipes FOR DELETE
  USING (auth.uid() = user_id);

-- -----------------------------------------------------------------------------
-- RLS Policies for personal_recipe_ingredients
-- Access is granted if user owns the parent recipe
-- -----------------------------------------------------------------------------
CREATE POLICY "Users can view own recipe ingredients"
  ON personal_recipe_ingredients FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM personal_recipes
      WHERE personal_recipes.id = personal_recipe_ingredients.recipe_id
      AND personal_recipes.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert own recipe ingredients"
  ON personal_recipe_ingredients FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM personal_recipes
      WHERE personal_recipes.id = personal_recipe_ingredients.recipe_id
      AND personal_recipes.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update own recipe ingredients"
  ON personal_recipe_ingredients FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM personal_recipes
      WHERE personal_recipes.id = personal_recipe_ingredients.recipe_id
      AND personal_recipes.user_id = auth.uid()
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM personal_recipes
      WHERE personal_recipes.id = personal_recipe_ingredients.recipe_id
      AND personal_recipes.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete own recipe ingredients"
  ON personal_recipe_ingredients FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM personal_recipes
      WHERE personal_recipes.id = personal_recipe_ingredients.recipe_id
      AND personal_recipes.user_id = auth.uid()
    )
  );

-- -----------------------------------------------------------------------------
-- RLS Policies for personal_recipe_steps
-- Access is granted if user owns the parent recipe
-- -----------------------------------------------------------------------------
CREATE POLICY "Users can view own recipe steps"
  ON personal_recipe_steps FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM personal_recipes
      WHERE personal_recipes.id = personal_recipe_steps.recipe_id
      AND personal_recipes.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert own recipe steps"
  ON personal_recipe_steps FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM personal_recipes
      WHERE personal_recipes.id = personal_recipe_steps.recipe_id
      AND personal_recipes.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update own recipe steps"
  ON personal_recipe_steps FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM personal_recipes
      WHERE personal_recipes.id = personal_recipe_steps.recipe_id
      AND personal_recipes.user_id = auth.uid()
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM personal_recipes
      WHERE personal_recipes.id = personal_recipe_steps.recipe_id
      AND personal_recipes.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete own recipe steps"
  ON personal_recipe_steps FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM personal_recipes
      WHERE personal_recipes.id = personal_recipe_steps.recipe_id
      AND personal_recipes.user_id = auth.uid()
    )
  );

-- =============================================================================
-- Trigger for auto-updating updated_at
-- =============================================================================

-- Create function for auto-updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_personal_recipes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at on personal_recipes
DROP TRIGGER IF EXISTS trigger_personal_recipes_updated_at ON personal_recipes;
CREATE TRIGGER trigger_personal_recipes_updated_at
  BEFORE UPDATE ON personal_recipes
  FOR EACH ROW
  EXECUTE FUNCTION update_personal_recipes_updated_at();

-- =============================================================================
-- Table Comments
-- =============================================================================
COMMENT ON TABLE personal_recipes IS 'Stores user-created personal recipes with metadata';
COMMENT ON COLUMN personal_recipes.user_id IS 'Owner of the recipe (foreign key to auth.users)';
COMMENT ON COLUMN personal_recipes.title IS 'Recipe title (required, max 255 chars)';
COMMENT ON COLUMN personal_recipes.image_url IS 'URL to recipe image (optional, from Supabase Storage)';
COMMENT ON COLUMN personal_recipes.servings IS 'Number of servings (1-20)';
COMMENT ON COLUMN personal_recipes.prep_time_minutes IS 'Preparation time in minutes (optional)';
COMMENT ON COLUMN personal_recipes.cook_time_minutes IS 'Cooking time in minutes (optional)';
COMMENT ON COLUMN personal_recipes.tags IS 'Array of recipe tags for categorization';
COMMENT ON COLUMN personal_recipes.source_recipe_id IS 'TheMealDB recipe ID if forked from API recipe';

COMMENT ON TABLE personal_recipe_ingredients IS 'Stores structured ingredients for personal recipes';
COMMENT ON COLUMN personal_recipe_ingredients.recipe_id IS 'Parent recipe (cascades on delete)';
COMMENT ON COLUMN personal_recipe_ingredients.name IS 'Ingredient name (required)';
COMMENT ON COLUMN personal_recipe_ingredients.quantity IS 'Numeric quantity (required)';
COMMENT ON COLUMN personal_recipe_ingredients.unit IS 'Unit of measurement (g, ml, pieces, etc.)';
COMMENT ON COLUMN personal_recipe_ingredients.note IS 'Optional note (e.g., "diced", "room temperature")';
COMMENT ON COLUMN personal_recipe_ingredients.sort_order IS 'Display order within recipe';

COMMENT ON TABLE personal_recipe_steps IS 'Stores instruction steps for personal recipes';
COMMENT ON COLUMN personal_recipe_steps.recipe_id IS 'Parent recipe (cascades on delete)';
COMMENT ON COLUMN personal_recipe_steps.step_number IS 'Step number for ordering (1-based)';
COMMENT ON COLUMN personal_recipe_steps.instruction IS 'Step instruction text';
