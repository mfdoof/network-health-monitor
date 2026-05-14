import { useState } from 'react'
import styles from '../styles/components/ScanPanel.module.css'

const ALL_PORTS = [
  { port: 22,   label: 'SSH' },
  { port: 80,   label: 'HTTP' },
  { port: 443,  label: 'HTTPS' },
  { port: 3389, label: 'RDP' },
  { port: 8080, label: 'HTTP-ALT' },
  { port: 21,   label: 'FTP' },
  { port: 25,   label: 'SMTP' },
  { port: 3306, label: 'MySQL' },
  { port: 5432, label: 'PostgreSQL' },
  { port: 6379, label: 'Redis' },
]

const DEFAULT_PORTS = [22, 80, 443]

export default function ScanPanel({ hostId, onScan, onClose }) {
  const [selected, setSelected] = useState(DEFAULT_PORTS)

  function togglePort(port) {
    setSelected(prev =>
      prev.includes(port)
        ? prev.filter(p => p !== port)
        : [...prev, port]
    )
  }

  function handleScan() {
    if (selected.length === 0) return
    onScan(hostId, selected)
  }

  return (
    <div className={styles.panel}>
      <div className={styles.label}>SELECT PORTS TO SCAN</div>

      <div className={styles.chips}>
        {ALL_PORTS.map(({ port, label }) => (
          <button
            key={port}
            className={`${styles.chip} ${selected.includes(port) ? styles.on : ''}`}
            onClick={() => togglePort(port)}
          >
            {port} {label}
          </button>
        ))}
      </div>

      <div className={styles.footer}>
        <span className={styles.selectedCount}>
          {selected.length} port{selected.length !== 1 ? 's' : ''} selected
        </span>
        <div className={styles.footerBtns}>
          <button className={styles.cancelBtn} onClick={onClose}>
            Cancel
          </button>
          <button
            className={styles.scanBtn}
            onClick={handleScan}
            disabled={selected.length === 0}
          >
            RUN SCAN
          </button>
        </div>
      </div>
    </div>
  )
}