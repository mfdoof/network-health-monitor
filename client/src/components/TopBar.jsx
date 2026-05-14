import styles from '../styles/components/TopBar.module.css'

const LOGO = `
██████╗  ██████╗  ██████╗ ███████╗
██╔══██╗██╔═══██╗██╔═══██╗██╔════╝
██║  ██║██║   ██║██║   ██║█████╗  
██║  ██║██║   ██║██║   ██║██╔══╝  
██████╔╝╚██████╔╝╚██████╔╝██║     
╚═════╝  ╚═════╝  ╚═════╝ ╚═╝     `.trimStart()

export default function TopBar({ activePage, onNavigate, ollamaModel }) {
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
        <div className={styles.modelBadge}>
          Ollama | {ollamaModel}
        </div>
      </div>
    </div>
  )
}