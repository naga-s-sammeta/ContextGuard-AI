"""CLI walkthrough of the ContextGuard demo scenarios (no server needed).
Usage:  python run_demo.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from pipeline import ContextGuardPipeline

C = {"BLOCKED": "\033[91m", "PASS": "\033[92m", "FLAGGED": "\033[93m", "end": "\033[0m", "dim": "\033[90m"}

SCN = [
    ("HERO · multi-table join, ungoverned",
     "What is the total settled safety cost for serious adverse events on immunology products?", "analyst", "naive"),
    ("HERO · same question, governed",
     "What is the total settled safety cost for serious adverse events on immunology products?", "analyst", "governed"),
    ("Stale / uncertified source",
     "What was STELARA sales revenue in 2026 Q1?", "analyst", "naive"),
    ("PHI to analyst (block)",
     "Show patient age, sex and reaction for Xarelto adverse events.", "analyst", "naive"),
    ("PHI to safety officer (allow)",
     "Show patient age, sex and reaction for Xarelto adverse events.", "safety_officer", "naive"),
    ("Row-level security (North manager)",
     "What is the total sales revenue by region?", "regional_manager_north", "naive"),
]


def fmt(r):
    if isinstance(r, list) and r and isinstance(r[0], list):
        if len(r) == 1 and len(r[0]) == 1:
            return f"{r[0][0]:,.2f}" if isinstance(r[0][0], (int, float)) else str(r[0][0])
        return f"{len(r)} rows"
    return str(r)


def main():
    pipe = ContextGuardPipeline()
    print(f"\nContextGuard demo · mode = {'LIVE LLM' if pipe.llm else 'deterministic (offline, $0)'}\n" + "=" * 64)
    total_risk = 0
    for title, q, role, mode in SCN:
        v = pipe.answer(q, role=role, candidate_mode=mode)
        col = C.get(v["verdict"], "")
        print(f"\n{title}\n  Q: {q}\n  role={role}  candidate={mode}")
        print(f"  -> {col}{v['verdict']}{C['end']}  {('failed: ' + ', '.join(v['failed_gates'])) if v['failed_gates'] else ''}")
        print(f"  candidate={fmt(v['candidate_result'])}   certified={fmt(v['certified_result'])}")
        if v["risk_amount"]:
            print(f"  {C['FLAGGED']}misstatement avoided: ₹{v['risk_amount']:,.2f}{C['end']}")
            total_risk += v["risk_amount"]
        print(f"  {C['dim']}narrowed to: {', '.join(v['retrieval']['tables'])}{C['end']}")
    print("\n" + "=" * 64)
    print(f"Total misstatement avoided across demo: ₹{total_risk:,.2f}\n")


if __name__ == "__main__":
    main()
