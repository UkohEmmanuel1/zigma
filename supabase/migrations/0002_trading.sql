CREATE TABLE IF NOT EXISTS trading_orders (
    id              UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID            NOT NULL REFERENCES users(id),
    symbol          TEXT            NOT NULL,
    side            TEXT            NOT NULL CHECK (side IN ('buy', 'sell')),
    order_type      TEXT            NOT NULL CHECK (order_type IN ('market', 'limit', 'stop')),
    quantity        NUMERIC(20,8)   NOT NULL,
    price           NUMERIC(20,2),
    stop_price      NUMERIC(20,2),
    filled_quantity NUMERIC(20,8)   NOT NULL DEFAULT 0,
    status          TEXT            NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trading_holdings (
    id              UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         UUID            NOT NULL REFERENCES users(id),
    symbol          TEXT            NOT NULL,
    quantity        NUMERIC(20,8)   NOT NULL,
    avg_entry_price NUMERIC(20,2)   NOT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, symbol)
);

ALTER TABLE trading_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_holdings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users read own orders"
    ON trading_orders FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users insert orders"
    ON trading_orders FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Server update orders"
    ON trading_orders FOR UPDATE
    USING (auth.role() = 'service_role');

CREATE POLICY "Users read own holdings"
    ON trading_holdings FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Server manage holdings"
    ON trading_holdings FOR ALL
    USING (auth.role() = 'service_role');
