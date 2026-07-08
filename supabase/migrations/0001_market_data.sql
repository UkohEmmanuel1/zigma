CREATE TABLE IF NOT EXISTS market_quotes (
    id         UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    symbol     TEXT        NOT NULL,
    bid        NUMERIC,
    ask        NUMERIC,
    last       NUMERIC,
    volume     NUMERIC,
    timestamp  TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_market_quotes_symbol ON market_quotes (symbol);

ALTER TABLE market_quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read access for market_quotes"
    ON market_quotes FOR SELECT USING (true);

CREATE POLICY "Public read access for price_history"
    ON price_history FOR SELECT USING (true);
