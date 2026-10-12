const BASE = import.meta.env.VITE_API_BASE || '/api'

// Throws an Error carrying the API's "detail" message and the HTTP status
async function request(url, options) {
  const res = await fetch(url, options)
  if (res.ok) return res.json()

  let body = null
  try {
    body = await res.json()
  } catch {
    // non-JSON error body
  }

  const err = new Error(errorMessage(res.status, body))
  err.status = res.status
  // Our own rate limiter (slowapi) answers 429 without a "detail" field
  err.isRateLimit = res.status === 429 && !body?.detail
  throw err
}

function errorMessage(status, body) {
  const detail = body?.detail
  if (typeof detail === 'string') return detail
  // 422 validation errors: a list of { loc, msg }
  if (Array.isArray(detail) && detail.length) {
    const field = detail[0].loc?.at(-1)
    const msg = String(detail[0].msg ?? '').replace(/^Value error, /, '')
    return field ? `${field}: ${msg}` : msg
  }
  return `Request failed (${status})`
}

// --- Hosts ---

export async function getHosts() {
  return request(`${BASE}/hosts`)
}

export async function addHost(host) {
  return request(`${BASE}/hosts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ host })
  })
}

export async function deleteHost(hostId) {
  return request(`${BASE}/hosts/${hostId}`, {
    method: 'DELETE'
  })
}

export async function pingHost(hostId) {
  return request(`${BASE}/hosts/${hostId}/ping`)
}

export async function scanHost(hostId, ports) {
  return request(`${BASE}/hosts/${hostId}/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ports })
  })
}

export async function analyzeHost(hostId) {
  return request(`${BASE}/hosts/${hostId}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
}

// --- DNS ---

export async function dnsLookup(target) {
  return request(`${BASE}/dns/lookup?target=${encodeURIComponent(target)}`)
}

export async function dnsAnalyze(target) {
  return request(`${BASE}/dns/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target })
  })
}

export async function getConfig() {
  return request(`${BASE}/config`)
}