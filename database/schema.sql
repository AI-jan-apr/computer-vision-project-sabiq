CREATE TABLE detections (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at  TIMESTAMPTZ DEFAULT now(),
    image_name  TEXT,
    damage_type TEXT CHECK (damage_type IN ('crack','pothole','other')),
    confidence  FLOAT,
    severity    TEXT DEFAULT 'low',
    latitude    FLOAT,
    longitude   FLOAT,
    bbox_x      FLOAT,
    bbox_y      FLOAT,
    bbox_w      FLOAT,
    bbox_h      FLOAT,
    status      TEXT DEFAULT 'pending',
    reported_to TEXT DEFAULT 'أمانة الرياض',
    notes       TEXT
);

CREATE TABLE reports (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at   TIMESTAMPTZ DEFAULT now(),
    detection_id UUID REFERENCES detections(id) ON DELETE CASCADE,
    reported_at  TIMESTAMPTZ,
    report_type  TEXT,
    notes        TEXT
);

ALTER TABLE detections ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "allow all" ON detections FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow all" ON reports FOR ALL USING (true) WITH CHECK (true);

