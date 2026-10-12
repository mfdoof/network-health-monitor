import { useState, useEffect } from 'react'
import { getHosts, addHost, deleteHost, pingHost, scanHost, analyzeHost, dnsLookup, dnsAnalyze, getConfig } from './api'
import TopBar from './components/TopBar'
import LeftPanel from './components/LeftPanel'
import RightPanel from './components/RightPanel'
import DNSPage from './pages/DNSPage'
import styles from './styles/App.module.css'

// --- Helpers ---

function createLogEntry(type, message, host = null) {
  return {
    id: crypto.randomUUID(),
    time: new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    type,
    message,
    host
  }
}

function updateHost(setHosts, hostId, patch) {
  setHosts(prev => prev.map(h => h.id === hostId ? { ...h, ...patch } : h))
}

function parseError(err) {
  if (err.isRateLimit) return '429'
  return err.message
}

function llmDisabledReason(config) {
  if (config === null) return 'Loading AI settings...'
  if (config.error) return 'Could not load AI settings from the API'
  if (!config.llm_enabled) return 'AI analysis is off. Set LLM_BASE_URL and LLM_MODEL in .env'
  return ''
}

export default function App() {
  const [hosts, setHosts] = useState([])
  const [activityLog, setActivityLog] = useState([])
  const [activePage, setActivePage] = useState('monitor')
  const [dnsResult, setDnsResult] = useState(null)
  const [dnsHistory, setDnsHistory] = useState([])
  const [llmConfig, setLlmConfig] = useState(null)

  function log(type, message, host = null) {
    setActivityLog(prev => [createLogEntry(type, message, host), ...prev].slice(0, 100))
  }

  // --- Load hosts on mount ---
  useEffect(() => {
    getHosts()
      .then(data => {
        const loaded = data.hosts.map(h => ({
          ...h,
          pingResult: null,
          scanResults: null,
          scanOpen: false,
          isLoading: false
        }))
        setHosts(loaded)
        log('INFO', `Loaded ${loaded.length} host(s) from server`)
      })
      .catch(err => log('ERROR', `Failed to load hosts: ${parseError(err)}`))
  }, [])

  useEffect(() => {
    getConfig()
      .then(data => {
        setLlmConfig(data)
        if (!data.llm_enabled) log('WARN', 'AI analysis is off. Set LLM_BASE_URL and LLM_MODEL in .env')
      })
      .catch(err => {
        setLlmConfig({ error: true })
        log('ERROR', `Failed to load AI settings: ${parseError(err)}`)
      })
  }, [])

  // --- Add host ---
  async function handleAddHost(hostValue) {
    try {
      const data = await addHost(hostValue)
      setHosts(prev => [...prev, {
        ...data.entry,
        pingResult: null,
        scanResults: null,
        scanOpen: false,
        isLoading: false
      }])
      log('INFO', 'Host added', hostValue)
    } catch (err) {
      const msg = parseError(err)
      log('ERROR', `Failed to add host: ${msg}`, hostValue)
    }
  }

  // --- Remove host ---
  async function handleRemoveHost(hostId) {
    const host = hosts.find(h => h.id === hostId)
    try {
      await deleteHost(hostId)
      setHosts(prev => prev.filter(h => h.id !== hostId))
      log('INFO', 'Host removed', host?.host)
    } catch (err) {
      const msg = parseError(err)
      log('ERROR', `Failed to remove host: ${msg}`, host?.host)
    }
  }

  // --- Ping ---
  async function handlePing(hostId) {
    const host = hosts.find(h => h.id === hostId)
    updateHost(setHosts, hostId, { isLoading: true })
    log('INFO', 'Ping started', host?.host)
    try {
      const result = await pingHost(hostId)
      updateHost(setHosts, hostId, { pingResult: result, isLoading: false })
      log('OK', `Ping complete — reachable=${result.reachable} latency=${result.latency_ms}ms loss=${result.packet_loss_percent}%`, host?.host)
    } catch (err) {
      const msg = parseError(err)
      updateHost(setHosts, hostId, { isLoading: false })
      if (msg === '429') {
        log('WARN', 'Rate limit hit — wait a moment before pinging again', host?.host)
      } else {
        log('ERROR', `Ping failed: ${msg}`, host?.host)
      }
    }
  }

  // --- Toggle scan panel ---
  function handleToggleScan(hostId) {
    setHosts(prev => prev.map(h => ({
      ...h,
      scanOpen: h.id === hostId ? !h.scanOpen : false
    })))
  }

  // --- Run scan ---
  async function handleScan(hostId, ports) {
    const host = hosts.find(h => h.id === hostId)
    updateHost(setHosts, hostId, { isLoading: true, scanOpen: false })
    log('INFO', `Scanning ${ports.length} port(s)`, host?.host)
    try {
      const result = await scanHost(hostId, ports)
      updateHost(setHosts, hostId, {
        scanResults: {
          ...result,
          scanned_at: new Date().toLocaleTimeString('en-GB', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
          })
        },
        isLoading: false
      })
      log('OK', `Scan complete — ${result.open_ports.length} open, ${result.closed_ports.length} closed`, host?.host)
    } catch (err) {
      const msg = parseError(err)
      updateHost(setHosts, hostId, { isLoading: false })
      if (msg === '429') {
        log('WARN', 'Rate limit hit — wait a moment before scanning again', host?.host)
      } else {
        log('ERROR', `Scan failed: ${msg}`, host?.host)
      }
    }
  }

  // --- Analyze ---
  async function handleAnalyze(hostId) {
    const host = hosts.find(h => h.id === hostId)
    if (!host?.scanResults) {
      log('WARN', 'No scan data — run a scan first', host?.host)
      return
    }
    updateHost(setHosts, hostId, { isLoading: true })
    log('INFO', 'AI analysis requested', host?.host)
    try {
      const result = await analyzeHost(hostId)
      updateHost(setHosts, hostId, {
        scanResults: { ...host.scanResults, analysis: result.analysis, analysisId: crypto.randomUUID() },
        isLoading: false
      })
      log('OK', 'AI analysis complete', host?.host)
    } catch (err) {
      const msg = parseError(err)
      updateHost(setHosts, hostId, { isLoading: false })
      if (msg === '429') {
        log('WARN', 'Rate limit hit — wait a moment before analyzing again', host?.host)
      } else {
        log('ERROR', `Analysis failed: ${msg}`, host?.host)
      }
    }
  }

  // --- DNS Lookup ---
  async function handleDnsLookup(target) {
    log('INFO', 'DNS lookup started', target)
    try {
      const result = await dnsLookup(target)
      setDnsResult(result)
      setDnsHistory(prev => {
        const filtered = prev.filter(h => h.target !== target)
        return [{ target, lookup_type: result.lookup_type }, ...filtered].slice(0, 10)
      })
      log('OK', `DNS lookup complete — ${result.lookup_type}`, target)
    } catch (err) {
      const msg = parseError(err)
      if (msg === '429') {
        log('WARN', 'Rate limit hit — wait a moment before looking up again', target)
      } else {
        log('ERROR', `DNS lookup failed: ${msg}`, target)
      }
    }
  }

  // --- DNS Analyze ---
  async function handleDnsAnalyze(result) {
    log('INFO', 'DNS AI analysis requested', result.target)
    try {
      const data = await dnsAnalyze(result.target)
      setDnsResult(prev => ({ ...prev, analysis: data.analysis, analysisId: crypto.randomUUID() }))
      log('OK', 'DNS AI analysis complete', result.target)
    } catch (err) {
      const msg = parseError(err)
      if (msg === '429') {
        log('WARN', 'Rate limit hit — wait a moment before analyzing again', result.target)
      } else {
        log('ERROR', `DNS analysis failed: ${msg}`, result.target)
      }
    }
  }

  // --- Stats derived from state ---
  const stats = {
    hosts: hosts.length,
    scanned: hosts.filter(h => h.scanResults).length,
    open: hosts.reduce((acc, h) => acc + (h.scanResults?.open_ports?.length ?? 0), 0),
    closed: hosts.reduce((acc, h) => acc + (h.scanResults?.closed_ports?.length ?? 0), 0)
  }

  const analyzeDisabledReason = llmDisabledReason(llmConfig)

  // --- Active ping/scan results (most recent) ---
  const activeHost = [...hosts].reverse().find(h => h.pingResult || h.scanResults) ?? null

  return (
    <div className={styles.app}>
      <TopBar activePage={activePage} onNavigate={setActivePage} llmConfig={llmConfig} />

      {activePage === 'monitor' ? (
        <div className={styles.layout}>
          <LeftPanel
            hosts={hosts}
            onAddHost={handleAddHost}
            onRemoveHost={handleRemoveHost}
            onPing={handlePing}
            onToggleScan={handleToggleScan}
            onScan={handleScan}
            onAnalyze={handleAnalyze}
            analyzeDisabledReason={analyzeDisabledReason}
          />
          <RightPanel
            stats={stats}
            hosts={hosts}
            activeHost={activeHost}
            activityLog={activityLog}
          />
        </div>
      ) : (
        <DNSPage
          dnsResult={dnsResult}
          dnsHistory={dnsHistory}
          onLookup={handleDnsLookup}
          onAnalyze={handleDnsAnalyze}
          analyzeDisabledReason={analyzeDisabledReason}
          activityLog={activityLog}
        />
      )}
    </div>
  )
}