CREATE TABLE IF NOT EXISTS kyc_verifications (
    id                  UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id             UUID            NOT NULL REFERENCES users(id) UNIQUE,
    status              TEXT            NOT NULL DEFAULT 'PENDING',
    document_type       TEXT,
    document_front_url  TEXT,
    document_back_url   TEXT,
    selfie_url          TEXT,
    verification_provider TEXT,
    provider_reference  TEXT,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

ALTER TABLE kyc_verifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users read own kyc"
    ON kyc_verifications FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users insert own kyc"
    ON kyc_verifications FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users update own kyc"
    ON kyc_verifications FOR UPDATE
    USING (auth.uid() = user_id);
