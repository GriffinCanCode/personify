/**
 * Core logging types for structured, extensible logging system
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error'

export interface LogContext {
  [key: string]: unknown
}

export interface LogEntry {
  timestamp: string
  level: LogLevel
  message: string
  context?: LogContext
  error?: ErrorDetails
  performance?: PerformanceMetrics
  requestId?: string
  userId?: string
  sessionId?: string
}

export interface ErrorDetails {
  name: string
  message: string
  stack?: string
  cause?: unknown
  code?: string | number
}

export interface PerformanceMetrics {
  duration?: number
  memory?: number
  timestamp: number
}

export interface LoggerTransport {
  name: string
  log: (entry: LogEntry) => void | Promise<void>
  shouldLog?: (level: LogLevel) => boolean
}

export interface LoggerConfig {
  minLevel?: LogLevel
  enableConsole?: boolean
  enablePerformance?: boolean
  enableErrorTracking?: boolean
  transports?: LoggerTransport[]
  context?: LogContext
}

export interface PerformanceTracker {
  start: () => void
  end: () => PerformanceMetrics
  mark: (name: string) => void
  measure: (name: string, startMark?: string, endMark?: string) => number
}
