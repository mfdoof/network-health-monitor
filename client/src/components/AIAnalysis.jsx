import { useEffect, useState } from 'react'
import styles from '../styles/components/AIAnalysis.module.css'

function formatAsLines(text) {
  if (!text) return []
  return text
    .split(/(?<=[.!?])\s+/)
    .filter(Boolean)
}

export default function AIAnalysis({ host, analysis }) {
  // Characters revealed so far, tagged with the text they belong to,
  // so a new analysis starts from 0 without resetting state in the effect
  const [progress, setProgress] = useState({ text: analysis, shown: 0 })
  const shown = progress.text === analysis ? progress.shown : 0
  const displayed = analysis.slice(0, shown)
  const done = shown >= analysis.length

  useEffect(() => {
    let i = 0
    const interval = setInterval(() => {
      i++
      setProgress({ text: analysis, shown: i })
      if (i >= analysis.length) clearInterval(interval)
    }, 18)
    return () => clearInterval(interval)
  }, [analysis])

  const lines = formatAsLines(displayed)
  const isLastLine = (idx) => idx === lines.length - 1

  return (
    <div className={styles.area}>
      <div className={styles.header}>
        <div className={styles.sectionLabel}>
          <span className={styles.corner}>←</span>
          {' AI DIAGNOSTIC '}
          <span className={styles.corner}>→</span>
        </div>
        <span className={styles.hostTag}>{host}</span>
      </div>

      <div className={styles.terminal}>
        <div className={styles.terminalPrompt}>
          <span className={styles.promptUser}>nhm</span>
          <span className={styles.promptAt}>@</span>
          <span className={styles.promptHost}>{host}</span>
          <span className={styles.promptSep}>:~$</span>
          <span className={styles.promptCmd}> analyze</span>
        </div>

        <div className={styles.outputBlock}>
          {lines.map((line, idx) => (
            <div key={idx} className={styles.outputLine}>
              <span className={styles.linePrefix}>&gt;</span>
              <span className={styles.lineText}>
                {line}
                {!done && isLastLine(idx) && (
                  <span className={styles.cursor}>█</span>
                )}
              </span>
            </div>
          ))}
          {done && (
            <div className={styles.outputLine}>
              <span className={styles.linePrefix}>&gt;</span>
              <span className={styles.doneLine}>
                analysis complete
                <span className={styles.doneTag}>OK</span>
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}