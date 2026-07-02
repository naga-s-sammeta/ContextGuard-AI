"""
Optional live LLM adapter (Featherless, OpenAI-compatible).

Used ONLY if FEATHERLESS_API_KEY is set. The morning swap is: export the key,
pass mode="llm". The governed self-verification still runs on the model's SQL,
so the guard protects you even when a real model writes the query.

We still hand the model ONLY the retrieved sub-schema -- that narrowing is the
accuracy lever; the model is not shown the full warehouse.
"""
import os
import json
import urllib.request

BASE_URL = os.environ.get("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1")
MODEL = os.environ.get("FEATHERLESS_MODEL", "Qwen/Qwen2.5-72B-Instruct")


def available():
    return bool(os.environ.get("FEATHERLESS_API_KEY"))


def _schema_text(retrieved, registry):
    lines = []
    for t in retrieved["tables"]:
        meta = registry.table(t)
        cols = ", ".join(meta["columns"].keys())
        lines.append(f"- {t} ({meta['grain']}): {cols}")
    joins = [f"{j['left']}.{j['left_key']} = {j['right']}.{j['right_key']}"
             for j in retrieved["joins"]]
    return "TABLES:\n" + "\n".join(lines) + "\nALLOWED JOINS:\n" + "\n".join(joins or ["(none)"])


def generate_sql(question, retrieved, registry):
    key = os.environ["FEATHERLESS_API_KEY"]
    prompt = (
        "You are a careful analytics engineer. Using ONLY the tables and joins below, "
        "write a single DuckDB SQL query that answers the question. Use only the listed "
        "join keys. Do not invent tables or columns. Return SQL only.\n\n"
        + _schema_text(retrieved, registry)
        + f"\n\nQUESTION: {question}\nSQL:"
    )
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 300,
    }).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    sql = data["choices"][0]["message"]["content"].strip()
    sql = re.sub(r"^```sql|^```|```$", "", sql, flags=re.M).strip()
    return sql


import re  # noqa: E402  (kept at bottom; only needed in generate_sql)
