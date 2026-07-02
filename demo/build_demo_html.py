"""Build a single self-contained demo/index.html with the real outputs embedded."""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "demo_data.json")))

HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ContextGuard — Trustworthy AI answers over J&J data</title>
<style>
  :root{--bg:#0d1117;--panel:#161b22;--line:#30363d;--ink:#e6edf3;--mut:#8b949e;
        --pass:#2ea043;--block:#f85149;--flag:#d29922;--accent:#58a6ff;}
  *{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--ink);
    font:15px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
  .wrap{max-width:1080px;margin:0 auto;padding:24px}
  h1{font-size:24px;margin:0 0 2px} .sub{color:var(--mut);margin:0 0 18px}
  .tag{display:inline-block;background:#1f6feb22;color:var(--accent);border:1px solid #1f6feb55;
       padding:2px 10px;border-radius:999px;font-size:12px;margin-bottom:14px}
  .grid{display:grid;grid-template-columns:300px 1fr;gap:18px}
  .scn{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px}
  .scn button{display:block;width:100%;text-align:left;background:transparent;color:var(--ink);
    border:1px solid transparent;border-radius:8px;padding:10px;margin:4px 0;cursor:pointer;font-size:13px}
  .scn button:hover{background:#21262d} .scn button.active{background:#1f6feb22;border-color:#1f6feb55}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px;margin-bottom:16px}
  .q{font-size:17px;font-weight:600;margin:0 0 4px} .role{color:var(--mut);font-size:13px}
  .banner{border-radius:10px;padding:14px 16px;font-weight:700;font-size:18px;margin:14px 0;display:flex;
    align-items:center;gap:10px}
  .BLOCKED{background:#f8514922;border:1px solid var(--block);color:#ffb4ad}
  .PASS{background:#2ea04322;border:1px solid var(--pass);color:#a3e6b4}
  .FLAGGED{background:#d2992222;border:1px solid var(--flag);color:#f1d99a}
  .cols{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  .box{border:1px solid var(--line);border-radius:8px;padding:12px;background:#0d1117}
  .box h4{margin:0 0 8px;font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--mut)}
  .ans{font-size:22px;font-weight:700} .ans.bad{color:var(--block)} .ans.good{color:var(--pass)}
  table.res{border-collapse:collapse;width:100%;font-size:12px} .res td{border:1px solid var(--line);padding:3px 6px}
  .gate{display:flex;gap:10px;align-items:flex-start;padding:7px 0;border-bottom:1px solid var(--line)}
  .dot{width:18px;height:18px;border-radius:50%;flex:0 0 18px;text-align:center;font-size:12px;line-height:18px;font-weight:700}
  .gp{background:#2ea04322;color:var(--pass)} .gf{background:#f8514922;color:var(--block)} .gn{background:#30363d;color:var(--mut)}
  .gname{font-weight:600} .gdet{color:var(--mut);font-size:13px}
  pre{background:#0d1117;border:1px solid var(--line);border-radius:8px;padding:10px;overflow:auto;font-size:12px;color:#c9d1d9}
  .chips span{display:inline-block;font-size:11px;padding:2px 8px;border-radius:6px;margin:2px}
  .keep{background:#2ea04322;color:#a3e6b4;border:1px solid #2ea04355}
  .drop{background:#6e768166;color:var(--mut);border:1px solid var(--line);text-decoration:line-through}
  .risk{color:var(--flag);font-weight:700}
  .dash{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:6px}
  .kpi{background:#0d1117;border:1px solid var(--line);border-radius:8px;padding:12px;text-align:center}
  .kpi b{display:block;font-size:22px} .kpi span{color:var(--mut);font-size:12px}
  .small{color:var(--mut);font-size:12px} a{color:var(--accent)}
</style></head><body><div class="wrap">
  <div class="tag">Statement 1 · Track #10 Security &amp; Guardrails · J&amp;J / Janssen pharma</div>
  <h1>ContextGuard</h1>
  <p class="sub">One semantic map, two jobs: it <b>narrows context</b> so multi-table answers are accurate,
     and it <b>guards every answer</b> for certified source, freshness, approved metric, and PHI/PII before a human sees it.</p>

  <div class="card"><div class="dash" id="dash"></div>
    <p class="small" id="dashnote" style="margin:10px 0 0"></p></div>

  <div class="grid">
    <div class="scn" id="scn"></div>
    <div id="panel"></div>
  </div>
  <p class="small" style="margin-top:18px">Demo data is precomputed from the real DuckDB warehouse (synthetic facts; real Janssen brand
     names &amp; openFDA reaction terms). Live mode swaps in a Featherless model — the same guard runs on its output.</p>
</div>
<script>
const DATA = __DATA__;
const fmt = n => (typeof n==='number') ? n.toLocaleString(undefined,{maximumFractionDigits:2}) : n;
function resTable(r){
  if(r==null) return '<span class="small">—</span>';
  if(Array.isArray(r) && Array.isArray(r[0])){
    return '<table class="res">'+r.map(row=>'<tr>'+row.map(c=>'<td>'+fmt(c)+'</td>').join('')+'</tr>').join('')+'</table>';
  }
  if(Array.isArray(r)) return '<span class="ans">'+fmt(r[0])+'</span>';
  return '<span class="ans">'+fmt(r)+'</span>';
}
function scalar(r){ if(Array.isArray(r)&&Array.isArray(r[0])&&r.length===1&&r[0].length===1) return r[0][0];
  if(Array.isArray(r)&&r.length===1&&!Array.isArray(r[0])) return r[0]; return null; }
function dotClass(s){return s==='pass'?'gp':s==='fail'?'gf':'gn'}
function dotChar(s){return s==='pass'?'✓':s==='fail'?'✕':'–'}

function render(i){
  const v = DATA[i];
  document.querySelectorAll('#scn button').forEach((b,j)=>b.classList.toggle('active',j===i));
  const candBad = v.verdict!=='PASS';
  const cs = scalar(v.candidate_result), gs = scalar(v.certified_result);
  let html = '<div class="card">';
  html += '<p class="q">'+v.question+'</p><p class="role">Asked as role: <b>'+v.role+'</b> · candidate engine: <b>'+v.candidate_engine+'</b></p>';
  html += '<div class="banner '+v.verdict+'">'+(v.verdict==='PASS'?'✓':v.verdict==='BLOCKED'?'⛔':'⚠')+' '+v.verdict+
          (v.failed_gates.length?(' — '+v.failed_gates.join(', ')):'')+'</div>';
  if(v.risk_amount>0) html += '<p class="small">Misstatement avoided: <span class="risk">₹'+fmt(v.risk_amount)+'</span></p>';
  html += '<div class="cols"><div class="box"><h4>Ungoverned / candidate answer</h4>'+
          '<div class="'+(candBad?'ans bad':'ans')+'">'+resTable(v.candidate_result)+'</div></div>'+
          '<div class="box"><h4>Certified answer (governed Gold)</h4>'+
          '<div class="ans good">'+resTable(v.certified_result)+'</div></div></div>';
  // gates
  html += '<div class="box" style="margin-top:14px"><h4>Governance gates</h4>';
  v.gates.forEach(g=>{ html += '<div class="gate"><div class="dot '+dotClass(g.status)+'">'+dotChar(g.status)+'</div>'+
     '<div><div class="gname">'+g.name+'</div><div class="gdet">'+g.detail+'</div></div></div>'; });
  html += '</div>';
  // retrieval narrowing
  html += '<div class="box" style="margin-top:14px"><h4>Accuracy lever — schema narrowed for this question</h4><div class="chips">';
  v.retrieval.tables.forEach(t=>html+='<span class="keep">'+t+'</span>');
  v.retrieval.dropped.forEach(t=>html+='<span class="drop">'+t+'</span>');
  html += '</div>';
  if(v.retrieval.joins.length) html += '<p class="small">Allowed joins: '+v.retrieval.joins.join(' &nbsp;·&nbsp; ')+'</p>';
  html += '</div>';
  // SQL
  html += '<div class="cols" style="margin-top:14px">'+
     '<div class="box"><h4>Candidate SQL</h4><pre>'+v.candidate_sql.replace(/</g,'&lt;')+'</pre></div>'+
     '<div class="box"><h4>Governed SQL</h4><pre>'+v.governed_sql.replace(/</g,'&lt;')+'</pre></div></div>';
  html += '</div>';
  document.getElementById('panel').innerHTML = html;
}
function dashboard(){
  const n=DATA.length, blocked=DATA.filter(d=>d.verdict==='BLOCKED').length,
        passed=DATA.filter(d=>d.verdict==='PASS').length,
        risk=DATA.reduce((s,d)=>s+(d.risk_amount||0),0);
  document.getElementById('dash').innerHTML =
    '<div class="kpi"><b>'+n+'</b><span>answers checked</span></div>'+
    '<div class="kpi"><b style="color:var(--block)">'+blocked+'</b><span>blocked</span></div>'+
    '<div class="kpi"><b style="color:var(--pass)">'+passed+'</b><span>passed</span></div>'+
    '<div class="kpi"><b class="risk">₹'+fmt(Math.round(risk))+'</b><span>misstatement avoided</span></div>';
  document.getElementById('dashnote').textContent =
    'Every answer is checked across 6 gates: certified source, freshness, PHI/PII access, SQL safety, approved metric, row-level security.';
}
function init(){
  const scn=document.getElementById('scn');
  scn.innerHTML = DATA.map((d,i)=>'<button onclick="render('+i+')">'+(i+1)+'. '+d.title+'</button>').join('');
  dashboard(); render(0);
}
init();
</script></body></html>"""

out = HTML.replace("__DATA__", json.dumps(DATA))
path = os.path.join(HERE, "index.html")
open(path, "w").write(out)
print("wrote", path, "(%d bytes)" % len(out))
