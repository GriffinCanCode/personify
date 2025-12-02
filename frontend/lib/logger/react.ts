/**
 * React-specific logging utilities and hooks
 */

'use client'

import { useCallback, useEffect, useRef } from 'react'
import { logger } from './index'
import { Performance } from './performance'
import type { LogContext } from './types'

/**
 * Hook for logging component lifecycle
 */
export function useLogger(componentName: string, context?: LogContext) {
  const mountTimeRef = useRef<number>(0)

  useEffect(() => {
    mountTimeRef.current = performance.now()
    logger.debug(`Component mounted: ${componentName}`, context)

    return () => {
      const duration = performance.now() - mountTimeRef.current
      logger.debug(`Component unmounted: ${componentName}`, {
        ...context,
        duration: Math.round(duration),
      })
    }
  }, [componentName, context])

  return useCallback(
    (message: string, additionalContext?: LogContext) => {
      logger.info(message, { ...context, ...additionalContext, component: componentName })
    },
    [componentName, context]
  )
}

/**
 * Hook for logging render performance
 */
export function useRenderLogger(componentName: string, deps?: unknown[]) {
  const renderCount = useRef(0)
  const lastRenderTime = useRef<number>(0)

  useEffect(() => {
    renderCount.current += 1
    const now = performance.now()
    const timeSinceLastRender = lastRenderTime.current ? now - lastRenderTime.current : 0

    logger.debug(`Component rendered: ${componentName}`, {
      renderCount: renderCount.current,
      timeSinceLastRender: Math.round(timeSinceLastRender),
      deps: deps?.length,
    })

    lastRenderTime.current = now
  })
}

/**
 * Hook for logging user interactions
 */
export function useInteractionLogger(componentName: string) {
  return useCallback(
    (action: string, details?: LogContext) => {
      logger.info(`User interaction: ${action}`, {
        component: componentName,
        ...details,
      })
    },
    [componentName]
  )
}

/**
 * Hook for tracking async operations with performance
 */
export function useAsyncLogger(componentName: string) {
  return useCallback(
    async <T>(operation: string, fn: () => Promise<T>, context?: LogContext): Promise<T> => {
      return logger.trackAsync(`${componentName}.${operation}`, fn, {
        ...context,
        component: componentName,
      })
    },
    [componentName]
  )
}

/**
 * Hook for measuring effect performance
 */
export function useEffectPerformance(
  effectName: string,
  effect: () => undefined | (() => void),
  deps?: unknown[]
) {
  const effectRef = useRef(effect)
  const effectNameRef = useRef(effectName)
  effectRef.current = effect
  effectNameRef.current = effectName

  useEffect(() => {
    const perf = new Performance()
    perf.start()

    const cleanup = effectRef.current()

    const metrics = perf.end()
    logger.perf(`Effect completed: ${effectNameRef.current}`, metrics)

    return () => {
      if (cleanup) {
        const cleanupPerf = new Performance()
        cleanupPerf.start()
        cleanup()
        const cleanupMetrics = cleanupPerf.end()
        logger.perf(`Effect cleanup: ${effectNameRef.current}`, cleanupMetrics)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)
}

/**
 * Hook for error logging
 */
export function useErrorLogger(componentName: string) {
  return useCallback(
    (error: unknown, context?: LogContext) => {
      logger.error(`Error in ${componentName}`, error, {
        ...context,
        component: componentName,
      })
    },
    [componentName]
  )
}
