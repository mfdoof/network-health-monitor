const BASE = import.meta.env.VITE_API_BASE

// --- Hosts ---

export async function getHosts() {
  const res = await fetch(`${BASE}/hosts`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function addHost(host) {
  const res = await fetch(`${BASE}/hosts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ host })
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function deleteHost(hostId) {
  const res = await fetch(`${BASE}/hosts/${hostId}`, {
    method: 'DELETE'
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function pingHost(hostId) {
  const res = await fetch(`${BASE}/hosts/${hostId}/ping`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function scanHost(hostId, ports) {
  const res = await fetch(`${BASE}/hosts/${hostId}/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ports })
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function analyzeHost(hostId) {
  const res = await fetch(`${BASE}/hosts/${hostId}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

// --- DNS ---

export async function dnsLookup(target) {
  const res = await fetch(`${BASE}/dns/lookup?target=${encodeURIComponent(target)}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function dnsAnalyze(dnsResult) {
  const res = await fetch(`${BASE}/dns/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dns_result: dnsResult })
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getConfig() {
  const res = await fetch(`${BASE}/config`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}