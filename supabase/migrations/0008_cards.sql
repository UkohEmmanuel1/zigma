CREATE TABLE IF NOT EXISTS bank_cards (
    id                  UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id             UUID            NOT NULL REFERENCES users(id),
    provider            TEXT            NOT NULL,
    provider_card_id    TEXT            NOT NULL,
    last4               TEXT            NOT NULL,
    expiry_month        INT,
    expiry_year         INT,
    brand               TEXT,
    status              TEXT            NOT NULL DEFAULT 'ACTIVE',
    daily_limit_cents   BIGINT,
    monthly_limit_cents BIGINT,
    online_enabled      BOOLEAN         NOT NULL DEFAULT TRUE,
    atm_enabled         BOOLEAN         NOT NULL DEFAULT FALSE,
    metadata            JSONB,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

ALTER TABLE bank_cards ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users read own cards"
    ON bank_cards FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users insert own cards"
    ON bank_cards FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users update own cards"
    ON bank_cards FOR UPDATE
    USING (auth.uid() = user_id);
