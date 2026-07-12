CREATE TABLE IF NOT EXISTS bank_accounts (
    id                  UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id             UUID            NOT NULL REFERENCES users(id),
    account_number      TEXT            UNIQUE,
    routing_number      TEXT,
    provider            TEXT,
    provider_account_id TEXT,
    balance_cents       BIGINT          NOT NULL DEFAULT 0,
    status              TEXT            NOT NULL DEFAULT 'ACTIVE',
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bank_transactions (
    id                  UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    account_id          UUID            NOT NULL REFERENCES bank_accounts(id) ON DELETE CASCADE,
    type                TEXT            NOT NULL,
    amount_cents        BIGINT          NOT NULL,
    balance_after_cents BIGINT          NOT NULL,
    description         TEXT,
    reference           TEXT,
    status              TEXT            NOT NULL DEFAULT 'COMPLETED',
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

ALTER TABLE bank_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE bank_transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users read own bank accounts"
    ON bank_accounts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users read own bank transactions"
    ON bank_transactions FOR SELECT
    USING (account_id IN (SELECT id FROM bank_accounts WHERE user_id = auth.uid()));
