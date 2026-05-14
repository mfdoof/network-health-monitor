import styles from '../styles/components/HostRow.module.css'
import ScanPanel from './ScanPanel'

export default function HostRow({
  host,
  onRemove,
  onPing,
  onToggleScan,
  onScan,
  onAnalyze
}) {
  const statusClass = host.pingResult
    ? host.pingResult.reachable
      ? styles.statusOnline
      : styles.statusUnreachable
    : styles.statusNeutral

  return (
    <div className={styles.wrapper}>
      <div className={styles.row}>
        <div className={`${styles.statusDot} ${statusClass}`} />

        <span className={styles.hostName} title={host.host}>
          {host.host}
        </span>

        <div className={styles.actions}>
          <button
            className={`${styles.btn} ${styles.ping}`}
            onClick={() => onPing(host.id)}
            disabled={host.isLoading}
          >
            Ping
          </button>
          <button
            className={`${styles.btn} ${styles.scan} ${host.scanOpen ? styles.scanActive : ''}`}
            onClick={() => onToggleScan(host.id)}
            disabled={host.isLoading}
          >
            Scan
          </button>
          <button
            className={`${styles.btn} ${styles.analyze}`}
            onClick={() => onAnalyze(host.id)}
            disabled={host.isLoading || !host.scanResults}
            title={!host.scanResults ? 'Run a scan first' : ''}
          >
            Analyze
          </button>
          <button
            className={styles.remove}
            onClick={() => onRemove(host.id)}
            disabled={host.isLoading}
          >
            &times;
          </button>
        </div>
      </div>

      {host.isLoading && (
        <div className={styles.loadingBar} />
      )}

      {host.scanOpen && (
        <ScanPanel
          hostId={host.id}
          onScan={onScan}
          onClose={() => onToggleScan(host.id)}
        />
      )}
    </div>
  )
}