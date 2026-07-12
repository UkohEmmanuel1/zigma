CREATE TABLE IF NOT EXISTS wallets (
    id              UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID            NOT NULL REFERENCES users(id) UNIQUE,
    balance_cents   BIGINT          NOT NULL DEFAULT 0,
    currency        TEXT            NOT NULL DEFAULT 'USD',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    id                  UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    wallet_id           UUID            NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    type                TEXT            NOT NULL,
    amount_cents        BIGINT          NOT NULL,
    balance_after_cents BIGINT          NOT NULL,
    status              TEXT            NOT NULL DEFAULT 'COMPLETED',
    reference           TEXT,
    description         TEXT,
    metadata            JSONB,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS p2p_transfers (
    id              UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    sender_id       UUID            NOT NULL REFERENCES users(id),
    recipient_id    UUID            NOT NULL REFERENCES users(id),
    amount_cents    BIGINT          NOT NULL,
    note            TEXT,
    status          TEXT            NOT NULL DEFAULT 'COMPLETED',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

ALTER TABLE wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE p2p_transfers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users read own wallet"
    ON wallets FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users read own transactions"
    ON transactions FOR SELECT
    USING (wallet_id IN (SELECT id FROM wallets WHERE user_id = auth.uid()));

CREATE POLICY "Users read own p2p"
    ON p2p_transfers FOR SELECT
    USING (auth.uid() = sender_id OR auth.uid() = recipient_id);
