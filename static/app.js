const API = 'http://localhost:8000';

const portDescriptions = {
  22: 'SSH', 80: 'HTTP', 443: 'HTTPS', 3389: 'RDP', 8080: 'HTTP-ALT'
};

// --- DOM REFERENCES ---
const hostInput     = document.getElementById('host-input');
const btnAddHost    = document.getElementById('btn-add-host');
const hostList      = document.getElementById('host-list');
const addError      = document.getElementById('add-error');
const portTagsEl    = document.getElementById('port-tags');
const portGrid      = document.getElementById('port-grid');
const scanHostLabel = document.getElementById('scan-host-label');
const aiBody        = document.getElementById('ai-body');
const aiRec         = document.getElementById('ai-rec');
const aiRecText     = document.getElementById('ai-rec-text');
const logEntries    = document.getElementById('log-entries');
const metricTotal   = document.getElementById('metric-total');
const metricOpen    = document.getElementById('metric-open');
const metricClosed  = document.getElementById('metric-closed');
const metricHosts   = document.getElementById('metric-hosts');


// --- LOGGING ---
function addLog(level, message) {
  const empty = logEntries.querySelector('.empty-state');
  if (empty) empty.remove();

  const now = new Date();
  const time = now.toTimeString().slice(0, 8);

  const row = document.createElement('div');
  row.className = 'log-row';
  row.innerHTML = `
    <span class="log-time">${time}</span>
    <span class="${level === 'ERROR' ? 'log-level-err' : 'log-level-info'}">${level}</span>
    <span class="log-msg">${message}</span>
  `;

  logEntries.insertBefore(row, logEntries.firstChild);
}


// --- PORT TAGS ---
function renderPortTags() {
  Object.entries(portDescriptions).forEach(([port, name]) => {
    const tag = document.createElement('span');
    tag.className = 'port-tag';
    tag.textContent = `${port} ${name}`;
    tag.dataset.port = port;
    tag.addEventListener('click', () => {
      tag.classList.toggle('active');
    });
    portTagsEl.appendChild(tag);
  });
}

function getSelectedPorts() {
  return [...portTagsEl.querySelectorAll('.port-tag.active')]
    .map(tag => parseInt(tag.dataset.port));
}

// --- METRICS ---
function updateMetrics(scanResult) {
  const open   = scanResult.open_ports.length;
  const closed = scanResult.closed_ports.length;
  metricTotal.textContent  = open + closed;
  metricOpen.textContent   = open;
  metricClosed.textContent = closed;
}

function updateHostCount() {
  const rows = hostList.querySelectorAll('.host-row');
  metricHosts.textContent = rows.length;
}


// --- RENDER HOST ROW ---
function renderHostRow(entry) {
  const row = document.createElement('div');
  row.className = 'host-row';
  row.dataset.id = entry.id;

  row.innerHTML = `
    <div class="host-info">
      <div class="host-dot dot-unknown" id="dot-${entry.id}"></div>
      <span class="host-name">${entry.host}</span>
    </div>
    <div class="host-actions">
      <button class="btn-scan"    data-id="${entry.id}">Scan</button>
      <button class="btn-analyze" data-id="${entry.id}">Analyze</button>
      <button class="btn-remove"  data-id="${entry.id}">✕</button>
    </div>
  `;

  row.querySelector('.btn-scan').addEventListener('click', () => scanHost(entry.id, entry.host));
  row.querySelector('.btn-analyze').addEventListener('click', () => analyzeHost(entry.id, entry.host));
  row.querySelector('.btn-remove').addEventListener('click', () => removeHost(entry.id, row));

  return row;
}


// --- RENDER PORT GRID ---
function renderPortGrid(result) {
  portGrid.innerHTML = '';
  scanHostLabel.textContent = result.host;

  const allPorts = [
    ...result.open_ports.map(p => ({ port: p, open: true })),
    ...result.closed_ports.map(p => ({ port: p, open: false }))
  ].sort((a, b) => a.port - b.port);

  allPorts.forEach(({ port, open }) => {
    const card = document.createElement('div');
    card.className = `port-card ${open ? 'port-open' : 'port-closed'}`;
    card.innerHTML = `
      <div class="port-number">${port}</div>
      <div class="port-service">${portDescriptions[port] || 'unknown'}</div>
      <div class="port-status-label">${open ? 'open' : 'closed'}</div>
    `;
    portGrid.appendChild(card);
  });
}


// --- LOAD HOSTS ON STARTUP ---
async function loadHosts() {
  try {
    const res  = await fetch(`${API}/hosts`);
    const data = await res.json();

    if (data.hosts.length === 0) return;

    const empty = hostList.querySelector('.empty-state');
    if (empty) empty.remove();

    data.hosts.forEach(entry => {
      hostList.appendChild(renderHostRow(entry));
    });

    updateHostCount();
    addLog('INFO', 'Host list loaded');
  } catch (err) {
    addLog('ERROR', 'Could not connect to API');
  }
}


// --- ADD HOST ---
async function addHost() {
  const host = hostInput.value.trim();
  addError.textContent = '';

  if (!host) {
    addError.textContent = 'Please enter a hostname or IP address';
    return;
  }

  const selectedPorts = getSelectedPorts();
  if (selectedPorts.length === 0) {
    addError.textContent = 'Please select at least one port to scan';
    return;
  }

  try {
    const res  = await fetch(`${API}/hosts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ host, ports: selectedPorts })
    });
    const data = await res.json();

    if (!res.ok) {
      addError.textContent = data.detail || 'Failed to add host';
      addLog('ERROR', `Host rejected: ${host} — ${data.detail}`);
      return;
    }

    const empty = hostList.querySelector('.empty-state');
    if (empty) empty.remove();

    hostList.appendChild(renderHostRow(data.entry));
    hostInput.value = '';
    updateHostCount();
    addLog('INFO', `Host added: ${host}`);

  } catch (err) {
    addError.textContent = 'Could not connect to API';
    addLog('ERROR', 'Could not connect to API');
  }
}


// --- SCAN HOST ---
async function scanHost(id, host) {
  addLog('INFO', `Scan started: ${host}`);

  const dot = document.getElementById(`dot-${id}`);
  if (dot) {
    dot.className = 'host-dot dot-unknown';
  }

  portGrid.innerHTML = `<div class="loading">Scanning ${host}...</div>`;
  scanHostLabel.textContent = host;

  try {
    const res  = await fetch(`${API}/hosts/${id}/scan`);
    const data = await res.json();

    if (!res.ok) {
      addLog('ERROR', `Scan failed: ${host} — ${data.detail}`);
      portGrid.innerHTML = `<div class="empty-state">Scan failed: ${data.detail}</div>`;
      return;
    }

    if (dot) {
      dot.className = `host-dot ${data.is_up ? 'dot-up' : 'dot-down'}`;
    }

    renderPortGrid(data);
    updateMetrics(data);
    addLog('INFO', `Scan complete: ${host} | open=[${data.open_ports}] | closed=[${data.closed_ports}]`);

  } catch (err) {
    addLog('ERROR', `Scan error: ${host}`);
    portGrid.innerHTML = `<div class="empty-state">Could not connect to API</div>`;
  }
}


// --- ANALYZE HOST ---
async function analyzeHost(id, host) {
  addLog('INFO', `Analyze requested: ${host}`);
  aiBody.textContent  = `Analyzing ${host}...`;
  aiRec.style.display = 'none';

  try {
    const res  = await fetch(`${API}/hosts/${id}/analyze`, { method: 'POST' });
    const data = await res.json();

    if (!res.ok) {
      aiBody.textContent = data.detail || 'Analysis failed';
      addLog('ERROR', `Analyze failed: ${host} — ${data.detail}`);
      return;
    }

    const lines = data.analysis.split('\n').filter(l => l.trim());
    const last  = lines.pop();
    const body  = lines.join(' ') || data.analysis;

    aiBody.textContent = body;

    if (last && last !== body) {
      aiRecText.textContent  = last;
      aiRec.style.display    = 'block';
    }

    addLog('INFO', `Analyze complete: ${host}`);

  } catch (err) {
    aiBody.textContent = 'Could not connect to API';
    addLog('ERROR', `Analyze error: ${host}`);
  }
}


// --- REMOVE HOST ---
async function removeHost(id, row) {
  const host = row.querySelector('.host-name').textContent;

  try {
    const res = await fetch(`${API}/hosts/${id}`, { method: 'DELETE' });

    if (!res.ok) {
      addLog('ERROR', `Remove failed: ${host}`);
      return;
    }

    row.remove();
    updateHostCount();
    addLog('INFO', `Host removed: ${host}`);

    if (hostList.children.length === 0) {
      hostList.innerHTML = '<div class="empty-state">No hosts added yet</div>';
    }

  } catch (err) {
    addLog('ERROR', `Remove error: ${host}`);
  }
}


// --- EVENT LISTENERS ---
btnAddHost.addEventListener('click', addHost);

hostInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') addHost();
});


// --- INIT ---
renderPortTags();
loadHosts();