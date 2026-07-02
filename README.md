# ContextGuard

**Trustworthy AI answers over governed enterprise data.**
Statement 1 · Track #10 Security & Guardrails · demoed on synthetic pharmaceutical data.

Business users ask questions in natural language across many tables. Today's text-to-SQL works at ~80% with one or two tables but **hallucinates as more tables are added** — wrong joins, dropped filters — and the underlying data holds **PHI, PII, and confidential business information**. ContextGuard answers all three demands at once: accuracy at scale, hallucination prevention, and data privacy.

## One semantic map, two jobs

A single governance artifact — the **semantic map** — does both jobs:

1. **Accuracy (anti-hallucination).** A schema-aware retrieval step narrows the tables, columns, and join keys shown to the model *for each question*, so it cannot invent a wrong join across a wide schema.
2. **Governance (ContextGuard).** Before any answer reaches a human, six gates validate it against the same map: certified source, data freshness, PHI/PII access by role, SQL safety, approved metric definition, and row-level security.

See `docs/architecture.svg` for the diagram.

## Quick start

```bash
pip install -r requirements.txt
python data/generate_data.py        # builds the synthetic warehouse (DuckDB)
python run_demo.py                   # CLI walkthrough of all 6 scenarios
python src/app.py                    # live app at http://localhost:7860
```

Open `demo/index.html` directly in a browser for the **self-contained visual demo** (no server, no install — precomputed from the real warehouse).

## Live LLM mode (optional, morning-of)

The system runs fully offline at **$0** using a deterministic SQL engine. To use a live model:

```bash
export FEATHERLESS_API_KEY=your-key      # from your Featherless promo
python src/app.py                        # the app auto-detects the key
```

The same six gates run on the model's SQL, so the guard protects you even when a real model writes the query.

## The hero result

Question: *"Total settled safety cost for serious adverse events on immunology products"* (a 3-table join: products → adverse_events → safety_costs).

| | Answer |
|---|---|
| Ungoverned (invents a cross-join, drops filters) | **₹240,806,409** — a ~15x hallucination |
| Governed (certified Gold tables) | **₹16,165,949** |
| Misstatement avoided | **₹224,640,459** |

## Layout

```
contextguard/
  data/generate_data.py        synthetic pharma warehouse (real brand names + openFDA terms)
  registry/semantic_map.yaml   THE single source of truth (tables, joins, PHI/PII, metrics, roles)
  registry/golden_questions.yaml  known-good answers for validation
  src/retrieval.py             schema-aware narrowing (the accuracy lever)
  src/generator.py             governed / naive / Featherless engines + self-verify
  src/contextguard.py          the 6 governance gates + verdicts
  src/pipeline.py              retrieve -> generate -> guard
  src/app.py                   live Flask app + audit dashboard
  demo/index.html              self-contained visual demo
  tests/test_scenarios.py      automated checks (6/6 passing)
  docs/                        architecture diagram, build guide, demo script
```

## Attribution

- LLM: Featherless-hosted open instruct model (pluggable; deterministic engine offline).
- Data grounding: real marketed drug brand names and adverse-event terms from the **openFDA FAERS API** (api.fda.gov, public; data updated 2026-04-28). All patient and financial facts are **synthetic**.
- Warehouse: DuckDB (production targets: Snowflake, BigQuery, and other cloud warehouses). Built with Flask, PyYAML.
