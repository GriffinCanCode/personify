import { chatApi, handleApiError } from '@/lib/api'
import axios from 'axios'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('axios')

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('chatApi', () => {
    it('should send a message', async () => {
      const mockResponse = {
        data: {
          response: 'Test response',
          confidence_score: 0.95,
          style_match: 0.9,
          conversation_id: 1,
          message_id: 123,
        },
      }

      vi.mocked(axios.create).mockReturnValue({
        post: vi.fn().mockResolvedValue(mockResponse),
      } as any)

      const result = await chatApi.sendMessage({ message: 'Hello' })
      expect(result.response).toBeDefined()
      expect(result.conversation_id).toBe(1)
    })
  })

  describe('handleApiError', () => {
    it('should handle axios errors', () => {
      const error = {
        isAxiosError: true,
        response: {
          data: {
            error: 'Test error',
          },
        },
      }

      vi.mocked(axios.isAxiosError).mockReturnValue(true)
      const result = handleApiError(error)
      expect(result).toBe('Test error')
    })

    it('should handle generic errors', () => {
      const error = new Error('Generic error')
      const result = handleApiError(error)
      expect(result).toBe('Generic error')
    })

    it('should handle unknown errors', () => {
      const result = handleApiError('string error')
      expect(result).toBe('An unexpected error occurred')
    })
  })
})
