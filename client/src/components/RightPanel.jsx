import styles from '../styles/components/RightPanel.module.css'
import StatsGrid from './StatsGrid'
import PingCard from './PingCard'
import ScanResults from './ScanResults'
import AIAnalysis from './AIAnalysis'
import ActivityLog from './ActivityLog'

export default function RightPanel({ stats, activeHost, activityLog }) {
  return (
    <div className={styles.panel}>
      <StatsGrid stats={stats} />

      {!activeHost && (
        <div className={styles.hintCard}>
          <div className={styles.hintTitle}>GET STARTED</div>
          <div className={styles.hintSteps}>
            <div className={styles.hintStep}>
              <span className={styles.stepNum}>01</span>
              <span className={styles.stepText}>Add a host in the left panel</span>
            </div>
            <div className={styles.hintStep}>
              <span className={styles.stepNum}>02</span>
              <span className={styles.stepText}>Ping to check reachability</span>
            </div>
            <div className={styles.hintStep}>
              <span className={styles.stepNum}>03</span>
              <span className={styles.stepText}>Scan to check open ports</span>
            </div>
            <div className={styles.hintStep}>
              <span className={styles.stepNum}>04</span>
              <span className={styles.stepText}>Analyze for AI diagnostics</span>
            </div>
          </div>
        </div>
      )}

      {activeHost?.pingResult && (
        <PingCard
          host={activeHost.host}
          result={activeHost.pingResult}
        />
      )}

      {activeHost?.scanResults && (
        <ScanResults
          host={activeHost.host}
          result={activeHost.scanResults}
        />
      )}

      {activeHost?.scanResults?.analysis && (
        <AIAnalysis
          host={activeHost.host}
          analysis={activeHost.scanResults.analysis}
        />
      )}

      <ActivityLog entries={activityLog} />
    </div>
  )
}