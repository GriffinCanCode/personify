import { useCallback, useEffect, useState } from 'react'
import { logger } from '../logger'

/**
 * Hook to persist state in localStorage with SSR safety
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((val: T) => T)) => void, () => void] {
  // Get from local storage then parse stored json or return initialValue
  const readValue = useCallback((): T => {
    if (typeof window === 'undefined') {
      return initialValue
    }

    try {
      const item = window.localStorage.getItem(key)
      return item ? (JSON.parse(item) as T) : initialValue
    } catch (error) {
      logger.error(`Error reading localStorage key "${key}"`, error)
      return initialValue
    }
  }, [initialValue, key])

  const [storedValue, setStoredValue] = useState<T>(readValue)

  // Return a wrapped version of useState's setter function that persists the new value to localStorage
  const setValue = useCallback(
    (value: T | ((val: T) => T)) => {
      if (typeof window === 'undefined') {
        logger.warn(
          `Tried setting localStorage key "${key}" even though environment is not browser`
        )
        return
      }

      try {
        const newValue = value instanceof Function ? value(storedValue) : value
        window.localStorage.setItem(key, JSON.stringify(newValue))
        setStoredValue(newValue)
        window.dispatchEvent(new Event('local-storage'))
        logger.debug('localStorage value set', { key })
      } catch (error) {
        logger.error(`Error setting localStorage key "${key}"`, error)
      }
    },
    [key, storedValue]
  )

  // Remove from localStorage
  const removeValue = useCallback(() => {
    try {
      window.localStorage.removeItem(key)
      setStoredValue(initialValue)
      window.dispatchEvent(new Event('local-storage'))
      logger.debug('localStorage value removed', { key })
    } catch (error) {
      logger.error(`Error removing localStorage key "${key}"`, error)
    }
  }, [initialValue, key])

  useEffect(() => {
    setStoredValue(readValue())
  }, [readValue])

  // Listen for changes from other tabs/windows
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue !== null) {
        try {
          setStoredValue(JSON.parse(e.newValue) as T)
          logger.debug('localStorage sync from other tab', { key })
        } catch (error) {
          logger.error(`Error parsing localStorage key "${key}"`, error)
        }
      }
    }

    window.addEventListener('storage', handleStorageChange)
    window.addEventListener('local-storage', () => setStoredValue(readValue()))

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('local-storage', () => setStoredValue(readValue()))
    }
  }, [key, readValue])

  return [storedValue, setValue, removeValue]
}
