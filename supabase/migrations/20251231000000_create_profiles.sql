-- Migration: Create profiles table
-- Created: 2025-12-31
-- Description: Creates the profiles table that extends auth.users with user profile data
--
-- DESIGN DECISIONS:
-- 1. NO email column - email is stored in auth.users only (single source of truth)
--    Use auth.users.email or auth.jwt()->>'email' when needed
-- 2. SELECT policy restricted to own profile only (no public access)
-- 3. No redundant index on id (primary key already creates one)

-- Enable moddatetime extension for auto-updating updated_at
create extension if not exists moddatetime schema extensions;

-- Create profiles table (NO email column - use auth.users.email instead)
create table public.profiles (
  id uuid references auth.users on delete cascade primary key,
  name text,
  avatar_url text,
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

-- Enable Row Level Security
alter table public.profiles enable row level security;

-- RLS Policy: Users can only view their own profile (NOT public)
create policy "Users can view own profile"
  on profiles for select
  using (auth.uid() = id);

-- RLS Policy: Users can insert their own profile
create policy "Users can insert own profile"
  on profiles for insert
  with check (auth.uid() = id);

-- RLS Policy: Users can update their own profile
create policy "Users can update own profile"
  on profiles for update
  using (auth.uid() = id);

-- Trigger for auto-updating updated_at timestamp
create trigger handle_updated_at before update on public.profiles
  for each row execute function moddatetime (updated_at);

-- Function to automatically create profile on user signup
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, name)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'name', new.raw_user_meta_data->>'display_name')
  );
  return new;
end;
$$ language plpgsql security definer;

-- Trigger to call handle_new_user on auth.users insert
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- Add comments for documentation
comment on table public.profiles is 'User profiles extending auth.users with application-specific data. Email is NOT stored here - use auth.users.email';
comment on column public.profiles.id is 'References auth.users.id';
comment on column public.profiles.name is 'User display name, extracted from registration metadata';
comment on function public.handle_new_user() is 'Auto-creates profile row when new user signs up';
