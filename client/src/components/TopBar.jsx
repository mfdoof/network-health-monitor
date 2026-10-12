import styles from '../styles/components/TopBar.module.css'

const LOGO = `
██████╗  ██████╗  ██████╗ ███████╗
██╔══██╗██╔═══██╗██╔═══██╗██╔════╝
██║  ██║██║   ██║██║   ██║█████╗  
██║  ██║██║   ██║██║   ██║██╔══╝  
██████╔╝╚██████╔╝╚██████╔╝██║     
╚═════╝  ╚═════╝  ╚═════╝ ╚═╝     `.trimStart()

function llmLabel(config) {
  if (config === null) return 'AI | ...'
  if (config.error) return 'AI | unavailable'
  if (!config.llm_enabled) return 'AI | off'
  return `${config.provider_host} | ${config.model}`
}

export default function TopBar({ activePage, onNavigate, llmConfig }) {
  return (
    <div className={styles.topbar}>
      <div className={styles.brand}>
        <pre className={styles.logoAscii}>{LOGO}</pre>
        <div className={styles.brandSub}>
          <span>NETWORK</span>
          <span>MONITOR</span>
        </div>
      </div>

      <nav className={styles.nav}>
        <button
          className={`${styles.navBtn} ${activePage === 'monitor' ? styles.active : ''}`}
          onClick={() => onNavigate('monitor')}
        >
          MONITOR
        </button>
        <button
          className={`${styles.navBtn} ${activePage === 'dns' ? styles.active : ''}`}
          onClick={() => onNavigate('dns')}
        >
          DNS LOOKUP
        </button>
      </nav>

      <div className={styles.right}>
        <div className={styles.apiBadge}>
          <div className={styles.apiDot} />
          API running
        </div>
        <div className={styles.modelBadge} title="LLM provider and model used for AI analysis">
          {llmLabel(llmConfig)}
        </div>
      </div>
    </div>
  )
}