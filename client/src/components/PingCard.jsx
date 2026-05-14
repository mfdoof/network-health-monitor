import styles from '../styles/components/PingCard.module.css'

export default function PingCard({ host, result }) {
 const { reachable, latency_ms, packets_sent, packets_received, packet_loss_percent } = result

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={`${styles.status} ${reachable ? styles.reachable : styles.unreachable}`}>
          {reachable ? 'REACHABLE' : 'UNREACHABLE'}
        </span>
        <span className={styles.host}>{host}</span>
      </div>

      <div className={styles.stats}>
        <div className={styles.stat}>
          <div className={styles.statLabel}>LATENCY</div>
          <div className={styles.statValue}>
            {latency_ms ?? '—'} <span>ms</span>
          </div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statLabel}>PACKETS</div>
          <div className={styles.statValue}>
            {packets_received ?? '—'} / {packets_sent ?? '—'}
          </div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statLabel}>LOSS</div>
          <div className={`${styles.statValue} ${lossColor(packet_loss_percent)}`}>
            {packet_loss_percent ?? '—'}<span>%</span>
        </div>
        </div>
      </div>
    </div>
  )
}

function lossColor(loss) {
  if (loss === null || loss === undefined) return ''
  if (loss === 0) return styles.lossGood
  if (loss < 50) return styles.lossWarn
  return styles.lossBad
}