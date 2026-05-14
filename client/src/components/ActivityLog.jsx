import { useEffect, useRef } from 'react'
import styles from '../styles/components/ActivityLog.module.css'

const TYPE_STYLES = {
  INFO: styles.info,
  OK: styles.ok,
  WARN: styles.warn,
  ERROR: styles.error,
}

export default function ActivityLog({ entries }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [entries])

  return (
    <div className={styles.area}>
      <div className={styles.sectionLabel}>
        <span className={styles.corner}>╔══</span>
        {' ACTIVITY LOG '}
        <span className={styles.corner}>══╗</span>
      </div>

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
          <div ref={bottomRef} />
        </div>
      )}

      <div className={styles.footer}>
        <span className={styles.corner}>╚{'═'.repeat(40)}╝</span>
      </div>
    </div>
  )
}