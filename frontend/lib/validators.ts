import { ALLOWED_FILE_TYPES, MAX_FILE_SIZE } from './constants'

/**
 * Validation utilities
 */

export const validators = {
  email: (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  },

  url: (url: string): boolean => {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  },

  fileSize: (size: number, maxSize: number = MAX_FILE_SIZE): boolean => {
    return size <= maxSize
  },

  fileType: (type: string, allowedTypes: string[] = ALLOWED_FILE_TYPES): boolean => {
    return allowedTypes.includes(type)
  },

  minLength: (value: string, min: number): boolean => {
    return value.length >= min
  },

  maxLength: (value: string, max: number): boolean => {
    return value.length <= max
  },

  required: (value: unknown): boolean => {
    if (typeof value === 'string') {
      return value.trim().length > 0
    }
    return value !== null && value !== undefined
  },

  number: (value: unknown): boolean => {
    return typeof value === 'number' && !Number.isNaN(value)
  },

  integer: (value: unknown): boolean => {
    return validators.number(value) && Number.isInteger(value as number)
  },

  positive: (value: number): boolean => {
    return validators.number(value) && value > 0
  },

  range: (value: number, min: number, max: number): boolean => {
    return validators.number(value) && value >= min && value <= max
  },
}

export type ValidationResult = {
  valid: boolean
  error?: string
}

export const validate = {
  email: (email: string): ValidationResult => {
    if (!validators.required(email)) {
      return { valid: false, error: 'Email is required' }
    }
    if (!validators.email(email)) {
      return { valid: false, error: 'Invalid email format' }
    }
    return { valid: true }
  },

  file: (file: File): ValidationResult => {
    if (!validators.fileType(file.type)) {
      return {
        valid: false,
        error: `File type ${file.type} is not allowed`,
      }
    }
    if (!validators.fileSize(file.size)) {
      return {
        valid: false,
        error: `File size must be less than ${MAX_FILE_SIZE / 1024 / 1024}MB`,
      }
    }
    return { valid: true }
  },

  message: (message: string): ValidationResult => {
    if (!validators.required(message)) {
      return { valid: false, error: 'Message is required' }
    }
    if (!validators.minLength(message, 1)) {
      return { valid: false, error: 'Message is too short' }
    }
    if (!validators.maxLength(message, 5000)) {
      return { valid: false, error: 'Message is too long (max 5000 characters)' }
    }
    return { valid: true }
  },
}
