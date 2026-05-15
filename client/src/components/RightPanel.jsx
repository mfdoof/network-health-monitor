import { useEffect, useState } from 'react'
import styles from '../styles/components/RightPanel.module.css'
import StatsGrid from './StatsGrid'
import PingCard from './PingCard'
import ScanResults from './ScanResults'
import AIAnalysis from './AIAnalysis'
import ActivityLog from './ActivityLog'

function LiveClock() {
  const [now, setNow] = useState(new Date())

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  const date = now.toLocaleDateString('en-PH', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  }).toUpperCase()

  const time = now.toLocaleTimeString('en-PH', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })

  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone

  return (
    <div className={styles.clockBlock}>
      <div className={styles.clockTime}>{time}</div>
      <div className={styles.clockDate}>{date}</div>
      <div className={styles.clockTz}>{tz}</div>
    </div>
  )
}

export default function RightPanel({ stats, activeHost, activityLog }) {
  return (
    <div className={styles.panel}>
      <StatsGrid stats={stats} />

      <div className={styles.scrollArea}>
        {!activeHost && (
          <div className={styles.hintCard}>
            <div className={styles.hintHeader}>
              <span className={styles.corner}>╔══</span>
              {' AWAITING TARGET '}
              <span className={styles.corner}>══╗</span>
            </div>

            <div className={styles.hintBody}>
              <div className={styles.terminal}>
                <div className={styles.terminalPrompt}>
                  <span className={styles.promptUser}>nhm</span>
                  <span className={styles.promptAt}>@</span>
                  <span className={styles.promptHost}>doof</span>
                  <span className={styles.promptSep}>:~$</span>
                </div>
                <div className={styles.termLines}>
                  <div className={styles.termLine}>
                    <span className={styles.prompt}>&gt;</span>
                    <span className={styles.cmd}>add_host</span>
                    <span className={styles.comment}># enter ip or hostname</span>
                  </div>
                  <div className={styles.termLine}>
                    <span className={styles.prompt}>&gt;</span>
                    <span className={styles.cmd}>ping</span>
                    <span className={styles.comment}># check reachability</span>
                  </div>
                  <div className={styles.termLine}>
                    <span className={styles.prompt}>&gt;</span>
                    <span className={styles.cmd}>scan --ports</span>
                    <span className={styles.comment}># detect open ports</span>
                  </div>
                  <div className={styles.termLine}>
                    <span className={styles.prompt}>&gt;</span>
                    <span className={styles.cmd}>analyze</span>
                    <span className={styles.comment}># run ai diagnostics</span>
                  </div>
                  <div className={styles.termLine} style={{ marginTop: '8px' }}>
                    <span className={styles.prompt}>&gt;</span>
                    <span className={styles.noTarget}>no target selected</span>
                  </div>
                </div>
              </div>

              <div className={styles.divider} />

              <div className={styles.clockWrap}>
                <div className={styles.clockLabel}>
                  <span className={styles.corner}>←</span>
                  {' SESSION TIME '}
                  <span className={styles.corner}>→</span>
                </div>
                <LiveClock />
                <div className={styles.clockHint}>timestamps sync to activity log</div>
              </div>
            </div>
          </div>
        )}

        {activeHost?.pingResult && (
          <PingCard host={activeHost.host} result={activeHost.pingResult} />
        )}

        {activeHost?.scanResults && (
          <ScanResults host={activeHost.host} result={activeHost.scanResults} />
        )}

        {activeHost?.scanResults?.analysis && (
          <AIAnalysis host={activeHost.host} analysis={activeHost.scanResults.analysis} />
        )}

        <ActivityLog entries={activityLog} />
      </div>
    </div>
  )
}