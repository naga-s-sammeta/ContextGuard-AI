"""
Text-to-SQL generation with THREE engines behind one interface:

  - "governed"      : deterministic, schema-aware builder that uses ONLY the
                      retrieved sub-schema + canonical joins + approved metric
                      filters, then runs a self-verification/repair pass.
                      (Free, offline, reliable -- the default for the demo.)
  - "naive"         : simulates the hallucinating baseline -- ignores retrieval,
                      invents a wrong/missing join, drops required filters, and
                      will happily read an uncertified stale table.
  - "llm" (optional): calls a Featherless-hosted model (OpenAI-compatible) when
                      an API key is present. Same interface; governed self-verify
                      still runs on its output.

The point of the project: the GOVERNED engine is correct because the semantic
map narrowed its context; the NAIVE engine is wrong because it didn't.
"""
import re
from collections import deque

# Brand names recognised in questions (kept in sync with the warehouse).
KNOWN_BRANDS = ["REMICADE", "STELARA", "SIMPONI", "TREMFYA", "XARELTO",
                "RISPERDAL", "INVEGA", "TOPAMAX", "DARZALEX", "IMBRUVICA", "ERLEADA"]
THERAPEUTIC_AREAS = ["Immunology", "Oncology", "Neuroscience", "Cardiovascular"]


class Generation:
    def __init__(self, sql, tables_used, engine, intent=None, notes=None, repaired=False):
        self.sql = sql
        self.tables_used = tables_used
        self.engine = engine
        self.intent = intent or {}
        self.notes = notes or []
        self.repaired = repaired

    def to_dict(self):
        return {
            "sql": self.sql, "tables_used": self.tables_used, "engine": self.engine,
            "intent": self.intent, "notes": self.notes, "repaired": self.repaired,
        }


# --------------------------------------------------------------------------- #
# Intent parsing (shared)
# --------------------------------------------------------------------------- #
def parse_intent(question):
    q = question.lower()
    intent = {"filters": {}, "group_by": None, "kind": None, "metric": None}

    # aggregate vs detail
    if any(w in q for w in ["how many", "count", "number of"]):
        intent["kind"] = "count"
    elif any(w in q for w in ["show", "list", "give me the patient", "patient age",
                              "age, sex", "name", "npi", "details"]):
        intent["kind"] = "detail"
    else:
        intent["kind"] = "sum"

    # metric / measure
    if any(w in q for w in ["revenue", "sales"]):
        intent["metric"] = "net_sales_revenue"
    elif "safety cost" in q or ("cost" in q and "safety" in q) or "settled" in q or "liability" in q:
        intent["metric"] = "settled_safety_cost" if "settled" in q else "total_safety_cost"

    # filters
    for ta in THERAPEUTIC_AREAS:
        if ta.lower() in q:
            intent["filters"]["therapeutic_area"] = ta
    for b in KNOWN_BRANDS:
        if b.lower() in q:
            intent["filters"]["brand_name"] = b
    if "non-serious" in q or "non serious" in q:
        intent["filters"]["outcome"] = "non-serious"
    elif "serious" in q:
        intent["filters"]["outcome"] = "serious"
    if "settled" in q:
        intent["filters"]["status"] = "settled"
    elif "pending" in q:
        intent["filters"]["status"] = "pending"
    m = re.search(r"2026\s*q\s*([12])", q) or re.search(r"\bq([12])\b", q)
    if m:
        intent["filters"]["period"] = "2026Q" + m.group(1)
    if "by region" in q or "per region" in q:
        intent["group_by"] = "region"

    # detail columns (PHI/PII exposure)
    detail_cols = []
    if intent["kind"] == "detail":
        if "age" in q: detail_cols.append("patient_age")
        if "sex" in q or "gender" in q: detail_cols.append("patient_sex")
        if "reaction" in q: detail_cols.append("reaction")
        if "name" in q: detail_cols.append("prescriber_name")
        if "npi" in q: detail_cols.append("npi")
    intent["detail_cols"] = detail_cols
    return intent


# --------------------------------------------------------------------------- #
# Join graph helpers (over the canonical joins in the semantic map)
# --------------------------------------------------------------------------- #
def _build_graph(registry):
    g = {}
    edge = {}
    for j in registry.joins:
        g.setdefault(j["left"], set()).add(j["right"])
        g.setdefault(j["right"], set()).add(j["left"])
        edge[(j["left"], j["right"])] = (j["left_key"], j["right_key"])
        edge[(j["right"], j["left"])] = (j["right_key"], j["left_key"])
    return g, edge


def _path(graph, src, dst):
    if src == dst:
        return [src]
    seen = {src}
    q = deque([[src]])
    while q:
        path = q.popleft()
        for nxt in sorted(graph.get(path[-1], [])):
            if nxt in seen:
                continue
            if nxt == dst:
                return path + [nxt]
            seen.add(nxt)
            q.append(path + [nxt])
    return None


def _alias(table):
    return "".join(w[0] for w in table.replace("gold_", "").replace("silver_", "").split("_"))[:3]


# --------------------------------------------------------------------------- #
# GOVERNED deterministic builder
# --------------------------------------------------------------------------- #
# which table a filter column lives on
COL_TABLE = {
    "therapeutic_area": "gold_products", "brand_name": "gold_products",
    "outcome": "gold_adverse_events", "status": "gold_safety_costs",
    "period": "gold_sales", "region": None,  # region exists on many; resolved to base
    "patient_age": "gold_adverse_events", "patient_sex": "gold_adverse_events",
    "reaction": "gold_adverse_events", "prescriber_name": "gold_prescribers",
    "npi": "gold_prescribers",
}


def _base_table(intent, registry):
    if intent["metric"]:
        return registry.metric(intent["metric"])["certified_table"]
    if intent["kind"] in ("count", "detail"):
        # adverse-event detail/count
        return "gold_adverse_events"
    return "gold_sales"


def _governed(question, intent, registry):
    base = _base_table(intent, registry)
    graph, edge = _build_graph(registry)

    # tables we must reach for filters / detail columns
    needed_cols = dict(intent["filters"])
    for c in intent.get("detail_cols", []):
        needed_cols[c] = None
    target_tables = set()
    for col in needed_cols:
        t = COL_TABLE.get(col)
        if t and t != base:
            target_tables.add(t)

    # build join chain from base to each target
    used = [base]
    joins_sql = []
    for tgt in sorted(target_tables):
        p = _path(graph, base, tgt)
        if not p:
            continue
        for a, b in zip(p, p[1:]):
            if b in used:
                continue
            lk, rk = edge[(a, b)]
            joins_sql.append(f"JOIN {b} {_alias(b)} ON {_alias(a)}.{lk} = {_alias(b)}.{rk}")
            used.append(b)

    # SELECT clause
    metric = registry.metric(intent["metric"]) if intent["metric"] else None
    if intent["kind"] == "count":
        select = "COUNT(*) AS n"
    elif intent["kind"] == "detail":
        cols = intent.get("detail_cols") or ["*"]
        select = ", ".join(f"{_alias(COL_TABLE.get(c, base))}.{c}" for c in cols)
    else:
        measure = "amount" if "safety" in (intent["metric"] or "") else "revenue"
        select = f"ROUND(SUM({_alias(base)}.{measure}), 2) AS value"

    # WHERE clause: question filters + approved metric required filters
    where = []
    for col, val in intent["filters"].items():
        if col == "region":
            continue
        t = COL_TABLE.get(col, base)
        where.append(f"{_alias(t)}.{col} = '{val}'")
    if metric:
        for rf in metric.get("required_filters", []):
            # required filters are like "status = 'settled'"
            colname = rf.split("=")[0].strip()
            if colname not in intent["filters"]:
                t = COL_TABLE.get(colname, base)
                where.append(f"{_alias(t)}.{rf.strip()}")

    # GROUP BY
    group = ""
    grp_select = ""
    if intent["group_by"] == "region":
        grp_select = f"{_alias(base)}.region, "
        group = f"GROUP BY {_alias(base)}.region ORDER BY {_alias(base)}.region"

    sql = f"SELECT {grp_select}{select}\nFROM {base} {_alias(base)}\n" + \
          ("\n".join(joins_sql) + "\n" if joins_sql else "")
    if where:
        sql += "WHERE " + " AND ".join(where) + "\n"
    sql += group
    return Generation(sql.strip(), used, "governed", intent=intent)


# --------------------------------------------------------------------------- #
# Self-verification / repair (governed safety net on top of any SQL)
# --------------------------------------------------------------------------- #
def self_verify(gen, retrieved, registry):
    """
    Lightweight checks before we trust generated SQL:
      - every table referenced must be in the retrieved (allowed) set
      - no cartesian join (ON 1=1)
      - no uncertified silver table
    If a check fails we record it; the governed builder is deterministic so it
    normally passes -- this mostly proves the guard works on LLM output too.
    """
    notes = list(gen.notes)
    allowed = set(retrieved["tables"])
    referenced = set(re.findall(r"\b(gold_\w+|silver_\w+)\b", gen.sql))
    bad = referenced - allowed
    if bad:
        notes.append(f"self-verify: SQL referenced non-retrieved tables {sorted(bad)}")
    if re.search(r"ON\s+1\s*=\s*1", gen.sql, re.I):
        notes.append("self-verify: cartesian join (ON 1=1) detected")
    silver = [t for t in referenced if t.startswith("silver_")]
    if silver:
        notes.append(f"self-verify: uncertified table(s) {silver}")
    gen.notes = notes
    return gen


# --------------------------------------------------------------------------- #
# NAIVE engine -- simulates the hallucinating baseline
# --------------------------------------------------------------------------- #
def _naive(question, intent, registry):
    """No retrieval, no metric discipline. Picks tables by surface keywords,
    invents a join, drops required filters, prefers a stale table if it matches."""
    notes = ["naive: ignored semantic map / retrieval"]

    # revenue/sales -> grab the (uncertified) silver table because it 'looks' like sales
    if intent["metric"] == "net_sales_revenue":
        brand = intent["filters"].get("brand_name")
        period = intent["filters"].get("period")
        where = []
        if brand: where.append(f"p.brand_name = '{brand}'")
        if period: where.append(f"s.period = '{period}'")
        sql = ("SELECT ROUND(SUM(s.revenue),2) AS value\n"
               "FROM silver_sales s\n"
               "JOIN gold_products p ON s.product_id = p.product_id\n"
               + ("WHERE " + " AND ".join(where) if where else ""))
        notes.append("naive: read uncertified silver_sales; dropped freshness/cert checks")
        return Generation(sql.strip(), ["silver_sales", "gold_products"], "naive",
                          intent=intent, notes=notes)

    # safety cost -> cross join products x safety_costs, DROP serious/settled filters
    if intent["metric"] in ("settled_safety_cost", "total_safety_cost"):
        ta = intent["filters"].get("therapeutic_area")
        where = f"WHERE p.therapeutic_area = '{ta}'" if ta else ""
        sql = ("SELECT ROUND(SUM(sc.amount),2) AS value\n"
               "FROM gold_products p\n"
               "JOIN gold_safety_costs sc ON 1=1\n"        # invented / missing join key
               + where)
        notes.append("naive: invented cross join (no key); dropped serious/settled filters")
        return Generation(sql.strip(), ["gold_products", "gold_safety_costs"], "naive",
                          intent=intent, notes=notes)

    # detail / count adverse events -> exposes PHI columns freely
    if intent["kind"] in ("detail", "count"):
        brand = intent["filters"].get("brand_name")
        where = f"WHERE p.brand_name = '{brand}'" if brand else ""
        cols = ", ".join(intent.get("detail_cols") or ["ae.patient_age", "ae.patient_sex", "ae.reaction"])
        cols = ", ".join(c if "." in c else f"ae.{c}" for c in (intent.get("detail_cols") or
                          ["patient_age", "patient_sex", "reaction"]))
        sql = (f"SELECT {cols}\n"
               "FROM gold_adverse_events ae\n"
               "JOIN gold_products p ON ae.product_id = p.product_id\n" + where)
        notes.append("naive: exposed PHI columns with no access check")
        return Generation(sql.strip(), ["gold_adverse_events", "gold_products"], "naive",
                          intent=intent, notes=notes)

    return Generation("SELECT 1", [], "naive", intent=intent, notes=notes)


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #
def generate(question, retrieved, registry, mode="governed", llm=None):
    intent = parse_intent(question)
    if mode == "naive":
        return _naive(question, intent, registry)

    if mode == "llm" and llm is not None:
        sql = llm(question, retrieved, registry)
        gen = Generation(sql, sorted(set(re.findall(r"\b(gold_\w+|silver_\w+)\b", sql))),
                         "llm", intent=intent)
    else:
        gen = _governed(question, intent, registry)

    return self_verify(gen, retrieved, registry)
