import styles from '../styles/components/AIAnalysis.module.css'

export default function AIAnalysis({ host, analysis }) {
  return (
    <div className={styles.area}>
      <div className={styles.header}>
        <span className={styles.title}>AI DIAGNOSTIC</span>
        <span className={styles.model}>ollama / llama3.2</span>
        <span className={styles.hostTag}>{host}</span>
      </div>
      <p className={styles.text}>{analysis}</p>
    </div>
  )
}