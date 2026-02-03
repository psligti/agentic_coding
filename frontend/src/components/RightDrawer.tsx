import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  useAccountsState,
  useAgentsState,
  useCurrentSession,
  useModelsState,
  useSelectedAccount,
  useSelectedAgent,
  useSelectedModel,
  useSelectedSkills,
  useSetCurrentSession,
  useSetDrawerOpen,
  useSetDrawerTab,
  useSetSelectedAccount,
  useSetSelectedAgent,
  useSetSelectedModel,
  useSetSelectedSkills,
  useStore,
  useToolsState,
  useSkillsState,
} from '../store'
import { useSessions } from '../hooks/useSessions'
import { useAccounts } from '../hooks/useAccounts'
import ThemePicker from './ThemePicker'
import './RightDrawer.css'

type DrawerTab = 'sessions' | 'agents' | 'models' | 'skills' | 'tools' | 'accounts' | 'settings' | 'info'

interface SessionsTabProps {
  onClose: () => void
}

interface AgentsTabProps {
  onClose: () => void
}

interface ModelsTabProps {
  onClose: () => void
}

interface SkillsTabProps {
  onClose: () => void
}

interface ToolsTabProps {
  onClose: () => void
}

interface AccountsTabProps {
  onClose: () => void
}

interface SettingsTabProps {
  onClose: () => void
}

interface InfoTabProps {
  onClose: () => void
}

/**
 * Sessions Tab Panel
 * Lists available sessions with search functionality
 */
function SessionsTab({ onClose }: SessionsTabProps) {
  const sessions = useStore((state) => state.sessions)
  const currentSession = useCurrentSession()
  const setCurrentSession = useSetCurrentSession()
  const { createSession, deleteSession } = useSessions()
  const [creating, setCreating] = useState(false)

  const handleCreate = async () => {
    setCreating(true)
    try {
      const session = await createSession(`Session ${Date.now()}`)
      setCurrentSession(session)
    } catch (error) {
      console.error('Failed to create session:', error)
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (sessionId: string) => {
    try {
      await deleteSession(sessionId)
    } catch (error) {
      console.error('Failed to delete session:', error)
    }
  }

  return (
    <div className="drawer__list">
      <div className="legend">
        <span className="legend__title">Sessions</span>
        <span className="legend__right">
          <button className="control chip" onClick={handleCreate} disabled={creating}>
            New
          </button>
          <button className="control chip" onClick={onClose} title="Close drawer (Esc)">
            ×
          </button>
        </span>
      </div>
      {sessions.length === 0 ? (
        <div className="chip">No sessions yet</div>
      ) : (
        sessions.map((session) => (
          <div key={session.id} className={`drawer__item drawer__item--row ${currentSession?.id === session.id ? 'is-active' : ''}`}>
            <button
              className="drawer__item-main"
              onClick={() => setCurrentSession(session)}
            >
              <span className="drawer__item-title">{session.title}</span>
            </button>
            <button
              className="drawer__item-action"
              onClick={() => handleDelete(session.id)}
              title="Delete session"
            >
              Delete
            </button>
          </div>
        ))
      )}
    </div>
  )
}

/**
 * Agents Tab Panel
 * Agent management and configuration (from PRD section 14)
 */
function AgentsTab({ onClose }: AgentsTabProps) {
  const agents = useAgentsState()
  const selectedAgent = useSelectedAgent()
  const setSelectedAgent = useSetSelectedAgent()

  return (
    <div className="drawer__list" role="listbox" aria-label="Agents">
      <div className="legend">
        <span className="legend__title">Agents</span>
        <span className="legend__right">
          <button className="control chip" onClick={onClose} title="Close drawer (Esc)">
            ×
          </button>
        </span>
      </div>
      {agents.length === 0 ? (
        <div className="chip">No agents available</div>
      ) : (
        agents.map((agent, index) => (
          <button
            key={agent.name}
            className={`control drawer__item ${selectedAgent === agent.name ? 'is-active' : ''}`}
            onClick={() => setSelectedAgent(agent.name)}
            role="option"
            aria-selected={selectedAgent === agent.name}
            data-agent-index={index}
          >
            <div className="drawer__item-title">{agent.name}</div>
            <div className="drawer__item-meta">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{agent.description}</ReactMarkdown>
            </div>
          </button>
        ))
      )}
    </div>
  )
}

function ModelsTab({ onClose }: ModelsTabProps) {
  const models = useModelsState()
  const selectedModel = useSelectedModel()
  const setSelectedModel = useSetSelectedModel()

  return (
    <div className="drawer__list">
      <div className="legend">
        <span className="legend__title">Models</span>
        <span className="legend__right">
          <button className="control chip" onClick={onClose} title="Close drawer (Esc)">
            ×
          </button>
        </span>
      </div>
      {models.length === 0 ? (
        <div className="chip">No models configured</div>
      ) : (
        models.map((model) => (
          <button
            key={`${model.name}-${model.model}`}
            className={`control drawer__item ${selectedModel === model.model ? 'is-active' : ''}`}
            onClick={() => setSelectedModel(model.model || null)}
          >
            <div className="drawer__item-title">{model.model || 'Unknown model'}</div>
            <div className="drawer__item-meta">
              {model.provider_id || 'Unknown provider'}{model.is_default ? ' • Default' : ''}
            </div>
          </button>
        ))
      )}
    </div>
  )
}

function SkillsTab({ onClose }: SkillsTabProps) {
  const skills = useSkillsState()
  const selectedSkills = useSelectedSkills()
  const setSelectedSkills = useSetSelectedSkills()

  const toggleSkill = (name: string) => {
    if (selectedSkills.includes(name)) {
      setSelectedSkills(selectedSkills.filter((skill) => skill !== name))
      return
    }
    setSelectedSkills([...selectedSkills, name])
  }

  return (
    <div className="drawer__list">
      <div className="legend">
        <span className="legend__title">Skills</span>
        <span className="legend__right">
          <button className="control chip" onClick={onClose} title="Close drawer (Esc)">
            ×
          </button>
        </span>
      </div>
      {skills.length === 0 ? (
        <div className="chip">No skills found</div>
      ) : (
        skills.map((skill) => (
          <label key={skill.name} className="drawer__item drawer__item--check">
            <input
              type="checkbox"
              checked={selectedSkills.includes(skill.name)}
              onChange={() => toggleSkill(skill.name)}
            />
            <div>
              <div className="drawer__item-title">{skill.name}</div>
              <div className="drawer__item-meta">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{skill.description}</ReactMarkdown>
              </div>
            </div>
          </label>
        ))
      )}
    </div>
  )
}

function ToolsTab({ onClose }: ToolsTabProps) {
  const tools = useToolsState()

  return (
    <div className="drawer__list">
      <div className="legend">
        <span className="legend__title">Tools</span>
        <span className="legend__right">
          <button className="control chip" onClick={onClose} title="Close drawer (Esc)">
            ×
          </button>
        </span>
      </div>
      {tools.length === 0 ? (
        <div className="chip">No tools available</div>
      ) : (
        tools.map((tool) => (
          <div key={tool.id} className="drawer__item drawer__item--stack">
            <div className="drawer__item-title">{tool.id}</div>
            <div className="drawer__item-meta">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{tool.description}</ReactMarkdown>
            </div>
          </div>
        ))
      )}
    </div>
  )
}

function AccountsTab({ onClose }: AccountsTabProps) {
  const accounts = useAccountsState()
  const selectedAccount = useSelectedAccount()
  const setSelectedAccount = useSetSelectedAccount()
  const { createAccount, deleteAccount, setDefaultAccount } = useAccounts()
  const [formState, setFormState] = useState({
    name: '',
    provider_id: '',
    model: '',
    api_key: '',
  })
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!formState.name || !formState.provider_id || !formState.model) return
    setSubmitting(true)
    try {
      const created = await createAccount({
        name: formState.name,
        provider_id: formState.provider_id,
        model: formState.model,
        api_key: formState.api_key || undefined,
        is_default: accounts.length === 0,
      })
      setSelectedAccount(created.name)
      setFormState({ name: '', provider_id: '', model: '', api_key: '' })
    } catch (error) {
      console.error('Failed to create account:', error)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="drawer__list">
      <div className="legend">
        <span className="legend__title">Accounts</span>
        <span className="legend__right">
          <button className="control chip" onClick={onClose} title="Close drawer (Esc)">
            ×
          </button>
        </span>
      </div>
      {accounts.length === 0 ? (
        <div className="chip">No accounts configured</div>
      ) : (
        accounts.map((account) => (
          <div key={account.name} className={`drawer__item drawer__item--row ${selectedAccount === account.name ? 'is-active' : ''}`}>
            <button
              className="drawer__item-main"
              onClick={() => setSelectedAccount(account.name)}
            >
              <span className="drawer__item-title">{account.name}</span>
              <span className="drawer__item-meta">
                {account.config.provider_id || 'provider'} • {account.config.model || 'model'}
                {account.is_default ? ' • Default' : ''}
              </span>
            </button>
            <button
              className="drawer__item-action"
              onClick={() => setDefaultAccount(account.name)}
              title="Set default"
            >
              Default
            </button>
            <button
              className="drawer__item-action"
              onClick={() => deleteAccount(account.name)}
              title="Delete account"
            >
              Delete
            </button>
          </div>
        ))
      )}

      <div className="drawer__form">
        <div className="drawer__section-title">Add account</div>
        <input
          className="drawer__input"
          placeholder="Account name"
          value={formState.name}
          onChange={(event) => setFormState({ ...formState, name: event.target.value })}
        />
        <input
          className="drawer__input"
          placeholder="Provider ID"
          value={formState.provider_id}
          onChange={(event) => setFormState({ ...formState, provider_id: event.target.value })}
        />
        <input
          className="drawer__input"
          placeholder="Model ID"
          value={formState.model}
          onChange={(event) => setFormState({ ...formState, model: event.target.value })}
        />
        <input
          className="drawer__input"
          placeholder="API key (optional)"
          type="password"
          value={formState.api_key}
          onChange={(event) => setFormState({ ...formState, api_key: event.target.value })}
        />
        <button className="control drawer__item" onClick={handleSubmit} disabled={submitting}>
          {submitting ? 'Adding...' : 'Add account'}
        </button>
      </div>
    </div>
  )
}

/**
 * Settings Tab Panel
 * Theme toggle and model status (from PRD section 4)
 */
function SettingsTab({ onClose }: SettingsTabProps) {
  const theme = useStore((state) => state.theme)
  const setTheme = useStore((state) => state.setTheme)

  return (
    <div className="drawer__list">
      <div className="legend">
        <span className="legend__title">Settings</span>
        <span className="legend__right">
          <button className="control chip" onClick={onClose} title="Close drawer (Esc)">
            ×
          </button>
        </span>
      </div>
      <div className="chip">Mode: {theme === 'dark' ? 'Dark' : 'Light'}</div>
      <button className="control drawer__item" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
        Toggle Mode
      </button>
      <ThemePicker />
    </div>
  )
}

/**
 * Info Tab Panel
 * About, help links, and credits (from PRD section 5)
 */
function InfoTab({ onClose }: InfoTabProps) {
  return (
    <div className="drawer__list">
      <div className="legend">
        <span className="legend__title">Info</span>
        <span className="legend__right">
          <button className="control chip" onClick={onClose} title="Close drawer (Esc)">
            ×
          </button>
        </span>
      </div>
      <div className="chip">About and Help</div>
    </div>
  )
}

/**
 * RightDrawer Component
 * Overlay drawer with stacked vertical tabs
 * Trigger: Ctrl+D
 * Tab content:
 * - Sessions: Session list
 * - Agents: Agent management (PRD section 14)
 * - Settings: Theme toggle (PRD section 4)
 * - Info: About and help (PRD section 5)
 */
export default function RightDrawer() {
  const drawerOpen = useStore((state) => state.drawerOpen)
  const drawerTab = useStore((state) => state.drawerTab) as DrawerTab
  const setDrawerTab = useSetDrawerTab()
  const setDrawerOpen = useSetDrawerOpen()
  const agents = useAgentsState()
  const selectedAgent = useSelectedAgent()
  const setSelectedAgent = useSetSelectedAgent()

  // Handle keyboard navigation (Left/Right arrows)
  useEffect(() => {
    if (!drawerOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') {
        e.preventDefault()
        const tabs: DrawerTab[] = ['sessions', 'agents', 'models', 'skills', 'tools', 'accounts', 'settings', 'info']
        const currentIndex = tabs.indexOf(drawerTab)
        const nextIndex = (currentIndex + 1) % tabs.length
        setDrawerTab(tabs[nextIndex])
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault()
        const tabs: DrawerTab[] = ['sessions', 'agents', 'models', 'skills', 'tools', 'accounts', 'settings', 'info']
        const currentIndex = tabs.indexOf(drawerTab)
        const prevIndex = (currentIndex - 1 + tabs.length) % tabs.length
        setDrawerTab(tabs[prevIndex])
      } else if (e.key === 'Escape') {
        e.preventDefault()
        setDrawerOpen(false)
      } else if (e.key === 'Tab' && drawerTab === 'agents') {
        e.preventDefault()
        if (agents.length === 0) return
        const currentIndex = agents.findIndex((agent) => agent.name === selectedAgent)
        const nextIndex = (currentIndex + 1) % agents.length
        setSelectedAgent(agents[nextIndex].name)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [drawerOpen, drawerTab, setDrawerTab, setDrawerOpen, agents, selectedAgent, setSelectedAgent])

  // Handle click outside to close
  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      setDrawerOpen(false)
    }
  }

  if (!drawerOpen) return null

  const tabs = [
    { id: 'sessions' as DrawerTab, label: 'Sessions' },
    { id: 'agents' as DrawerTab, label: 'Agents' },
    { id: 'models' as DrawerTab, label: 'Models' },
    { id: 'skills' as DrawerTab, label: 'Skills' },
    { id: 'tools' as DrawerTab, label: 'Tools' },
    { id: 'accounts' as DrawerTab, label: 'Accounts' },
    { id: 'settings' as DrawerTab, label: 'Settings' },
    { id: 'info' as DrawerTab, label: 'Info' },
  ]

  const tabComponents = {
    sessions: <SessionsTab onClose={() => setDrawerOpen(false)} />,
    agents: <AgentsTab onClose={() => setDrawerOpen(false)} />,
    models: <ModelsTab onClose={() => setDrawerOpen(false)} />,
    skills: <SkillsTab onClose={() => setDrawerOpen(false)} />,
    tools: <ToolsTab onClose={() => setDrawerOpen(false)} />,
    accounts: <AccountsTab onClose={() => setDrawerOpen(false)} />,
    settings: <SettingsTab onClose={() => setDrawerOpen(false)} />,
    info: <InfoTab onClose={() => setDrawerOpen(false)} />,
  }

  return (
    <div className="drawerOverlay" onClick={handleOverlayClick}>
      <div className="panel drawer" onMouseDown={(e) => e.stopPropagation()}>
        <div className="drawer__tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`control drawer__tab ${drawerTab === tab.id ? 'is-active' : ''}`}
              onClick={() => setDrawerTab(tab.id)}
              aria-selected={drawerTab === tab.id}
              role="tab"
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="drawer__content">
          {tabComponents[drawerTab]}
        </div>
      </div>
    </div>
  )
}
