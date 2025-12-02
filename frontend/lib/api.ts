import axios, { type AxiosError, type AxiosInstance } from 'axios'
import { env } from './env'
import type { ApiResponse } from '@/types'

// API Client Configuration
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: env.NEXT_PUBLIC_API_URL,
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 30000,
  })

  // Request interceptor
  client.interceptors.request.use(
    (config) => {
      if (env.NEXT_PUBLIC_ENABLE_DEBUG) {
        console.log('API Request:', config.method?.toUpperCase(), config.url)
      }
      return config
    },
    (error) => Promise.reject(error)
  )

  // Response interceptor
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (env.NEXT_PUBLIC_ENABLE_DEBUG) {
        console.error('API Error:', error.response?.status, error.message)
      }
      return Promise.reject(error)
    }
  )

  return client
}

export const api = createApiClient()

// Type Definitions
export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: string
}

export interface Conversation {
  id: string
  title?: string
  messages: Message[]
  createdAt: string
  updatedAt: string
}

export interface SendMessageRequest {
  message: string
  conversationId?: string
}

export interface SendMessageResponse {
  message: Message
  conversationId: string
}

export interface Document {
  id: string
  filename: string
  fileType: string
  size: number
  uploadedAt: string
  status: 'processing' | 'completed' | 'failed'
}

export interface UploadStats {
  totalDocuments: number
  totalSize: number
  processingCount: number
  completedCount: number
  failedCount: number
}

export interface PersonalityProfile {
  traits: Record<string, number>
  communicationStyle: string
  lastAnalyzed?: string
}

export interface FeedbackRequest {
  messageId: string
  rating: number
  comment?: string
}

// Chat API
export const chatApi = {
  sendMessage: async (
    data: SendMessageRequest
  ): Promise<ApiResponse<SendMessageResponse>> => {
    const response = await api.post<ApiResponse<SendMessageResponse>>(
      '/api/v1/chat/message',
      {
        message: data.message,
        conversation_id: data.conversationId,
      }
    )
    return response.data
  },

  getConversations: async (): Promise<ApiResponse<Conversation[]>> => {
    const response = await api.get<ApiResponse<Conversation[]>>('/api/v1/chat/conversations')
    return response.data
  },

  getConversation: async (conversationId: string): Promise<ApiResponse<Conversation>> => {
    const response = await api.get<ApiResponse<Conversation>>(
      `/api/v1/chat/conversations/${conversationId}`
    )
    return response.data
  },
}

// Upload API
export const uploadApi = {
  uploadFiles: async (files: File[]): Promise<ApiResponse<Document[]>> => {
    const formData = new FormData()
    for (const file of files) {
      formData.append('files', file)
    }

    const response = await api.post<ApiResponse<Document[]>>(
      '/api/v1/upload/files',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  getDocuments: async (): Promise<ApiResponse<Document[]>> => {
    const response = await api.get<ApiResponse<Document[]>>('/api/v1/upload/documents')
    return response.data
  },

  getStats: async (): Promise<ApiResponse<UploadStats>> => {
    const response = await api.get<ApiResponse<UploadStats>>('/api/v1/upload/stats')
    return response.data
  },
}

// Personality API
export const personalityApi = {
  getProfile: async (): Promise<ApiResponse<PersonalityProfile>> => {
    const response = await api.get<ApiResponse<PersonalityProfile>>(
      '/api/v1/personality/profile'
    )
    return response.data
  },

  updateProfile: async (
    profile: Partial<PersonalityProfile>
  ): Promise<ApiResponse<PersonalityProfile>> => {
    const response = await api.put<ApiResponse<PersonalityProfile>>(
      '/api/v1/personality/profile',
      profile
    )
    return response.data
  },

  analyzeData: async (): Promise<ApiResponse<PersonalityProfile>> => {
    const response = await api.post<ApiResponse<PersonalityProfile>>(
      '/api/v1/personality/analyze'
    )
    return response.data
  },
}

// Feedback API
export const feedbackApi = {
  submitFeedback: async (data: FeedbackRequest): Promise<ApiResponse<{ success: boolean }>> => {
    const response = await api.post<ApiResponse<{ success: boolean }>>('/api/v1/feedback', {
      message_id: data.messageId,
      rating: data.rating,
      comment: data.comment,
    })
    return response.data
  },
}

// Error handler utility
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ error?: string; message?: string }>
    return (
      axiosError.response?.data?.error ||
      axiosError.response?.data?.message ||
      axiosError.message ||
      'An unexpected error occurred'
    )
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'An unexpected error occurred'
}
