-- Migration: Create recipe-images storage bucket
-- Date: 2026-01-04
-- Feature: Personal Recipe Management - Image Upload Storage
-- Task Group 2: Supabase Storage Bucket

-- =============================================================================
-- STORAGE BUCKET: recipe-images
-- =============================================================================
-- Purpose: Store user-uploaded recipe photos for personal recipes
-- Access: Authenticated users only (private bucket)
-- File size limit: 5MB (enforced at application level)
-- URL pattern: recipe-images/{user_id}/{recipe_id}/{filename}

-- Create the storage bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'recipe-images',
  'recipe-images',
  false,  -- Private bucket: authenticated access only
  5242880,  -- 5MB in bytes (5 * 1024 * 1024)
  ARRAY['image/jpeg', 'image/png', 'image/webp']::text[]
)
ON CONFLICT (id) DO UPDATE SET
  public = EXCLUDED.public,
  file_size_limit = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

-- =============================================================================
-- IMPORTANT: STORAGE RLS POLICIES - MANUAL SETUP REQUIRED
-- =============================================================================
-- Storage policies on storage.objects cannot be created via SQL migrations
-- because the table is owned by Supabase. You MUST create these policies
-- manually through the Supabase Dashboard.
--
-- Go to: Storage > Policies > New Policy (for bucket 'recipe-images')
--
-- Create these 4 policies with Target roles = "authenticated":
--
-- 1. SELECT Policy:
--    Name: "Users can view own recipe images"
--    Expression: (storage.foldername(name))[1] = auth.uid()::text
--
-- 2. INSERT Policy:
--    Name: "Users can upload own recipe images"
--    Expression: (storage.foldername(name))[1] = auth.uid()::text
--
-- 3. UPDATE Policy:
--    Name: "Users can update own recipe images"
--    Expression: (storage.foldername(name))[1] = auth.uid()::text
--
-- 4. DELETE Policy:
--    Name: "Users can delete own recipe images"
--    Expression: (storage.foldername(name))[1] = auth.uid()::text
--
-- =============================================================================

-- =============================================================================
-- STORAGE URL PATTERN DOCUMENTATION
-- =============================================================================
--
-- URL Pattern: recipe-images/{user_id}/{recipe_id}/{filename}
--
-- Examples:
--   recipe-images/123e4567-e89b-12d3-a456-426614174000/abc123/photo.jpg
--   recipe-images/123e4567-e89b-12d3-a456-426614174000/def456/tarte-aux-pommes.webp
--
-- Full Storage URL:
--   https://{project-ref}.supabase.co/storage/v1/object/authenticated/recipe-images/{user_id}/{recipe_id}/{filename}
--
-- Service Implementation Notes:
--   - Upload endpoint should construct path as: {user_id}/{recipe_id}/{uuid}.{extension}
--   - Use UUID for filename to avoid conflicts and ensure uniqueness
--   - Validate file type (jpeg, png, webp) before upload
--   - Validate file size (max 5MB) at application layer
--   - Store the full path in personal_recipes.image_url field
--   - When deleting a recipe, also delete associated images from storage
--
-- =============================================================================
