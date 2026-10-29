-- REA_INDEPENDENTE independent event ledger; no operational data is shipped with source.
CREATE TABLE IF NOT EXISTS system_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS memory_events (
  seq INTEGER PRIMARY KEY,
  event_id TEXT NOT NULL UNIQUE,
  created_utc TEXT NOT NULL,
  kind TEXT NOT NULL CHECK(kind IN ('DECISION','EVIDENCE','PENDENCY','STATUS','NOTE')),
  subject TEXT NOT NULL CHECK(length(subject) BETWEEN 1 AND 200),
  detail_json TEXT NOT NULL,
  reference TEXT NOT NULL DEFAULT '',
  source_sha256 TEXT NOT NULL DEFAULT '',
  prev_digest TEXT NOT NULL,
  digest TEXT NOT NULL UNIQUE
);
CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON memory_events
BEGIN SELECT RAISE(ABORT,'memory history append only'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON memory_events
BEGIN SELECT RAISE(ABORT,'memory history append only'); END;
CREATE INDEX IF NOT EXISTS idx_memory_kind ON memory_events(kind);
