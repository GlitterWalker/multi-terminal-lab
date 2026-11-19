HOME_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>Linux + Docker Lab</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:system-ui,sans-serif;background:#0d1117;color:#e6edf3;display:flex;min-height:100vh;align-items:center;justify-content:center;margin:0}
.card{background:#161b22;padding:32px;border-radius:12px;width:min(420px,90vw);text-align:center}
input,button{width:100%;padding:12px;margin-top:12px;border-radius:8px;border:1px solid #30363d;font-size:16px;box-sizing:border-box}
input{background:#0d1117;color:#e6edf3}
button{background:#238636;color:#fff;border:0;cursor:pointer}
button:disabled{opacity:.6}
a{color:#58a6ff}
</style></head><body><div class="card">
<h2>Linux + Docker Lab</h2>
<p>15 tasks &middot; 15 minutes &middot; real terminal</p>
<input id="n" placeholder="Your name" maxlength="30" autofocus>
<button id="b">Start lab</button>
<p id="m"></p>
<p><a href="/board">View leaderboard</a></p>
</div>
<script>
const n = document.getElementById('n'), b = document.getElementById('b'), m = document.getElementById('m');
async function go() {
  const name = n.value.trim();
  if (!name) { m.textContent = 'Enter your name first'; return; }
  b.disabled = true; m.textContent = 'Starting your lab...';
  try {
    const r = await fetch('/start', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name: name})});
    const d = await r.json();
    if (d.url) { location.href = d.url; }
    else { m.textContent = d.error || 'Failed to start'; b.disabled = false; }
  } catch (e) { m.textContent = 'Error: ' + e; b.disabled = false; }
}
b.addEventListener('click', go);
n.addEventListener('keydown', function (e) { if (e.key === 'Enter') go(); });
</script></body></html>"""

BOARD_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>Leaderboard</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:system-ui,sans-serif;background:#0d1117;color:#e6edf3;margin:0;padding:32px}
h1{text-align:center}
table{border-collapse:collapse;margin:24px auto;width:min(700px,95vw)}
th,td{padding:12px 16px;text-align:left;border-bottom:1px solid #30363d}
th{color:#8b949e}
p{text-align:center;color:#8b949e}
a{color:#58a6ff}
</style></head><body>
<h1>Leaderboard</h1>
<table><thead><tr><th>#</th><th>Name</th><th>Score</th><th>Time</th></tr></thead><tbody id="tb"></tbody></table>
<p id="empty">No results yet</p>
<p><a href="/">Start the lab</a> &middot; refreshes every 5s</p>
<script>
const medals = ['\\ud83e\\udd47', '\\ud83e\\udd48', '\\ud83e\\udd49'];
async function load() {
  try {
    const r = await fetch('/leaderboard'); const d = await r.json();
    const rows = Array.isArray(d) ? d : [];
    const tb = document.getElementById('tb'); tb.innerHTML = '';
    document.getElementById('empty').style.display = rows.length ? 'none' : 'block';
    rows.forEach(function (x, i) {
      const tr = document.createElement('tr');
      [medals[i] || (i + 1), x.name, x.score + '/' + x.total, Math.floor(x.time / 60) + 'm ' + (x.time % 60) + 's'].forEach(function (v) {
        const td = document.createElement('td'); td.textContent = v; tr.appendChild(td);
      });
      tb.appendChild(tr);
    });
  } catch (e) {}
}
load(); setInterval(load, 5000);
</script></body></html>"""
