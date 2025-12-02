import { useDebounce } from '@/lib/hooks/use-debounce'
import { renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should return initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('initial', 500))
    expect(result.current).toBe('initial')
  })

  it('should debounce value changes', async () => {
    const { result, rerender } = renderHook(({ value, delay }) => useDebounce(value, delay), {
      initialProps: { value: 'initial', delay: 500 },
    })

    expect(result.current).toBe('initial')

    // Update value
    rerender({ value: 'updated', delay: 500 })
    expect(result.current).toBe('initial') // Still old value

    // Fast-forward time
    vi.advanceTimersByTime(500)

    await waitFor(() => {
      expect(result.current).toBe('updated')
    })
  })

  it('should cancel previous timeout on rapid changes', async () => {
    const { result, rerender } = renderHook(({ value, delay }) => useDebounce(value, delay), {
      initialProps: { value: 'initial', delay: 500 },
    })

    rerender({ value: 'first', delay: 500 })
    vi.advanceTimersByTime(200)

    rerender({ value: 'second', delay: 500 })
    vi.advanceTimersByTime(200)

    rerender({ value: 'final', delay: 500 })
    vi.advanceTimersByTime(500)

    await waitFor(() => {
      expect(result.current).toBe('final')
    })
  })
})
