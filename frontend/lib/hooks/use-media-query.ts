import { useEffect, useState } from 'react'
import { logger } from '../logger'

/**
 * Hook to detect media query matches
 * Useful for responsive behavior
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    try {
      const media = window.matchMedia(query)

      if (media.matches !== matches) {
        setMatches(media.matches)
      }

      const listener = (event: MediaQueryListEvent) => {
        setMatches(event.matches)
        logger.debug('Media query changed', { query, matches: event.matches })
      }

      media.addEventListener('change', listener)

      return () => media.removeEventListener('change', listener)
    } catch (error) {
      logger.error('Error in useMediaQuery', error, { query })
      return undefined
    }
  }, [matches, query])

  return matches
}

// Preset hooks for common breakpoints
export const useIsMobile = () => useMediaQuery('(max-width: 768px)')
export const useIsTablet = () => useMediaQuery('(min-width: 769px) and (max-width: 1024px)')
export const useIsDesktop = () => useMediaQuery('(min-width: 1025px)')
