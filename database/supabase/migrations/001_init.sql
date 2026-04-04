-- ============================================================
-- SABIQ Database Schema
-- Road Damage Detection System
-- ============================================================

-- جدول الكشوفات
CREATE TABLE detections (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at  TIMESTAMPTZ DEFAULT now(),
    damage_type TEXT CHECK (damage_type IN ('crack', 'pothole', 'other')),
    confidence  FLOAT,
    severity    TEXT DEFAULT 'low',
    latitude    FLOAT,
    longitude   FLOAT,
    google_maps_url TEXT GENERATED ALWAYS AS (
        'https://www.google.com/maps?q=' || latitude::text || ',' || longitude::text
    ) STORED
);

-- جدول التقارير
CREATE TABLE reports (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at   TIMESTAMPTZ DEFAULT now(),
    detection_id UUID REFERENCES detections(id) ON DELETE CASCADE,
    reported_at  TIMESTAMPTZ,
    report_type  TEXT,
    notes        TEXT
);

-- الأمان
ALTER TABLE detections ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports    ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow all" ON detections FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow all" ON reports    FOR ALL USING (true) WITH CHECK (true);

