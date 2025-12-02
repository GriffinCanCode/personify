import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { type RenderOptions, render as rtlRender } from '@testing-library/react'
import React from 'react'
import type { ReactElement } from 'react'

/**
 * Custom render function that wraps components with providers
 */
export function render(ui: ReactElement, options?: RenderOptions) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  }

  return rtlRender(ui, { wrapper: Wrapper, ...options })
}

// Re-export everything from testing-library
export * from '@testing-library/react'
export { default as userEvent } from '@testing-library/user-event'
