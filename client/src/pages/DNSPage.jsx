import { useState } from 'react'
import ActivityLog from '../components/ActivityLog'
import styles from '../styles/components/DNSPage.module.css'

export default function DNSPage({ dnsResult, dnsHistory, onLookup, onAnalyze, activityLog }) {
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  async function handleLookup() {
    const val = input.trim()
    if (!val) return
    setIsLoading(true)
    await onLookup(val)
    setIsLoading(false)
  }

  async function handleAnalyze() {
    if (!dnsResult) return
    setIsAnalyzing(true)
    await onAnalyze(dnsResult)
    setIsAnalyzing(false)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') handleLookup()
  }

  function handleHistoryClick(target) {
    setInput(target)
    onLookup(target)
  }

  return (
    <div className={styles.page}>

      {/* Left Panel */}
      <div className={styles.leftPanel}>

        {/* Search */}
        <div className={styles.card}>
          <div className={styles.sectionLabel}>DNS LOOKUP</div>
          <div className={styles.inputRow}>
            <input
              className={styles.input}
              placeholder="hostname or IP address"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
            />
            <button
              className={styles.lookupBtn}
              onClick={handleLookup}
              disabled={isLoading || !input.trim()}
            >
              {isLoading ? '...' : 'LOOKUP'}
            </button>
          </div>
        </div>

        {/* History */}
        <div className={`${styles.card} ${styles.historyCard}`}>
          <div className={styles.sectionLabel}>RECENT LOOKUPS</div>
          {dnsHistory.length === 0 ? (
            <div className={styles.empty}>No lookups yet</div>
          ) : (
            <div className={styles.historyList}>
              {dnsHistory.map((entry, i) => (
                <div
                  key={i}
                  className={styles.historyRow}
                  onClick={() => handleHistoryClick(entry.target)}
                >
                  <span className={`${styles.typeBadge} ${entry.lookup_type === 'forward' ? styles.forward : styles.reverse}`}>
                    {entry.lookup_type === 'forward' ? 'FWD' : 'REV'}
                  </span>
                  <span className={styles.historyTarget}>{entry.target}</span>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      {/* Right Panel */}
      <div className={styles.rightPanel}>

        {/* DNS Result */}
        {dnsResult ? (
          <>
            {/* Summary */}
            <div className={styles.summaryCard}>
              <div className={styles.summaryHeader}>
                <div className={styles.sectionLabel}>
                  {dnsResult.lookup_type === 'forward' ? 'FORWARD LOOKUP' : 'REVERSE LOOKUP'}
                </div>
                <span className={styles.targetTag}>{dnsResult.target}</span>
                <button
                  className={styles.analyzeBtn}
                  onClick={handleAnalyze}
                  disabled={isAnalyzing || !!dnsResult.analysis}
                  title={dnsResult.analysis ? 'Analysis already done' : ''}
                >
                  {isAnalyzing ? 'Analyzing...' : 'AI Analyze'}
                </button>
              </div>
              {dnsResult.errors?.length > 0 && (
                <div className={styles.errors}>
                  {dnsResult.errors.map((e, i) => (
                    <div key={i} className={styles.errorRow}>⚠ {e}</div>
                  ))}
                </div>
              )}
            </div>

            {/* Forward lookup records */}
            {dnsResult.lookup_type === 'forward' && (
              <div className={styles.recordsGrid}>

                {/* A Records */}
                <div className={styles.recordCard}>
                  <div className={styles.recordLabel}>A RECORDS <span className={styles.recordCount}>{dnsResult.a_records?.length ?? 0}</span></div>
                  {dnsResult.a_records?.length > 0 ? (
                    dnsResult.a_records.map((r, i) => (
                      <div key={i} className={styles.recordRow}>
                        <span className={styles.recordValue}>{r.address}</span>
                        <span className={styles.recordTtl}>TTL {r.ttl}</span>
                      </div>
                    ))
                  ) : (
                    <div className={styles.recordEmpty}>None found</div>
                  )}
                </div>

                {/* AAAA Records */}
                <div className={styles.recordCard}>
                  <div className={styles.recordLabel}>AAAA RECORDS <span className={styles.recordCount}>{dnsResult.aaaa_records?.length ?? 0}</span></div>
                  {dnsResult.aaaa_records?.length > 0 ? (
                    dnsResult.aaaa_records.map((r, i) => (
                      <div key={i} className={styles.recordRow}>
                        <span className={styles.recordValue}>{r.address}</span>
                        <span className={styles.recordTtl}>TTL {r.ttl}</span>
                      </div>
                    ))
                  ) : (
                    <div className={styles.recordEmpty}>None found</div>
                  )}
                </div>

                {/* MX Records */}
                <div className={styles.recordCard}>
                  <div className={styles.recordLabel}>MX RECORDS <span className={styles.recordCount}>{dnsResult.mx_records?.length ?? 0}</span></div>
                  {dnsResult.mx_records?.length > 0 ? (
                    dnsResult.mx_records.map((r, i) => (
                      <div key={i} className={styles.recordRow}>
                        <span className={styles.priorityBadge}>{r.preference}</span>
                        <span className={styles.recordValue}>{r.host}</span>
                        <span className={styles.recordTtl}>TTL {r.ttl}</span>
                      </div>
                    ))
                  ) : (
                    <div className={styles.recordEmpty}>None found</div>
                  )}
                </div>

                {/* NS Records */}
                <div className={styles.recordCard}>
                  <div className={styles.recordLabel}>NS RECORDS <span className={styles.recordCount}>{dnsResult.ns_records?.length ?? 0}</span></div>
                  {dnsResult.ns_records?.length > 0 ? (
                    dnsResult.ns_records.map((r, i) => (
                      <div key={i} className={styles.recordRow}>
                        <span className={styles.recordValue}>{r.nameserver}</span>
                        <span className={styles.recordTtl}>TTL {r.ttl}</span>
                      </div>
                    ))
                  ) : (
                    <div className={styles.recordEmpty}>None found</div>
                  )}
                </div>

              </div>
            )}

            {/* Reverse lookup records */}
            {dnsResult.lookup_type === 'reverse' && (
              <div className={styles.recordCard}>
                <div className={styles.recordLabel}>PTR RECORDS <span className={styles.recordCount}>{dnsResult.ptr_records?.length ?? 0}</span></div>
                {dnsResult.ptr_records?.length > 0 ? (
                  dnsResult.ptr_records.map((r, i) => (
                    <div key={i} className={styles.recordRow}>
                      <span className={styles.recordValue}>{r.hostname}</span>
                      <span className={styles.recordTtl}>TTL {r.ttl}</span>
                    </div>
                  ))
                ) : (
                  <div className={styles.recordEmpty}>No PTR records found</div>
                )}
              </div>
            )}

            {/* AI Analysis */}
            {dnsResult.analysis && (
              <div className={styles.aiCard}>
                <div className={styles.aiHeader}>
                  <span className={styles.aiTitle}>AI DIAGNOSTIC</span>
                  <span className={styles.aiModel}>ollama / llama3.2</span>
                  <span className={styles.targetTag}>{dnsResult.target}</span>
                </div>
                <p className={styles.aiText}>{dnsResult.analysis}</p>
              </div>
            )}
          </>
        ) : (
          <div className={styles.emptyState}>
            <div className={styles.emptyTitle}>DOOF DNS LOOKUP</div>
            <div className={styles.emptyHint}>Enter a hostname or IP address to begin</div>
          </div>
        )}

        {/* Activity Log */}
        <ActivityLog entries={activityLog} />

      </div>
    </div>
  )
}