# ULTRAWORK STATUS - TUI Epics Implementation

## Rules of Engagement

### Isolation Model
- **Event-driven integration**: Use `opencode_python/src/opencode_python/core/event_bus.py` for cross-epic communication
- **Plugin-style extensions**: Each epic adds new modules under its domain package
- **Minimal hotspot edits**: When hotspots must be touched, add only what's needed
- **Conflict posture**: Conflicts expected in Wave 4; resolve via integration worktree
- **Safety**: No remote history rewrite; use merge commits for integration

### Epic Worktree Conventions
- Base branch: `main` (wt/tui is current worktree)
- Branch naming: `epic/<slug>`
- Worktree path: `./.worktrees/<slug>`
- Commit message format: `epic(<slug>): <short summary>`

### TUI Framework
- **Textual 7.4.0** is authoritative (no Rich-only migration)
- Rich is used for formatting only, not as TUI framework

## Integration Contract

### Hotspot Files (Edit Only When Unavoidable)
These files are high-risk collision points. Single-touch only, document every edit.

| File | Primary Owner(s) | Notes |
|------|------------------|-------|
| `opencode_python/src/opencode_python/tui/app.py` | Epic 1, Epic 7 | Register screens/bindings only |
| `opencode_python/src/opencode_python/core/models.py` | Epic 3, Epic 4 | Session model has `extra="forbid"` |
| `opencode_python/src/opencode_python/core/session.py` | Epic 3, Epic 4 | SessionManager API |
| `opencode_python/src/opencode_python/core/settings.py` | Epic 2, Epic 4, Epic 6, Epic 7, Epic 8 | Add settings keys only |
| `opencode_python/src/opencode_python/storage/store.py` | Epic 3, Epic 6, Epic 8 | Use separate storage namespaces |
| `opencode_python/src/opencode_python/core/event_bus.py` | Epic 3, Epic 4, Epic 6, Epic 8 | Primary integration point |

### Medium-Risk Shared Points
| File | Owner Epics | Notes |
|------|--------------|-------|
| `opencode_python/src/opencode_python/tui/keybindings.py` | Epic 1, Epic 7 | Coordinate keybinding additions |
| `opencode_python/src/opencode_python/tui/screens/settings_screen.py` | Epic 2, Epic 7, Epic 8 | Screen ownership TBD |
| `opencode_python/src/opencode_python/tools/framework.py` | Epic 6 | Tool registration |
| `opencode_python/src/opencode_python/tools/registry.py` | Epic 5, Epic 6 | Tool/skill interaction |
| `opencode_python/src/opencode_python/permissions/evaluate.py` | Epic 1, Epic 6, Epic 8 | Permission logic |

### Integration Rules
1. Prefer new modules under domain packages:
   - `opencode_python/src/opencode_python/providers/` (Epic 2)
   - `opencode_python/src/opencode_python/skills/` (Epic 5)
   - `opencode_python/src/opencode_python/tools/` (Epic 6)
   - `opencode_python/src/opencode_python/agents/` (Epic 4)
   - `opencode_python/src/opencode_python/storage/` (Epic 3, Epic 6, Epic 8)
   - `opencode_python/src/opencode_python/observability/` (Epic 8)

2. Register via:
   - Events in `opencode_python/src/opencode_python/core/event_bus.py` (primary)
   - Registry patterns for tools/skills/providers
   - Settings defaults in `opencode_python/src/opencode_python/core/settings.py` (additive only)

3. Do NOT extend `Session` model in `opencode_python/src/opencode_python/core/models.py` unless absolutely required. Store epic-specific metadata under new storage namespaces instead.

### Event Namespace Registry
Each epic declares event names it emits/subscribes to. Prevents duplicate semantics.

| Epic | Emits | Subscribes To |
|------|--------|---------------|
| Epic 1 (Shell/Nav) | `screen:change`, `command:execute`, `palette:open` | `session:created`, `provider:changed`, `account:changed` |
| Epic 2 (Providers) | `provider:created`, `provider:updated`, `provider:deleted`, `provider:test`, `account:created`, `account:updated`, `account:deleted`, `account:active` | `session:start`, `tool:execute` |
| Epic 3 (Sessions) | `session:created`, `session:updated`, `session:deleted`, `session:resumed`, `session:autosave`, `session:export` | `screen:change`, `agent:execute`, `tool:execute` |
| Epic 4 (Agents) | `agent:profile:select`, `agent:config:update`, `agent:execute`, `agent:complete` | `session:start`, `skill:enable`, `tool:execute` |
| Epic 5 (Skills) | `skill:enable`, `skill:disable`, `skill:block`, `skill:execute` | `agent:execute`, `session:start` |
| Epic 6 (Tools) | `tool:discover`, `tool:allow`, `tool:deny`, `tool:execute`, `tool:log` | `session:start`, `skill:enable`, `agent:execute` |
| Epic 7 (Themes/UX) | `theme:change`, `keybinding:update`, `layout:toggle` | All screen events |
| Epic 8 (Observability) | `timeline:label`, `session:blocked`, `destructive:request`, `dryrun:toggle` | All epic events (observer pattern) |

## Epic Tracking Table

| Epic | Slug | Branch | Worktree Path | Status | Last Update | Key Files Changed | Notes | Next Step |
|------|-------|--------|---------------|---------|-------------|------------------|--------|------------|
| Epic 1 - TUI Shell & Navigation | `tui-shell-navigation` | `epic/tui-shell-navigation` | `./.worktrees/tui-shell-navigation` | Done | 2026-01-30 12:15:00 | Home screen, command palette, custom events | tui/screens/home_screen.py, tui/palette/command_palette.py, tui/app.py (minimal), tests/tui/test_home_screen.py |
| Epic 2 - Providers & Accounts | `providers-accounts` | `epic/providers-accounts` | `./.worktrees/providers-accounts` | Planned | 2026-01-30 12:00:00 | None yet | Provider CRUD, test connection, secure credential storage, active account switching | Implement ProviderManager |
| Epic 3 - Sessions | `sessions` | `epic/sessions` | `./.worktrees/sessions` | Done | 2026-01-30 12:00:00 | storage/session_meta.py, core/session.py, export/session_exporter.py, tui/screens/session_creation_screen.py, tui/widgets/save_indicator.py | Session creation with validation, auto-save, resume exactly, export MD/JSON with redaction implemented | - |
| Epic 4 - Agents | `agents` | `epic/agents` | `./.worktrees/agents` | Done | 2026-01-30 11:45:00 | agents/ package, core/settings.py (minimal) | Profile selection, prerequisite checking, per-session config (model/temp/budget), audit trail | - |
 | Epic 5 - Skills | `skills` | `epic/skills` | `./.worktrees/skills` | Done | 2026-01-30 12:20:00 | skills/ package, core/event_bus.py, tui/screens/skills_panel_screen.py, tests/skills/ | Skills enable/disable, runtime blocking, and contracts implemented | - |
| Epic 6 - Tools | `tools` | `epic/tools` | `./.worktrees/tools` | Planned | 2026-01-30 12:00:00 | None yet | Tool discovery panel, allow/deny workflow, execution log with diffs | Implement ToolPermissionSystem |
| Epic 7 - Themes & UX | `themes-ux` | `epic/themes-ux` | `./.worktrees/themes-ux` | Planned | 2026-01-30 12:00:00 | None yet | Theme switching (hot reload), reduced motion, configurable keybindings, restore defaults | Implement ThemeManager |
| Epic 8 - Observability & Safety | `observability-safety` | `epic/observability-safety` | `./.worktrees/observability-safety` | Done | 2026-01-30 12:15:00 | observability/ package, event_bus.py, settings.py, tests/observability/ | Timeline, status tracking, and safety rails implemented | All requirements met |

## Requirements Staging

### Epic 1 - TUI Shell & Navigation

**Acceptance Criteria (from TUI_EPICS_ONE.md):**

**Story 1.1 — Launch & Home**
- On launch, show home screen with active provider/account, recent sessions, and quick actions
- Actions: "New Session", "Resume Session", "Settings"
- Resume recent session loads session state from storage

**Story 1.2 — Global command palette**
- Command palette accessible from anywhere (Ctrl+P)
- Fuzzy search for actions
- Command palette respects permissions (hide restricted actions)

**MVP Scope:**

**IN Scope (MVP):**
- HomeScreen widget with 3 sections: Provider/Account display, Recent Sessions list, Quick Actions buttons
- Recent Sessions shows last 5 sessions (displayed from session storage)
- Quick Actions: New Session (creates new, opens session screen), Resume Session (select from recent), Settings (opens settings screen)
- CommandPalette widget: Ctrl+P opens, fuzzy search on action names, executes selected action
- Permission-aware action filtering (query permissions system, hide actions user can't access)
- Screen navigation: Home ↔ Session ↔ Settings

**OUT Scope (Deferred):**
- Session filtering/search on home screen
- Recent sessions metadata (duration, last worked timestamp)
- Command palette keyboard shortcuts (e.g., Ctrl+N for new session)
- Quick actions keyboard hints
- Session thumbnails/previews
- Home screen stats (total sessions, active agents, etc.)

**Scenario Checklists:**

| Scenario | Implementation Notes | Validation Approach |
|----------|----------------------|---------------------|
| Show quick actions on launch | HomeScreen: VerticalContainer with ProviderInfo, RecentSessions, QuickActions widgets. QuickActions: 3 Button widgets with labels. On app init, push HomeScreen to screen stack. | Launch TUI → Verify 3 sections present → Verify Provider/Account shows "No provider" if none → Verify Recent Sessions shows empty list → Verify Quick Actions buttons clickable |
| Resume a recent session | RecentSessions: DataTable widget with session list. On row select, emit `session:resumed` event with session_id. Listen to event, load session from storage, push SessionScreen. | Create 2 sessions → Go to home → Verify both appear in list → Select session 2 → Verify SessionScreen opens → Verify session state matches (repo, objective, messages) |
| Open command palette and run an action | CommandPalette: Modal with Input widget for search, ActionList for filtered results. Subscribe to `keyboard:ctrl+p` event. On input change, filter actions by name match. On select, execute action via event bus. | Press Ctrl+P → Verify palette opens → Type "new" → Verify "New Session" highlighted → Press Enter → Verify New Session executes (session created, screen opened) |
| Command palette respects permissions | Before displaying actions, query PermissionEvaluator for each action's required permission. Filter out actions where `evaluate(action_permission) == False`. | Create restricted account (no session:write) → Press Ctrl+P → Type "new" → Verify "New Session" not in results → Type "settings" → Verify "Settings" appears |

---

### Epic 2 - Providers & Accounts

**Acceptance Criteria (from TUI_EPICS_ONE.md):**

**Story 2.1 — Provider configuration**
- Add/edit/remove providers with name, base URL, model list
- Test connection to provider
- Show success or specific error message with retry guidance

**Story 2.2 — Accounts & credentials**
- Add accounts per provider with API keys
- API keys stored securely, never displayed in full after saving
- Switch active account per provider
- New sessions use active account by default
- Existing sessions keep their current account

**MVP Scope:**

**IN Scope (MVP):**
- Provider model: id, name, base_url, models[] (list of model names)
- Provider CRUD: CreateProviderScreen (form: name, base_url, models input), ProviderListScreen (list providers, edit/delete actions)
- TestConnection function: HTTP GET to {base_url}/models or health endpoint, catch errors, return success/message
- Account model: provider_id, account_name, api_key (encrypted), is_active flag
- Account CRUD: AccountListScreen per provider, AddAccountScreen (form: account_name, api_key)
- Secure credential storage: Use keyring library or AES encryption in storage layer. API key stored as masked value (`********`), original encrypted in secure store.
- Active account switching: AccountListScreen with radio/select for active account. On change, emit `account:active` event.
- SessionManager: On session create, use active account from selected provider. Existing sessions reference their assigned account_id (immutable after creation).

**OUT Scope (Deferred):**
- Provider templates (OpenAI, Anthropic, local presets)
- Model validation against provider
- API key rotation
- Multi-region support per provider
- Account permissions/roles
- Provider health monitoring/dashboard
- Batch provider import/export

**Scenario Checklists:**

| Scenario | Implementation Notes | Validation Approach |
|----------|----------------------|---------------------|
| Add a provider | ProviderSettingsScreen: Form with Input for name, base_url, TextArea for models (one per line). On save, validate non-empty, create Provider record, emit `provider:created` event. Store in providers storage namespace. | Go to Settings → Providers → Add Provider → Enter "OpenAI", "https://api.openai.com/v1", models "gpt-4,gpt-3.5-turbo" → Save → Verify appears in ProviderList |
| Validate provider connectivity | TestConnectionButton in ProviderListScreen row. On click, call `ProviderClient.test_connection(base_url)`: requests.get(base_url + "/models", timeout=10). Catch RequestException, return success/error. Display in Modal. | Add provider with bad URL → Click "Test Connection" → Verify error message shown → Fix URL → Click "Test Connection" → Verify success shown |
| Add account with secret credential | AddAccountScreen for selected provider. Form: account_name, api_key (Input with password=True). On save, encrypt api_key via `security.encrypt(api_key)`, store as `api_key_encrypted`. Display as `********` in list. Emit `account:created` event. | Go to Provider → Accounts → Add Account → Enter "dev-account", "sk-..." → Save → Verify appears with `********` → Verify storage contains encrypted key |
| Switch active account | AccountListScreen: DataTable with account rows. RadioColumn for is_active. On radio change, update provider.active_account_id, emit `account:active` event with provider_id, account_id. | Provider has 2 accounts → Select account 2 as active → Verify radio checked for account 2 → Create new session → Verify session uses account 2 → Verify old session still uses account 1 |

---

### Epic 3 - Sessions

**Acceptance Criteria (from TUI_EPICS_ONE.md):**

**Story 3.1 — Create session with context**
- Create session with repo path, objective, constraints
- Validate repo path exists
- Session header shows repo path and objective

**Story 3.2 — Persist & resume**
- Auto-save session state (messages, tool calls, artifacts)
- Non-intrusive save indicator
- Resume session exactly (timeline, pending tasks)

**Story 3.3 — Session export**
- Export to Markdown with messages, decisions, tool usage summaries
- Export to JSON with structured tool call records (timestamps, outcomes)
- Secrets redacted in exports

**MVP Scope:**

**IN Scope (MVP):**
- Session model: id, created_at, updated_at, repo_path, objective, constraints, status (draft/active/blocked/done), messages[], tool_calls[], artifacts[], provider_id, account_id, agent_profile_id
- NewSessionScreen: Form with DirectorySelector (repo path), Input (objective), TextArea (constraints). On submit, validate repo_path exists (Path(repo_path).exists()), create session, emit `session:created` event.
- SessionScreen: Header (repo_path, objective), Timeline widget (messages + tool calls), InputArea (send messages). Message model: role (user/assistant/tool), content, timestamp.
- Auto-save: On any state change (message sent, tool executed), write to storage. Emit `session:autosave` event. Show save indicator (e.g., small "💾" icon) that fades after 2s.
- Resume: Load session from storage by id. Reconstruct Timeline with all messages/tool_calls. Pending tasks: store task state in session metadata, restore on load.
- ExportMarkdown: Generate MD file with sections: Header, Objective, Constraints, Timeline (messages as quotes, tool calls as code blocks), Summary. Redact: replace API keys with `[REDACTED]`, password fields, etc. via regex patterns.
- ExportJSON: Serialize session model to JSON, include all tool_calls with timestamps, outcomes, inputs/outputs. Same redaction logic.

**OUT Scope (Deferred):**
- Session templates (e.g., "Bug fix", "Feature dev")
- Branch/session association
- Session search/filter
- Session sharing (public/private)
- Session versioning (fork sessions)
- Auto-resume on crash
- Session analytics (time spent, tools used)
- Diff exports (show changes between sessions)

**Scenario Checklists:**

| Scenario | Implementation Notes | Validation Approach |
|----------|----------------------|---------------------|
| Create a session with repo context | NewSessionScreen: DirectorySelector widget (navigate dirs, confirm path). Input: objective (required), TextArea: constraints (optional). On submit: Path(repo_path).is_dir(), create Session dict, store, emit event. Push SessionScreen. | Go to New Session → Select valid repo → Enter objective "Fix login bug" → Constraints "No tests" → Create → Verify SessionScreen shows header "Fix login bug • /path/to/repo" |
| Reject invalid repo path | Path validation before session creation. If not Path(repo_path).exists(), show error Modal with message "Repo path does not exist". | New Session → Enter non-existent path → Create → Verify error shown → Verify no session created |
| Auto-save session state | SessionScreen: on_message_sent, on_tool_executed → call SessionManager.save(session). Emit `session:autosave`. Show SaveIndicator widget in footer. | Send message → Verify save indicator appears → Check storage → Verify session updated → Wait 2s → Verify indicator fades |
| Resume session exactly | SessionManager.load(session_id). Load messages[], tool_calls[], reconstruct Timeline. Restore task state from session.metadata.tasks. Load artifacts. | Create session, send 3 messages, run 2 tools → Close TUI → Reopen → Resume session → Verify Timeline shows all messages/tools → Verify task state restored |
| Export to Markdown | ExportManager.to_markdown(session): iterate messages, format as `> role: content`, tool calls as ````tool: name\noutput```. Redact secrets via regex `sk-[a-zA-Z0-9]{32}` → `[REDACTED]`. Write to file. | Create session with API key in messages → Export to MD → Open MD → Verify API key redacted → Verify messages formatted correctly |
| Export to JSON for automation | ExportManager.to_json(session): json.dumps(session.model_dump(), indent=2). Redact secrets. Include tool_calls with timestamp, tool_name, parameters, outcome. | Export to JSON → Validate JSON schema → Verify tool_calls include timestamps → Verify secrets redacted |

---

### Epic 4 - Agents

**Acceptance Criteria (from TUI_EPICS_ONE.md):**

**Story 4.1 — Agent selection & capabilities**
- Choose agent profile (coder/reviewer/planner) when starting session
- Show agent's description, enabled skills, tools
- Prevent running with missing prerequisites (warn, offer options)

**Story 4.2 — Agent configuration per session**
- Override agent settings per session (model, temperature, budget)
- Subsequent agent turns use new settings
- Changes recorded in audit trail

**MVP Scope:**

**IN Scope (MVP):**
- AgentProfile model: id, name, description, default_model, default_temperature, required_skills[], required_tools[], capabilities[]
- Built-in profiles: Coder, Reviewer, Planner (defined in config)
- NewSessionScreen: AgentProfile selector (Dropdown). On selection, show agent.description, agent.capabilities in preview panel. Validate prerequisites: check if required_skills in enabled skills, required_tools available. If missing, show warning Modal with options: "Enable missing and continue", "Choose another agent".
- Session: Add agent_profile_id, agent_config (model, temperature, budget) fields. agent_config overrides profile defaults.
- SessionSettingsScreen: Agent configuration panel. Inputs: model (Dropdown from provider.models), temperature (Slider 0-2), budget (Input tokens). On change, update session.agent_config, emit `agent:config:update` event. Record change in session.audit_trail[].
- Audit trail: Each config change entry: {timestamp, field, old_value, new_value, action_source}.
- Agent execution: On message send, use session.agent_config for LLM call.

**OUT Scope (Deferred):**
- Custom agent profiles (user-defined)
- Agent versioning
- Agent performance metrics
- Multi-agent collaboration
- Agent skill composition (inheritence)
- Agent A/B testing
- Agent marketplace
- Agent telemetry dashboard

**Scenario Checklists:**

| Scenario | Implementation Notes | Validation Approach |
|----------|----------------------|---------------------|
| Choose agent profile when starting session | NewSessionScreen: AgentProfile Dropdown. On change, show Description widget (Rich text), Capabilities widget (DataTable: skill, tool). Store agent_profile_id in session. | New Session → Select "Coder" → Verify description shown → Verify capabilities list skills/tools → Create session → Verify session.agent_profile_id set |
| Prevent running with missing prerequisites | On agent select, check: missing_skills = [s for s in agent.required_skills if s not in enabled_skills]. If non-empty, show Modal: "Agent requires skills: {missing_skills}. Enable now?" → Options: "Enable and continue", "Choose another". | Create session, disable "Test Generation" skill → Select "Reviewer" agent (requires Test Generation) → Verify warning Modal → Click "Enable and continue" → Verify skill enabled, session created |
| Override model settings | SessionSettingsScreen: Model Dropdown (provider.models), Temperature Slider (0-2, step 0.1), Budget Input. On submit, update session.agent_config, add audit entry. Emit `agent:config:update`. | Open session settings → Change model to "gpt-4" → Change temperature to 0.7 → Save → Verify agent uses new model on next turn → Check audit trail → Verify entry with timestamp, field, old/new values |

---

### Epic 5 - Skills

**Acceptance Criteria (from TUI_EPICS_ONE.md):**

**Story 5.1 — Browse and enable skills**
- Enable/disable skills in session
- Skills control what agent can do
- Disabling blocks agent from using skill's tools

**Story 5.2 — Skill-scoped prompts**
- Each skill has prompt contract and output schema
- Structured results (machine-readable)

**MVP Scope:**

**IN Scope (MVP):**
- Skill model: id, name, description, prompt_contract (system prompt), output_schema (Pydantic model or JSON schema), tools[]
- Built-in skills: Test Generation, Code Review, Refactor, Docs (defined in config)
- SkillsPanel widget (in SessionScreen): DataTable with skill rows (name, description, enabled toggle). On toggle change, update session.enabled_skills, emit `skill:enable` or `skill:disable` event.
- Runtime blocking: When agent requests tool from disabled skill, ToolPermissionEvaluator checks tool.skill_id in session.enabled_skills. If false, return blocked result: {"error": "Skill '{skill_name}' is disabled"}. Log to tool_execution_log.
- Skill contracts: Each skill has prompt_contract field (system prompt template). When agent executes skill, prepend prompt_contract to context.
- Output schemas: Each skill defines output_schema as JSON schema. Agent instructed to output JSON matching schema. Validate with `jsonschema.validate()`.

**OUT Scope (Deferred):**
- Custom skill creation (user-defined skills)
- Skill composition (chaining skills)
- Skill marketplace
- Skill versioning
- Skill analytics (usage stats)
- Skill dependency management
- Skill sandboxing

**Scenario Checklists:**

| Scenario | Implementation Notes | Validation Approach |
|----------|----------------------|---------------------|
| Enable a skill in a session | SkillsPanel: DataTable with ToggleColumn for enabled. On change, update session.enabled_skills (add/remove skill_id). Emit `skill:enable`/`skill:disable` event. Log to session audit trail. | Open Skills panel → Toggle "Test Generation" → Verify enabled → Send message requesting tests → Verify agent generates tests → Toggle off → Verify agent blocked |
| Disable a risky skill | Same as enable. On agent tool request, check tool.skill_id in session.enabled_skills. If disabled, return blocked response: "Shell Execution is disabled. Enable in Skills panel to proceed." | "Shell Execution" enabled → Agent runs shell command → Toggle off → Agent attempts shell → Verify blocked response shown in timeline |
| Skill returns structured results | Skill.output_schema defines JSON schema. Agent prompt: "Output JSON matching schema". On response, parse JSON, validate with jsonschema. Store in session.tool_calls[].output. | Run "Code Review" skill → Verify output JSON matches schema (severity, file, fix) → Validate with jsonschema → Store in tool_calls |

---

### Epic 6 - Tools

**Acceptance Criteria (from TUI_EPICS_ONE.md):**

**Story 6.1 — Tool discovery & permissioning**
- Show tools and permission state (Allowed/Denied, why)
- Deny tool usage without consent (prompt to approve/deny)

**Story 6.2 — Tool execution log**
- Show tool call record with name, timestamp, parameters, output
- Diff preview for file changes

**MVP Scope:**

**IN Scope (MVP):**
- Tool model: id, name, description, permission_mode (allow/deny/confirm), skill_id (nullable), parameters_schema (JSON schema)
- ToolRegistry: Register tools with metadata. tools/discover() returns all tools with permission state.
- ToolsPanel widget: DataTable with tool rows (name, description, permission state). Permission column shows "Allowed" (green), "Denied" (red), "Confirm" (yellow). Click to toggle (allow/deny modes only).
- Permission workflows:
  - allow: Always permitted
  - deny: Always blocked
  - confirm: Prompt user via Modal on each use. Options: "Allow once", "Deny", "Allow always" (converts to allow)
- ToolExecutionLog widget (in SessionScreen timeline): Expandable entries per tool call. Show: tool_name, timestamp, parameters (collapsed), output (collapsed). If file changes detected, show DiffPreview (git-style diff).
- Permission state storage: session.tool_permissions = {tool_id: permission_mode}. Persist in session storage.
- On tool execute: check permission_mode. If confirm, show prompt. Record decision in tool_execution_log.

**OUT Scope (Deferred):**
- Tool groups/categories
- Tool templates
- Tool execution history (across sessions)
- Tool performance metrics
- Tool sandboxing
- Tool marketplace
- Custom tool creation
- Tool A/B testing

**Scenario Checklists:**

| Scenario | Implementation Notes | Validation Approach |
|----------|----------------------|---------------------|
| Show tools and permission state | ToolsPanel: Query ToolRegistry for all tools. For each tool, check session.tool_permissions[tool_id] or default_permission_mode. Display DataTable with columns: name, description, permission. | Open Tools panel → Verify all tools listed → Verify permission states displayed (Allow/Deny/Confirm) |
| Deny tool usage without consent | On tool execute: mode = session.tool_permissions[tool_id]. If mode == "deny", return blocked result. If mode == "confirm", show Modal with options. | Set "Write Files" to "deny" → Agent attempts write → Verify blocked response → Change to "confirm" → Agent attempts write → Verify approval prompt shown → Click "Deny" → Verify no files changed |
| Show a tool call record | ToolExecutionLog: Each tool call creates entry with tool_name, timestamp, parameters, output, diff (if files changed). Expand to show details. DiffPreview: use difflib.unified_diff for before/after. | Agent runs "Git Diff" → Verify log entry appears → Click entry → Verify timestamp, parameters shown → Verify output displayed → If files changed, verify diff shown |

---

### Epic 7 - Themes & UX

**Acceptance Criteria (from TUI_EPICS_ONE.md):**

**Story 7.1 — Theme selection**
- Switch themes (dark/light/high-contrast)
- UI updates immediately
- Theme persists after restart
- Reduced motion toggle

**Story 7.2 — Keybindings**
- Rebind action keys
- Conflict detection
- Restore defaults

**MVP Scope:**

**IN Scope (MVP):**
- Theme model: id, name, colors (dict of widget→color values), fonts (size, family), spacing (compact/normal)
- Built-in themes: Dark (default), Light, High Contrast (defined in YAML config)
- ThemeManager: load themes from config, apply theme via Textual's `app.theme = theme.colors`. Hot reload: on theme change, update app.theme immediately, emit `theme:change` event.
- ThemeSelectionScreen: List themes with preview (screenshot or color palette). On select, set active theme, persist to settings.
- Reduced motion: settings.reduced_motion (bool). If true, disable animations (e.g., fade transitions, scrolling effects).
- Keybinding model: action_id, default_key, current_key
- KeybindingManager: Load keybindings from config. Map action_id → key. On key press, resolve action.
- KeybindingSettingsScreen: DataTable with action, current_key, default_key. Edit cell to rebind. On save, check for conflicts (same key bound to multiple actions). If conflict, show warning. Persist to settings.
- Restore defaults: Button to reset all keybindings to default_key values.

**OUT Scope (Deferred):**
- Custom theme creation (user-defined themes)
- Theme marketplace
- Theme import/export
- Advanced animation controls
- Per-screen layouts
- Keyboard macro support
- Action groups
- Keybinding profiles

**Scenario Checklists:**

| Scenario | Implementation Notes | Validation Approach |
|----------|----------------------|---------------------|
| Change theme | ThemeSelectionScreen: Select "High Contrast" → ThemeManager.apply_theme(theme_id) → app.theme = theme.colors → emit `theme:change`. Persist to settings.active_theme. | Open Theme Settings → Select "High Contrast" → Verify UI updates immediately → Restart TUI → Verify theme persists |
| Accessibility-friendly defaults | Settings: reduced_motion flag. If true, set animation durations to 0 in widgets (e.g., FadeTransition.duration = 0). Toggle in ThemeSelectionScreen. | Enable "Reduced Motion" → Navigate between screens → Verify no animations → Disable → Verify animations return |
| Rebind an action | KeybindingSettingsScreen: Edit "Open command palette" key to "Ctrl+O". KeybindingManager.bind("palette:open", "Ctrl+O"). Check conflicts: find all actions with current_key == "Ctrl+O". If conflict, show warning. | Open Keybinding Settings → Edit "palette:open" to "Ctrl+O" → Save → Press Ctrl+O → Verify palette opens → Check for conflicts |
| Restore defaults | KeybindingSettingsScreen: "Restore defaults" button → Reset all keybindings to default_key values → Persist. | Customize some bindings → Click "Restore defaults" → Verify all bindings reset → Press default keys → Verify actions work |

---

### Epic 8 - Observability & Safety

**Acceptance Criteria (from TUI_EPICS_ONE.md):**

**Story 8.1 — Session timeline & statuses**
- Timeline labels for planning/tooling/coding/review steps
- Failures expandable with details
- Session status: blocked, with reason and next steps

**Story 8.2 — Safety rails for destructive actions**
- Confirmation dialog for destructive git operations (force push, delete)
- Default action is "Cancel"
- Dry-run mode for bulk changes (diff preview only, no modifications)

**MVP Scope:**

**IN Scope (MVP):**
- TimelineLabel enum: PLAN, TOOL, CODE, REVIEW, FAILURE, INFO
- Timeline widget: Each event has label_color based on type. Failures expandable: click to show error details.
- Session status enum: DRAFT, ACTIVE, BLOCKED, DONE. status_reason field.
- Status detection: On agent error or missing prerequisite, set session.status = "blocked", status_reason = error message. Show status banner in SessionScreen with reason and "Unblock" button (e.g., fix credentials, enable skill).
- Destructive operations list: force_push, delete_branch, rm_rf, etc. Configured in settings.destructive_actions.
- DestructiveActionGuard: On tool execute, check if tool_name in destructive_actions. If yes, show Modal with description, default "Cancel" button, "Proceed" button. Emit `destructive:request` event.
- Dry-run mode: session.dry_run (bool). If true, skip actual tool execution, generate diff/patch preview instead. Show "Dry-run mode active" banner. Toggle in SessionSettings.
- Timeline labeling: On event emit, include event_type. Timeline widget maps type to label and color.

**OUT Scope (Deferred):**
- Session status analytics (time in each status)
- Multi-step undo/redo
- Destructive operation approval workflows (multi-user)
- Audit log for all safety events
- Custom destructive action rules
- Status notifications (alerts)
- Session health scores

**Scenario Checklists:**

| Scenario | Implementation Notes | Validation Approach |
|----------|----------------------|---------------------|
| Label timeline events | Timeline widget: On tool execute, emit `timeline:label` with event_type (TOOL, CODE, etc.). TimelineEntry widget renders label with color. | Agent runs plan → Timeline shows "Plan" label (blue) → Agent runs git diff → Shows "Tool" label (yellow) → Agent writes file → Shows "Code" label (green) |
| Mark session as blocked | On agent error (e.g., missing credentials), set session.status = "blocked", status_reason = "Missing API key". SessionScreen shows banner: "⚠️ BLOCKED: Missing API key. Add account in Settings." with "Fix" button. | Simulate missing credential error → Verify status banner appears → Verify reason shown → Click "Fix" → Navigate to Settings → Add credential → Resume session → Verify status = "active" |
| Require confirmation for destructive git operations | On "force_push" tool, check settings.destructive_actions. If present, show Modal: "Force push will overwrite remote. Confirm?" Buttons: "Cancel" (default, red), "Proceed" (yellow). Emit `destructive:request`. | Agent attempts force push → Verify Modal appears → Verify "Cancel" default → Click "Proceed" → Verify push executes |
| Dry-run mode for bulk changes | Toggle dry_run in SessionSettings. If true, tool execution returns diff preview instead of modifying files. Show banner "🔍 Dry-run mode - No changes will be made". | Enable dry-run → Agent proposes 10 file changes → Verify diff shown → Verify no files modified → Disable dry-run → Re-execute → Verify files modified |

---

## Execution Waves

### Wave 0: Preflight ✅
- [x] 0.1 Repo hygiene verified
- [x] 0.2 ULTRAWORK_STATUS.md created
- [x] 0.3 Integration contract + hotspot list + event namespace registry documented
- [x] 0.4 Requirements staged for all 8 epics

### Wave 1: Worktree Creation (Parallel)
Status: **Completed** ✅
- [x] Create 8 branches: `epic/<slug>` off `main`
- [x] Create 8 worktrees at: `./.worktrees/<slug>`
- [x] Update status to `Created` for each epic

### Wave 2: Requirements Staging (Parallel per Epic)
Status: **Completed** ✅
- [x] Extract acceptance criteria from `TUI_EPICS_ONE.md`
- [x] Define MVP scope (explicit IN/OUT)
- [x] Create checklists: Scenario → Implementation → Validation
- [x] Update status to `Planned` + 1-line MVP summary

### Wave 3: Epic Execution (8 Parallel Workers)
Status: **Pending**
- Each Epic Worker implements MVP in its worktree
- Runs checks (pytest, ruff, mypy)
- Commits with `epic(<slug>): <summary>`
- Updates status to `In Progress` → `Done`

### Wave 4: Integration (Conditional)
Status: **Pending**
- Create `integrate/epics` worktree + branch
- Merge epic branches in priority order
- Resolve conflicts
- Run full verification suite

### Wave 5: Final Output
Status: **Pending**
- Consolidated PR readiness report
- Per-epic: summary, validation, risks, follow-ups
- PR opening instructions

## Epic Execution / Merge Order (for Wave 4)

1. **Epic 3 (Sessions)** - Foundation: persistence/resume/export
2. **Epic 2 (Providers & Accounts)** - Foundation: active provider/account
3. **Epic 6 (Tools)** - Foundation: permissioning/logging
4. **Epic 5 (Skills)** - Depends on tools/permissions
5. **Epic 4 (Agents)** - Depends on sessions + providers + tools/skills
6. **Epic 1 (Shell & Navigation)** - Wires screens/palette/home
7. **Epic 7 (Themes & UX)** - UI-layer: keybindings/themes
8. **Epic 8 (Observability & Safety)** - Cross-cutting: timeline/status/safeguards

## Conflict Log (Wave 4)

| Epic | File | Conflict | Resolution | Timestamp |
|------|------|-----------|-------------|------------|
| - | - | - | - | - |

## Validation Results

| Epic | Tests Run | Result | Evidence | Timestamp |
 |------|------------|--------|-----------|------------|
| - | - | - | - | - | - |
| 
## Validation Results

 | Epic | Tests Run | Result | Evidence | Timestamp |
|------|------------|--------|-----------|------------|
| Epic 5 - Skills | tests/skills/test_skills.py | 24 passed | All skill models, contracts, registry, and blocking tests pass | 2026-01-30 12:20:00 |
| 
---

**Last Updated**: 2026-01-30 12:20:00

**Current Wave**: Wave 3 (Epic Execution)
