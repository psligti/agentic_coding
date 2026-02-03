import { useCurrentSession } from '../store'
import './TopBar.css'

export function TopBar() {
  const currentSession = useCurrentSession()

  return (
    <div className="topbar">
      <div className="topbar__left">
        <div className="topbar__logo">
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
            <path
              d="M12 6L12 18M6 12L18 12"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
          <span className="topbar__logo-text">OpenCode</span>
        </div>
        {currentSession && (
          <span className="topbar__title" title={currentSession.title}>
            {currentSession.title}
          </span>
        )}
      </div>
    </div>
  )
}
