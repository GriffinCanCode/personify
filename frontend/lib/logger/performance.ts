/**
 * Performance tracking utilities
 */

import type { PerformanceMetrics, PerformanceTracker } from './types'

export class Performance {
  private startTime: number | null = null
  private marks: Map<string, number> = new Map()

  start(): void {
    this.startTime = performance.now()
  }

  end(): PerformanceMetrics {
    const endTime = performance.now()
    const duration = this.startTime ? endTime - this.startTime : 0

    return {
      duration: Math.round(duration * 100) / 100, // Round to 2 decimals
      memory: this.getMemoryUsage(),
      timestamp: Date.now(),
    }
  }

  mark(name: string): void {
    this.marks.set(name, performance.now())
  }

  measure(_name: string, startMark?: string, endMark?: string): number {
    const start = startMark ? this.marks.get(startMark) : this.startTime
    const end = endMark ? this.marks.get(endMark) : performance.now()

    if (start === null || start === undefined) {
      throw new Error(`Start mark "${startMark}" not found`)
    }

    const duration = (end ?? 0) - start
    return Math.round(duration * 100) / 100
  }

  private getMemoryUsage(): number | undefined {
    if (typeof window === 'undefined') return undefined

    // @ts-expect-error - memory API is not standard
    const memory = performance.memory
    if (memory) {
      return Math.round((memory.usedJSHeapSize / 1024 / 1024) * 100) / 100 // MB
    }
    return undefined
  }

  reset(): void {
    this.startTime = null
    this.marks.clear()
  }
}

/**
 * Create a performance tracker for a specific operation
 */
export function createPerformanceTracker(): PerformanceTracker {
  const perf = new Performance()

  return {
    start: () => perf.start(),
    end: () => perf.end(),
    mark: (name: string) => perf.mark(name),
    measure: (name: string, startMark?: string, endMark?: string) =>
      perf.measure(name, startMark, endMark),
  }
}

/**
 * Decorator for measuring function execution time
 */
export function measurePerformance<T extends (...args: unknown[]) => unknown>(
  fn: T,
  label?: string
): T {
  return ((...args: unknown[]) => {
    const tracker = createPerformanceTracker()
    tracker.start()

    try {
      const result = fn(...args)

      // Handle promises
      if (result instanceof Promise) {
        return result.finally(() => {
          const metrics = tracker.end()
          console.debug(`[Performance] ${label || fn.name}:`, metrics)
        })
      }

      const metrics = tracker.end()
      console.debug(`[Performance] ${label || fn.name}:`, metrics)
      return result
    } catch (error) {
      const metrics = tracker.end()
      console.debug(`[Performance] ${label || fn.name} (error):`, metrics)
      throw error
    }
  }) as T
}
