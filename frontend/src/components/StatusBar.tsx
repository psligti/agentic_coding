import { useMemoryUsage, useModelStatus, useTokenUsage, useTelemetry } from '../store'

interface StatusBarProps {
  className?: string
}

export function StatusBar({ className = '' }: StatusBarProps) {
  const memoryUsage = useMemoryUsage()
  const modelStatus = useModelStatus()
  const tokenUsage = useTokenUsage()
  const telemetry = useTelemetry()

  const formattedMemory = `${formatBytes(memoryUsage.used)} / ${formatBytes(memoryUsage.total)}`
  const formattedTokens = `${formatTokens(tokenUsage.total)} / ${tokenUsage.limit ? formatTokens(tokenUsage.limit) : '∞'}`
  const gitIndicator = formatGitIndicator(telemetry.git)
  const toolsIndicator = formatToolsIndicator(telemetry.tools)
  const effortEmoji = getEffortEmoji(telemetry.effort?.effort_score)

  return (
    <div className={`flex items-center justify-between bg-surface-panel border border-normal rounded-[14px] px-3 py-2 h-9 text-xs flex-shrink-0 ${className}`}>
      <div className="flex items-center gap-2">
        <span className={`inline-flex items-center ${modelStatus.connected ? 'text-success' : 'text-tertiary'}`}>
          {modelStatus.connected ? '●' : '○'}
        </span>
        <span className="text-secondary font-medium">{modelStatus.name}</span>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-secondary" data-testid="status-git" title="Git status">
          {gitIndicator}
        </span>
        <span className="text-border-normal opacity-50">|</span>
        <span className="text-secondary" data-testid="status-tools" title="Tools status">
          {toolsIndicator}
        </span>
        <span className="text-border-normal opacity-50">|</span>
        <span className="text-secondary" data-testid="status-effort" title="Effort score">
          {effortEmoji}
        </span>
        <span className="text-border-normal opacity-50">|</span>
        <span className="text-secondary" title="Memory usage">
          {formattedMemory}
        </span>
        <span className="text-border-normal opacity-50">|</span>
        <span className="text-secondary" title="Token usage">
          {formattedTokens}
        </span>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-tertiary">Ctrl+K</span>
        <span className="text-border-normal opacity-50">|</span>
        <span className="text-tertiary">Ctrl+D</span>
        <span className="text-border-normal opacity-50">|</span>
        <span className="text-tertiary">Esc</span>
      </div>
    </div>
  )
}

function formatGitIndicator(git: { is_repo: boolean; branch?: string; dirty_count?: number; ahead?: number; behind?: number }): string {
  if (!git.is_repo) return '—'
  const branch = git.branch || '—'
  const dirty = git.dirty_count && git.dirty_count > 0 ? `+${git.dirty_count}` : ''
  const ahead = git.ahead && git.ahead > 0 ? `↑${git.ahead}` : ''
  const behind = git.behind && git.behind > 0 ? `↓${git.behind}` : ''
  
  if (!dirty && !ahead && !behind) return branch
  if (dirty && !ahead && !behind) return `${branch} ${dirty}`
  if (!dirty && ahead && !behind) return `${branch} ${ahead}`
  if (!dirty && !ahead && behind) return `${branch} ${behind}`
  
  const suffixes = [dirty, ahead, behind].filter(p => p)
  return `${branch} ${suffixes.join(' ')}`.trim()
}

function formatToolsIndicator(tools: { running?: { tool_id: string; since: number }; last?: { tool_id: string; status: 'running' | 'completed' | 'failed' | 'cancelled' }; error_count?: number }): string {
  if (tools.running) {
    return `↻ ${tools.running.tool_id}`
  }
  if (tools.last) {
    const failureBadge = tools.error_count && tools.error_count > 0 ? ` (${tools.error_count}⚠)` : ''
    return `${tools.last.tool_id}${failureBadge}`
  }
  return '—'
}

function getEffortEmoji(score?: number): string {
  if (score === undefined || score === null) return '🤓'
  switch (score) {
    case 0: return '🤓'
    case 1: return '🧐'
    case 2: return '🧠'
    case 3: return '🧠⚡'
    case 4: return '🧠🔥'
    case 5: return '🧠💥'
    default: return '🤓'
  }
}

function formatBytes(bytes: number): string {
  const mb = bytes / (1024 * 1024)
  if (mb < 1) {
    const kb = bytes / 1024
    return `${kb.toFixed(1)} KB`
  }
  return `${mb.toFixed(1)} GB`
}

function formatTokens(tokens: number): string {
  if (tokens >= 1_000_000) {
    return `${(tokens / 1_000_000).toFixed(1)}M`
  }
  if (tokens >= 1_000) {
    return `${(tokens / 1_000).toFixed(1)}K`
  }
  return tokens.toString()
}
