"""
Generate a synthetic PHARMA warehouse in DuckDB
for the ContextGuard demo.

Statement 1 says the data "may contain PHI, PII, or confidential business
information." A drug-safety + commercial pharma warehouse hits all three:
  - PHI  : patient age / sex / reaction in adverse-event reports (FAERS-style)
  - PII  : prescriber name + NPI
  - CONF : product sales revenue and legal safety-cost / settlement amounts

Brand names are REAL marketed drugs and reactions are REAL terms from the
openFDA FAERS API (api.fda.gov, free/public). All facts (patients, amounts,
dates) are SYNTHETIC and deterministic (fixed seed). No real patient/financial
data is used.
"""
import os
import random
import datetime as dt
import duckdb

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from config import DB_PATH

random.seed(42)

REGIONS = ["North", "South", "East", "West"]

# Real marketed drug brand names (from openFDA) mapped to therapeutic areas.
PRODUCTS = [
    ("REMICADE",  "infliximab",   "Immunology"),
    ("STELARA",   "ustekinumab",  "Immunology"),
    ("SIMPONI",   "golimumab",    "Immunology"),
    ("TREMFYA",   "guselkumab",   "Immunology"),
    ("XARELTO",   "rivaroxaban",  "Cardiovascular"),
    ("RISPERDAL", "risperidone",  "Neuroscience"),
    ("INVEGA",    "paliperidone", "Neuroscience"),
    ("TOPAMAX",   "topiramate",   "Neuroscience"),
    ("DARZALEX",  "daratumumab",  "Oncology"),
    ("IMBRUVICA", "ibrutinib",    "Oncology"),
    ("ERLEADA",   "apalutamide",  "Oncology"),
]

# Real FAERS reaction terms (from openFDA).
REACTIONS = [
    "DRUG INEFFECTIVE", "OFF LABEL USE", "FATIGUE", "PAIN", "NAUSEA",
    "HEADACHE", "DIARRHOEA", "ARTHRALGIA", "CONDITION AGGRAVATED",
    "DYSPNOEA", "RASH",
]
SPECIALTIES = ["Rheumatology", "Cardiology", "Psychiatry", "Oncology", "Dermatology"]
SEXES = ["M", "F"]


def build():
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
    except OSError:
        pass  # mount may block delete; CREATE OR REPLACE handles reruns
    con = duckdb.connect(DB_PATH)

    # ---- gold_products (dimension) ----
    products = [(i + 1, b, g, ta, "Synthetic Pharma Co") for i, (b, g, ta) in enumerate(PRODUCTS)]
    con.execute("""CREATE OR REPLACE TABLE gold_products(
        product_id INT, brand_name VARCHAR, generic_name VARCHAR,
        therapeutic_area VARCHAR, manufacturer VARCHAR)""")
    con.executemany("INSERT INTO gold_products VALUES (?,?,?,?,?)", products)

    # ---- gold_prescribers (dimension, PII) ----
    prescribers = []
    for pid in range(1, 41):
        prescribers.append((
            pid,
            "Dr. " + random.choice(["Rao", "Mehta", "Khan", "Iyer", "Nair", "Das", "Bose", "Shah", "Patel", "Reddy"]),
            str(random.randint(1000000000, 1999999999)),   # NPI (PII)
            random.choice(SPECIALTIES),
            random.choice(REGIONS),
        ))
    con.execute("""CREATE OR REPLACE TABLE gold_prescribers(
        prescriber_id INT, prescriber_name VARCHAR, npi VARCHAR,
        specialty VARCHAR, region VARCHAR)""")
    con.executemany("INSERT INTO gold_prescribers VALUES (?,?,?,?,?)", prescribers)

    # ---- gold_adverse_events (fact, PHI) ----
    events = []
    eid = 1
    base = dt.date(2026, 1, 1)
    for _ in range(2000):
        product_id = random.randint(1, len(PRODUCTS))
        prescriber_id = random.randint(1, 40)
        region = random.choice(REGIONS)
        outcome = "serious" if random.random() < 0.30 else "non-serious"
        events.append((
            eid, product_id, prescriber_id, region,
            random.randint(18, 89),               # patient_age (PHI)
            random.choice(SEXES),                  # patient_sex (PHI)
            random.choice(REACTIONS),              # reaction (PHI)
            outcome,
            base + dt.timedelta(days=random.randint(0, 100)),
        ))
        eid += 1
    con.execute("""CREATE OR REPLACE TABLE gold_adverse_events(
        event_id INT, product_id INT, prescriber_id INT, region VARCHAR,
        patient_age INT, patient_sex VARCHAR, reaction VARCHAR,
        outcome VARCHAR, report_date DATE)""")
    con.executemany("INSERT INTO gold_adverse_events VALUES (?,?,?,?,?,?,?,?,?)", events)

    # ---- gold_safety_costs (fact, confidential): legal/remediation cost per serious event ----
    costs = []
    cid = 1
    for e in events:
        if e[7] == "serious" and random.random() < 0.8:
            amount = round(random.uniform(5000, 250000), 2)
            status = "settled" if random.random() < 0.6 else "pending"
            costs.append((cid, e[0], e[3], amount, status))   # cost_id, event_id, region, amount, status
            cid += 1
    con.execute("""CREATE OR REPLACE TABLE gold_safety_costs(
        cost_id INT, event_id INT, region VARCHAR,
        amount DOUBLE, status VARCHAR)""")
    con.executemany("INSERT INTO gold_safety_costs VALUES (?,?,?,?,?)", costs)

    # ---- gold_sales (fact, confidential) ----
    sales = []
    sid = 1
    for product_id in range(1, len(PRODUCTS) + 1):
        for region in REGIONS:
            for q in ["2026Q1", "2026Q2"]:
                units = random.randint(500, 8000)
                revenue = round(units * random.uniform(80, 1200), 2)
                sales.append((sid, product_id, region, q, units, revenue))
                sid += 1
    con.execute("""CREATE OR REPLACE TABLE gold_sales(
        sale_id INT, product_id INT, region VARCHAR, period VARCHAR,
        units INT, revenue DOUBLE)""")
    con.executemany("INSERT INTO gold_sales VALUES (?,?,?,?,?,?)", sales)

    # ---- STALE silver copies (uncertified) for the freshness catch ----
    # silver = an OLDER ETL snapshot: understated revenue, missing the latest
    # period, and a partial cost load. Deterministic so the demo never drifts.
    con.execute("CREATE OR REPLACE TABLE silver_safety_costs AS "
                "SELECT * FROM gold_safety_costs WHERE cost_id % 3 <> 0")  # ~1/3 missing
    con.execute("CREATE OR REPLACE TABLE silver_sales AS "
                "SELECT sale_id, product_id, region, period, units, "
                "ROUND(revenue*0.6,2) AS revenue "             # understated older snapshot
                "FROM gold_sales WHERE period = '2026Q1'")     # Q2 not yet loaded

    # ---- freshness metadata ----
    con.execute("CREATE OR REPLACE TABLE _table_freshness(table_name VARCHAR, last_loaded TIMESTAMP, sla_hours INT)")
    now = dt.datetime(2026, 6, 18, 9, 0, 0)
    con.executemany("INSERT INTO _table_freshness VALUES (?,?,?)", [
        ("gold_products",       now - dt.timedelta(hours=6),   24),
        ("gold_prescribers",    now - dt.timedelta(hours=6),   24),
        ("gold_adverse_events", now - dt.timedelta(hours=4),   24),
        ("gold_safety_costs",   now - dt.timedelta(hours=3),   24),   # fresh
        ("gold_sales",          now - dt.timedelta(hours=2),   24),   # fresh
        ("silver_safety_costs", now - dt.timedelta(hours=240), 24),   # STALE: 10 days
        ("silver_sales",        now - dt.timedelta(hours=192), 24),   # STALE: 8 days
    ])

    con.close()
    print("Built warehouse at", DB_PATH)
    _summary()


def _summary():
    con = duckdb.connect(DB_PATH, read_only=True)
    for t in ["gold_products", "gold_prescribers", "gold_adverse_events",
              "gold_safety_costs", "gold_sales", "silver_safety_costs", "silver_sales"]:
        n = con.execute("SELECT count(*) FROM " + t).fetchone()[0]
        print("  %-20s %6d rows" % (t, n))
    con.close()


if __name__ == "__main__":
    build()
