CREATE TABLE IF NOT EXISTS notifications (
    id                  UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id             UUID        NOT NULL REFERENCES users(id),
    type                TEXT        NOT NULL,
    title               TEXT        NOT NULL,
    message             TEXT        NOT NULL,
    related_object_type TEXT,
    related_object_id   TEXT,
    is_read             BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_created
    ON notifications (user_id, created_at DESC);

ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users read own notifications"
    ON notifications FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users update own notifications"
    ON notifications FOR UPDATE
    USING (auth.uid() = user_id);
