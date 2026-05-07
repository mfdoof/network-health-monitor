const API = 'https://doof.quest';

const dnsInput    = document.getElementById('dns-input');
const btnLookup   = document.getElementById('btn-lookup');
const dnsError    = document.getElementById('dns-error');
const dnsResults  = document.getElementById('dns-results');
const dnsBody     = document.getElementById('dns-body');
const dnsAiCard   = document.getElementById('dns-ai-card');
const dnsAiBody   = document.getElementById('dns-ai-body');

let lastDnsResult = null;


// --- LOOKUP ---
async function runLookup() {
  const target = dnsInput.value.trim();
  dnsError.textContent = '';

  if (!target) {
    dnsError.textContent = 'Please enter a domain or IP address';
    return;
  }

  dnsResults.style.display = 'block';
  dnsAiCard.style.display  = 'none';
  dnsBody.innerHTML = `<div class="loading">Looking up ${target}...</div>`;

  try {
    const res  = await fetch(`${API}/dns/lookup?target=${encodeURIComponent(target)}`);
    const data = await res.json();

    if (!res.ok) {
      dnsBody.innerHTML = `<div class="empty-state">${data.detail || 'Lookup failed'}</div>`;
      return;
    }

    lastDnsResult = data;
    renderDnsResults(data);
    showAnalyzeButton();

  } catch (err) {
    dnsBody.innerHTML = `<div class="empty-state">Could not connect to API</div>`;
  }
}


// --- RENDER RESULTS ---
function renderDnsResults(data) {
  if (data.lookup_type === 'reverse') {
    const ptrs = data.ptr_records.length
      ? data.ptr_records.map(r => `
          <div class="dns-row">
            <span class="dns-key">PTR</span>
            <span class="dns-val">${r.hostname}</span>
            <span class="dns-ttl">TTL ${r.ttl}</span>
          </div>`).join('')
      : `<div class="empty-state">No PTR record found</div>`;

    dnsBody.innerHTML = `
      <div class="dns-target">Reverse lookup — ${data.target}</div>
      ${ptrs}
      ${renderErrors(data.errors)}
    `;
    return;
  }

  // Forward lookup
  dnsBody.innerHTML = `
    <div class="dns-target">${data.target}</div>
    ${renderRecordGroup('A', data.a_records, r => r.address, r => r.ttl)}
    ${renderRecordGroup('AAAA', data.aaaa_records, r => r.address, r => r.ttl)}
    ${renderRecordGroup('MX', data.mx_records, r => `${r.host} <span class="dns-pref">priority ${r.preference}</span>`, r => r.ttl)}
    ${renderRecordGroup('NS', data.ns_records, r => r.nameserver, r => r.ttl)}
    ${renderErrors(data.errors)}
  `;
}

function renderRecordGroup(type, records, labelFn, ttlFn) {
  if (!records || records.length === 0) return '';
  return records.map(r => `
    <div class="dns-row">
      <span class="dns-key">${type}</span>
      <span class="dns-val">${labelFn(r)}</span>
      <span class="dns-ttl">TTL ${ttlFn(r)}</span>
    </div>
  `).join('');
}

function renderErrors(errors) {
  if (!errors || errors.length === 0) return '';
  return errors.map(e => `
    <div class="dns-row dns-row-error">
      <span class="dns-key-err">WARN</span>
      <span class="dns-val-err">${e}</span>
    </div>
  `).join('');
}


// --- ANALYZE BUTTON ---
function showAnalyzeButton() {
  dnsAiCard.style.display = 'block';
  dnsAiBody.innerHTML = `
    <button class="btn-analyze" id="btn-dns-analyze">Analyze with Ollama</button>
  `;
  document.getElementById('btn-dns-analyze').addEventListener('click', runAnalyze);
}


// --- ANALYZE ---
async function runAnalyze() {
  if (!lastDnsResult) return;

  dnsAiBody.textContent = 'Analyzing...';

  try {
    const res  = await fetch(`${API}/dns/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dns_result: lastDnsResult })
    });
    const data = await res.json();

    if (!res.ok) {
      dnsAiBody.textContent = data.detail || 'Analysis failed';
      return;
    }

    dnsAiBody.textContent = data.analysis;

  } catch (err) {
    dnsAiBody.textContent = 'Could not connect to API';
  }
}


// --- EVENTS ---
btnLookup.addEventListener('click', runLookup);

dnsInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') runLookup();
});