import styles from '../styles/components/LeftPanel.module.css'
import HostRow from './HostRow'
import { useState } from 'react'

export default function LeftPanel({
  hosts,
  onAddHost,
  onRemoveHost,
  onPing,
  onToggleScan,
  onScan,
  onAnalyze
}) {
  const [input, setInput] = useState('')

  function handleAdd() {
    const val = input.trim()
    if (!val) return
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
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button className={styles.addBtn} onClick={handleAdd}>
            + ADD
          </button>
        </div>
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

    </div>
  )
}