-- Migration: Create shopping_list_items table
-- Description: Stores shopping list items generated from weekly meal plans
-- Date: 2026-01-03

-- Create the shopping_list_items table
CREATE TABLE IF NOT EXISTS shopping_list_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    ingredient_name TEXT NOT NULL,
    quantity TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'autres',
    is_checked BOOLEAN NOT NULL DEFAULT FALSE,
    week_start DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint: one ingredient per user per week
    CONSTRAINT unique_user_ingredient_week UNIQUE (user_id, ingredient_name, week_start),

    -- Category validation
    CONSTRAINT valid_category CHECK (
        category IN (
            'legumes',
            'viandes',
            'poissons',
            'produits_laitiers',
            'epicerie',
            'boissons',
            'surgeles',
            'autres'
        )
    ),

    -- Week start must be a Monday (weekday 1 in PostgreSQL)
    CONSTRAINT week_start_is_monday CHECK (EXTRACT(DOW FROM week_start) = 1)
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_shopping_list_items_user_id
    ON shopping_list_items(user_id);

CREATE INDEX IF NOT EXISTS idx_shopping_list_items_week_start
    ON shopping_list_items(week_start);

CREATE INDEX IF NOT EXISTS idx_shopping_list_items_user_week
    ON shopping_list_items(user_id, week_start);

CREATE INDEX IF NOT EXISTS idx_shopping_list_items_category
    ON shopping_list_items(category);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_shopping_list_items_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_shopping_list_items_updated_at ON shopping_list_items;
CREATE TRIGGER trigger_shopping_list_items_updated_at
    BEFORE UPDATE ON shopping_list_items
    FOR EACH ROW
    EXECUTE FUNCTION update_shopping_list_items_updated_at();

-- Enable Row Level Security
ALTER TABLE shopping_list_items ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own shopping list items

-- SELECT policy: users can only read their own items
DROP POLICY IF EXISTS "Users can read own shopping list items" ON shopping_list_items;
CREATE POLICY "Users can read own shopping list items"
    ON shopping_list_items
    FOR SELECT
    USING (auth.uid() = user_id);

-- INSERT policy: users can only insert for themselves
DROP POLICY IF EXISTS "Users can insert own shopping list items" ON shopping_list_items;
CREATE POLICY "Users can insert own shopping list items"
    ON shopping_list_items
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- UPDATE policy: users can only update their own items
DROP POLICY IF EXISTS "Users can update own shopping list items" ON shopping_list_items;
CREATE POLICY "Users can update own shopping list items"
    ON shopping_list_items
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- DELETE policy: users can only delete their own items
DROP POLICY IF EXISTS "Users can delete own shopping list items" ON shopping_list_items;
CREATE POLICY "Users can delete own shopping list items"
    ON shopping_list_items
    FOR DELETE
    USING (auth.uid() = user_id);

-- Comment on table
COMMENT ON TABLE shopping_list_items IS 'Shopping list items generated from weekly meal plans';
COMMENT ON COLUMN shopping_list_items.ingredient_name IS 'Name of the ingredient (case-normalized)';
COMMENT ON COLUMN shopping_list_items.quantity IS 'Aggregated quantity with unit(s)';
COMMENT ON COLUMN shopping_list_items.category IS 'Category for grouping (legumes, viandes, etc.)';
COMMENT ON COLUMN shopping_list_items.is_checked IS 'Whether the item has been purchased';
COMMENT ON COLUMN shopping_list_items.week_start IS 'Monday of the week this list belongs to';
