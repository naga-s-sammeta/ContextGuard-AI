"""
ContextGuard -- the governance layer. Evaluates an AI-generated answer BEFORE it
reaches a human and returns one of three verdicts:

    PASS     - certified source, fresh, approved metric, no PHI/PII leak, correct
    FLAGGED  - answer is usable but something needs attention (e.g. number drifts
               from the certified value, or a soft policy issue)
    BLOCKED  - a hard governance violation: uncertified/stale source, PHI/PII
               exposure for this role, unsafe SQL, wrong metric logic, or a
               result that contradicts the certified figure

Each verdict carries a per-gate breakdown and, when blocking, the CERTIFIED
answer computed from governed Gold tables. Every evaluation is returned in a
shape ready to be logged to an audit trail (feeds the dashboard).
"""
import re
import datetime as dt
from config import NOW
from db import table_last_loaded

PASS, FLAGGED, BLOCKED = "PASS", "FLAGGED", "BLOCKED"


def _referenced_tables(sql):
    return sorted(set(re.findall(r"\b(gold_\w+|silver_\w+)\b", sql)))


def _scalar(result):
    """Return a single numeric value if the result is 1 row x 1 column, else None."""
    if result is None:
        return None
    if isinstance(result, (list, tuple)):
        if len(result) != 1:
            return None
        row = result[0]
        if isinstance(row, (list, tuple)):
            return row[0] if len(row) == 1 else None
        return row
    return result


class Gate:
    def __init__(self, name, status, detail):
        self.name = name        # gate label
        self.status = status    # "pass" | "fail" | "warn" | "n/a"
        self.detail = detail

    def to_dict(self):
        return {"name": self.name, "status": self.status, "detail": self.detail}


class Guard:
    def __init__(self, registry):
        self.reg = registry

    # -- individual gates ----------------------------------------------------
    def _gate_certified(self, tables):
        bad = [t for t in tables if not self.reg.is_certified(t)]
        if bad:
            return Gate("Certified source", "fail",
                        f"Uses uncertified table(s): {', '.join(bad)}")
        return Gate("Certified source", "pass", "All sources are certified Gold tables")

    def _gate_freshness(self, tables):
        stale = []
        for t in tables:
            last, sla = table_last_loaded(t)
            if last is None:
                continue
            age_h = (NOW - last).total_seconds() / 3600.0
            if sla is not None and age_h > sla:
                stale.append(f"{t} ({age_h:.0f}h old, SLA {sla}h)")
        if stale:
            return Gate("Data freshness", "fail", "Stale beyond SLA: " + "; ".join(stale))
        return Gate("Data freshness", "pass", "All sources within freshness SLA")

    def _gate_phi_pii(self, sql, tables, role):
        rolecfg = self.reg.role(role) or {}
        deny_phi = rolecfg.get("deny_phi", True)
        deny_pii = rolecfg.get("deny_pii", True)
        exposed = []
        for t in tables:
            for col in self.reg.sensitive_columns(t, phi=deny_phi, pii=deny_pii):
                # column referenced in SQL?
                if re.search(rf"\b{re.escape(col)}\b", sql):
                    meta = self.reg.table(t)["columns"][col]
                    kind = "PHI" if meta.get("phi") else "PII"
                    exposed.append(f"{col} ({kind})")
        if exposed:
            return Gate("PHI/PII access", "fail",
                        f"Role '{role}' may not see: {', '.join(sorted(set(exposed)))}")
        return Gate("PHI/PII access", "pass", f"No PHI/PII exposed to role '{role}'")

    def _gate_sql_safety(self, sql):
        if re.search(r"\b(drop|delete|update|insert|alter|truncate|grant)\b", sql, re.I):
            return Gate("SQL safety", "fail", "Contains a data-modifying / DDL statement")
        if re.search(r"on\s+1\s*=\s*1", sql, re.I) or re.search(r"\bcross\s+join\b", sql, re.I):
            return Gate("SQL safety", "fail", "Cartesian join (no join key) — logically invalid")
        return Gate("SQL safety", "pass", "Read-only, properly joined query")

    def _gate_metric(self, intent, sql, tables):
        mname = intent.get("metric")
        if not mname:
            return Gate("Approved metric", "n/a", "No standard metric in this question")
        metric = self.reg.metric(mname)
        if metric["certified_table"] not in tables:
            return Gate("Approved metric", "fail",
                        f"Metric '{mname}' must use {metric['certified_table']}")
        missing = []
        for rf in metric.get("required_filters", []):
            col = rf.split("=")[0].strip()
            if not re.search(rf"\b{re.escape(col)}\b", sql):
                missing.append(rf)
        if missing:
            return Gate("Approved metric", "fail",
                        f"Missing required filter(s): {', '.join(missing)}")
        return Gate("Approved metric", "pass", f"Matches approved definition of '{mname}'")

    def _gate_rls(self, sql, role):
        rolecfg = self.reg.role(role) or {}
        rf = rolecfg.get("row_filter")
        if not rf:
            return Gate("Row-level security", "n/a", "No row restriction for this role")
        norm = re.sub(r"\s+", "", sql.lower())
        target = re.sub(r"\s+", "", rf.lower())
        if target in norm:
            return Gate("Row-level security", "pass", f"Row filter applied: {rf}")
        return Gate("Row-level security", "fail",
                    f"Role '{role}' requires row filter [{rf}] which was not applied")

    def _gate_consistency(self, candidate_result, governed_result):
        cv, gv = _scalar(candidate_result), _scalar(governed_result)
        if not isinstance(cv, (int, float)) or not isinstance(gv, (int, float)):
            return Gate("Result consistency", "n/a", "Not a single-value answer"), 0.0
        if gv == 0:
            same = (cv == 0)
        else:
            same = abs(cv - gv) / abs(gv) <= 0.001
        if same:
            return Gate("Result consistency", "pass",
                        f"Matches certified value ({gv:,.2f})"), 0.0
        return (Gate("Result consistency", "fail",
                     f"Answer {cv:,.2f} vs certified {gv:,.2f}"), abs(cv - gv))

    # -- main ----------------------------------------------------------------
    def evaluate(self, question, candidate_gen, candidate_result,
                 role, governed_result=None):
        tables = candidate_gen.tables_used or _referenced_tables(candidate_gen.sql)
        intent = getattr(candidate_gen, "intent", {}) or {}

        hard_gates = [
            self._gate_certified(tables),
            self._gate_freshness(tables),
            self._gate_phi_pii(candidate_gen.sql, tables, role),
            self._gate_sql_safety(candidate_gen.sql),
            self._gate_metric(intent, candidate_gen.sql, tables),
            self._gate_rls(candidate_gen.sql, role),
        ]
        consistency, risk = self._gate_consistency(candidate_result, governed_result)
        gates = hard_gates + [consistency]

        hard_fail = any(g.status == "fail" for g in hard_gates)
        soft_fail = consistency.status == "fail"

        if hard_fail:
            verdict = BLOCKED
        elif soft_fail:
            verdict = FLAGGED
        else:
            verdict = PASS

        failed = [g.name for g in gates if g.status == "fail"]
        return {
            "verdict": verdict,
            "role": role,
            "question": question,
            "candidate_sql": candidate_gen.sql,
            "candidate_engine": candidate_gen.engine,
            "candidate_result": _display(candidate_result),
            "certified_result": _display(governed_result),
            "gates": [g.to_dict() for g in gates],
            "failed_gates": failed,
            "risk_amount": round(risk, 2),
            "ts": dt.datetime.now().isoformat(timespec="seconds"),
        }


def _display(result):
    """Make a result JSON-friendly and human-readable."""
    if result is None:
        return None
    if isinstance(result, (list, tuple)) and result and isinstance(result[0], (list, tuple)):
        return [list(r) for r in result]
    if isinstance(result, (list, tuple)):
        return list(result)
    return result
