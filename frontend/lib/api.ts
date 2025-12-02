import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Chat API
export const chatApi = {
  sendMessage: async (message: string, conversationId?: string) => {
    const response = await api.post('/api/v1/chat/message', {
      message,
      conversation_id: conversationId,
    })
    return response.data
  },
  
  getConversations: async () => {
    const response = await api.get('/api/v1/chat/conversations')
    return response.data
  },
  
  getConversation: async (conversationId: string) => {
    const response = await api.get(`/api/v1/chat/conversations/${conversationId}`)
    return response.data
  },
}

// Upload API
export const uploadApi = {
  uploadFiles: async (files: File[]) => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    
    const response = await api.post('/api/v1/upload/files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
  
  getDocuments: async () => {
    const response = await api.get('/api/v1/upload/documents')
    return response.data
  },
  
  getStats: async () => {
    const response = await api.get('/api/v1/upload/stats')
    return response.data
  },
}

// Personality API
export const personalityApi = {
  getProfile: async () => {
    const response = await api.get('/api/v1/personality/profile')
    return response.data
  },
  
  updateProfile: async (profile: any) => {
    const response = await api.put('/api/v1/personality/profile', profile)
    return response.data
  },
  
  analyzeData: async () => {
    const response = await api.post('/api/v1/personality/analyze')
    return response.data
  },
}

// Feedback API
export const feedbackApi = {
  submitFeedback: async (messageId: string, rating: number, comment?: string) => {
    const response = await api.post('/api/v1/feedback', {
      message_id: messageId,
      rating,
      comment,
    })
    return response.data
  },
}

