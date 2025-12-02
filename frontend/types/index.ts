/**
 * Global type definitions
 */

import type React from 'react'

export interface ApiResponse<T> {
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  hasNext: boolean
}

export interface ErrorResponse {
  error: string
  details?: Record<string, unknown>
}

// Utility types
export type Nullable<T> = T | null
export type Optional<T> = T | undefined
export type AsyncData<T> = Promise<T>

// Component props utilities
export type PropsWithClassName<P = unknown> = P & {
  className?: string
}

export type PropsWithChildren<P = unknown> = P & {
  children?: React.ReactNode
}
