# React Web App - Frontend

FastAPI + React + TypeScript web application for OpenCode Python SDK.

## Tech Stack

- **Build Tool**: Vite 7.2.4 (fast, modern, developer experience)
- **Language**: TypeScript 5.9.3 (type safety, matches Python Pydantic models)
- **UI Framework**: React 19.2.0
- **State Management**: Zustand 5.0.11 (minimal, handles React concurrency)
- **Virtualization**: react-virtuoso 4.18.1 (dynamic heights, infinite scroll)
- **Markdown**: react-markdown 10.1.0 + rehype-sanitize 6.0.0 (XSS protection)
- **Hotkeys**: react-hotkeys-hook 5.2.4 (keyboard shortcuts with scopes)
- **Testing**: Vitest + @testing-library/react + Playwright (TDD approach)

## Project Structure

```
frontend/
├── public/          # Static assets
├── src/
│   ├── App.tsx      # Main application component
│   ├── main.tsx     # Entry point
│   └── ...          # Components, hooks, stores
├── index.html       # HTML template
├── package.json     # Dependencies
├── tsconfig.json    # TypeScript config
└── vite.config.ts   # Vite config
```

## Getting Started

### Prerequisites

- Node.js 18+ (recommended)
- npm or yarn or pnpm

### Installation

```bash
cd frontend
npm install
```

### Development

Start the Vite dev server:

```bash
npm run dev
```

The application will be available at http://localhost:5173

### Build

Build for production:

```bash
npm run build
```

### Preview

Preview the production build:

```bash
npm run preview
```

### Lint

Run ESLint:

```bash
npm run lint
```

## Key Dependencies

| Package | Purpose |
|---------|---------|
| zustand | Lightweight state management with React concurrency support |
| react-virtuoso | Virtualized lists for long conversation timelines |
| react-markdown + rehype-sanitize | Markdown rendering with XSS protection |
| react-hotkeys-hook | Keyboard shortcuts (Ctrl+K, Ctrl+D, Esc, Ctrl+Enter) |

## Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

## Integration with Backend

The frontend connects to the FastAPI backend at:

- API Base URL: http://localhost:8000/api/v1
- SSE Streaming: `/api/v1/sessions/{session_id}/execute`

## Development Workflow

1. Make changes in `src/` directory
2. Changes hot-reload in browser automatically
3. Run tests with `npm test`
4. Build with `npm run build` before deploying

## Notes

- React 19 is used with concurrent features (Actions, useTransition, useDeferredValue)
- All styling is CSS-in-JS or CSS modules (future implementation)
- No external CSS files in root (CSS loaded via components)
- Theme system uses CSS variables with data-theme attribute
