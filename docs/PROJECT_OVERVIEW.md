# ContextGuard — Project Overview

## The business problem (Statement 1)

> Business users across large organizations need answers from their data but don't know SQL and can't constantly rely on data teams. The goal is an AI-powered platform where a user can connect up to multiple BigQuery tables, ask questions in natural language, and get accurate answers even when the answer requires joining or reasoning across multiple tables. The current approach works at 80% accuracy with 1-2 tables but starts hallucinating when more are added. The underlying tables may contain PHI, PII, or confidential business information, so security and access control are non-negotiable. The solution must handle accuracy at scale, prevent hallucinations, and respect data privacy.

## What we set out to achieve

The statement contains two problems wearing one coat. The first is an accuracy problem: natural-language-to-SQL degrades as tables are added because the model is handed the entire schema and has to guess join paths across tables it has never seen related. The second is a governance problem: even a correct-looking query can read the wrong (uncertified or stale) source, expose PHI/PII to someone who shouldn't see it, or silently violate access rules. Most tools in this space chase only the first half. Our thesis is that both halves are actually the same artifact seen from two sides, which is why the project is framed as **one semantic map, two jobs**.

The semantic map is a single governed description of the warehouse — which tables are certified, how they legitimately join, which columns are PHI/PII/confidential, the approved definition of each business metric, the freshness SLA per table, and the access policy per role. **Job one** uses that map to *narrow* the schema shown to the model for a given question, so it reasons over a small, correct sub-schema and cannot invent a wrong join. **Job two** uses the same map to *validate* the generated answer before a human trusts it. The same file that makes the answer accurate is the file that proves the answer is safe.

## What is achieved (working today)

We built a complete, runnable reference implementation that answers the statement end to end, offline, at zero cost. Concretely, the following works and is tested:

The accuracy lever is real. A schema-aware retrieval step scores every table against the question and hands the generator only the relevant tables plus the canonical join edges connecting them. On the hero question — *"total settled safety cost for serious adverse events on immunology products,"* which requires a three-table join across products, adverse events and safety costs — the ungoverned baseline invents a cross-join and drops the required filters, returning ₹240,806,409 (a ~15x hallucination), while the governed pipeline returns the certified ₹16,165,949. That is the accuracy-at-scale claim demonstrated on a concrete multi-table case rather than asserted.

The governance layer is real. Every answer passes through six gates — certified source, data freshness against SLA, PHI/PII access by role, SQL safety, approved-metric definition, and row-level security — producing a PASS / FLAGGED / BLOCKED verdict with a per-gate explanation and, when it blocks, the certified answer computed from Gold tables. Privacy is enforced in both directions: the same PHI question (patient age, sex, reaction) is blocked for an `analyst` role but allowed for a `safety_officer`; a stale uncertified staging table is blocked (STELARA Q1 revenue: stale ₹6,217,982 vs certified ₹10,363,303); and a North-region manager is blocked from a query that would leak other regions. Every decision is captured for an audit dashboard, and across the demo set ₹228,785,781 of misstatement is caught.

The engineering around it is real. There is a synthetic Johnson & Johnson / Janssen pharma warehouse (real Janssen brand names and real openFDA FAERS adverse-event terms, with all patient and financial values synthetic and deterministic), a Python pipeline (retrieve → generate → guard), a pluggable generator with a deterministic offline engine and an optional live-LLM path, a Flask web app with the audit dashboard, a self-contained HTML demo that needs no server, an automated test suite (6/6 passing), an architecture diagram, and a pitch deck.

## What is yet to do

The honest scope line matters, because overclaiming is what gets dismantled in judging. What remains is the following.

The accuracy mechanism is proven on the demo's questions, not generalised to arbitrary questions across an arbitrary number of tables; a production version would add embedding-based schema retrieval and a stronger self-consistency / query-planning loop on the generation side. The platform currently runs on a DuckDB stand-in executing the identical SQL — connecting it to live BigQuery (and the role/PHI policies to real IAM and column policies) is the productionisation step, with BigQuery named as the target rather than demoed live. The live LLM path (Featherless) is wired but runs offline by default; switching it on for natural-language questions on the day is a credential swap, not a rebuild. The richer governance surface from the earlier plan — document/policy RAG that flags draft-vs-approved policy versions, and multi-turn memory that holds the governed context across follow-up questions — is designed but not yet part of the working prototype. Finally, a polished Lovable front-end and a persistent (rather than in-memory) audit store are nice-to-haves that don't change the substance.

## What we did for the simulation (tools and process)

The purpose of the simulation was to prove the entire flow on free/open tools before the event, so the buildathon day reduces to a few credential swaps rather than a from-scratch build. Two things happened here, and both are worth stating plainly.

The originally planned simulation used a no-code, OpenAI-compatible stack so that D-day meant only changing base URLs and keys:

| Job | Simulation (free) | Event-day swap |
|---|---|---|
| Orchestration / RAG / agent brain | Dify (free tier) | same |
| Warehouse + vector store | Supabase Postgres + pgvector | same |
| Embeddings + reranker | Jina v4 embeddings, Jina Reranker v2 | same |
| LLM (SQL + verdict) | Groq Llama 3.3 70B (free) | Featherless-hosted model |
| Live web / freshness | Tavily (free ~1,000 credits) | Tavily (event credits) |
| Frontend | Dify chat UI / Lovable free | Lovable ($100 free credits) |

The process was staged: create free accounts and keys; load the warehouse and validate the certified-vs-naive number disagreement; build the knowledge base by chunking the certified-tables and metric-catalog metadata plus the policy documents, embedding them into pgvector; wire retrieval with a certified-only metadata filter and a reranker; then build the hero flow (question → SQL → governance verdict → BLOCK with the certified correction) first, before adding the document-version flow and multi-turn memory; and finally a governance-observability dashboard reading the audit log. The guiding rule throughout was that one hero flow done crisply beats three half-built.

Alongside that plan, we also built a **self-contained working simulation** that needs no accounts at all — the Python/DuckDB reference implementation described above. It reproduces the same retrieval-narrowing and six-gate governance behaviour deterministically and offline, which is what makes the demo reliable on stage and keeps the total cost at zero. The two are complementary: the no-code stack is the path to a polished hosted app, and the offline implementation is the guarantee that the logic is correct and the demo will not break.

## The bottom line

We can fully satisfy the governance, privacy, and access-control half of Statement 1 today, and we demonstrate a real, working accuracy mechanism for the multi-table hallucination half on concrete cases — with a precise, defensible line between what is solved now and what is the next iteration.
