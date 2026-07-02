"""Run the pipeline for the demo scenarios and dump demo_data.json (capped)."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pipeline import ContextGuardPipeline


def cap(result, n=6):
    if isinstance(result, list) and result and isinstance(result[0], list) and len(result) > n:
        return result[:n] + [["… +%d more rows" % (len(result) - n)]]
    return result


SCENARIOS = [
    ("Hero — multi-table join (ungoverned)",
     "What is the total settled safety cost for serious adverse events on immunology products?",
     "analyst", "naive"),
    ("Hero — same question, governed",
     "What is the total settled safety cost for serious adverse events on immunology products?",
     "analyst", "governed"),
    ("Stale / uncertified source",
     "What was STELARA sales revenue in 2026 Q1?", "analyst", "naive"),
    ("PHI exposure — analyst (must block)",
     "Show patient age, sex and reaction for Xarelto adverse events.", "analyst", "naive"),
    ("PHI access — safety officer (allowed)",
     "Show patient age, sex and reaction for Xarelto adverse events.", "safety_officer", "naive"),
    ("Row-level security — North manager",
     "What is the total sales revenue by region?", "regional_manager_north", "naive"),
]


def main():
    pipe = ContextGuardPipeline()
    out = []
    for title, q, role, mode in SCENARIOS:
        v = pipe.answer(q, role=role, candidate_mode=mode)
        v["candidate_result"] = cap(v["candidate_result"])
        v["certified_result"] = cap(v["certified_result"])
        v["title"] = title
        out.append(v)
    path = os.path.join(os.path.dirname(__file__), "demo_data.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print("wrote", path, "with", len(out), "scenarios")
    # quick verdict summary
    for v in out:
        print(f"  {v['verdict']:8s} {v['title']}")


if __name__ == "__main__":
    main()
