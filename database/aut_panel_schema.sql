PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS panels (
  panel_id TEXT NOT NULL,
  revision TEXT NOT NULL,
  title TEXT,
  role TEXT,
  engineering_status TEXT NOT NULL DEFAULT 'HOLD',
  enclosure_width_mm REAL,
  enclosure_height_mm REAL,
  enclosure_depth_mm REAL,
  workbook_template_id TEXT,
  image_template_id TEXT,
  created_at TEXT NOT NULL,
  PRIMARY KEY (panel_id, revision)
);

CREATE TABLE IF NOT EXISTS components (
  component_id TEXT PRIMARY KEY,
  manufacturer TEXT,
  family TEXT,
  model TEXT,
  category TEXT,
  lifecycle_status TEXT,
  engineering_status TEXT,
  width_mm REAL,
  height_mm REAL,
  depth_mm REAL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
  source_id TEXT PRIMARY KEY,
  component_id TEXT,
  equipment TEXT,
  manufacturer TEXT,
  model_family TEXT,
  document_type TEXT,
  title TEXT,
  document_code TEXT,
  revision TEXT,
  publication_date TEXT,
  language TEXT,
  official_url TEXT,
  direct_url TEXT,
  consultation_date TEXT,
  lifecycle_status TEXT,
  application TEXT,
  page_section TEXT,
  notes TEXT,
  validator_a_status TEXT,
  validator_b_status TEXT,
  reverification_at TEXT,
  FOREIGN KEY (component_id) REFERENCES components(component_id)
);

CREATE TABLE IF NOT EXISTS suppliers (
  supplier_id TEXT PRIMARY KEY,
  component_id TEXT,
  company TEXT NOT NULL,
  region TEXT,
  channel_type TEXT,
  official_url TEXT,
  product_url TEXT,
  support_url TEXT,
  verified_at TEXT,
  FOREIGN KEY (component_id) REFERENCES components(component_id)
);

CREATE TABLE IF NOT EXISTS panel_components (
  panel_id TEXT NOT NULL,
  panel_revision TEXT NOT NULL,
  instance_tag TEXT NOT NULL,
  component_id TEXT NOT NULL,
  quantity INTEGER NOT NULL CHECK(quantity > 0),
  unit TEXT NOT NULL DEFAULT 'un',
  surface TEXT,
  engineering_status TEXT NOT NULL,
  source_id TEXT,
  PRIMARY KEY (panel_id, panel_revision, instance_tag),
  FOREIGN KEY (panel_id, panel_revision) REFERENCES panels(panel_id, revision),
  FOREIGN KEY (component_id) REFERENCES components(component_id),
  FOREIGN KEY (source_id) REFERENCES sources(source_id)
);

CREATE TABLE IF NOT EXISTS io_points (
  io_id INTEGER PRIMARY KEY AUTOINCREMENT,
  panel_id TEXT NOT NULL,
  panel_revision TEXT NOT NULL,
  tag TEXT NOT NULL,
  signal_type TEXT NOT NULL,
  controller TEXT,
  address TEXT,
  protocol TEXT,
  network_entity INTEGER NOT NULL DEFAULT 0,
  source_id TEXT,
  UNIQUE(panel_id, panel_revision, tag),
  FOREIGN KEY (panel_id, panel_revision) REFERENCES panels(panel_id, revision),
  FOREIGN KEY (source_id) REFERENCES sources(source_id)
);

CREATE TABLE IF NOT EXISTS agent_runs (
  run_id TEXT PRIMARY KEY,
  agent_id TEXT NOT NULL,
  panel_id TEXT,
  panel_revision TEXT,
  stage TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL,
  input_fingerprint TEXT,
  output_fingerprint TEXT,
  metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS memory_events (
  event_id TEXT PRIMARY KEY,
  agent_id TEXT NOT NULL,
  panel_id TEXT,
  panel_revision TEXT,
  event_type TEXT NOT NULL,
  event_at TEXT NOT NULL,
  summary TEXT NOT NULL,
  evidence_json TEXT,
  immutable_history INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS qa_runs (
  qa_run_id TEXT PRIMARY KEY,
  panel_id TEXT,
  panel_revision TEXT,
  artifact_revision TEXT,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL,
  deterministic_status TEXT,
  ml_risk_score REAL,
  manifest_sha256 TEXT
);

CREATE TABLE IF NOT EXISTS qa_findings (
  finding_id TEXT PRIMARY KEY,
  qa_run_id TEXT NOT NULL,
  rule_id TEXT,
  severity TEXT NOT NULL,
  category TEXT NOT NULL,
  message TEXT NOT NULL,
  artifact_path TEXT,
  evidence_json TEXT,
  disposition TEXT,
  FOREIGN KEY (qa_run_id) REFERENCES qa_runs(qa_run_id)
);

CREATE TABLE IF NOT EXISTS render_metrics (
  metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
  panel_id TEXT NOT NULL,
  panel_revision TEXT NOT NULL,
  artifact_sha256 TEXT NOT NULL,
  fill_ratio REAL,
  overlap_count INTEGER,
  min_clearance_mm REAL,
  template_diff_score REAL,
  label_readability_score REAL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS training_examples (
  example_id TEXT PRIMARY KEY,
  panel_id TEXT,
  panel_revision TEXT,
  qa_run_id TEXT,
  features_json TEXT NOT NULL,
  label TEXT NOT NULL,
  label_source TEXT NOT NULL,
  reviewed_by_human INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  FOREIGN KEY (qa_run_id) REFERENCES qa_runs(qa_run_id)
);

CREATE TABLE IF NOT EXISTS model_registry (
  model_id TEXT PRIMARY KEY,
  model_type TEXT NOT NULL,
  dataset_fingerprint TEXT NOT NULL,
  feature_schema_version TEXT NOT NULL,
  trained_at TEXT NOT NULL,
  metrics_json TEXT NOT NULL,
  artifact_path TEXT,
  status TEXT NOT NULL,
  approved_for_advisory_use INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS evolution_proposals (
  proposal_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  source_model_id TEXT,
  problem TEXT NOT NULL,
  evidence_json TEXT NOT NULL,
  candidate_change_json TEXT NOT NULL,
  affected_files_json TEXT NOT NULL,
  expected_benefit TEXT,
  risk TEXT NOT NULL,
  tests_json TEXT NOT NULL,
  rollback_plan TEXT NOT NULL,
  confidence REAL,
  requires_human_approval INTEGER NOT NULL DEFAULT 1,
  approval_status TEXT NOT NULL DEFAULT 'PENDING',
  applied_commit_sha TEXT,
  FOREIGN KEY (source_model_id) REFERENCES model_registry(model_id)
);

CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id TEXT PRIMARY KEY,
  panel_id TEXT,
  panel_revision TEXT,
  artifact_type TEXT NOT NULL,
  path TEXT NOT NULL,
  sha256 TEXT,
  created_at TEXT NOT NULL,
  status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plugin_registry (
  plugin_id TEXT PRIMARY KEY,
  repository TEXT NOT NULL,
  role_json TEXT NOT NULL,
  status TEXT NOT NULL,
  pinned_version TEXT,
  license_status TEXT,
  security_review_status TEXT,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skill_registry (
  skill_id TEXT PRIMARY KEY,
  path TEXT NOT NULL,
  version TEXT NOT NULL,
  status TEXT NOT NULL,
  sha256 TEXT,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sources_component ON sources(component_id);
CREATE INDEX IF NOT EXISTS idx_panel_components_component ON panel_components(component_id);
CREATE INDEX IF NOT EXISTS idx_qa_findings_run ON qa_findings(qa_run_id);
CREATE INDEX IF NOT EXISTS idx_training_examples_panel ON training_examples(panel_id, panel_revision);
CREATE INDEX IF NOT EXISTS idx_memory_events_panel ON memory_events(panel_id, panel_revision);
