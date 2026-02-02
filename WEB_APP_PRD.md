# Agentic Coding Agent Web UI (React) — Posting-inspired, Cleaner, Themeable

This is the same design/behavior spec as the Textual TUI version, but translated into a **React web app**. It keeps:
- **Conversation-first** main window (timeline is the “truth”)
- **Reactive composer** at the bottom
- **Top bar + bottom status bar**
- **Command palette** (Ctrl+K) for everything else
- **Right drawer overlay** with **vertical tabs**
- **Rounded corners everywhere**
- **Contrast-driven theming** (theme-agnostic tokens)
- **Border-embedded headers** (“legend header” on the border line)
- **Progressive disclosure** (thinking/tool details collapsed by default)

---

## 0) Layout Blueprint (Vertical Stack + Overlays)

**Always visible**
1) `TopBar` (fixed height)
2) `ConversationTimeline` (fills)
3) `ComposerBar` (auto-grow to max lines)
4) `BottomStatusBar` (fixed height)

**Overlays**
- `CommandPalette` (modal, centered, Ctrl+K)
- `RightDrawer` (overlay from right, Ctrl+D, width ~30–45%)

No permanent multi-pane layout. Drawer/palette provide all auxiliary navigation and controls.

---

## 1) Theme + Contrast System (Theme-agnostic tokens)

Use CSS variables + a theme registry. Themes only change token values; components never use hard-coded colors.

### Required tokens (CSS variables)
Surfaces
- `--surface-base`
- `--surface-panel`
- `--surface-raised`

Text
- `--text-primary`
- `--text-secondary`
- `--text-tertiary`

Borders
- `--border-normal`
- `--border-focus`

Accents
- `--accent-primary`
- `--accent-secondary`

States
- `--success`
- `--warning`
- `--error`
- `--info`

Radii (rounded corners everywhere)
- `--r-panel`
- `--r-control`
- `--r-pill`

Spacing
- `--pad-sm`
- `--pad-md`
- `--gap-sm`
- `--gap-md`

### Contrast rules (portable across themes)
- 3 surface levels: base → panel → raised
- 3 text levels: primary → secondary → tertiary
- Focus/selection must use **two cues**:
    - color + border thickness
    - OR color + glyph/icon
    - OR color + elevation (shadow) + border

### Theme switching
- Apply theme by toggling a `data-theme="dark"` attribute on `<html>` (or a theme class).
- All components rely on variables.

---

## 2) Rounded Corners Everywhere (no mixed geometry)

### Rule
Panels, controls, tabs, chips, buttons, modals, drawer, selection highlights all share a consistent radius system.

### Radii usage
- Panels: `border-radius: var(--r-panel)`
- Controls (buttons/inputs): `border-radius: var(--r-control)`
- Chips/badges: `border-radius: var(--r-pill)` (pill)

---

## 3) Border-Embedded Headers (“Legend Header”)

Posting-style motif: panel title sits “in the border”.

### Implementation pattern
- Panel border and background are normal.
- Title is a small pill/label overlapping the top border.

Rules:
- 1–3 words title
- Optional right-aligned chips (status/model/agent)
- Titles never wrap; truncate with ellipsis

---

## 4) Reduce Clutter: Progressive Disclosure Defaults

Collapsed by default:
- Thinking blocks
- Tool details beyond summary
- Metadata (timing, token counts, internal ids)

Expandable inline in each message card.

---

## 5) Component Mapping (React)

### App Shell
- `AppLayout`
    - `TopBar`
    - `ConversationTimeline`
    - `ComposerBar`
    - `BottomStatusBar`
    - `CommandPalette` (portal modal)
    - `RightDrawer` (portal overlay)

### Timeline cards (message transaction log)
Message types:
- `UserMessageCard`
- `AgentMessageCard`
- `ToolRunCard` (summary row + expandable details)
- `ThinkingCard` (collapsed by default)
- `QuestionCard` (needs-response highlight)
- `SystemCard`

Each card:
- Header row: role + timestamp + status chips
- Body: content (markdown)
- Footer row: actions (copy, expand, reference, rerun) shown on hover/focus

---

## 6) Keyboard Model (Web)

Global hotkeys (when not typing in a focused input unless specified):
- `Ctrl+K` → open command palette
- `Ctrl+D` → toggle right drawer
- `Esc` → close palette/drawer first; otherwise blur/cancel
- `Ctrl+Enter` → send message (safe default)
- Optional: `Ctrl+J / Ctrl+K` for timeline navigation (if you want vim-ish)

Focus rules:
- Default focus is the composer input.
- When palette opens:
    - focus palette input
    - restore prior focus on close
- Drawer open should not destroy composer draft

---

## 7) User Stories (same as TUI, adapted to Web)

### Epic A — Shell & Layout
- A1 Vertical stack shell
- A2 Universal rounded corners
- A3 Legend headers on panels

### Epic B — Conversation Timeline
- B1 Message cards
- B2 Collapsible thinking
- B3 Tool runs shown + expandable
- B4 Jump to message

### Epic C — Composer
- C1 Auto-growing input
- C2 Draft persistence

### Epic D — Command Palette
- D1 Open palette
- D2 Switch model/provider/account
- D3 Search & jump
- D4 Toggle compact/verbose + show/hide thinking

### Epic E — Drawer
- E1 Open drawer overlay
- E2 Vertical tabs
- E3 Navigator jumps timeline

### Epic F — Theming
- F1 Semantic tokens
- F2 Runtime theme switch

---

## 8) Gherkins (Acceptance Criteria — Web Specific)

### Feature: Command Palette Modal

Scenario: Open palette and focus input
Given the application is running
When I press Ctrl+K
Then the command palette modal should open
And focus should move to the palette input
And the background should remain visible behind the modal

Scenario: Close palette and restore focus
Given the command palette is open
And I had focus in the composer before opening it
When I press Escape
Then the palette should close
And focus should return to the composer

Scenario: Execute command from palette
Given the command palette is open
When I type a query and select a result
Then the selected command should run
And the palette should close

### Feature: Right Drawer Overlay

Scenario: Open drawer from keyboard
Given the application is running
When I press Ctrl+D
Then the right drawer should open as an overlay
And the drawer should occupy between 30% and 45% of the width

Scenario: Switch vertical tabs
Given the drawer is open
When I select the "Navigator" tab
Then the drawer content should update to show conversation index items
And the selected tab should show a focused highlight

Scenario: Jump from navigator to message
Given the drawer is open on Navigator
When I select a navigator item
Then the timeline should scroll to the associated message
And that message should be visually highlighted

### Feature: Conversation Timeline

Scenario: Thinking is collapsed by default
Given the agent produces thinking content
When the timeline renders
Then the thinking section should be collapsed
And only a one-line summary should be visible

Scenario: Expand tool details inline
Given a tool run is rendered as a card
When I click expand on the tool run
Then the detailed output should be displayed within the same card

### Feature: Theming

Scenario: Switching theme preserves contrast
Given multiple themes exist
When I switch themes
Then primary text remains readable against panel surfaces
And focus states remain visually distinct
And state colors remain recognizable

---

## 9) Component Checklists (React/Web)

### 9.1 Design Tokens & Theme Manager
- [ ] Theme registry (theme name → token values)
- [ ] Apply tokens via CSS variables on `:root` or `[data-theme]`
- [ ] Runtime theme switch
- [ ] No hard-coded colors in component styles
- [ ] Contrast QA checklist (manual)

### 9.2 AppLayout (Vertical Stack)
- [ ] Fixed top bar
- [ ] Scrollable timeline
- [ ] Auto-growing composer
- [ ] Fixed bottom status bar
- [ ] Overlays implemented via portals (palette + drawer)

### 9.3 TopBar
- [ ] Session name (truncate)
- [ ] Agent chip
- [ ] Provider/account/model chips
- [ ] Status chip (idle/running/error)
- [ ] Primary action button (Run/Stop)
- [ ] Rounded everything

### 9.4 ConversationTimeline
- [ ] Virtualized list (recommended for long sessions)
- [ ] MessageCard component + variants
- [ ] Collapsible sections for thinking/tool details
- [ ] Jump-to-anchor + highlight
- [ ] Copy action
- [ ] Actions appear on hover/focus (reduce clutter)

### 9.5 ComposerBar
- [ ] Auto-growing textarea (max lines)
- [ ] Send button
- [ ] Ctrl+Enter send
- [ ] Draft persistence while opening palette/drawer

### 9.6 BottomStatusBar
- [ ] Session indicator
- [ ] Last warning/error summary
- [ ] Key hints (Ctrl+K, Ctrl+D)

### 9.7 CommandPalette (Modal)
- [ ] Global open/close hotkeys
- [ ] Query input + results list
- [ ] Fuzzy search
- [ ] Executes selection and closes
- [ ] Focus trap while open
- [ ] Restores prior focus on close

### 9.8 RightDrawer (Overlay)
- [ ] Slide-in overlay right
- [ ] Vertical tabs on left edge of drawer
- [ ] List-first content per tab
- [ ] Navigator selection scrolls timeline
- [ ] Does not destroy composer draft

---

## 10) Recommended React Stack
- State: React Context + reducer (or Zustand)
- Modal/overlay: React Portal
- Hotkeys: `react-hotkeys-hook` or manual `keydown` listeners
- Virtualized list: `react-virtuoso` or `react-window`
- Markdown: `react-markdown`

---

## 11) Starter Skeleton (React)

~~~tsx
// App.tsx
import React, { useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";

type MessageKind = "user" | "agent" | "tool" | "thinking" | "question" | "system";

type TimelineItem = {
  id: string;
  kind: MessageKind;
  title?: string;      // e.g., tool name
  ts: number;
  status?: "idle" | "running" | "ok" | "warn" | "error";
  content: string;     // markdown
  collapsedByDefault?: boolean;
};

type CommandItem = {
  id: string;
  title: string;
  keywords: string;
  run: () => void;
};

function useGlobalHotkeys(handlers: {
  onPalette: () => void;
  onDrawer: () => void;
  onEscape: () => void;
}) {
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      // Avoid hijacking when typing in an input/textarea unless you want to allow it.
      const el = e.target as HTMLElement | null;
      const isTyping =
        el?.tagName === "INPUT" || el?.tagName === "TEXTAREA" || el?.isContentEditable;

      if (e.ctrlKey && e.key.toLowerCase() === "k") {
        e.preventDefault();
        handlers.onPalette();
        return;
      }
      if (e.ctrlKey && e.key.toLowerCase() === "d") {
        e.preventDefault();
        handlers.onDrawer();
        return;
      }
      if (e.key === "Escape") {
        handlers.onEscape();
        return;
      }

      // Ctrl+Enter send can be handled inside Composer (better, because it knows focus)
      if (isTyping) return;
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [handlers]);
}

function LegendPanel({
  title,
  right,
  children,
  className = "",
}: {
  title: string;
  right?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`panel ${className}`}>
      <div className="legend">
        <span className="legend__title">{title}</span>
        <span className="legend__right">{right}</span>
      </div>
      {children}
    </div>
  );
}

function MessageCard({
  item,
  onJumpFocus,
}: {
  item: TimelineItem;
  onJumpFocus?: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState(!item.collapsedByDefault);

  return (
    <div className={`panel message message--${item.kind}`} id={`msg-${item.id}`}>
      <div className="legend">
        <span className="legend__title">{item.kind.toUpperCase()}</span>
        <span className="legend__right">
          {item.status && <span className={`chip chip--${item.status}`}>{item.status}</span>}
          <span className="chip">{new Date(item.ts).toLocaleTimeString()}</span>
        </span>
      </div>

      {item.kind === "thinking" || item.kind === "tool" ? (
        <>
          <button className="control chip" onClick={() => setExpanded((v) => !v)}>
            {expanded ? "▾ Hide" : "▸ Show"} {item.kind === "thinking" ? "Thinking" : "Details"}
          </button>
          {expanded && <div className="message__body">{item.content}</div>}
        </>
      ) : (
        <div className="message__body">{item.content}</div>
      )}

      <div className="message__footer">
        <button className="control" onClick={() => navigator.clipboard.writeText(item.content)}>
          Copy
        </button>
        {onJumpFocus && (
          <button className="control" onClick={() => onJumpFocus(item.id)}>
            Focus
          </button>
        )}
      </div>
    </div>
  );
}

function CommandPalette({
  open,
  items,
  onClose,
}: {
  open: boolean;
  items: CommandItem[];
  onClose: () => void;
}) {
  const [q, setQ] = useState("");
  const inputRef = useRef<HTMLInputElement | null>(null);

  const filtered = useMemo(() => {
    const s = q.trim().toLowerCase();
    if (!s) return items;
    return items.filter((it) => it.title.toLowerCase().includes(s) || it.keywords.toLowerCase().includes(s));
  }, [q, items]);

  useEffect(() => {
    if (open) {
      setQ("");
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [open]);

  if (!open) return null;

  return createPortal(
    <div className="overlay" role="dialog" aria-modal="true" onMouseDown={onClose}>
      <div className="panel palette" onMouseDown={(e) => e.stopPropagation()}>
        <div className="legend">
          <span className="legend__title">Command Palette</span>
          <span className="legend__right">
            <span className="chip">Esc</span>
          </span>
        </div>

        <input
          ref={inputRef}
          className="control palette__input"
          placeholder="Type to search…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Escape") onClose();
          }}
        />

        <div className="palette__list">
          {filtered.slice(0, 50).map((it) => (
            <button
              key={it.id}
              className="control palette__item"
              onClick={() => {
                it.run();
                onClose();
              }}
            >
              {it.title}
            </button>
          ))}
        </div>
      </div>
    </div>,
    document.body
  );
}

function RightDrawer({
  open,
  tab,
  setTab,
  onClose,
  onJump,
}: {
  open: boolean;
  tab: string;
  setTab: (t: string) => void;
  onClose: () => void;
  onJump: (messageId: string) => void;
}) {
  if (!open) return null;

  const tabs = ["Todos", "Tools", "Agents", "Sessions", "Navigator"];

  return createPortal(
    <div className="drawerOverlay" onMouseDown={onClose}>
      <div className="panel drawer" onMouseDown={(e) => e.stopPropagation()}>
        <div className="drawer__tabs">
          {tabs.map((t) => (
            <button
              key={t}
              className={`control drawer__tab ${tab === t ? "is-active" : ""}`}
              onClick={() => setTab(t)}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="drawer__content">
          <div className="legend">
            <span className="legend__title">{tab}</span>
            <span className="legend__right">
              <button className="control chip" onClick={onClose}>Esc</button>
            </span>
          </div>

          {tab === "Navigator" ? (
            <div className="drawer__list">
              {/* Example navigator items; wire to your real timeline index */}
              <button className="control drawer__item" onClick={() => onJump("m1")}>
                Agent: Planned steps…
              </button>
              <button className="control drawer__item" onClick={() => onJump("m2")}>
                Tool: ripgrep results…
              </button>
            </div>
          ) : (
            <div className="drawer__list">
              <div className="chip">List content for {tab}…</div>
            </div>
          )}
        </div>
      </div>
    </div>,
    document.body
  );
}

export default function App() {
  const composerRef = useRef<HTMLTextAreaElement | null>(null);

  const [paletteOpen, setPaletteOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerTab, setDrawerTab] = useState("Navigator");

  const [draft, setDraft] = useState("");
  const [timeline, setTimeline] = useState<TimelineItem[]>([
    { id: "m1", kind: "user", ts: Date.now() - 60000, content: "Hello agent.", status: "ok" },
    { id: "m2", kind: "agent", ts: Date.now() - 50000, content: "I can help.", status: "ok" },
    { id: "m3", kind: "thinking", ts: Date.now() - 45000, content: "Internal reasoning…", status: "ok", collapsedByDefault: true },
  ]);

  const commands: CommandItem[] = useMemo(() => {
    return [
      { id: "toggle-drawer", title: "Toggle Drawer", keywords: "drawer nav tabs", run: () => setDrawerOpen((v) => !v) },
      { id: "theme-next", title: "Switch Theme: Next", keywords: "theme appearance", run: () => {/* implement */} },
      { id: "jump-latest", title: "Jump: Latest Message", keywords: "jump timeline", run: () => {
        const last = timeline[timeline.length - 1];
        if (last) document.getElementById(`msg-${last.id}`)?.scrollIntoView({ block: "center", behavior: "smooth" });
      }},
    ];
  }, [timeline]);

  useGlobalHotkeys({
    onPalette: () => setPaletteOpen(true),
    onDrawer: () => setDrawerOpen((v) => !v),
    onEscape: () => {
      if (paletteOpen) { setPaletteOpen(false); composerRef.current?.focus(); return; }
      if (drawerOpen) { setDrawerOpen(false); composerRef.current?.focus(); return; }
    },
  });

  const send = () => {
    const text = draft.trim();
    if (!text) return;
    const now = Date.now();
    setTimeline((t) => [
      ...t,
      { id: `m${t.length + 1}`, kind: "user", ts: now, content: text, status: "ok" },
      { id: `m${t.length + 2}`, kind: "agent", ts: now + 1, content: "Acknowledged. (stub)", status: "running" },
    ]);
    setDraft("");
  };

  const jumpTo = (id: string) => {
    document.getElementById(`msg-${id}`)?.scrollIntoView({ block: "center", behavior: "smooth" });
    // optional: add highlight class
  };

  return (
    <div className="app">
      <div className="topbar panel">
        <div className="topbar__left">
          <span className="chip">Session: Default</span>
          <span className="chip">Agent: coder</span>
        </div>
        <div className="topbar__right">
          <span className="chip">Model: gpt</span>
          <button className="control">Run</button>
        </div>
      </div>

      <div className="timeline">
        {timeline.map((item) => (
          <MessageCard key={item.id} item={item} onJumpFocus={jumpTo} />
        ))}
      </div>

      <div className="composer panel">
        <textarea
          ref={composerRef}
          className="control composer__input"
          value={draft}
          placeholder="Message the agent…"
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.ctrlKey && e.key === "Enter") {
              e.preventDefault();
              send();
            }
          }}
          rows={2}
        />
        <button className="control composer__send" onClick={send}>
          Send
        </button>
      </div>

      <div className="statusbar panel">
        <span className="chip">Ctrl+K Palette</span>
        <span className="chip">Ctrl+D Drawer</span>
        <span className="chip">Esc Close</span>
      </div>

      <CommandPalette open={paletteOpen} items={commands} onClose={() => { setPaletteOpen(false); composerRef.current?.focus(); }} />

      <RightDrawer
        open={drawerOpen}
        tab={drawerTab}
        setTab={setDrawerTab}
        onClose={() => { setDrawerOpen(false); composerRef.current?.focus(); }}
        onJump={jumpTo}
      />
    </div>
  );
}
~~~

---

## 12) Minimal CSS (variables + rounded + legend headers)

~~~css
/* styles.css */
:root {
  --surface-base: #0b0f18;
  --surface-panel: #0f172a;
  --surface-raised: #111c33;

  --text-primary: #e6e8ef;
  --text-secondary: #a8b0c2;
  --text-tertiary: #7b849c;

  --border-normal: #6b5cff;
  --border-focus: #20c5ff;

  --accent-primary: #20c5ff;
  --accent-secondary: #6b5cff;

  --success: #38d07a;
  --warning: #f0c24b;
  --error: #ff5c7a;
  --info: #20c5ff;

  --r-panel: 14px;
  --r-control: 14px;
  --r-pill: 999px;

  --pad-sm: 8px;
  --pad-md: 12px;
  --gap-sm: 8px;
  --gap-md: 12px;

  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--surface-base);
  color: var(--text-primary);
  gap: var(--gap-sm);
  padding: var(--pad-md);
  box-sizing: border-box;
}

.panel {
  background: var(--surface-panel);
  border: 1px solid var(--border-normal);
  border-radius: var(--r-panel);
  padding: var(--pad-md);
  position: relative;
}

.control {
  border: 1px solid var(--border-normal);
  border-radius: var(--r-control);
  background: var(--surface-raised);
  color: var(--text-primary);
  padding: 6px 10px;
  cursor: pointer;
}

.control:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 2px rgba(32, 197, 255, 0.2);
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--border-normal);
  border-radius: var(--r-pill);
  padding: 2px 10px;
  background: var(--surface-raised);
  color: var(--text-secondary);
}

.legend {
  position: absolute;
  top: -10px;
  left: 12px;
  display: inline-flex;
  align-items: center;
  gap: var(--gap-sm);
  padding: 0 10px;
  background: var(--surface-panel);
  border: 1px solid var(--border-normal);
  border-radius: var(--r-pill);
  height: 20px;
}

.legend__title {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 12px;
}
.legend__right {
  display: inline-flex;
  gap: var(--gap-sm);
}

.topbar, .statusbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.timeline {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: var(--gap-md);
  padding: 4px;
}

.message {
  padding-top: 18px; /* room for legend */
}
.message__body {
  color: var(--text-primary);
  white-space: pre-wrap;
}
.message__footer {
  margin-top: var(--gap-sm);
  display: flex;
  gap: var(--gap-sm);
  opacity: 0.6;
}
.message:hover .message__footer,
.message:focus-within .message__footer {
  opacity: 1;
}

.composer {
  display: flex;
  gap: var(--gap-sm);
  align-items: flex-end;
}
.composer__input {
  width: 100%;
  min-height: 42px;
  resize: none;
}
.composer__send {
  white-space: nowrap;
}

.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
}

.palette {
  width: min(900px, 92vw);
  max-height: 70vh;
  overflow: hidden;
}
.palette__input {
  width: 100%;
  margin-top: 14px;
}
.palette__list {
  margin-top: var(--gap-sm);
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 52vh;
  overflow: auto;
}

.drawerOverlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.25);
  display: flex;
  justify-content: flex-end;
}

.drawer {
  width: min(45vw, 560px);
  height: 100%;
  border-radius: 0;
  border-top-left-radius: var(--r-panel);
  border-bottom-left-radius: var(--r-panel);
  display: flex;
  gap: var(--gap-sm);
  padding-top: 18px; /* legend */
}

.drawer__tabs {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 120px;
}
.drawer__tab.is-active {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 2px rgba(32, 197, 255, 0.2);
}

.drawer__content {
  flex: 1;
  overflow: auto;
  position: relative;
}
.drawer__list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.drawer__item {
  text-align: left;
}
~~~

---

## 13) React-specific “clean look” guardrails
- Keep only **one** always-visible primary surface (timeline).
- Move all “settings” to palette/drawer.
- Only show message action buttons on hover/focus.
- Default collapsed: thinking + tool details.
- Provide `Compact mode` toggle to reduce padding/gaps.
- Use virtualization when timeline grows.
