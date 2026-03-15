"""Dashboard HTML – served at /"""
DASHBOARD_HTML = r"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Ansible · LLM Error Monitor</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    /* ── Design tokens ─────────────────────────────────── */
    :root {
      --bg:        #080c14;
      --surface-1: #0d1420;
      --surface-2: #111927;
      --surface-3: #162030;
      --border:    rgba(255,255,255,.07);
      --border-hi: rgba(96,165,250,.25);
      --text:      #dce8f7;
      --muted:     #5c7a9a;
      --dim:       #2a3e56;

      --cyan:   #38bdf8;
      --green:  #4ade80;
      --amber:  #fbbf24;
      --red:    #f87171;
      --violet: #a78bfa;
      --blue:   #60a5fa;

      --sev-low:      #4ade80;
      --sev-medium:   #fbbf24;
      --sev-high:     #f97316;
      --sev-critical: #f87171;

      --mono: 'JetBrains Mono', 'Fira Code', monospace;
      --sans: 'Syne', sans-serif;

      --r:   12px;
      --r-lg: 20px;
      --shadow: 0 24px 48px rgba(0,0,0,.45);
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: var(--mono);
      font-size: 13px;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      overflow-x: hidden;
    }

    /* subtle scanline texture */
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(255,255,255,.012) 2px,
        rgba(255,255,255,.012) 4px
      );
      pointer-events: none;
      z-index: 0;
    }

    /* corner glow accents */
    body::after {
      content: '';
      position: fixed;
      top: -200px; left: -200px;
      width: 600px; height: 600px;
      background: radial-gradient(circle, rgba(56,189,248,.06) 0%, transparent 60%);
      pointer-events: none;
      z-index: 0;
    }

    /* ── Layout ─────────────────────────────────────────── */
    .shell {
      position: relative;
      z-index: 1;
      max-width: 1600px;
      margin: 0 auto;
      padding: 24px 28px;
    }

    /* ── Topbar ─────────────────────────────────────────── */
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      margin-bottom: 28px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 20px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .brand-icon {
      width: 42px; height: 42px;
      background: linear-gradient(135deg, rgba(56,189,248,.15), rgba(96,165,250,.08));
      border: 1px solid rgba(56,189,248,.3);
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 20px;
      box-shadow: 0 0 20px rgba(56,189,248,.1);
    }

    .brand h1 {
      font-family: var(--sans);
      font-size: 18px;
      font-weight: 800;
      letter-spacing: .3px;
      line-height: 1.2;
    }

    .brand-sub {
      color: var(--muted);
      font-size: 11px;
      letter-spacing: .8px;
      text-transform: uppercase;
      margin-top: 2px;
    }

    .topbar-right {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    /* ── Status pill ────────────────────────────────────── */
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      background: var(--surface-2);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 8px 16px;
      font-size: 12px;
      font-family: var(--mono);
      letter-spacing: .3px;
      transition: border-color .3s;
    }

    .status-pill.s-idle     { border-color: rgba(92,122,154,.3); }
    .status-pill.s-queued   { border-color: rgba(251,191,36,.3); }
    .status-pill.s-analyzing{ border-color: rgba(56,189,248,.35); }
    .status-pill.s-done     { border-color: rgba(74,222,128,.3); }
    .status-pill.s-error    { border-color: rgba(248,113,113,.35); }

    .s-dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: var(--muted);
      flex-shrink: 0;
    }
    .s-idle     .s-dot { background: var(--muted); }
    .s-queued   .s-dot { background: var(--amber); box-shadow: 0 0 8px var(--amber); }
    .s-analyzing .s-dot {
      background: var(--cyan);
      box-shadow: 0 0 10px var(--cyan);
      animation: blink 1.1s ease-in-out infinite;
    }
    .s-done   .s-dot { background: var(--green); box-shadow: 0 0 8px var(--green); }
    .s-error  .s-dot { background: var(--red);   box-shadow: 0 0 8px var(--red); }

    @keyframes blink {
      0%, 100% { opacity: 1; transform: scale(1); }
      50%       { opacity: .5; transform: scale(1.4); }
    }

    /* live badge */
    .live-badge {
      font-size: 10px;
      letter-spacing: 1px;
      text-transform: uppercase;
      color: var(--green);
      background: rgba(74,222,128,.08);
      border: 1px solid rgba(74,222,128,.2);
      border-radius: 4px;
      padding: 3px 8px;
      font-family: var(--mono);
    }

    /* ── Metric strip ───────────────────────────────────── */
    .metrics {
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 10px;
      margin-bottom: 20px;
    }

    .metric {
      background: var(--surface-1);
      border: 1px solid var(--border);
      border-radius: var(--r);
      padding: 14px 16px;
      position: relative;
      overflow: hidden;
      transition: border-color .2s;
    }

    .metric::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 2px;
      background: var(--accent-line, transparent);
      transition: background .3s;
    }

    .metric:hover { border-color: rgba(255,255,255,.12); }

    .metric-label {
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: .8px;
      color: var(--muted);
      margin-bottom: 8px;
    }

    .metric-value {
      font-family: var(--sans);
      font-size: 22px;
      font-weight: 700;
      line-height: 1;
      color: var(--text);
      word-break: break-all;
    }

    .metric-value.small { font-size: 13px; font-family: var(--mono); }
    .metric-value.cyan   { color: var(--cyan); }
    .metric-value.green  { color: var(--green); }
    .metric-value.amber  { color: var(--amber); }
    .metric-value.red    { color: var(--red); }

    /* ── Two-column grid ────────────────────────────────── */
    .main-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 16px;
    }

    .bottom-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }

    /* ── Card ───────────────────────────────────────────── */
    .card {
      background: var(--surface-1);
      border: 1px solid var(--border);
      border-radius: var(--r-lg);
      overflow: hidden;
      box-shadow: var(--shadow);
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
      background: rgba(255,255,255,.015);
    }

    .card-title {
      font-family: var(--sans);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1.2px;
      color: var(--muted);
    }

    .card-body {
      padding: 20px;
    }

    /* ── Error incoming card ────────────────────────────── */
    .error-host {
      font-family: var(--sans);
      font-size: 24px;
      font-weight: 800;
      line-height: 1.1;
      margin-bottom: 6px;
      word-break: break-all;
    }

    .error-task {
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 14px;
    }

    .meta-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 14px;
    }

    .tag {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 11px;
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid var(--border);
      color: var(--muted);
      background: rgba(255,255,255,.025);
      font-family: var(--mono);
      white-space: nowrap;
    }

    .tag.event   { border-color: rgba(96,165,250,.25); color: var(--blue); }
    .tag.host    { border-color: rgba(56,189,248,.2);  color: var(--cyan); }
    .tag.failed  { border-color: rgba(248,113,113,.25); color: var(--red); }
    .tag.ok      { border-color: rgba(74,222,128,.25);  color: var(--green); }
    .tag.ts      { font-size: 10px; }

    /* severity badge */
    .sev {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 600;
      padding: 4px 12px;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: .6px;
    }
    .sev-low      { background: rgba(74,222,128,.1);  color: var(--sev-low);      border: 1px solid rgba(74,222,128,.25); }
    .sev-medium   { background: rgba(251,191,36,.1);  color: var(--sev-medium);   border: 1px solid rgba(251,191,36,.25); }
    .sev-high     { background: rgba(249,115,22,.1);  color: var(--sev-high);     border: 1px solid rgba(249,115,22,.25); }
    .sev-critical { background: rgba(248,113,113,.1); color: var(--sev-critical); border: 1px solid rgba(248,113,113,.35); }

    /* ── Analysis progress banner ───────────────────────── */
    .progress-bar-wrap {
      background: rgba(56,189,248,.06);
      border: 1px solid rgba(56,189,248,.2);
      border-radius: 10px;
      padding: 12px 14px;
      display: none;
      align-items: center;
      gap: 12px;
    }

    .progress-bar-wrap.show { display: flex; }

    .spinner {
      width: 16px; height: 16px;
      border: 2px solid rgba(56,189,248,.2);
      border-top-color: var(--cyan);
      border-radius: 50%;
      animation: spin .8s linear infinite;
      flex-shrink: 0;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    .progress-text {
      font-size: 12px;
      color: #93c5fd;
      flex: 1;
    }

    /* ── Diagnosis report ───────────────────────────────── */
    .report-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }

    .report-title {
      font-family: var(--sans);
      font-size: 18px;
      font-weight: 700;
      line-height: 1.2;
      flex: 1;
    }

    .confidence-badge {
      font-size: 11px;
      font-family: var(--mono);
      padding: 4px 10px;
      border-radius: 6px;
      background: rgba(167,139,250,.08);
      border: 1px solid rgba(167,139,250,.2);
      color: var(--violet);
      white-space: nowrap;
    }

    .report-meta {
      font-size: 11px;
      color: var(--muted);
      margin-bottom: 16px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }

    .report-body {
      white-space: pre-wrap;
      line-height: 1.75;
      font-size: 13px;
      color: #c8daf0;
      max-height: 360px;
      overflow-y: auto;
    }

    .report-body::-webkit-scrollbar { width: 4px; }
    .report-body::-webkit-scrollbar-track { background: transparent; }
    .report-body::-webkit-scrollbar-thumb { background: var(--dim); border-radius: 2px; }

    .empty-state {
      color: var(--muted);
      font-style: italic;
      font-size: 13px;
      text-align: center;
      padding: 32px 0;
    }

    /* ── JSON box ───────────────────────────────────────── */
    .json-box {
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: var(--r);
      padding: 16px;
      white-space: pre-wrap;
      word-break: break-word;
      overflow-y: auto;
      max-height: 380px;
      font-size: 12px;
      line-height: 1.6;
      color: #8aaccc;
    }

    .json-box::-webkit-scrollbar { width: 4px; }
    .json-box::-webkit-scrollbar-track { background: transparent; }
    .json-box::-webkit-scrollbar-thumb { background: var(--dim); border-radius: 2px; }

    /* JSON syntax colors */
    .j-key    { color: #7dd3fc; }
    .j-str    { color: #86efac; }
    .j-num    { color: #fdba74; }
    .j-bool   { color: #c084fc; }
    .j-null   { color: var(--muted); }

    /* ── History list ───────────────────────────────────── */
    .history-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-height: 380px;
      overflow-y: auto;
    }

    .history-list::-webkit-scrollbar { width: 4px; }
    .history-list::-webkit-scrollbar-track { background: transparent; }
    .history-list::-webkit-scrollbar-thumb { background: var(--dim); border-radius: 2px; }

    .history-item {
      display: grid;
      grid-template-columns: 6px 1fr auto;
      gap: 10px;
      align-items: start;
      padding: 12px 14px;
      background: var(--surface-2);
      border: 1px solid var(--border);
      border-radius: 10px;
      cursor: pointer;
      transition: border-color .15s, background .15s;
    }

    .history-item:hover {
      border-color: rgba(255,255,255,.12);
      background: var(--surface-3);
    }

    .history-dot {
      width: 6px; height: 6px;
      border-radius: 50%;
      margin-top: 4px;
      flex-shrink: 0;
    }

    .history-content { min-width: 0; }

    .history-title {
      font-size: 12px;
      font-weight: 500;
      color: var(--text);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-bottom: 3px;
    }

    .history-sub {
      font-size: 11px;
      color: var(--muted);
    }

    .history-time {
      font-size: 10px;
      color: var(--dim);
      white-space: nowrap;
    }

    /* ── Tabs ───────────────────────────────────────────── */
    .tab-row {
      display: flex;
      gap: 4px;
    }

    .tab-btn {
      font-family: var(--mono);
      font-size: 11px;
      padding: 5px 12px;
      border-radius: 6px;
      border: 1px solid transparent;
      background: transparent;
      color: var(--muted);
      cursor: pointer;
      letter-spacing: .3px;
      transition: all .15s;
    }

    .tab-btn:hover  { color: var(--text); background: rgba(255,255,255,.04); }
    .tab-btn.active { color: var(--cyan); border-color: rgba(56,189,248,.25); background: rgba(56,189,248,.06); }

    /* ── Divider ────────────────────────────────────────── */
    hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }

    /* ── Utilities ──────────────────────────────────────── */
    .flex { display: flex; align-items: center; gap: 8px; }
    .flex-between { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .truncate { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

    /* ── Responsive ─────────────────────────────────────── */
    @media (max-width: 1100px) {
      .metrics    { grid-template-columns: repeat(3, 1fr); }
      .main-grid  { grid-template-columns: 1fr; }
      .bottom-grid{ grid-template-columns: 1fr; }
    }

    @media (max-width: 640px) {
      .metrics { grid-template-columns: repeat(2, 1fr); }
      .topbar  { flex-direction: column; align-items: flex-start; }
    }

    /* ── Fade-in on load ────────────────────────────────── */
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(12px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .shell > * {
      animation: fadeUp .4s ease both;
    }
    .shell > *:nth-child(2) { animation-delay: .05s; }
    .shell > *:nth-child(3) { animation-delay: .10s; }
    .shell > *:nth-child(4) { animation-delay: .15s; }
    .shell > *:nth-child(5) { animation-delay: .20s; }
  </style>
</head>
<body>
<div class="shell">

  <!-- ── Topbar ───────────────────────────── -->
  <header class="topbar">
    <div class="brand">
      <div class="brand-icon">⚡</div>
      <div>
        <h1>Ansible · LLM Monitor</h1>
        <div class="brand-sub">Error Intelligence Dashboard</div>
      </div>
    </div>
    <div class="topbar-right">
      <span class="live-badge">● LIVE</span>
      <div id="statusPill" class="status-pill s-idle">
        <span id="statusDot" class="s-dot"></span>
        <span id="statusText">Inicializando…</span>
      </div>
    </div>
  </header>

  <!-- ── Metrics strip ────────────────────── -->
  <div class="metrics">
    <div class="metric" style="--accent-line: var(--cyan)">
      <div class="metric-label">Estado</div>
      <div id="mStatus" class="metric-value cyan small">idle</div>
    </div>
    <div class="metric" style="--accent-line: var(--amber)">
      <div class="metric-label">Cola</div>
      <div id="mQueue" class="metric-value amber">0</div>
    </div>
    <div class="metric" style="--accent-line: var(--green)">
      <div class="metric-label">Analizados</div>
      <div id="mTotal" class="metric-value green">0</div>
    </div>
    <div class="metric" style="--accent-line: var(--red)">
      <div class="metric-label">Errores LLM</div>
      <div id="mErrors" class="metric-value red">0</div>
    </div>
    <div class="metric">
      <div class="metric-label">Proveedor</div>
      <div id="mProvider" class="metric-value small">—</div>
    </div>
    <div class="metric">
      <div class="metric-label">Modelo</div>
      <div id="mModel" class="metric-value small truncate">—</div>
    </div>
  </div>

  <!-- ── Main two-col ─────────────────────── -->
  <div class="main-grid">

    <!-- LEFT: latest error -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">Último error recibido</span>
        <span id="errorTimestamp" class="tag ts">Sin eventos</span>
      </div>
      <div class="card-body">
        <div id="errorHost" class="error-host" style="color: var(--cyan)">—</div>
        <div id="errorTask" class="error-task">Esperando eventos desde Ansible…</div>

        <div id="errorTags" class="meta-row"></div>

        <div id="progressBanner" class="progress-bar-wrap">
          <div class="spinner"></div>
          <div id="progressText" class="progress-text">Procesando…</div>
        </div>
      </div>
    </div>

    <!-- RIGHT: diagnosis -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">Diagnóstico LLM</span>
        <span id="reportSeverityBadge"></span>
      </div>
      <div class="card-body">
        <div class="report-header">
          <div id="reportTitle" class="report-title">Sin diagnóstico</div>
          <span id="reportConfidence" class="confidence-badge" style="display:none"></span>
        </div>
        <div id="reportMeta" class="report-meta">Esperando análisis…</div>
        <div id="reportBody" class="report-body empty-state">El modelo todavía no procesó ningún error.</div>
      </div>
    </div>
  </div>

  <!-- ── Bottom two-col ───────────────────── -->
  <div class="bottom-grid">

    <!-- Raw JSON / Ops state tabs -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">Datos crudos</span>
        <div class="tab-row">
          <button class="tab-btn active" onclick="switchTab('raw', this)">Raw payload</button>
          <button class="tab-btn" onclick="switchTab('ops', this)">Estado operativo</button>
        </div>
      </div>
      <div class="card-body" style="padding-top: 14px;">
        <div id="tabRaw">
          <div id="rawJson" class="json-box">Esperando payload…</div>
        </div>
        <div id="tabOps" style="display:none">
          <div id="opsBox" class="json-box">Cargando estado…</div>
        </div>
      </div>
    </div>

    <!-- History -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">Historial reciente</span>
        <span id="historyCount" class="tag">0 diagnósticos</span>
      </div>
      <div class="card-body" style="padding-top: 14px;">
        <div id="historyList" class="history-list">
          <div class="empty-state">Sin historial todavía</div>
        </div>
      </div>
    </div>

  </div>
</div>

<script>
// ── Utilities ──────────────────────────────────────────────
function fmtDate(v) {
  if (!v) return '—';
  try { return new Date(v).toLocaleString('es-ES', {hour12: false}); } catch { return v; }
}

function fmtRelative(v) {
  if (!v) return '';
  try {
    const diff = (Date.now() - new Date(v).getTime()) / 1000;
    if (diff < 60) return `hace ${Math.round(diff)}s`;
    if (diff < 3600) return `hace ${Math.round(diff/60)}m`;
    return `hace ${Math.round(diff/3600)}h`;
  } catch { return ''; }
}

function safeStr(obj) {
  if (!obj) return 'Sin datos';
  return JSON.stringify(obj, null, 2);
}

function syntaxHighlight(json) {
  if (typeof json !== 'string') json = JSON.stringify(json, null, 2);
  json = json.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  return json.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
    m => {
      if (/^"/.test(m)) {
        return /:$/.test(m)
          ? `<span class="j-key">${m}</span>`
          : `<span class="j-str">${m}</span>`;
      }
      if (/true|false/.test(m)) return `<span class="j-bool">${m}</span>`;
      if (/null/.test(m))       return `<span class="j-null">${m}</span>`;
      return `<span class="j-num">${m}</span>`;
    }
  );
}

// ── Tabs ───────────────────────────────────────────────────
function switchTab(name, btn) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('tabRaw').style.display = name === 'raw' ? '' : 'none';
  document.getElementById('tabOps').style.display = name === 'ops' ? '' : 'none';
}

// ── Status rendering ───────────────────────────────────────
const STATUS_LABELS = {
  idle: 'Inactivo', queued: 'En cola',
  analyzing: 'Analizando…', done: 'Completado', error: 'Error'
};

function applyStatus(status) {
  const pill = document.getElementById('statusPill');
  const txt  = document.getElementById('statusText');
  const met  = document.getElementById('mStatus');
  pill.className = 'status-pill s-' + (status || 'idle');
  txt.textContent  = STATUS_LABELS[status] || status || 'idle';
  met.textContent  = status || 'idle';
  met.className    = 'metric-value small ' + (status === 'analyzing' ? 'cyan' : status === 'error' ? 'red' : status === 'done' ? 'green' : '');
}

// ── Progress banner ────────────────────────────────────────
function applyBanner(system) {
  const wrap = document.getElementById('progressBanner');
  const text = document.getElementById('progressText');
  const { status, current_task_label: label, queue_size: qs } = system;
  if (status === 'queued') {
    wrap.classList.add('show');
    text.textContent = `En cola: ${label || '—'} · ${qs} errores pendientes`;
    return;
  }
  if (status === 'analyzing') {
    wrap.classList.add('show');
    text.textContent = `Analizando: ${label || '—'} · ${qs} en cola`;
    return;
  }
  if (status === 'error') {
    wrap.classList.add('show');
    text.innerHTML = `<span style="color:var(--red)">⚠ Falló el análisis:</span> ${system.last_error_message || '—'}`;
    return;
  }
  wrap.classList.remove('show');
}

// ── Tags ───────────────────────────────────────────────────
function buildTags(payload) {
  const tags = [];
  if (payload.event_type) tags.push(`<span class="tag event">⚡ ${payload.event_type}</span>`);
  if (payload.host)       tags.push(`<span class="tag host">🖥 ${payload.host}</span>`);
  if (payload.failed)     tags.push(`<span class="tag failed">✗ failed</span>`);
  if (payload.unreachable)tags.push(`<span class="tag failed">✗ unreachable</span>`);
  if (payload.rc != null) tags.push(`<span class="tag">rc=${payload.rc}</span>`);
  if (payload.changed)    tags.push(`<span class="tag ok">✓ changed</span>`);
  return tags.join('');
}

// ── Severity ───────────────────────────────────────────────
function severityBadge(sev) {
  if (!sev) return '';
  const labels = { low: '▼ LOW', medium: '◆ MEDIUM', high: '▲ HIGH', critical: '⬛ CRITICAL' };
  return `<span class="sev sev-${sev}">${labels[sev] || sev.toUpperCase()}</span>`;
}

// ── Raw error panel ────────────────────────────────────────
function applyRaw(raw) {
  const host  = document.getElementById('errorHost');
  const task  = document.getElementById('errorTask');
  const tags  = document.getElementById('errorTags');
  const ts    = document.getElementById('errorTimestamp');
  const rawEl = document.getElementById('rawJson');

  if (!raw) {
    host.textContent = '—';
    task.textContent = 'Esperando eventos desde Ansible…';
    tags.innerHTML = '';
    ts.textContent = 'Sin eventos';
    rawEl.innerHTML = 'Esperando payload…';
    return;
  }
  const p = raw.payload || {};
  host.textContent = p.host || raw.title || '—';
  task.textContent = p.task || p.action || '—';
  tags.innerHTML   = buildTags(p);
  ts.textContent   = fmtRelative(raw.received_at) || fmtDate(raw.received_at);
  rawEl.innerHTML  = syntaxHighlight(raw);
}

// ── Diagnosis panel ────────────────────────────────────────
function applyResult(result, system) {
  const title  = document.getElementById('reportTitle');
  const meta   = document.getElementById('reportMeta');
  const body   = document.getElementById('reportBody');
  const sevEl  = document.getElementById('reportSeverityBadge');
  const confEl = document.getElementById('reportConfidence');

  if (!result) {
    const busy = system?.status === 'queued' || system?.status === 'analyzing';
    title.textContent = busy ? 'Análisis en progreso…' : 'Sin diagnóstico';
    meta.textContent  = busy ? 'El modelo está procesando el error recibido.' : 'Esperando análisis…';
    body.textContent  = busy ? 'Los resultados aparecerán aquí al finalizar.' : 'El modelo todavía no procesó ningún error.';
    body.className    = 'report-body empty-state';
    sevEl.innerHTML   = '';
    confEl.style.display = 'none';
    return;
  }
  title.textContent = result.title || 'Diagnóstico procesado';
  meta.innerHTML    = [
    result.host  ? `<span class="tag host">🖥 ${result.host}</span>` : '',
    result.task  ? `<span class="tag">📋 ${result.task}</span>` : '',
    `<span class="tag ts">🕐 ${fmtDate(result.analyzed_at)}</span>`,
    `<span class="tag">${result.provider || '—'}</span>`,
  ].filter(Boolean).join('');
  body.textContent  = result.natural_report || 'Sin contenido.';
  body.className    = 'report-body';
  sevEl.innerHTML   = severityBadge(result.severity);
  if (result.confidence != null) {
    confEl.style.display = '';
    confEl.textContent   = `conf ${(result.confidence * 100).toFixed(0)}%`;
  } else {
    confEl.style.display = 'none';
  }
}

// ── History ────────────────────────────────────────────────
const SEV_COLORS = {
  low: 'var(--sev-low)', medium: 'var(--sev-medium)',
  high: 'var(--sev-high)', critical: 'var(--sev-critical)',
};

function applyHistory(recent) {
  const list  = document.getElementById('historyList');
  const count = document.getElementById('historyCount');
  if (!recent || !recent.length) {
    list.innerHTML = '<div class="empty-state">Sin historial todavía</div>';
    count.textContent = '0 diagnósticos';
    return;
  }
  count.textContent = `${recent.length} diagnóstico${recent.length !== 1 ? 's' : ''}`;
  const items = [...recent].reverse().map(r => {
    const col = SEV_COLORS[r.severity] || 'var(--muted)';
    return `
      <div class="history-item" title="${r.natural_report ? r.natural_report.slice(0,200) : ''}">
        <span class="history-dot" style="background:${col}; box-shadow: 0 0 6px ${col}"></span>
        <div class="history-content">
          <div class="history-title">${r.title || '—'}</div>
          <div class="history-sub">${r.host || '—'} · ${r.task || '—'}</div>
        </div>
        <span class="history-time">${fmtRelative(r.analyzed_at)}</span>
      </div>`;
  }).join('');
  list.innerHTML = items;
}

// ── Main poll loop ─────────────────────────────────────────
async function poll() {
  try {
    const r    = await fetch('/api/dashboard');
    const data = await r.json();
    const sys  = data.system || {};

    applyStatus(sys.status);
    document.getElementById('mQueue').textContent  = String(sys.queue_size ?? 0);
    document.getElementById('mTotal').textContent  = String(sys.total_analyzed ?? 0);
    document.getElementById('mErrors').textContent = String(sys.total_errors ?? 0);
    document.getElementById('mProvider').textContent = sys.llm_provider || '—';
    document.getElementById('mModel').textContent    = sys.llm_model    || '—';
    document.getElementById('opsBox').innerHTML = syntaxHighlight(data);

    applyBanner(sys);
    applyRaw(data.latest_raw);
    applyResult(data.latest_result, sys);
    applyHistory(data.recent_results);

  } catch (err) {
    document.getElementById('statusText').textContent = 'Conexión perdida';
    console.error(err);
  }
}

poll();
setInterval(poll, 2000);
</script>
</body>
</html>
"""
