"""
End-to-end pipeline: retrieve -> generate (governed truth) -> generate candidate
-> guard. Returns one rich dict per question that drives the UI and the audit log.
"""
import os
from registry import Registry
from retrieval import retrieve
from generator import generate
from contextguard import Guard
from db import run_sql


class ContextGuardPipeline:
    def __init__(self):
        self.reg = Registry()
        self.guard = Guard(self.reg)
        self.llm = None
        try:
            import llm_featherless
            if llm_featherless.available():
                self.llm = llm_featherless.generate_sql
        except Exception:
            self.llm = None

    def _safe_run(self, sql):
        try:
            cols, rows = run_sql(sql)
            return rows, None
        except Exception as e:
            return None, str(e)

    def answer(self, question, role="analyst", candidate_mode="naive"):
        retrieved = retrieve(question, self.reg)

        # governed = trustworthy reference answer
        governed = generate(question, retrieved, self.reg, mode="governed")
        gov_rows, gov_err = self._safe_run(governed.sql)

        # candidate = what an ungoverned/naive (or live LLM) system would do
        if candidate_mode == "llm" and self.llm:
            candidate = generate(question, retrieved, self.reg, mode="llm", llm=self.llm)
        else:
            candidate = generate(question, retrieved, self.reg, mode=candidate_mode)
        cand_rows, cand_err = self._safe_run(candidate.sql)

        verdict = self.guard.evaluate(
            question, candidate, cand_rows, role, governed_result=gov_rows)

        verdict["candidate_error"] = cand_err
        verdict["retrieval"] = {
            "tables": retrieved["tables"],
            "dropped": retrieved["dropped"],
            "joins": [f"{j['left']}.{j['left_key']} = {j['right']}.{j['right_key']}"
                      for j in retrieved["joins"]],
        }
        verdict["governed_sql"] = governed.sql
        verdict["candidate_notes"] = candidate.notes
        verdict["mode"] = "llm" if (candidate_mode == "llm" and self.llm) else candidate_mode
        return verdict
