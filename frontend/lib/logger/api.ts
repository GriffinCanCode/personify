/**
 * API-specific logging utilities
 */

import type { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios'
import { loggerContext } from './context'
import { logger } from './index'
import { Performance } from './performance'

export interface ApiLogContext {
  method?: string
  url?: string
  status?: number
  duration?: number
  requestId?: string
  headers?: Record<string, string>
  data?: unknown
}

/**
 * Log API request
 */
export function logApiRequest(config: AxiosRequestConfig): void {
  const requestId = loggerContext.generateRequestId()

  logger.debug('API Request', {
    method: config.method?.toUpperCase(),
    url: config.url,
    requestId,
    baseURL: config.baseURL,
    params: config.params,
    ...(config.data instanceof FormData ? { hasFormData: true } : { data: config.data }),
  })
}

/**
 * Log API response
 */
export function logApiResponse(response: AxiosResponse, duration: number): void {
  const requestId = loggerContext.getCurrentRequestId() ?? undefined

  logger.info('API Response', {
    method: response.config.method?.toUpperCase(),
    url: response.config.url,
    status: response.status,
    duration,
    requestId,
    dataSize: JSON.stringify(response.data).length,
  })

  loggerContext.clearRequestId()
}

/**
 * Log API error
 */
export function logApiError(error: AxiosError, duration?: number): void {
  const requestId = loggerContext.getCurrentRequestId() ?? undefined

  const context: ApiLogContext = {
    method: error.config?.method?.toUpperCase(),
    url: error.config?.url,
    status: error.response?.status,
    duration,
    requestId,
  }

  if (error.response) {
    // Server responded with error status
    logger.error('API Error Response', error, {
      ...context,
      responseData: error.response.data,
    } as Record<string, unknown>)
  } else if (error.request) {
    // Request was made but no response
    logger.error('API No Response', error, {
      ...context,
      errorCode: error.code,
    } as Record<string, unknown>)
  } else {
    // Error setting up request
    logger.error('API Request Setup Error', error, context as Record<string, unknown>)
  }

  loggerContext.clearRequestId()
}

/**
 * Create a performance tracker for API calls
 */
export function createApiPerformanceTracker() {
  const perf = new Performance()
  perf.start()

  return {
    end: () => perf.end().duration || 0,
  }
}

/**
 * Log slow API calls
 */
export function logSlowApiCall(url: string, duration: number, threshold = 2000): void {
  if (duration > threshold) {
    logger.warn('Slow API call detected', {
      url,
      duration,
      threshold,
    })
  }
}
