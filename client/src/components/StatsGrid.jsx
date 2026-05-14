import styles from '../styles/components/StatsGrid.module.css'

export default function StatsGrid({ stats }) {
  return (
    <div className={styles.grid}>
      <div className={styles.card}>
        <div className={styles.label}>HOSTS</div>
        <div className={`${styles.value} ${styles.hosts}`}>{stats.hosts}</div>
      </div>
      <div className={styles.card}>
        <div className={styles.label}>SCANNED</div>
        <div className={`${styles.value} ${styles.neutral}`}>{stats.scanned}</div>
      </div>
      <div className={styles.card}>
        <div className={styles.label}>OPEN</div>
        <div className={`${styles.value} ${styles.open}`}>{stats.open}</div>
      </div>
      <div className={styles.card}>
        <div className={styles.label}>CLOSED</div>
        <div className={`${styles.value} ${styles.closed}`}>{stats.closed}</div>
      </div>
    </div>
  )
}