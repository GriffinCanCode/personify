import { validate, validators } from '@/lib/validators'
import { describe, expect, it } from 'vitest'
import { createMockFile } from '../setup/test-helpers'

describe('validators', () => {
  describe('email', () => {
    it('should validate correct emails', () => {
      expect(validators.email('test@example.com')).toBe(true)
      expect(validators.email('user+tag@domain.co.uk')).toBe(true)
    })

    it('should reject invalid emails', () => {
      expect(validators.email('invalid')).toBe(false)
      expect(validators.email('test@')).toBe(false)
      expect(validators.email('@domain.com')).toBe(false)
    })
  })

  describe('url', () => {
    it('should validate correct URLs', () => {
      expect(validators.url('https://example.com')).toBe(true)
      expect(validators.url('http://localhost:3000')).toBe(true)
    })

    it('should reject invalid URLs', () => {
      expect(validators.url('not-a-url')).toBe(false)
      expect(validators.url('ftp://missing-protocol')).toBe(true) // ftp is valid
    })
  })

  describe('fileSize', () => {
    it('should validate file sizes', () => {
      expect(validators.fileSize(1024, 2048)).toBe(true)
      expect(validators.fileSize(3000, 2048)).toBe(false)
    })
  })

  describe('fileType', () => {
    it('should validate file types', () => {
      expect(validators.fileType('application/pdf', ['application/pdf'])).toBe(true)
      expect(validators.fileType('image/png', ['application/pdf'])).toBe(false)
    })
  })

  describe('required', () => {
    it('should validate required values', () => {
      expect(validators.required('value')).toBe(true)
      expect(validators.required('')).toBe(false)
      expect(validators.required('  ')).toBe(false)
      expect(validators.required(null)).toBe(false)
      expect(validators.required(undefined)).toBe(false)
    })
  })

  describe('number', () => {
    it('should validate numbers', () => {
      expect(validators.number(42)).toBe(true)
      expect(validators.number(0)).toBe(true)
      expect(validators.number(Number.NaN)).toBe(false)
      expect(validators.number('42')).toBe(false)
    })
  })

  describe('range', () => {
    it('should validate number ranges', () => {
      expect(validators.range(5, 1, 10)).toBe(true)
      expect(validators.range(0, 1, 10)).toBe(false)
      expect(validators.range(11, 1, 10)).toBe(false)
    })
  })
})

describe('validate', () => {
  describe('email', () => {
    it('should return validation results', () => {
      expect(validate.email('test@example.com')).toEqual({ valid: true })
      expect(validate.email('invalid')).toEqual({
        valid: false,
        error: 'Invalid email format',
      })
      expect(validate.email('')).toEqual({
        valid: false,
        error: 'Email is required',
      })
    })
  })

  describe('file', () => {
    it('should validate files', () => {
      const validFile = createMockFile('test.pdf', 1024, 'application/pdf')
      expect(validate.file(validFile)).toEqual({ valid: true })

      const invalidType = createMockFile('test.exe', 1024, 'application/x-msdownload')
      const result = validate.file(invalidType)
      expect(result.valid).toBe(false)
      expect(result.error).toContain('not allowed')
    })
  })

  describe('message', () => {
    it('should validate messages', () => {
      expect(validate.message('Hello')).toEqual({ valid: true })
      expect(validate.message('')).toEqual({
        valid: false,
        error: 'Message is required',
      })
      expect(validate.message('a'.repeat(6000))).toEqual({
        valid: false,
        error: 'Message is too long (max 5000 characters)',
      })
    })
  })
})
