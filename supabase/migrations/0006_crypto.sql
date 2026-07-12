CREATE TABLE IF NOT EXISTS crypto_wallets (
    id              UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID            NOT NULL REFERENCES users(id),
    currency        TEXT            NOT NULL,
    balance         NUMERIC(38,18)  NOT NULL DEFAULT 0,
    address         TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, currency)
);

CREATE TABLE IF NOT EXISTS crypto_orders (
    id              UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID            NOT NULL REFERENCES users(id),
    symbol          TEXT            NOT NULL,
    side            TEXT            NOT NULL CHECK (side IN ('BUY', 'SELL')),
    order_type      TEXT            NOT NULL CHECK (order_type IN ('MARKET', 'LIMIT')),
    quantity        NUMERIC(38,18)  NOT NULL,
    price           NUMERIC(38,18),
    filled_quantity NUMERIC(38,18)  NOT NULL DEFAULT 0,
    status          TEXT            NOT NULL DEFAULT 'PENDING',
    is_paper        BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    executed_at     TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS crypto_holdings (
    id              UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID            NOT NULL REFERENCES users(id),
    symbol          TEXT            NOT NULL,
    quantity        NUMERIC(38,18)  NOT NULL DEFAULT 0,
    avg_entry_price NUMERIC(38,18),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, symbol)
);

CREATE TABLE IF NOT EXISTS crypto_swaps (
    id              UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID            NOT NULL REFERENCES users(id),
    from_currency   TEXT            NOT NULL,
    to_currency     TEXT            NOT NULL,
    from_amount     NUMERIC(38,18)  NOT NULL,
    to_amount       NUMERIC(38,18),
    rate            NUMERIC(38,18),
    status          TEXT            NOT NULL DEFAULT 'PENDING',
    is_paper        BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    executed_at     TIMESTAMPTZ
);

ALTER TABLE crypto_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE crypto_swaps ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users read own crypto wallets"
    ON crypto_wallets FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users read own crypto orders"
    ON crypto_orders FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users insert crypto orders"
    ON crypto_orders FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users read own crypto holdings"
    ON crypto_holdings FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users read own crypto swaps"
    ON crypto_swaps FOR SELECT
    USING (auth.uid() = user_id);
