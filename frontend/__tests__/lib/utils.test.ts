import { describe, it, expect } from 'vitest'
import { cn } from '@/lib/utils'

describe('utils', () => {
  describe('cn (className utility)', () => {
    it('should merge class names correctly', () => {
      const result = cn('px-4', 'py-2', 'bg-blue-500')
      expect(result).toContain('px-4')
      expect(result).toContain('py-2')
      expect(result).toContain('bg-blue-500')
    })

    it('should handle conditional classes', () => {
      const isActive = true
      const result = cn('base-class', isActive && 'active-class')
      expect(result).toContain('base-class')
      expect(result).toContain('active-class')
    })

    it('should handle falsy values', () => {
      const result = cn('base-class', false, null, undefined, 0, '')
      expect(result).toBe('base-class')
    })

    it('should merge conflicting Tailwind classes correctly', () => {
      const result = cn('px-4 py-2', 'px-8')
      // tailwind-merge should keep only px-8
      expect(result).toContain('px-8')
      expect(result).not.toContain('px-4')
    })
  })
})

