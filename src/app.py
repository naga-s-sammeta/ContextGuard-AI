"""
ContextGuard live app (Flask). Run:  python src/app.py   then open http://localhost:7860

- POST /api/ask {question, role, mode}  -> full verdict (and logs to audit trail)
- GET  /api/audit                       -> verdict mix, gate breakdown, risk avoided
Live LLM mode activates automatically when FEATHERLESS_API_KEY is set.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flask import Flask, request, jsonify, Response
from pipeline import ContextGuardPipeline

app = Flask(__name__)
PIPE = ContextGuardPipeline()
AUDIT = []   # in-memory audit log (one row per validated answer)

PAGE = """<!DOCTYPE html><html><head><meta charset=utf-8><title>ContextGuard (live)</title>
<style>
 body{margin:0;background:#0d1117;color:#e6edf3;font:15px/1.5 system-ui,Segoe UI,Roboto,Arial}
 .wrap{max-width:980px;margin:0 auto;padding:24px}
 h1{margin:0 0 2px} .sub{color:#8b949e;margin:0 0 16px}
 select,input,button,textarea{font:inherit} .row{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
 textarea{flex:1;min-width:320px;background:#161b22;color:#e6edf3;border:1px solid #30363d;border-radius:8px;padding:10px}
 select{background:#161b22;color:#e6edf3;border:1px solid #30363d;border-radius:8px;padding:8px}
 button{background:#1f6feb;color:#fff;border:0;border-radius:8px;padding:10px 16px;cursor:pointer}
 .card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px;margin-top:14px}
 .banner{border-radius:10px;padding:12px 14px;font-weight:700;font-size:18px;margin:10px 0}
 .BLOCKED{background:#f8514922;border:1px solid #f85149;color:#ffb4ad}
 .PASS{background:#2ea04322;border:1px solid #2ea043;color:#a3e6b4}
 .FLAGGED{background:#d2992222;border:1px solid #d29922;color:#f1d99a}
 .gate{padding:6px 0;border-bottom:1px solid #30363d} .det{color:#8b949e;font-size:13px}
 .ok{color:#2ea043}.bad{color:#f85149}.na{color:#8b949e}
 pre{background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:10px;overflow:auto;font-size:12px}
 .kpis{display:flex;gap:10px}.kpi{flex:1;background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:10px;text-align:center}
 .kpi b{display:block;font-size:20px}.chip{display:inline-block;font-size:11px;padding:2px 7px;border-radius:6px;margin:2px;border:1px solid #30363d}
 .keep{background:#2ea04322;color:#a3e6b4}.drop{color:#8b949e;text-decoration:line-through}
 .ex{color:#58a6ff;cursor:pointer;font-size:13px;margin-right:12px}
</style></head><body><div class=wrap>
<h1>ContextGuard <span style="font-size:13px;color:#8b949e">live</span></h1>
<p class=sub>Ask in natural language. Every answer is governed before you trust it. Mode <b id=mode></b>.</p>
<div class=row>
 <textarea id=q rows=2 placeholder="e.g. total settled safety cost for serious adverse events on immunology products"></textarea>
</div>
<div class=row>
 <select id=role>
   <option value=analyst>analyst (no PHI/PII)</option>
   <option value=safety_officer>safety_officer (PHI ok)</option>
   <option value=regional_manager_north>regional_manager_north (RLS: North)</option>
 </select>
 <select id=cmode>
   <option value=naive>candidate: naive (ungoverned)</option>
   <option value=governed>candidate: governed</option>
   <option value=llm>candidate: live LLM (Featherless)</option>
 </select>
 <button onclick=ask()>Validate</button>
</div>
<div class=row style="margin-top:0">
 <span class=ex onclick="setq('What is the total settled safety cost for serious adverse events on immunology products?')">▶ hero join</span>
 <span class=ex onclick="setq('What was STELARA sales revenue in 2026 Q1?')">▶ stale source</span>
 <span class=ex onclick="setq('Show patient age, sex and reaction for Xarelto adverse events.')">▶ PHI</span>
 <span class=ex onclick="setq('What is the total sales revenue by region?')">▶ RLS</span>
</div>
<div id=out></div>
<div class=card><b>Audit dashboard</b><div class=kpis id=kpis style=margin-top:8px></div></div>
</div>
<script>
const fmt=n=>typeof n==='number'?n.toLocaleString(undefined,{maximumFractionDigits:2}):n;
function setq(t){document.getElementById('q').value=t}
function res(r){if(r==null)return '—';
 if(Array.isArray(r)&&Array.isArray(r[0]))return '<pre>'+r.map(x=>x.join(' | ')).join('\\n')+'</pre>';
 if(Array.isArray(r))return '<b style=font-size:20px>'+fmt(r[0])+'</b>'; return '<b>'+fmt(r)+'</b>';}
async function ask(){
 const body={question:q.value,role:role.value,mode:cmode.value};
 const r=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 const v=await r.json();
 let h='<div class=card><div class="banner '+v.verdict+'">'+v.verdict+(v.failed_gates.length?' — '+v.failed_gates.join(', '):'')+'</div>';
 if(v.risk_amount>0)h+='<p>Misstatement avoided: <b style=color:#d29922>₹'+fmt(v.risk_amount)+'</b></p>';
 h+='<div style=display:grid;grid-template-columns:1fr_1fr;gap:12px>'+
    '<div><div class=det>Candidate</div>'+res(v.candidate_result)+'</div>'+
    '<div><div class=det>Certified</div>'+res(v.certified_result)+'</div></div>';
 h+='<div style=margin-top:10px>'+v.gates.map(g=>'<div class=gate><span class="'+(g.status==='pass'?'ok':g.status==='fail'?'bad':'na')+'">'+
    (g.status==='pass'?'✓':g.status==='fail'?'✕':'–')+'</span> <b>'+g.name+'</b><div class=det>'+g.detail+'</div></div>').join('')+'</div>';
 h+='<div style=margin-top:10px><div class=det>Schema narrowed to:</div>'+
    v.retrieval.tables.map(t=>'<span class="chip keep">'+t+'</span>').join('')+
    v.retrieval.dropped.map(t=>'<span class="chip drop">'+t+'</span>').join('')+'</div>';
 h+='<div style=display:grid;grid-template-columns:1fr_1fr;gap:12px;margin-top:10px>'+
    '<div><div class=det>Candidate SQL</div><pre>'+v.candidate_sql.replace(/</g,'&lt;')+'</pre></div>'+
    '<div><div class=det>Governed SQL</div><pre>'+v.governed_sql.replace(/</g,'&lt;')+'</pre></div></div>';
 h+='</div>'; out.innerHTML=h; dash();
}
async function dash(){const a=await (await fetch('/api/audit')).json();
 kpis.innerHTML='<div class=kpi><b>'+a.total+'</b>checked</div>'+
  '<div class=kpi><b style=color:#f85149>'+a.blocked+'</b>blocked</div>'+
  '<div class=kpi><b style=color:#2ea043>'+a.passed+'</b>passed</div>'+
  '<div class=kpi><b style=color:#d29922>₹'+fmt(Math.round(a.risk))+'</b>avoided</div>';}
fetch('/api/mode').then(r=>r.json()).then(m=>mode.textContent=m.mode); dash();
</script></body></html>"""


@app.route("/")
def index():
    return Response(PAGE, mimetype="text/html")


@app.route("/api/mode")
def mode():
    return jsonify({"mode": "live LLM (Featherless)" if PIPE.llm else "deterministic (offline, $0)"})


@app.route("/api/ask", methods=["POST"])
def api_ask():
    d = request.get_json(force=True)
    v = PIPE.answer(d.get("question", ""), role=d.get("role", "analyst"),
                    candidate_mode=d.get("mode", "naive"))
    AUDIT.append(v)
    return jsonify(v)


@app.route("/api/audit")
def api_audit():
    blocked = sum(1 for v in AUDIT if v["verdict"] == "BLOCKED")
    passed = sum(1 for v in AUDIT if v["verdict"] == "PASS")
    flagged = sum(1 for v in AUDIT if v["verdict"] == "FLAGGED")
    risk = sum(v.get("risk_amount", 0) for v in AUDIT)
    gate_fails = {}
    for v in AUDIT:
        for g in v["failed_gates"]:
            gate_fails[g] = gate_fails.get(g, 0) + 1
    return jsonify({"total": len(AUDIT), "blocked": blocked, "passed": passed,
                    "flagged": flagged, "risk": round(risk, 2), "gate_fails": gate_fails})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7860)), debug=False)
