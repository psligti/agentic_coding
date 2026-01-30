Epics (TUI Coding Agent)
	1.	TUI Shell & Navigation
	2.	Providers & Accounts
	3.	Sessions
	4.	Agents
	5.	Skills
	6.	Tools
	7.	Themes & UX
	8.	Observability & Safety

⸻

User stories + Gherkins

Epic 1 — TUI Shell & Navigation

Story 1.1 — Launch & Home
	•	As a developer, I want a home screen that shows my current provider/account, recent sessions, and quick actions, so I can start work fast.

Feature: Home screen
  Scenario: Show quick actions on launch
    Given I launch the TUI
    When the home screen loads
    Then I should see the active provider and account
    And I should see a list of recent sessions
    And I should see actions for "New Session", "Resume Session", and "Settings"

  Scenario: Resume a recent session
    Given I am on the home screen
    And I have at least one recent session
    When I select a recent session and confirm
    Then the session should open
    And the session state should be loaded from storage

Story 1.2 — Global command palette
	•	As a developer, I want a command palette, so I can quickly reach any action without memorizing deep menus.

Feature: Command palette
  Scenario: Open command palette and run an action
    Given I am anywhere in the TUI
    When I open the command palette
    And I type "new session"
    And I select the matching action
    Then a new session should be created
    And I should be taken to the session view

  Scenario: Command palette respects permissions
    Given I am logged in with a restricted account
    When I open the command palette
    Then actions I do not have access to should not be shown


⸻

Epic 2 — Providers & Accounts

Story 2.1 — Provider configuration
	•	As a developer, I want to add/edit/remove providers (OpenAI, Anthropic, local, etc.), so I can switch backends.

Feature: Provider management
  Scenario: Add a provider
    Given I am in Provider Settings
    When I add a provider with a name, base URL, and model list
    Then the provider should be saved
    And it should appear in the provider list

  Scenario: Validate provider connectivity
    Given I have a configured provider
    When I run "Test Connection"
    Then the TUI should show success or a specific error message
    And the error should include retry guidance when possible

Story 2.2 — Accounts & credentials
	•	As a developer, I want to manage accounts per provider (API keys, profiles), so I can use multiple identities safely.

Feature: Account management
  Scenario: Add account with secret credential
    Given I am in Account Settings for a provider
    When I create a new account and enter an API key
    Then the API key should be stored securely
    And it should never be displayed in full after saving

  Scenario: Switch active account
    Given I have multiple accounts configured for a provider
    When I select an account as active
    Then new sessions should use the active account by default
    And existing sessions should keep their current account unless I change them


⸻

Epic 3 — Sessions

Story 3.1 — Create session with context
	•	As a developer, I want to create a session with repo path, goals, and constraints, so the agent has the right working context.

Feature: Session creation
  Scenario: Create a session with repo context
    Given I am on the home screen
    When I choose "New Session"
    And I set repo path, objective, and constraints
    Then the session should be created
    And the session header should show repo path and objective

  Scenario: Reject invalid repo path
    Given I am creating a session
    When I enter a repo path that does not exist
    Then I should see a validation error
    And the session should not be created

Story 3.2 — Persist & resume
	•	As a developer, I want sessions to persist (messages, tool calls, artifacts), so I can stop and resume without losing work.

Feature: Session persistence
  Scenario: Auto-save session state
    Given I have an open session
    When I send messages or run tools
    Then the session state should be saved automatically
    And I should see a non-intrusive save indicator

  Scenario: Resume session exactly
    Given I previously saved a session
    When I reopen the session
    Then the timeline should match the prior state
    And pending tasks should be restored

Story 3.3 — Session export
	•	As a developer, I want to export a session to Markdown/JSON, so I can share or audit what happened.

Feature: Session export
  Scenario: Export to Markdown
    Given I have a completed session
    When I export the session as Markdown
    Then the export should include messages, decisions, and tool usage summaries
    And secrets should be redacted

  Scenario: Export to JSON for automation
    Given I have a session with tool calls
    When I export as JSON
    Then the JSON should include structured tool call records
    And each record should include timestamps and outcomes


⸻

Epic 4 — Agents

Story 4.1 — Agent selection & capabilities
	•	As a developer, I want to choose an agent profile (coder/reviewer/planner) and see its capabilities, so I know what it will do.

Feature: Agent selection
  Scenario: Choose agent profile when starting session
    Given I am creating a session
    When I select the "Coder" agent profile
    Then the session should display the agent's description
    And the session should list enabled skills and tools

  Scenario: Prevent running with missing prerequisites
    Given an agent requires tools that are not available
    When I select that agent
    Then I should be warned about missing prerequisites
    And I should be offered options to install/enable them or choose another agent

Story 4.2 — Agent configuration per session
	•	As a developer, I want to override agent settings per session (model, temperature, budget), so I can tune behavior to the task.

Feature: Per-session agent configuration
  Scenario: Override model settings
    Given I have an open session
    When I open "Session Settings"
    And I change model and temperature
    Then subsequent agent turns should use the new settings
    And the change should be recorded in the session audit trail


⸻

Epic 5 — Skills

Story 5.1 — Browse and enable skills
	•	As a developer, I want to enable/disable skills (planning, refactor, tests, docs), so I can control what the agent is allowed to do.

Feature: Skill management
  Scenario: Enable a skill in a session
    Given I have an open session
    When I open the Skills panel
    And I enable "Test Generation"
    Then the skill should become available to the agent
    And the session should record that the skill was enabled

  Scenario: Disable a risky skill
    Given "Shell Execution" is enabled
    When I disable "Shell Execution"
    Then the agent should be blocked from using shell tools
    And any attempt should produce a clear denial message

Story 5.2 — Skill-scoped prompts
	•	As a developer, I want each skill to have its own prompt contract and output schema, so results are consistent and machine-readable.

Feature: Skill contracts
  Scenario: Skill returns structured results
    Given a skill "Code Review" is enabled
    When the agent runs the skill
    Then the output should include a structured list of findings
    And each finding should include severity, file, and recommended fix


⸻

Epic 6 — Tools

Story 6.1 — Tool discovery & permissioning
	•	As a developer, I want to see which tools are available (filesystem, git, tests, search), and which are permitted, so I can trust agent actions.

Feature: Tool discovery and permissions
  Scenario: Show tools and permission state
    Given I open the Tools panel
    Then I should see a list of tools
    And each tool should show "Allowed" or "Denied" and why

  Scenario: Deny tool usage without consent
    Given "Write Files" requires confirmation
    When the agent attempts to write files
    Then I should be prompted to approve or deny
    And if I deny, no files should be changed

Story 6.2 — Tool execution log
	•	As a developer, I want a tool execution log with inputs/outputs and diffs, so I can audit changes.

Feature: Tool execution log
  Scenario: Show a tool call record
    Given the agent ran a "Git Diff" tool
    When I open the tool log entry
    Then I should see the tool name, timestamp, and parameters
    And I should see the output or summary
    And if files changed, I should see a diff preview


⸻

Epic 7 — Themes & UX

Story 7.1 — Theme selection
	•	As a developer, I want to switch themes (dark/light/high-contrast) and font/layout density, so the TUI fits my environment.

Feature: Themes
  Scenario: Change theme
    Given I am in Appearance Settings
    When I select "High Contrast"
    Then the UI should update immediately
    And the theme should persist after restart

  Scenario: Accessibility-friendly defaults
    Given I enable "Reduced motion"
    When transitions would normally animate
    Then animations should be disabled

Story 7.2 — Keybindings
	•	As a developer, I want configurable keybindings, so I can optimize my workflow.

Feature: Keybindings
  Scenario: Rebind an action
    Given I am in Keybinding Settings
    When I bind "Open command palette" to "Ctrl+P"
    Then "Ctrl+P" should open the command palette
    And conflicts should be detected and displayed

  Scenario: Restore defaults
    Given I customized keybindings
    When I select "Restore defaults"
    Then keybindings should revert to default mappings


⸻

Epic 8 — Observability & Safety

Story 8.1 — Session timeline & statuses
	•	As a developer, I want a timeline that labels planning/tooling/coding/review steps, so I can understand progress and failure points.

Feature: Timeline and status tracking
  Scenario: Label timeline events
    Given I have an open session
    When the agent produces a plan and then runs tools
    Then timeline entries should be labeled "Plan" and "Tool"
    And failures should be labeled and expandable

  Scenario: Mark session as blocked
    Given the agent cannot proceed due to missing credentials
    When the agent detects the blocker
    Then the session status should become "Blocked"
    And the UI should show the reason and next steps

Story 8.2 — Safety rails for destructive actions
	•	As a developer, I want guardrails for destructive operations (delete, force push, mass refactor), so accidents don’t happen.

Feature: Destructive action safeguards
  Scenario: Require confirmation for destructive git operations
    Given "Force push" is considered destructive
    When the agent attempts a force push
    Then I should be shown a confirmation dialog describing impact
    And the default action should be "Cancel"

  Scenario: Dry-run mode for bulk changes
    Given the agent proposes changes across many files
    When I enable "Dry-run"
    Then the agent should only produce a diff/patch preview
    And no files should be modified

Absolutely — “Posting” has a bunch of TUI interaction patterns worth copying directly into your coding-agent TUI.

Design notes to borrow from Posting

Core interaction patterns
  • Command palette (global, searchable actions) opened with Ctrl+P.  ￼
  • Jump mode for fast focus switching between panes/widgets (Ctrl+O, then a single key).  ￼
  • Contextual help per focused widget (F1 / Ctrl+?) that lists all bindings and tips for that widget (not just footer hints).  ￼
  • Runtime view controls in the command palette (expand/collapse/“fullscreen” sections, sidebar toggle).  ￼

Customization system
  • Theme system in YAML with built-ins + user themes, hot reload / live preview while editing.  ￼
  • Config layering: config file + env vars + dotenv.  ￼
  • Keymap overrides in config (IDs mapped to key chords, multiple keys per action).  ￼
  • Layout switching (horizontal/vertical) and compact spacing mode to fit more on screen (also toggleable at runtime).  ￼

Power-user workflow glue
  • Open focused text in external editor (F4) and pager (F3), with a special JSON pager option.  ￼
  • “Designed for efficient workflows”: keyboard-centric, autocompletion, etc.  ￼


