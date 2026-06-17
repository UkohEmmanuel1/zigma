-- =============================================================================
-- Zigma – Supabase Schema Setup (OPTIONAL)
-- =============================================================================
-- NOTE: As of the latest version, Zigma manages its own User table via
-- Django migrations (``apps/users/models.py``).  The SQL below is only
-- needed if you want an additional ``public.users`` view for direct SQL
-- access from Supabase.
--
-- If you do not need direct SQL access to user data, skip this file
-- entirely – Django will create the ``users`` table automatically.
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.users (
    id         UUID        PRIMARY KEY,
    email      TEXT        NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
