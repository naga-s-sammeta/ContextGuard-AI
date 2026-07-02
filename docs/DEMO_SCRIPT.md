# Demo & Pitch Script

## 60-second pitch (memorise the opening — the wrong number must land in ~12 seconds)

> "Ask a company's AI assistant: *what's our total settled safety cost for serious adverse events on our immunology drugs?* It answers instantly — **₹240 million**. Confident. Wrong. To get there it joined three tables, invented the join, and quietly dropped the 'serious' and 'settled' filters. The certified number is **₹16 million** — off by fifteen times. Nobody catches it, because the AI sounds sure.
>
> **ContextGuard is the layer that catches it.** It's built on one idea — *one semantic map, two jobs.* The same governed map that tells the model which tables and joins are valid — so the answer is accurate in the first place — also checks every answer before a human trusts it: certified source? fresh data? approved metric? And critically for pharma data — does this person's role allow PHI? If any check fails, it blocks the answer and returns the certified one.
>
> I demoed it on Johnson & Johnson data — real Janssen brand names, real openFDA adverse-event terms, synthetic patients. It blocks PHI for an analyst but allows it for a safety officer, blocks stale staging tables, and enforces region-level access — every decision logged to an audit dashboard. Production target is BigQuery; the LLM is pluggable. I built it solo on the governance patterns I use in production data engineering. **I'm looking for one analytics team to pilot it.**"

## Live demo runbook (do it in this order)

Open `demo/index.html` (safest) or the live app at `localhost:7860`.

1. **HERO — the hallucination (scenario 1).** Show the ungoverned answer: **₹240,806,409**, BLOCKED, failed gates highlighted (SQL safety = cartesian join; approved metric = missing `status='settled'`). Point at the red banner and the "₹224,640,459 misstatement avoided".
2. **HERO — governed (scenario 2).** Same question, governed engine: **₹16,165,949**, PASS. Point at the "schema narrowed to 3 tables, silver dropped" chips — *this* is why it's right.
3. **Stale source (scenario 3).** STELARA Q1 revenue: ungoverned reads the stale silver table → **₹6.2M**, BLOCKED on certified-source + freshness; certified = **₹10.4M**.
4. **Privacy, both directions (scenarios 4 & 5).** Same PHI question — patient age/sex/reaction for Xarelto. As **analyst** → BLOCKED (PHI/PII access). As **safety_officer** → PASS. One engine, role-aware.
5. **Row-level security (scenario 6).** "Revenue by region" as **regional_manager_north** → BLOCKED because the North-only row filter wasn't applied.
6. **Dashboard.** Point at the KPIs: answers checked, blocked, and total misstatement avoided (**₹228,785,781** across the demo set).

Backup: play the recorded video if wifi dies.

## Objection cheat-sheet

**"Isn't this just filtering to certified sources?"**
A hard filter silently drops the bad source — no record, no learning, and it fails the moment tagging is incomplete. And there is no "filter" for a *generated* SQL query — the model invented it. ContextGuard validates the generated query live, explains the catch, and logs it. Suppression isn't governance; verifiable enforcement is.

**"Doesn't this just solve half of Statement 1 — governance, not accuracy?"**
No — that's the whole point of *one map, two jobs*. The same semantic map that governs the answer is what narrows the schema before generation, which is the accuracy fix. Watch scenario 1 vs 2: identical question, the only difference is whether the map narrowed the context. Ungoverned hallucinates a 3-table join; governed gets it right.

**"You can't fully solve multi-table accuracy in a buildathon."**
Correct, and I don't claim a generalised fix at infinite scale. I claim a real, demoed mechanism — schema-aware retrieval + self-verification — that demonstrably fixes the join on a concrete 3-table question, plus a complete governance layer. I'm precise about what's solved now and what's the next iteration.

**"Why DuckDB not BigQuery / Snowflake?"**
The governance layer is warehouse-agnostic — it validates generated SQL and metadata, not a specific engine. DuckDB runs the identical SQL locally for a $0, offline-reliable demo. BigQuery is the production target.

**"The model isn't deterministic — sometimes it writes a safe query."**
Exactly why you need a guard that validates *every* answer regardless of what the model did that run. And notice it correctly **passes** the safe ones — no false positives (scenario 2).

## Numbers to have memorised

- Hero: ungoverned ₹240,806,409 → certified ₹16,165,949 → avoided ₹224,640,459 (~15x).
- STELARA Q1: stale ₹6,217,982 → certified ₹10,363,303.
- Xarelto adverse events: 166 (PHI blocked for analyst, allowed for safety officer).
- Total misstatement avoided across the demo: ₹228,785,781.
- Six gates: certified source, freshness, PHI/PII access, SQL safety, approved metric, row-level security.
