import styles from '../styles/components/ActivityLog.module.css'

const TYPE_STYLES = {
  INFO:  styles.info,
  OK:    styles.ok,
  WARN:  styles.warn,
  ERROR: styles.error,
}

export default function ActivityLog({ entries }) {
  return (
    <div className={styles.area}>
      <div className={styles.sectionLabel}>ACTIVITY LOG</div>

      {entries.length === 0 ? (
        <div className={styles.empty}>No activity yet</div>
      ) : (
        <div className={styles.rows}>
          {entries.map(entry => (
            <div key={entry.id} className={styles.row}>
              <span className={styles.time}>{entry.time}</span>
              <span className={`${styles.badge} ${TYPE_STYLES[entry.type] ?? styles.info}`}>
                {entry.type}
              </span>
              <span className={styles.msg}>
                {entry.message}
                {entry.host && (
                  <span className={styles.host}> {entry.host}</span>
                )}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}