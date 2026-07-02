"""Load and expose the semantic map + golden questions."""
import os
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REG_DIR = os.path.join(ROOT, "registry")


class Registry:
    def __init__(self, semantic_path=None, golden_path=None):
        semantic_path = semantic_path or os.path.join(REG_DIR, "semantic_map.yaml")
        golden_path = golden_path or os.path.join(REG_DIR, "golden_questions.yaml")
        with open(semantic_path) as f:
            self.map = yaml.safe_load(f)
        with open(golden_path) as f:
            self.golden = yaml.safe_load(f)

    # ---- tables ----
    @property
    def tables(self):
        return self.map["tables"]

    def table(self, name):
        return self.map["tables"].get(name)

    def is_certified(self, name):
        t = self.table(name)
        return bool(t and t.get("certified"))

    def sensitive_columns(self, name, phi=True, pii=True):
        """Return column names flagged PHI and/or PII for a table."""
        t = self.table(name) or {}
        out = []
        for col, meta in t.get("columns", {}).items():
            if (phi and meta.get("phi")) or (pii and meta.get("pii")):
                out.append(col)
        return out

    # ---- joins / metrics / roles ----
    @property
    def joins(self):
        return self.map.get("joins", [])

    @property
    def metrics(self):
        return self.map.get("metrics", {})

    def metric(self, name):
        return self.map.get("metrics", {}).get(name)

    @property
    def roles(self):
        return self.map.get("roles", {})

    def role(self, name):
        return self.map.get("roles", {}).get(name)

    # ---- golden ----
    def golden_by_id(self, qid):
        for g in self.golden:
            if g["id"] == qid:
                return g
        return None
