/**
 * Modern, extensible logging system for 2025
 *
 * Features:
 * - Structured logging with context
 * - Performance tracking
 * - Request correlation IDs
 * - Multiple transports (console, JSON, localStorage)
 * - React integration hooks
 * - Type-safe API
 */

import { env } from '../env'
import { Logger } from './core'

// Export types
export type * from './types'

// Export utilities
export { loggerContext } from './context'
export { createPerformanceTracker, measurePerformance } from './performance'
export {
  ConsoleTransport,
  JsonTransport,
  LocalStorageTransport,
} from './transports'

// Export React hooks
export {
  useLogger,
  useRenderLogger,
  useInteractionLogger,
  useAsyncLogger,
  useEffectPerformance,
  useErrorLogger,
} from './react'

// Create default logger instance
export const logger = new Logger({
  minLevel: env.NEXT_PUBLIC_ENABLE_DEBUG ? 'debug' : 'warn',
  enableConsole: true,
  enablePerformance: env.NEXT_PUBLIC_ENABLE_DEBUG,
  enableErrorTracking: true,
})

// Convenience method to create child loggers
export function createLogger(context: Record<string, unknown>) {
  return logger.child(context)
}

// Global error handler
if (typeof window !== 'undefined') {
  window.addEventListener('error', (event) => {
    logger.error('Unhandled error', event.error, {
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
    })
  })

  window.addEventListener('unhandledrejection', (event) => {
    logger.error('Unhandled promise rejection', event.reason, {
      promise: event.promise,
    })
  })
}

// Export default
export default logger
