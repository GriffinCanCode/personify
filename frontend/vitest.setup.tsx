import * as matchers from '@testing-library/jest-dom/matchers'
import { cleanup } from '@testing-library/react'
import React from 'react'
import { afterEach, beforeAll, expect, vi } from 'vitest'
import failOnConsole from 'vitest-fail-on-console'

// Extend Vitest matchers with Testing Library
expect.extend(matchers)

// Cleanup after each test
afterEach(() => {
  cleanup()
})

// Fail tests on console errors/warnings (optional, can be configured)
if (process.env.FAIL_ON_CONSOLE !== 'false') {
  failOnConsole({
    shouldFailOnWarn: false,
    shouldFailOnError: true,
    shouldFailOnLog: false,
    shouldFailOnDebug: false,
    shouldFailOnInfo: false,
  })
}

// Mock Next.js router
beforeAll(() => {
  vi.mock('next/navigation', () => ({
    useRouter: () => ({
      push: vi.fn(),
      replace: vi.fn(),
      prefetch: vi.fn(),
      back: vi.fn(),
      pathname: '/',
      query: {},
      asPath: '/',
    }),
    usePathname: () => '/',
    useSearchParams: () => new URLSearchParams(),
    useParams: () => ({}),
  }))

  // Mock Next.js Image component
  vi.mock('next/image', () => ({
    default: (props: React.ImgHTMLAttributes<HTMLImageElement>) => {
      // biome-ignore lint/a11y/useAltText: This is a mock component for testing
      return <img {...props} />
    },
  }))

  // Mock environment variables (use Object.defineProperty for readonly properties)
  Object.defineProperty(process.env, 'NEXT_PUBLIC_API_URL', {
    value: 'http://localhost:8000',
    writable: true,
    configurable: true,
  })
  Object.defineProperty(process.env, 'NEXT_PUBLIC_ENABLE_DEBUG', {
    value: 'false',
    writable: true,
    configurable: true,
  })
  Object.defineProperty(process.env, 'NEXT_PUBLIC_ENABLE_ANALYTICS', {
    value: 'false',
    writable: true,
    configurable: true,
  })
})

// Global test utilities
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})
