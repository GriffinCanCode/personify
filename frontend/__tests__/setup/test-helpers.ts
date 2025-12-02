import { vi } from 'vitest'
import type { Mock } from 'vitest'

/**
 * Test helper utilities
 */

// Mock API responses
export const mockApiResponse = <T>(data: T, delay = 0) => {
  return new Promise((resolve) => {
    setTimeout(() => resolve({ data }), delay)
  })
}

export const mockApiError = (error: string, status = 500, delay = 0) => {
  return new Promise((_, reject) => {
    setTimeout(
      () =>
        reject({
          response: {
            data: { error },
            status,
          },
        }),
      delay
    )
  })
}

// Create mock function with type safety
export const createMockFn = <T extends (...args: unknown[]) => unknown>(): Mock<T> => {
  return vi.fn() as Mock<T>
}

// Wait for async updates
export const waitFor = async (callback: () => void, timeout = 1000) => {
  const startTime = Date.now()

  while (Date.now() - startTime < timeout) {
    try {
      callback()
      return
    } catch (_error) {
      await new Promise((resolve) => setTimeout(resolve, 50))
    }
  }

  callback() // Final attempt, will throw if still failing
}

// Mock localStorage
export const mockLocalStorage = () => {
  const store: Record<string, string> = {}

  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key]
    }),
    clear: vi.fn(() => {
      for (const key of Object.keys(store)) delete store[key]
    }),
  }
}

// Mock fetch
export const mockFetch = (response: unknown, ok = true) => {
  return vi.fn().mockResolvedValue({
    ok,
    status: ok ? 200 : 500,
    json: async () => response,
    text: async () => JSON.stringify(response),
  })
}

// Create a mock file
export const createMockFile = (name = 'test.pdf', size = 1024, type = 'application/pdf'): File => {
  const blob = new Blob(['a'.repeat(size)], { type })
  return new File([blob], name, { type })
}

// Flush promises
export const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0))
