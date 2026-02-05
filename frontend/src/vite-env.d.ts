/// <reference types="vite/client" />

interface ImportMetaEnv {
  /**
   * Base URL for the backend API
   * @default "http://localhost:8000/api/v1"
   */
  readonly VITE_API_BASE_URL?: string

  /**
   * Enable debug mode in the UI (shows additional diagnostic information)
   * @default false
   */
  readonly VITE_DEBUG?: string | boolean

  /**
   * Enable experimental features
   * @default false
   */
  readonly VITE_EXPERIMENTAL?: string | boolean
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
