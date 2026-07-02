"""Shared paths/config. The DuckDB lives in a writable scratch dir during the
build/run (the project mount blocks file deletes, which DuckDB needs for its
WAL). At packaging time a clean copy is placed in the project folder."""
import os

# Project root (…./contextguard)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# DB path: override with env CG_DB. Default to a writable scratch location.
DB_PATH = os.environ.get("CG_DB", os.path.join(ROOT, "data", "pharma_warehouse.duckdb"))

REGISTRY_DIR = os.path.join(ROOT, "registry")
SEMANTIC_MAP = os.path.join(REGISTRY_DIR, "semantic_map.yaml")
GOLDEN_QS = os.path.join(REGISTRY_DIR, "golden_questions.yaml")

import datetime as _dt
# Reference "now" for freshness checks (matches the synthetic warehouse load times).
NOW = _dt.datetime(2026, 6, 18, 9, 0, 0)
