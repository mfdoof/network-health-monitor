import styles from '../styles/components/LeftPanel.module.css'
import HostRow from './HostRow'
import { useState } from 'react'

const FROG_OPEN = `
  / \\
 _(I)(I)_
( _ .. _ )
\`.\\--'.') 
( ,-./  \\,-.
(_( || || )_)
 __\\\\||--||'/__
\`-._||/\\/||_.-'
   \`--'\`--'`.trim()

const FROG_BLINK = `
  / \\
 _(-)(-)_
( _ .. _ )
\`.\\--'.') 
( ,-./  \\,-.
(_( || || )_)
 __\\\\||--||'/__
\`-._||/\\/||_.-'
   \`--'\`--'`.trim()

export default function LeftPanel({
  hosts,
  onAddHost,
  onRemoveHost,
  onPing,
  onToggleScan,
  onScan,
  onAnalyze
}) {
  const [error, setError] = useState('')
  const [input, setInput] = useState('')

  function isValidHost(val) {
    const ipv4 = /^(\d{1,3}\.){3}\d{1,3}$/
    if (ipv4.test(val)) {
      const parts = val.split('.').map(Number)
      return parts.every(p => p >= 0 && p <= 255)
    }
    const hostname = /^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/
    return hostname.test(val)
  }

  function handleAdd() {
    const val = input.trim()
    if (!val) return
    if (!isValidHost(val)) {
      setError('Invalid hostname or IP address')
      return
    }
    setError('')
    onAddHost(val)
    setInput('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') handleAdd()
  }

  return (
    <div className={styles.panel}>

      {/* Add Host */}
      <div className={styles.card}>
        <div className={styles.sectionLabel}>ADD HOST</div>
        <div className={styles.inputRow}>
          <input
            className={styles.input}
            placeholder="192.168.1.1 or google.com"
            value={input}
            onChange={e => { setInput(e.target.value); setError('') }}
            onKeyDown={handleKeyDown}
          />
          <button className={styles.addBtn} onClick={handleAdd}>
            + ADD
          </button>
        </div>
        {error && <div className={styles.inputError}>{error}</div>}
      </div>

      {/* Host List */}
      <div className={`${styles.card} ${styles.hostListCard}`}>
        <div className={styles.sectionLabel}>MONITORED HOSTS</div>
        {hosts.length === 0 ? (
          <div className={styles.emptyHint}>No hosts added yet</div>
        ) : (
          <div className={styles.hostList}>
            {hosts.map(host => (
              <HostRow
                key={host.id}
                host={host}
                onRemove={onRemoveHost}
                onPing={onPing}
                onToggleScan={onToggleScan}
                onScan={onScan}
                onAnalyze={onAnalyze}
              />
            ))}
          </div>
        )}
      </div>

      {/* Frog Server Card */}
        <div className={styles.froggieCard}>
        <div className={styles.froggieLabel}>
            <span className={styles.corner}>←</span>
            {' DOOF SERVER '}
            <span className={styles.corner}>→</span>
        </div>

        <div className={styles.froggieSpacer}>
            <pre className={`${styles.froggie} ${styles.frogOpen}`}>{FROG_OPEN}</pre>
            <pre className={`${styles.froggie} ${styles.frogBlink}`}>{FROG_BLINK}</pre>
        </div>

        <p className={styles.froggieDisclaimer}>
            For internal use only. Do not scan hosts you do not own or have explicit permission to test. Use responsibly.
        </p>

        <div className={styles.froggieStatus}>STAY VIGILANT</div>
        </div>
    </div>
  )
}