CREATE TABLE IF NOT EXISTS ai_chat_sessions (
    id          UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     UUID        NOT NULL REFERENCES users(id),
    title       TEXT        NOT NULL DEFAULT 'New Chat',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_messages (
    id          UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id  UUID        NOT NULL REFERENCES ai_chat_sessions(id) ON DELETE CASCADE,
    role        TEXT        NOT NULL,
    content     TEXT        NOT NULL,
    metadata    JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_messages_session
    ON ai_messages (session_id, created_at);

ALTER TABLE ai_chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own sessions"
    ON ai_chat_sessions FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Users manage own messages"
    ON ai_messages FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM ai_chat_sessions s
            WHERE s.id = ai_messages.session_id AND s.user_id = auth.uid()
        )
    );
