/**
 * Core logger implementation with structured logging
 */

import { env } from '../env'
import { loggerContext } from './context'
import { Performance } from './performance'
import { ConsoleTransport } from './transports'
import type {
  ErrorDetails,
  LogContext,
  LogEntry,
  LogLevel,
  LoggerConfig,
  LoggerTransport,
  PerformanceMetrics,
} from './types'

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
}

export class Logger {
  private config: Required<Omit<LoggerConfig, 'context'>>
  private transports: LoggerTransport[]
  private globalContext: LogContext

  constructor(config?: LoggerConfig) {
    this.config = {
      minLevel: config?.minLevel || this.getDefaultMinLevel(),
      enableConsole: config?.enableConsole ?? true,
      enablePerformance: config?.enablePerformance ?? env.NEXT_PUBLIC_ENABLE_DEBUG,
      enableErrorTracking: config?.enableErrorTracking ?? true,
      transports: config?.transports || [],
    }

    this.globalContext = config?.context || {}
    this.transports = config?.transports || []

    // Add console transport if enabled
    if (this.config.enableConsole) {
      this.transports.unshift(new ConsoleTransport(this.config.minLevel))
    }
  }

  private getDefaultMinLevel(): LogLevel {
    if (env.NEXT_PUBLIC_ENABLE_DEBUG) return 'debug'
    return process.env.NODE_ENV === 'production' ? 'warn' : 'info'
  }

  private shouldLog(level: LogLevel): boolean {
    return LOG_LEVELS[level] >= LOG_LEVELS[this.config.minLevel]
  }

  private formatError(error: unknown): ErrorDetails {
    if (error instanceof Error) {
      return {
        name: error.name,
        message: error.message,
        stack: error.stack,
        cause: error.cause,
      }
    }

    if (typeof error === 'object' && error !== null) {
      return {
        name: 'Error',
        message: JSON.stringify(error),
      }
    }

    return {
      name: 'Error',
      message: String(error),
    }
  }

  private createLogEntry(
    level: LogLevel,
    message: string,
    context?: LogContext,
    error?: unknown,
    performance?: PerformanceMetrics
  ): LogEntry {
    const contextData = loggerContext.getAllContext()

    const mergedContext = {
      ...this.globalContext,
      ...contextData,
      ...context,
    }

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
    }

    if (Object.keys(mergedContext).length > 0) {
      entry.context = mergedContext
    }
    if (error) {
      entry.error = this.formatError(error)
    }
    if (performance) {
      entry.performance = performance
    }
    if (contextData.requestId) {
      entry.requestId = contextData.requestId as string
    }
    if (contextData.userId) {
      entry.userId = contextData.userId as string
    }
    if (contextData.sessionId) {
      entry.sessionId = contextData.sessionId as string
    }

    return entry
  }

  private log(
    level: LogLevel,
    message: string,
    context?: LogContext,
    error?: unknown,
    performance?: PerformanceMetrics
  ): void {
    if (!this.shouldLog(level)) return

    const entry = this.createLogEntry(level, message, context, error, performance)

    for (const transport of this.transports) {
      try {
        if (!transport.shouldLog || transport.shouldLog(level)) {
          transport.log(entry)
        }
      } catch (err) {
        console.error(`Transport ${transport.name} failed:`, err)
      }
    }
  }

  debug(message: string, context?: LogContext): void {
    this.log('debug', message, context)
  }

  info(message: string, context?: LogContext): void {
    this.log('info', message, context)
  }

  warn(message: string, context?: LogContext): void {
    this.log('warn', message, context)
  }

  error(message: string, error?: unknown, context?: LogContext): void {
    this.log('error', message, context, error)
  }

  /**
   * Log with performance metrics
   */
  perf(message: string, metrics: PerformanceMetrics, context?: LogContext): void {
    if (!this.config.enablePerformance) return
    this.log('debug', message, context, undefined, metrics)
  }

  /**
   * Track async operation with automatic performance logging
   */
  async trackAsync<T>(operation: string, fn: () => Promise<T>, context?: LogContext): Promise<T> {
    const perf = new Performance()
    perf.start()

    this.debug(`Starting: ${operation}`, context)

    try {
      const result = await fn()
      const metrics = perf.end()
      this.perf(`Completed: ${operation}`, metrics, context)
      return result
    } catch (error) {
      const metrics = perf.end()
      this.error(`Failed: ${operation}`, error, { ...context, ...metrics })
      throw error
    }
  }

  /**
   * Track sync operation with automatic performance logging
   */
  track<T>(operation: string, fn: () => T, context?: LogContext): T {
    const perf = new Performance()
    perf.start()

    this.debug(`Starting: ${operation}`, context)

    try {
      const result = fn()
      const metrics = perf.end()
      this.perf(`Completed: ${operation}`, metrics, context)
      return result
    } catch (error) {
      const metrics = perf.end()
      this.error(`Failed: ${operation}`, error, { ...context, ...metrics })
      throw error
    }
  }

  /**
   * Create a child logger with additional context
   */
  child(context: LogContext): Logger {
    return new Logger({
      ...this.config,
      context: { ...this.globalContext, ...context },
      transports: this.transports,
    })
  }

  /**
   * Add a custom transport
   */
  addTransport(transport: LoggerTransport): void {
    this.transports.push(transport)
  }

  /**
   * Remove a transport by name
   */
  removeTransport(name: string): void {
    this.transports = this.transports.filter((t) => t.name !== name)
  }
}
