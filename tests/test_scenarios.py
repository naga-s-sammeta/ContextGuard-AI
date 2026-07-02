"""Automated checks for the demo scenarios. Run:  python -m pytest -q  (or python tests/test_scenarios.py)"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pipeline import ContextGuardPipeline

pipe = ContextGuardPipeline()


def _scalar(r):
    return r[0][0] if isinstance(r, list) and r and isinstance(r[0], list) and len(r) == 1 and len(r[0]) == 1 else None


def test_hero_naive_blocked():
    v = pipe.answer("What is the total settled safety cost for serious adverse events on immunology products?", "analyst", "naive")
    assert v["verdict"] == "BLOCKED"
    assert "SQL safety" in v["failed_gates"]

def test_hero_governed_correct():
    v = pipe.answer("What is the total settled safety cost for serious adverse events on immunology products?", "analyst", "governed")
    assert v["verdict"] == "PASS"
    assert abs(_scalar(v["candidate_result"]) - 16165949.87) < 1

def test_stale_source_blocked():
    v = pipe.answer("What was STELARA sales revenue in 2026 Q1?", "analyst", "naive")
    assert v["verdict"] == "BLOCKED"
    assert "Certified source" in v["failed_gates"] and "Data freshness" in v["failed_gates"]

def test_phi_blocked_for_analyst():
    v = pipe.answer("Show patient age, sex and reaction for Xarelto adverse events.", "analyst", "naive")
    assert v["verdict"] == "BLOCKED" and "PHI/PII access" in v["failed_gates"]

def test_phi_allowed_for_safety_officer():
    v = pipe.answer("Show patient age, sex and reaction for Xarelto adverse events.", "safety_officer", "naive")
    assert "PHI/PII access" not in v["failed_gates"]

def test_rls_blocked_for_region_manager():
    v = pipe.answer("What is the total sales revenue by region?", "regional_manager_north", "naive")
    assert "Row-level security" in v["failed_gates"]


if __name__ == "__main__":
    fns = [f for n, f in sorted(globals().items()) if n.startswith("test_")]
    passed = 0
    for f in fns:
        try:
            f(); print("PASS", f.__name__); passed += 1
        except AssertionError as e:
            print("FAIL", f.__name__, e)
    print(f"\n{passed}/{len(fns)} tests passed")
