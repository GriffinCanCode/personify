import { useEffect, useState } from 'react'
import { logger } from '../logger'

/**
 * Debounces a value by the specified delay
 * Useful for search inputs and other frequent updates
 */
export function useDebounce<T>(value: T, delay = 500): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    logger.debug('Debounce started', { delay })

    const handler = setTimeout(() => {
      setDebouncedValue(value)
      logger.debug('Debounced value updated', { delay })
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}
