/**
 * Logger transports for different output destinations
 */

import type { LogEntry, LogLevel, LoggerTransport } from './types'

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
}

/**
 * Console transport with colored output
 */
export class ConsoleTransport implements LoggerTransport {
  name = 'console'
  private minLevel: LogLevel

  constructor(minLevel: LogLevel = 'debug') {
    this.minLevel = minLevel
  }

  shouldLog(level: LogLevel): boolean {
    return LOG_LEVELS[level] >= LOG_LEVELS[this.minLevel]
  }

  log(entry: LogEntry): void {
    const { level, message, context, error, performance, requestId } = entry

    const prefix = `[${entry.timestamp}]${requestId ? ` [${requestId}]` : ''}`
    const metadata = {
      ...(context && Object.keys(context).length > 0 && { context }),
      ...(performance && { performance }),
    }

    const hasMetadata = Object.keys(metadata).length > 0

    switch (level) {
      case 'debug':
        console.debug(prefix, message, hasMetadata ? metadata : '')
        break
      case 'info':
        console.info(prefix, message, hasMetadata ? metadata : '')
        break
      case 'warn':
        console.warn(prefix, message, hasMetadata ? metadata : '')
        break
      case 'error':
        console.error(prefix, message, hasMetadata ? metadata : '', error || '')
        break
    }
  }
}

/**
 * Structured JSON transport for external logging services
 */
export class JsonTransport implements LoggerTransport {
  name = 'json'
  private buffer: LogEntry[] = []
  private flushInterval: number
  private maxBufferSize: number
  private flushCallback?: (entries: LogEntry[]) => Promise<void>

  constructor(options?: {
    flushInterval?: number
    maxBufferSize?: number
    flushCallback?: (entries: LogEntry[]) => Promise<void>
  }) {
    this.flushInterval = options?.flushInterval || 5000
    this.maxBufferSize = options?.maxBufferSize || 100
    this.flushCallback = options?.flushCallback

    // Auto-flush periodically
    if (typeof window !== 'undefined') {
      setInterval(() => void this.flush(), this.flushInterval)
    }
  }

  log(entry: LogEntry): void {
    this.buffer.push(entry)
    if (this.buffer.length >= this.maxBufferSize) {
      this.flush()
    }
  }

  async flush(): Promise<void> {
    if (this.buffer.length === 0) return

    const entries = [...this.buffer]
    this.buffer = []

    if (this.flushCallback) {
      try {
        await this.flushCallback(entries)
      } catch (error) {
        console.error('Failed to flush logs:', error)
      }
    }
  }

  getBuffer(): LogEntry[] {
    return [...this.buffer]
  }
}

/**
 * Local storage transport for persistent logging
 */
export class LocalStorageTransport implements LoggerTransport {
  name = 'localStorage'
  private storageKey: string
  private maxEntries: number

  constructor(storageKey = 'app_logs', maxEntries = 1000) {
    this.storageKey = storageKey
    this.maxEntries = maxEntries
  }

  log(entry: LogEntry): void {
    if (typeof window === 'undefined') return

    try {
      const existing = this.getLogs()
      const updated = [entry, ...existing].slice(0, this.maxEntries)
      localStorage.setItem(this.storageKey, JSON.stringify(updated))
    } catch (error) {
      // Storage might be full or disabled
      console.warn('Failed to write to localStorage:', error)
    }
  }

  getLogs(): LogEntry[] {
    if (typeof window === 'undefined') return []

    try {
      const data = localStorage.getItem(this.storageKey)
      return data ? JSON.parse(data) : []
    } catch {
      return []
    }
  }

  clear(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem(this.storageKey)
  }
}
