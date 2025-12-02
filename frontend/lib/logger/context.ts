/**
 * Logging context management for correlation IDs and user tracking
 */

import { nanoid } from 'nanoid'
import type { LogContext } from './types'

class LoggerContext {
  private static instance: LoggerContext
  private context: LogContext = {}
  private requestId: string | null = null
  private sessionId: string | null = null

  private constructor() {
    // Initialize session ID once per page load
    this.sessionId = nanoid(10)
  }

  static getInstance(): LoggerContext {
    if (!LoggerContext.instance) {
      LoggerContext.instance = new LoggerContext()
    }
    return LoggerContext.instance
  }

  setContext(key: string, value: unknown): void {
    this.context[key] = value
  }

  setMultipleContext(context: LogContext): void {
    this.context = { ...this.context, ...context }
  }

  getContext(): LogContext {
    return { ...this.context }
  }

  clearContext(key?: string): void {
    if (key) {
      delete this.context[key]
    } else {
      this.context = {}
    }
  }

  generateRequestId(): string {
    this.requestId = nanoid(12)
    return this.requestId
  }

  getCurrentRequestId(): string | null {
    return this.requestId
  }

  clearRequestId(): void {
    this.requestId = null
  }

  getSessionId(): string {
    return this.sessionId ?? ''
  }

  getAllContext(): LogContext {
    return {
      ...this.context,
      ...(this.requestId && { requestId: this.requestId }),
      ...(this.sessionId && { sessionId: this.sessionId }),
    }
  }
}

export const loggerContext = LoggerContext.getInstance()
