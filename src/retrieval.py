"""
Schema-aware retrieval  --  THE ACCURACY LEVER (anti-hallucination).

Problem (Statement 1): text-to-SQL works at ~80% with 1-2 tables but collapses
as more tables are added, because the model is handed the ENTIRE schema and has
to guess join paths and which columns mean what.

Fix: don't dump the whole schema. Score every table against the question using
the semantic map (names + synonyms + column names), keep only the relevant
tables, then attach ONLY the canonical join edges connecting them. The model
(or the deterministic engine) then reasons over a tiny, correct sub-schema, so
it cannot invent a wrong join such as claims.region = providers.region.

This is intentionally dependency-free (keyword + synonym scoring) so it runs
offline tonight. The same interface accepts embeddings later if you want.
"""
import re

STOPWORDS = {
    "the", "a", "an", "of", "for", "by", "to", "and", "or", "is", "are", "what",
    "how", "many", "much", "total", "show", "me", "give", "in", "on", "per",
    "with", "have", "has", "do", "does", "across", "all", "number",
}


def _tokens(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS]


def _table_terms(name, meta):
    """All words that should make a table 'match' a question."""
    terms = set()
    terms.update(_tokens(name.replace("gold_", "").replace("silver_", "")))
    terms.update(_tokens(meta.get("description", "")))
    for s in meta.get("synonyms", []):
        terms.update(_tokens(s))
    for col in meta.get("columns", {}):
        terms.update(_tokens(col))
    return terms


def score_tables(question, registry):
    """Return list of (table_name, score) sorted desc. Certified tables win ties."""
    q = set(_tokens(question))
    scored = []
    for name, meta in registry.tables.items():
        terms = _table_terms(name, meta)
        overlap = len(q & terms)
        # Small bonus for certified gold tables so we never prefer silver on a tie.
        bonus = 0.5 if meta.get("certified") else 0.0
        scored.append((name, overlap + bonus, overlap))
    scored.sort(key=lambda x: (x[1]), reverse=True)
    return [(n, s) for n, s, _ in scored if _ > 0] or [(scored[0][0], scored[0][1])]


def _connect(tables, registry):
    """
    Given a set of needed tables, return the minimal join edges from the
    canonical join list that connect them. If the chosen tables aren't directly
    connected, pull in bridge tables (e.g. encounters between claims & providers).
    """
    needed = set(tables)
    edges = []
    # First: edges fully inside `needed`.
    for j in registry.joins:
        if j["left"] in needed and j["right"] in needed:
            edges.append(j)
    # Then: add bridge tables to connect disconnected requested tables.
    # Greedy: if claims & providers requested but encounters not, add bridges.
    changed = True
    while changed:
        changed = False
        for j in registry.joins:
            l, r = j["left"], j["right"]
            if (l in needed) ^ (r in needed):
                # one side in, one side out -> consider adding the outside table
                # only if it bridges toward another requested table
                outside = r if l in needed else l
                # add the bridge if it touches >=2 needed tables via joins
                touches = sum(
                    1 for jj in registry.joins
                    if (jj["left"] == outside and jj["right"] in needed)
                    or (jj["right"] == outside and jj["left"] in needed)
                )
                if touches >= 1 and outside not in needed:
                    # add bridge only when it links two requested endpoints
                    endpoints = {x for e in [(jj["left"], jj["right"]) for jj in registry.joins
                                            if outside in (jj["left"], jj["right"])]
                                 for x in e if x in needed}
                    if len(endpoints) >= 2:
                        needed.add(outside)
                        changed = True
    # recompute edges within final needed set
    edges = [j for j in registry.joins if j["left"] in needed and j["right"] in needed]
    return needed, edges


def retrieve(question, registry, top_k=3):
    """
    Main entry point. Returns a focused sub-schema:
        {tables: [...], joins: [...], columns: {table: {...}}, dropped: [...]}
    Only this narrowed context is handed to the generator.
    """
    ranked = score_tables(question, registry)
    chosen = [n for n, _ in ranked[:top_k]]

    # Never expose an uncertified table when a certified equivalent matched.
    certified_names = {n for n in chosen if registry.is_certified(n)}
    if certified_names:
        chosen = [n for n in chosen if registry.is_certified(n)]

    tables, joins = _connect(chosen, registry)
    tables = sorted(tables)

    columns = {t: registry.table(t)["columns"] for t in tables}
    dropped = [n for n in registry.tables if n not in tables]
    return {
        "question": question,
        "tables": tables,
        "joins": joins,
        "columns": columns,
        "dropped": dropped,
        "ranking": ranked,
    }
