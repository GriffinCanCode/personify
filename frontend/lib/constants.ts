/**
 * Application-wide constants
 */

export const APP_NAME = 'Personify'
export const APP_DESCRIPTION = 'Your personal AI communication assistant'

// API
export const API_TIMEOUT = 30000
export const API_RETRY_ATTEMPTS = 3

// UI
export const DEBOUNCE_DELAY = 500
export const TOAST_DURATION = 5000
export const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
export const ALLOWED_FILE_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
]

// Pagination
export const DEFAULT_PAGE_SIZE = 20
export const MAX_PAGE_SIZE = 100

// Cache
export const QUERY_STALE_TIME = 5 * 60 * 1000 // 5 minutes
export const QUERY_CACHE_TIME = 10 * 60 * 1000 // 10 minutes

// Routes
export const ROUTES = {
  HOME: '/',
  CHAT: '/chat',
  UPLOAD: '/upload',
  PERSONALITY: '/personality',
} as const

// Local Storage Keys
export const STORAGE_KEYS = {
  THEME: 'personify-theme',
  CONVERSATION_ID: 'personify-conversation-id',
  USER_PREFERENCES: 'personify-user-prefs',
} as const
