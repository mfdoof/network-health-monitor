import styles from '../styles/components/ScanResults.module.css'

const PORT_LABELS = {
  21:   'FTP',
  22:   'SSH',
  25:   'SMTP',
  80:   'HTTP',
  443:  'HTTPS',
  3306: 'MySQL',
  3389: 'RDP',
  5432: 'PostgreSQL',
  6379: 'Redis',
  8080: 'HTTP-ALT',
}

export default function ScanResults({ host, result }) {
  const { open_ports, closed_ports, is_up } = result
  const allPorts = [
    ...open_ports.map(p => ({ port: p, open: true })),
    ...closed_ports.map(p => ({ port: p, open: false }))
  ].sort((a, b) => a.port - b.port)

  return (
    <div className={styles.area}>
      <div className={styles.header}>
        <div className={styles.sectionLabel}>SCAN RESULTS</div>
        <div className={styles.hostTag}>{host}</div>
        <div className={`${styles.upBadge} ${is_up ? styles.up : styles.down}`}>
          {is_up ? 'UP' : 'DOWN'}
        </div>
      </div>

      {allPorts.length === 0 ? (
        <div className={styles.empty}>No ports scanned</div>
      ) : (
        allPorts.map(({ port, open }) => (
          <div key={port} className={styles.row}>
            <span className={styles.portNum}>{port}</span>
            <span className={styles.portService}>
              {PORT_LABELS[port] ?? 'unknown'}
            </span>
            <span className={`${styles.badge} ${open ? styles.badgeOpen : styles.badgeClosed}`}>
              {open ? 'OPEN' : 'CLOSED'}
            </span>
          </div>
        ))
      )}
    </div>
  )
}