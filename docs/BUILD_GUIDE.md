# Build & Run Guide (morning-of)

This is everything already built and tested overnight. The core runs **offline at $0**. Your morning job is to stand it up, optionally plug in the live model, and (optionally) wrap a nicer UI in Lovable. Nothing here needs a credit card.

## 0. What's already done (don't rebuild it)

- Synthetic pharma warehouse, semantic map, retrieval, generator, the six governance gates, the pipeline, a Flask app, a self-contained HTML demo, automated tests (6/6 passing), architecture diagram, and the pitch deck.
- The hero numbers are locked and verified against the real database.

## 1. Stand it up (5 minutes)

```bash
cd contextguard
pip install -r requirements.txt
python data/generate_data.py     # writes data/pharma_warehouse.duckdb
python tests/test_scenarios.py   # expect: 6/6 tests passed
python run_demo.py               # sanity-check the 6 scenarios in the terminal
```

If `run_demo.py` prints BLOCKED for the hero (ungoverned) and PASS for the governed version, you're green.

## 2. The two ways to demo

**Safest (no server):** open `demo/index.html` in a browser. It's a single file with the real outputs embedded — it cannot break on stage and needs no wifi.

**Live (interactive):** `python src/app.py` → open `http://localhost:7860`. Type questions, switch roles, switch candidate engine. Has an audit dashboard.

Lead with the static file; keep the live app as the "and it works interactively" follow-up.

## 3. Optional — plug in the live LLM (Featherless)

Only do this once the offline demo is solid. Featherless is free for the month on your promo.

```bash
export FEATHERLESS_API_KEY=your-key
# optional: export FEATHERLESS_MODEL=Qwen/Qwen2.5-72B-Instruct
python src/app.py
```

In the app, pick candidate engine = **live LLM**. The model only ever sees the *narrowed* sub-schema (the accuracy lever), and the six gates still validate its SQL. Keep `max_tokens` low — it's already capped at 300.

> Credit discipline: Featherless is the tight budget. Don't loop generations; the deterministic engine already covers every demo question for free.

## 4. Optional — wrap the UI in Lovable

You do NOT need Lovable to win — `demo/index.html` is already presentable. If you want a polished front-end:

- Redeem the free 100 credits (code `COMM-DATHON-9535`), then **set a reminder to cancel within one month** so you're never charged.
- Point a Lovable page at the Flask `/api/ask` endpoint (host the Flask app, or run it locally and use a tunnel). Be surgical with prompts — each iteration burns credits.

## 5. Warehouse framing (important for judging)

Statement 1 mentions BigQuery; we demo on DuckDB running the *identical* SQL. Name **Snowflake as the primary production target — with BigQuery and other cloud warehouses supported** on the architecture slide, and say the governance layer is warehouse-agnostic. This is honest and standard practice.

## 6. Submission checklist

- [ ] Live link or the `demo/index.html` file
- [ ] Backup video (record the 60-sec hero flow)
- [ ] `ContextGuard_Pitch_Deck.pptx`
- [ ] GitHub repo pushed (code + README + attribution — openFDA, Featherless, DuckDB)
- [ ] Confirm sponsor-API usage is within each ToS

## Troubleshooting

- **`duckdb ... Operation not permitted` on rebuild:** the DB can't be deleted in some sandboxes. Set a fresh path: `CG_DB=/tmp/cg.duckdb python data/generate_data.py` and run the app with the same `CG_DB`.
- **Numbers look off:** re-run `python data/generate_data.py` (seed is fixed; values are deterministic) then `python tests/test_scenarios.py`.
- **Featherless errors/rate-limits:** just switch the candidate engine back to deterministic — the demo is identical and free.
