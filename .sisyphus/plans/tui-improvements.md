# TUI Improvements Plan

## TL;DR

> **Quick Summary**: Fix three TUI issues - change 'q' quit to ctrl+q, add agent conversation system with selector, add dedicated Settings screen, and enhance session management (switch/create, configure agents/models/themes).
>
> **Deliverables**:
> - Fixed keyboard bindings (q → ctrl+q for quit)
> - Agent selector in MessageScreen with change-anytime capability
> - Dedicated Settings screen (theme, model, agent selection)
> - Enhanced session management (switch, create, configure)
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Keybinding fixes → Settings screen → Agent selector → Integration testing

---

## Context

### Original Request
User reported three TUI issues:
1. No location for prompts in ./opencode/ - actually meant: no way to start conversations with agents
2. 'q' button quits even when typing words with 'q' - keyboard binding issue
3. Menus lack all options and settings - incomplete UI

### Interview Summary

**Key Discussions**:
- **'q' key fix**: Change to ctrl+q (user choice)
- **Agent conversations**: Don't want to manage prompts, just start conversations with defined agents
- **Agent selector**: Pre-started with agent (default: 'build'), can change anytime
- **Settings**: Dedicated screen (not command palette only) with theme, model, agent selection
- **Session management**: Choose agents, models, themes, switch sessions, create new sessions
- **NO deletion or rename**: User clarified not needed

**User Decisions**:
- Quit key: ctrl+q instead of 'q'
- Default agent: 'build' on TUI startup
- Settings: Dedicated Settings screen
- Session management: Switch sessions, create new, configure (no delete/rename)
- Test strategy: Tests after implementation (pytest with pytest-asyncio)

### Research Findings

**TUI Framework**: Textual (Python)
- Main app: `opencode_python/src/opencode_python/tui/app.py`
- Keybindings: `opencode_python/src/opencode_python/tui/keybindings.py`
- Dialogs: `opencode_python/src/opencode_python/tui/dialogs/` (CommandPaletteDialog, ModelSelectDialog, ThemeSelectDialog, SelectDialog, ConfirmDialog, PromptDialog)
- Screens: `opencode_python/src/opencode_python/tui/screens/` (MessageScreen, SessionListScreen, ContextBrowser)
- Widgets: `opencode_python/src/opencode_python/tui/widgets/` (SessionHeader, SessionFooter)

**Agent Config**: Python codebase agents (`agents/builtin.py`)
- 4 agents available: build, plan, general, explore
- Each agent defined in Python code

**Settings System**: `core/settings.py`
- Pydantic BaseSettings with provider_default, model_default, tui_theme
- Environment variable driven with OPENCODE_PYTHON_ prefix

**Current Keybinding Locations**:
- `app.py` line 62: `Binding("q", "quit", "Quit")`
- `keybindings.py` line 11: `Binding("q", "quit", "Quit", show=True)`
- `footer.py` line 85: hints `"q: quit | /: commands | Enter: confirm | Escape: cancel"`
- All screens: Each has own BINDINGS arrays with escape, ctrl+c

### Metis Review

**Identified Gaps** (addressed):
- **Agent switching behavior**: Affects only future messages (no handover messages)
- **Pre-started definition**: UI state only, no API calls until first message
- **Settings persistence**: Use existing Settings class
- **Scope creep guardrails**: No agent descriptions, filtering, favorites; no custom keybinding editor; no session tags/search

---

## Work Objectives

### Core Objective
Enhance TUI with fixed keyboard bindings, agent conversation capability, dedicated Settings screen, and improved session management.

### Concrete Deliverables
1. Keybinding changes (q → ctrl+q) across all TUI screens and components
2. Agent selector in MessageScreen with default 'build' agent and change-anytime capability
3. Dedicated Settings screen with theme, model, and agent selection
4. Enhanced session management (switch sessions, create new, configure agents/models/themes)

### Definition of Done
- [ ] 'q' key types normally in input fields without triggering quit
- [ ] 'ctrl+q' quits from all screens (app, MessageScreen, SessionListScreen, dialogs)
- [ ] Footer displays "ctrl+q: quit" hints
- [ ] Agent selector visible in MessageScreen with default 'build' agent
- [ ] User can change agent before or during conversation
- [ ] Settings screen accessible with theme, model, agent selection
- [ ] Settings changes persist via Settings class
- [ ] User can switch between sessions
- [ ] User can create new sessions with custom title
- [ ] All tests pass: `pytest tests/ -v`

### Must Have
- Ctrl+q quit behavior across all screens
- Agent selector in MessageScreen (dropdown or similar)
- Default 'build' agent selected on TUI startup
- Dedicated Settings screen (not just command palette)
- Session list with switch and create functionality
- Settings persistence using existing Settings class

### Must NOT Have (Guardrails)
- **Agent descriptions, filtering, favorites, last-used tracking** - scope creep
- **Custom keybinding editor** - read-only display only
- **New CSS themes** - use existing ones only
- **Session deletion or rename** - user clarified not needed
- **Session search/filtering, tags, export/import** - scope creep
- **Agent handover messages when switching** - simple switch only
- **API calls on startup** - UI state only (pre-started)

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest, pytest-asyncio, pytest-cov)
- **User wants tests**: YES (Tests after implementation)
- **Framework**: pytest with pytest-asyncio
- **Test approach**: Add test tasks after implementation tasks
- **Test files location**: opencode_python/tests/tui/

### Automated Verification Strategy

**For Keybinding Changes**:
```bash
# Test 'q' key doesn't trigger quit in input fields
# Test 'ctrl+q' quits from app and all screens
# Verify footer hints updated
```

**For Agent Selector**:
```bash
# Test agent selector displays all agents from config
# Test selecting agent before starting conversation
# Test changing agent during conversation
# Test default 'build' agent on startup
```

**For Settings Screen**:
```bash
# Test Settings screen opens and closes correctly
# Test theme selection applies immediately
# Test model selection persists
# Test agent selection persists
```

**For Session Management**:
```bash
# Test switching between sessions
# Test creating new session with title
# Test new session appears in session list
```

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
├── Task 1: Fix 'q' → 'ctrl+q' keybindings
└── Task 4: Create dedicated Settings screen

Wave 2 (After Wave 1):
├── Task 2: Add agent selector to MessageScreen
└── Task 5: Enhance session management (switch, create)

Wave 3 (After Wave 2):
└── Task 3: Wire Settings screen into TUI

Wave 4 (After Wave 3):
└── Task 6: Add tests and integration testing

CRITICAL: Tests run IN PARALLEL with their respective features (Task 6 creates tests for Tasks 1-6 simultaneously, not as final wave)

Critical Path: Task 1 → Task 4 → Task 2 → Task 3 → Task 6
Parallel Speedup: ~60% faster than sequential (tests run in parallel with features)
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 | None | 2, 4 | None |
| 2 | 1 | 3, 5 | 5 |
| 3 | 2, 4 | 6 | None (final) |
| 4 | None | 3 | 1 |
| 5 | 1 | 6 | 2, 3 |
| 6 | 2, 3, 5 | None | None (final, runs in parallel with implementation tasks) |

NOTE: Task 6 (tests) runs in parallel with Tasks 1-5, not as a sequential final wave.

### Agent Dispatch Summary

| Wave | Tasks | Recommended Agents |
|------|-------|-------------------|
| 1 | 1, 4 | delegate_task(category="quick", load_skills=[], run_in_background=true) |
| 2 | 2, 5 | delegate_task(category="visual-engineering", load_skills=["frontend-ui-ux"], run_in_background=true) |
| 3 | 3 | delegate_task(category="quick", load_skills=[], run_in_background=false) |
| 6 | 1, 2, 3, 4, 5, 6 | delegate_task(category="quick", load_skills=[], run_in_background=true, session_id="<test-tasks>") |

NOTE: Task 6 (tests) runs in parallel with Tasks 1-5, not as a sequential final wave.

---

## TODOs

> Implementation + Test = ONE Task. Never separate.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info.

- [x] 1. Fix 'q' → 'ctrl+q' keybindings across all TUI components

  **What to do**:
  - Replace `Binding("q", "quit")` with `Binding("ctrl+q", "quit")` in:
    - `app.py` BINDINGS array
    - `keybindings.py` keybindings list
   - Update footer hints in `widgets/footer.py` (line 85) from `"q: quit"` to `"ctrl+q: quit"`
   - Verify specific screens (MessageScreen, SessionListScreen, ContextBrowser, SettingsScreen, all dialogs) use ctrl+q or inherit from app
  - Ensure 'q' key works for typing in Input widgets (should not trigger quit)

  **Must NOT do**:
  - Don't change ctrl+c quit behavior (keep as fallback)
  - Don't add other keyboard shortcuts (only q → ctrl+q)
  - Don't modify Input widget behavior (Textual handles this)

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Simple file replacements and edits across multiple files, straightforward task
  - **Skills**: `[]`
    - No specific skills needed - basic file editing only
  - **Skills Evaluated but Omitted**:
    - `git-master`: Not needed - just file editing, no git operations
    - `frontend-ui-ux`: Not needed - keyboard bindings, no UI components

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 4)
  - **Blocks**: Tasks 2, 5
  - **Blocked By**: None

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `opencode_python/src/opencode_python/tui/app.py:61-65` - BINDINGS array pattern
   - `opencode_python/src/opencode_python/tui/keybindings.py:10-20` - Keybindings list structure
   - `opencode_python/src/opencode_python/tui/widgets/footer.py:85` - Footer hints string location
  - `opencode_python/src/opencode_python/tui/screens/message_screen.py` - Screen BINDINGS pattern

  **API/Type References** (contracts to implement against):
  - `textual.widgets.Select` - Dropdown/select widget for agent selection
  - `textual.widgets.Input` - Input widget for message typing
  - `core/models.py:Message` - Message model structure
  - `core/models.py:Session` - Session model structure (verify fields for metadata)
  - `core/settings.py:Settings` - Settings class (verify if agent_default field exists, or add new field)
  - `core/session.py:SessionManager` - Session CRUD methods (verify create_session signature for metadata)

  **Implementation Details**:
  - Agent storage: Add `agent_default` field to Settings class OR verify Session model has agent field
  - Agent loading: Load agent list from Python code (`agents/builtin.py`)
  - AISession integration: Modify `_start_ai_stream()` to accept agent parameter, pass agent name directly
  - Agent selector location: Add to MessageScreen's input-area Horizontal container, between SessionHeader and messages_container (see message_screen.py compose() for layout structure)
  - Selector widget: Use `textual.widgets.Select` with options generated from agent list
  - Agent storage in MessageScreen: Add `self.current_agent: reactive[str]` property with default "build"
  - Agent storage in Session: Add optional `agent: Optional[str]` field to Session model in core/models.py

  **Dependencies**: Task 6 must create test files BEFORE Tasks 1-5 can reference them. Tasks 1-5 acceptance criteria will reference tests created in Task 6.

  **Test References**:
  - `opencode_python/tests/tui/test_dialogs.py` - Dialog testing pattern
  - `opencode_python/tests/tui/test_header.py` - Header widget testing

  **Documentation References**:
  - Textual Select widget: https://textual.textual.io/widgets/select

  **WHY Each Reference Matters**:
  - `model_select_dialog.py` - Shows how to create selection UI with ListView, can reuse pattern
  - `message_screen.py` - Main screen to modify, needs agent selector integration
  - `header.py` - Location to display current agent name, pattern for widget updates

  **Acceptance Criteria**:

  ```bash
  # Test agent selector displays all agents from config
  python -m pytest tests/tui/test_message_screen.py::test_agent_selector_shows_all_agents -v
  # Expected: PASS

  # Test default 'build' agent selected on startup
  python -m pytest tests/tui/test_message_screen.py::test_default_agent_is_build -v
  # Expected: PASS

  # Test changing agent before starting conversation
  python -m pytest tests/tui/test_message_screen.py::test_change_agent_before_conversation -v
  # Expected: PASS

  # Test changing agent during conversation
  python -m pytest tests/tui/test_message_screen.py::test_change_agent_during_conversation -v
  # Expected: PASS

  # Test agent name displayed in header
  python -m pytest tests/tui/test_header.py::test_header_shows_current_agent -v
  # Expected: PASS
  ```

  **Evidence to Capture**:
  - [ ] pytest output showing all agent selector tests pass
  - [ ] Screenshot of MessageScreen with agent selector visible

  **Commit**: YES
  - Message: `feat(tui): add agent selector to MessageScreen`
  - Files: `screens/message_screen.py, widgets/header.py`
  - Pre-commit: `pytest tests/tui/test_message_screen.py -v`

---

- [x] 3. Wire Settings screen into TUI (add keyboard shortcut or menu access)

  **What to do**:
  - Add keyboard shortcut or menu option to open Settings screen
  - Update command palette dialog to include "settings" command
  - Ensure Settings screen can be opened from main app and sub-screens
  - Wire Settings screen actions to persist via Settings class
  - Ensure theme changes apply immediately to TUI
  - Ensure model changes persist to Settings
  - Ensure agent changes persist to Settings

  **Implementation Details**:
  - Theme application: Use `self.app.theme = theme_name` to apply theme immediately
  - Settings persistence: Call `settings.tui_theme = selected_theme; settings.save()` (or equivalent)
  - Pattern reference: See Textual docs on theme switching, no existing pattern in codebase

  **Must NOT do**:
  - Don't add custom keybinding editor (read-only display only)
  - Don't add new CSS themes (use existing ones)
  - Don't add advanced preferences (timezone, language, notifications)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Integration work - wiring existing components together
  - **Skills**: `[]`
    - No specific skills needed - basic wiring of dialog/app
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: Not needed - Settings screen already created
    - `git-master`: Not needed - no git operations

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (after Wave 2)
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 2, 4

  **References**:

  **Pattern References**:
  - `opencode_python/src/opencode_python/tui/dialogs/command_palette_dialog.py` - Command palette structure
  - `opencode_python/src/opencode_python/tui/app.py:263-267` - action_open_command pattern
  - `opencode_python/src/opencode_python/tui/app.py:61-65` - BINDINGS array for adding settings shortcut

  **API/Type References**:
  - `core/settings.py:Settings` - Settings class with persistence
  - `textual.app.App.push_screen()` - Screen navigation method

  **Test References**:
  - `opencode_python/tests/tui/test_dialogs.py::test_command_palette` - Command palette testing

  **Documentation References**:
  - Textual screen management: https://textual.textual.io/guide/screens

  **WHY Each Reference Matters**:
  - `command_palette_dialog.py` - Shows commands list structure, needs "settings" command added
  - `app.py:263-267` - Shows how to add action_open_command, similar for action_open_settings
  - `app.py:61-65` - BINDINGS array, needs settings shortcut (e.g., 's' key)

  **Acceptance Criteria**:

  ```bash
  # Test Settings screen opens via command palette
  python -m pytest tests/tui/test_app.py::test_settings_opens_from_command_palette -v
  # Expected: PASS

  # Test Settings screen opens via keyboard shortcut
  python -m pytest tests/tui/test_app.py::test_settings_opens_via_shortcut -v
  # Expected: PASS

  # Test theme selection applies immediately
  python -m pytest tests/tui/test_app.py::test_theme_applies_immediately -v
  # Expected: PASS

  # Test model selection persists
  python -m pytest tests/tui/test_settings_screen.py::test_model_persists -v
  # Expected: PASS

  # Test agent selection persists
  python -m pytest tests/tui/test_settings_screen.py::test_agent_persists -v
  # Expected: PASS
  ```

  **Evidence to Capture**:
  - [ ] pytest output showing all Settings wiring tests pass
  - [ ] Screenshot of Settings screen accessible from command palette

  **Commit**: YES
  - Message: `feat(tui): wire Settings screen into TUI`
  - Files: `app.py, dialogs/command_palette_dialog.py`
  - Pre-commit: `pytest tests/tui/test_app.py::test_settings -v`

---

- [x] 4. Create dedicated Settings screen with theme, model, and agent selection

  **What to do**:
  - Create new `settings_screen.py` in `screens/` directory
  - Reuse existing `ThemeSelectDialog` for theme selection
  - Reuse existing `ModelSelectDialog` for model selection
  - Create agent selector similar to MessageScreen agent selector
  - Organize screen with sections or tabs for each setting type
  - Add Save and Cancel buttons
  - Apply theme selection immediately (no restart needed)
  - Persist model and agent selections via Settings class
  - Follow existing dialog/screen patterns (ModalScreen, compose method)

  **Implementation Details**:
  - Use Vertical container with three sections (theme, model, agent), NOT tabs
  - Reuse `ThemeSelectDialog` and `ModelSelectDialog` logic IN-SCREEN: Copy ListView widget patterns from `model_select_dialog.py:76-86` inline (not as separate ModalScreens)
  - Create `agent_select_widget` using same ListView pattern from `model_select_dialog.py:76-86`
  - Pattern reference: See `session_list_screen.py:41-44` for Vertical layout pattern
  - Settings persistence: Use pydantic-settings built-in save() method OR implement custom file writing to .env (settings.py currently uses env variables, may need to support file-based persistence for runtime changes)
  - Load settings: Settings.instance is already loaded, can use directly for runtime updates

  **Must NOT do**:
  - Don't add custom keybinding editor
  - Don't add new CSS themes beyond existing
  - Don't add advanced preferences (timezone, language, sound effects)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Screen creation using existing dialog patterns, straightforward
  - **Skills**: `[]`
    - No specific skills needed - screen composition with existing widgets
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: Not needed - reusing existing dialog patterns

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 3
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `opencode_python/src/opencode_python/tui/dialogs/theme_select_dialog.py` - ThemeSelectDialog pattern
  - `opencode_python/src/opencode_python/tui/dialogs/model_select_dialog.py` - ModelSelectDialog pattern
  - `opencode_python/src/opencode_python/tui/dialogs/__init__.py:17-86` - BaseDialog and ConfirmDialog patterns
  - `opencode_python/src/opencode_python/tui/screens/session_list_screen.py` - Screen structure example

  **API/Type References**:
  - `textual.screen.ModalScreen` - Base class for settings screen
  - `textual.widgets.Button` - Save/Cancel buttons
  - `core/settings.py:Settings` - Settings class for persistence

  **Test References**:
  - `opencode_python/tests/tui/test_dialogs.py` - Dialog testing pattern
  - `opencode_python/tests/tui/test_header.py` - Widget testing pattern

  **Documentation References**:
  - Textual ModalScreen: https://textual.textual.io/guide/screens/#modal-screens

  **WHY Each Reference Matters**:
  - `theme_select_dialog.py` - Existing dialog to embed/reuse for theme section
  - `model_select_dialog.py` - Existing dialog to embed/reuse for model section
  - `dialogs/__init__.py:17-86` - Shows BaseDialog pattern, ConfirmDialog for Save/Cancel
  - `session_list_screen.py` - Example of screen structure, BINDINGS, compose method

  **Acceptance Criteria**:

  ```bash
  # Test Settings screen opens and closes correctly
  python -m pytest tests/tui/test_settings_screen.py::test_settings_opens -v
  # Expected: PASS

  # Test theme selection uses existing ThemeSelectDialog
  python -m pytest tests/tui/test_settings_screen.py::test_theme_selector_works -v
  # Expected: PASS

  # Test model selection uses existing ModelSelectDialog
  python -m pytest tests/tui/test_settings_screen.py::test_model_selector_works -v
  # Expected: PASS

  # Test agent selector displays all agents
  python -m pytest tests/tui/test_settings_screen.py::test_agent_selector_works -v
  # Expected: PASS

  # Test Save button persists settings
  python -m pytest tests/tui/test_settings_screen.py::test_save_persists -v
  # Expected: PASS

  # Test Cancel button discards changes
  python -m pytest tests/tui/test_settings_screen.py::test_cancel_discards -v
  # Expected: PASS
  ```

  **Evidence to Capture**:
  - [ ] pytest output showing all Settings screen tests pass
  - [ ] Screenshot of Settings screen with theme/model/agent sections

  **Commit**: YES
  - Message: `feat(tui): create dedicated Settings screen`
  - Files: `screens/settings_screen.py`
  - Pre-commit: `pytest tests/tui/test_settings_screen.py -v`

---

- [x] 5. Enhance session management (switch sessions, create new, configure agents/models/themes)

  **What to do**:
  - Add "Create Session" button to SessionListScreen or main app
  - Add "Create Session" command to command palette
  - Use PromptDialog to get session title from user
  - Create new session via SessionManager
  - Allow switching between sessions via DataTable selection in SessionListScreen
  - Ensure session metadata includes selected agent, model, theme
  - Display current session info in SessionHeader
  - Follow existing session CRUD patterns (SessionManager, SessionStorage)

  **Implementation Details**:
  - Session metadata storage: Add agent, model, theme fields to Session model in core/models.py (update extra='forbid' to extra='allow' or declare fields with forward refs)
  - Update SessionManager.create_session() signature to accept optional agent, model, theme parameters
  - Pattern reference: See core/models.py for Session model structure, verify field compatibility
  - "Create Session" button location: Add to SessionListScreen sidebar (below DataTable) or main app toolbar (executor can choose based on UX)
  - Session creation UX: PromptDialog gets title, then show agent/model/theme selectors before final creation
  - Agent/model/theme for new session: Use MessageScreen agent selector value (runtime) OR show 3-way dialog (agent, model, theme)
  - Dialog flow: If user provides title, then immediately show new session with configured settings

  **Must NOT do**:
  - Don't add session deletion or rename
  - Don't add search/filtering, tags, export/import
  - Don't add session grouping or advanced metadata

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI enhancements (buttons, session switching), session management UX
  - **Skills**: `["frontend-ui-ux"]`
    - `frontend-ui-ux`: Designing session management UX, button placement, session selection
  - **Skills Evaluated but Omitted**:
    - `git-master`: Not needed - session management via SessionManager, no git operations

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Task 2)
  - **Blocks**: Task 6
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `opencode_python/src/opencode_python/tui/screens/session_list_screen.py` - SessionListScreen structure
  - `opencode_python/src/opencode_python/core/session.py:SessionManager` - Session CRUD methods
  - `opencode_python/src/opencode_python/tui/dialogs/__init__.py:305-391` - PromptDialog for getting session title
  - `opencode_python/src/opencode_python/tui/dialogs/command_palette_dialog.py` - Command palette for adding "create-session" command

  **API/Type References**:
  - `core/session.py:SessionManager.create_session()` - Method to create new session
  - `core/models.py:Session` - Session model structure
  - `textual.widgets.DataTable` - Session list widget

  **Test References**:
  - `opencode_python/tests/tui/test_dialogs.py` - Dialog testing pattern
  - `opencode_python/tests/test_export_import.py` - SessionManager testing examples

  **Documentation References**:
  - Textual DataTable: https://textual.textual.io/widgets/data-table

  **WHY Each Reference Matters**:
  - `session_list_screen.py` - Screen to modify for "Create Session" button
  - `session.py:SessionManager` - Shows create_session method to call
  - `dialogs/__init__.py:305-391` - PromptDialog pattern for getting title
  - `command_palette_dialog.py` - Needs "create-session" command added

  **Acceptance Criteria**:

  ```bash
  # Test creating new session with title
  python -m pytest tests/tui/test_session_list_screen.py::test_create_session_with_title -v
  # Expected: PASS

  # Test new session appears in session list
  python -m pytest tests/tui/test_session_list_screen.py::test_new_session_in_list -v
  # Expected: PASS

  # Test switching between sessions
  python -m pytest tests/tui/test_session_list_screen.py::test_switch_sessions -v
  # Expected: PASS

  # Test "Create Session" command in command palette
  python -m pytest tests/tui/test_dialogs.py::test_create_session_command -v
  # Expected: PASS
  ```

  **Evidence to Capture**:
  - [ ] pytest output showing all session management tests pass
  - [ ] Screenshot of SessionListScreen with "Create Session" button

  **Commit**: YES
  - Message: `feat(tui): enhance session management (create, switch, configure)`
  - Files: `screens/session_list_screen.py, dialogs/command_palette_dialog.py`
  - Pre-commit: `pytest tests/tui/test_session_list_screen.py -v`

---

- [x] 6. Add comprehensive tests for all TUI improvements

  **What to do**:
  - Create test file `tests/tui/test_app.py` for app-level tests (keybindings, settings access)
  - Create test file `tests/tui/test_settings_screen.py` for Settings screen tests
  - Add tests to `tests/tui/test_message_screen.py` for agent selector tests
  - Add tests to `tests/tui/test_session_list_screen.py` for session management tests
  - Ensure all tests use pytest-asyncio pattern
  - Verify 'q' key doesn't trigger quit in all contexts
  - Verify 'ctrl+q' quits from all screens
  - Verify agent selector works in all scenarios
  - Verify Settings screen persistence
  - Verify session management operations
  - Run full test suite: `pytest tests/ -v --cov=opencode_python`
  - Ensure coverage meets minimum (target: 80%)

  **Must NOT do**:
  - Don't add end-to-end tests requiring API calls
  - Don't add UI screenshot tests (manual only)
  - Don't add integration tests with external services

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Test file creation and test writing, straightforward
  - **Skills**: `[]`
    - No specific skills needed - pytest test writing
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not needed - unit tests only, no browser
    - `git-master`: Not needed - tests only

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (final wave)
  - **Blocks**: None
  - **Blocked By**: Tasks 2, 3, 5

  **References**:

  **Pattern References**:
  - `opencode_python/tests/tui/test_dialogs.py` - Test structure example
  - `opencode_python/tests/tui/test_footer.py` - Widget testing example
  - `opencode_python/tests/tui/test_header.py` - Widget testing with pytest-asyncio
  - `opencode_python/pyproject.toml:23-25` - pytest configuration

  **API/Type References**:
  - `pytest-asyncio` - Async test support
  - `textual.app.App` - App class for testing

  **Test References**:
  - All test files in `tests/tui/` directory

  **Documentation References**:
  - pytest documentation: https://docs.pytest.org/en/stable/
  - pytest-asyncio: https://pytest-asyncio.readthedocs.io/

  **WHY Each Reference Matters**:
  - `test_dialogs.py` - Shows test structure, fixtures, pytest-asyncio usage
  - `test_footer.py`, `test_header.py` - Widget testing patterns
  - `pyproject.toml:23-25` - Shows pytest config (asyncio_mode, testpaths)

  **Acceptance Criteria**:

  ```bash
  # Run full test suite
  pytest tests/ -v --cov=opencode_python
  # Expected: All tests pass, coverage >= 80%

  # Test keybinding changes
  pytest tests/tui/test_app.py -v
  # Expected: PASS

  # Test agent selector
  pytest tests/tui/test_message_screen.py -v
  # Expected: PASS

  # Test Settings screen
  pytest tests/tui/test_settings_screen.py -v
  # Expected: PASS

  # Test session management
  pytest tests/tui/test_session_list_screen.py -v
  # Expected: PASS
  ```

  **Evidence to Capture**:
  - [ ] pytest output showing all tests pass
  - [ ] Coverage report showing >= 80%

  **Commit**: YES
  - Message: `test(tui): add comprehensive tests for TUI improvements`
  - Files: `tests/tui/test_app.py, tests/tui/test_settings_screen.py, tests/tui/test_message_screen.py, tests/tui/test_session_list_screen.py`
  - Pre-commit: `pytest tests/ -v --cov`

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `fix(tui): change 'q' to 'ctrl+q' for quit` | app.py, keybindings.py, widgets/footer.py | pytest tests/tui/test_app.py -v |
| 2 | `feat(tui): add agent selector to MessageScreen` | screens/message_screen.py, widgets/header.py | pytest tests/tui/test_message_screen.py -v |
| 3 | `feat(tui): wire Settings screen into TUI` | app.py, dialogs/command_palette_dialog.py | pytest tests/tui/test_app.py::test_settings -v |
| 4 | `feat(tui): create dedicated Settings screen` | screens/settings_screen.py | pytest tests/tui/test_settings_screen.py -v |
| 5 | `feat(tui): enhance session management` | screens/session_list_screen.py, dialogs/command_palette_dialog.py | pytest tests/tui/test_session_list_screen.py -v |
| 6 | `test(tui): add comprehensive tests` | tests/tui/test_app.py, test_settings_screen.py, test_message_screen.py, test_session_list_screen.py | pytest tests/ -v --cov |

---

## Success Criteria

### Verification Commands
```bash
# Run full test suite
pytest tests/ -v --cov=opencode_python

# Start TUI and verify ctrl+q quits
python -m opencode_python.tui.app
# Press ctrl+q → TUI exits

# Start TUI and verify agent selector visible
python -m opencode_python.tui.app
# Verify agent selector shows 'build' default

# Start TUI and open Settings
python -m opencode_python.tui.app
# Press '/' → type 'settings' → press Enter
# Settings screen opens
```

### Documentation Updates

**Architecture Documentation**:
- Update TUI architecture docs to describe agent selector, Settings screen, and keybinding changes
- Document session metadata structure (agent, model, theme fields)
- Update keyboard binding documentation (ctrl+q instead of 'q')

**Design Documentation**:
- Create mockups or diagrams for agent selector placement in MessageScreen
- Document Settings screen layout (theme, model, agent sections)
- Document session creation flow with agent/model/theme selection

**ADR (Architecture Decision Records)**:
- ADR for adding agent_default field to Settings class (runtime persistence approach)
- ADR for Session model extension (metadata fields for agent/model/theme)
  - ADR for agent selection in Python TUI (using agents/builtin.py)
- ADR for agent selector UI pattern (Select widget vs custom implementation)

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass (pytest tests/ -v)
- [ ] Coverage >= 80% (--cov option)
- [ ] 'q' key types normally in input fields
- [ ] 'ctrl+q' quits from all screens
- [ ] Agent selector works in MessageScreen
- [ ] Settings screen accessible and functional
- [ ] Session create and switch works
