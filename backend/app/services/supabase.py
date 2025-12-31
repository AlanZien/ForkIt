"""Supabase client initialization."""

from supabase import Client, create_client

from app.config import settings


def get_supabase_client() -> Client:
    """Get Supabase client with anon key for public operations."""
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def get_supabase_admin() -> Client:
    """Get Supabase client with service role key for admin operations."""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
