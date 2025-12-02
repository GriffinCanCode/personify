import type { ApiResponse } from '@/types'
import axios, { type AxiosError, type AxiosInstance } from 'axios'
import { env } from './env'
import { logger } from './logger'
import {
  createApiPerformanceTracker,
  logApiError,
  logApiRequest,
  logApiResponse,
  logSlowApiCall,
} from './logger/api'

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
      const tracker = createApiPerformanceTracker()
      // @ts-expect-error - Adding custom property for tracking
      config.metadata = { startTime: tracker }

      logApiRequest(config)
      return config
    },
    (error) => {
      logger.error('API request interceptor error', error)
      return Promise.reject(error)
    }
  )

  // Response interceptor
  client.interceptors.response.use(
    (response) => {
      // @ts-expect-error - Reading custom property
      const tracker = response.config.metadata?.startTime
      const duration = tracker ? tracker.end() : 0

      logApiResponse(response, duration)
      logSlowApiCall(response.config.url || '', duration)

      return response
    },
    (error: AxiosError) => {
      // @ts-expect-error - Reading custom property
      const tracker = error.config?.metadata?.startTime
      const duration = tracker ? tracker.end() : undefined

      logApiError(error, duration)
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
  response: string
  confidence_score: number
  style_match: number
  conversation_id: number
  message_id: number
  validation_issues?: string[]
}

export interface Document {
  id: number
  filename: string
  source_type: string
  created_at?: string
  processed_at?: string | null
  chunk_count?: number
  metadata?: Record<string, unknown>
  processing_status?: string
  processing_progress?: number
}

export interface ProcessingStatus {
  document_id: number
  status: 'queued' | 'processing' | 'completed' | 'failed'
  stage: string
  progress: number
  chunks_created?: number
  error?: string
}

export interface UploadStats {
  total_documents: number
  total_size: number
  processing_count: number
  processed_documents: number
  total_chunks: number
}

// Writing Style Types
export interface RhythmPattern {
  pacing_description: string
  sentence_variation: string
  paragraph_style: string
  flow_characteristics: string[]
}

export interface StylisticMarkers {
  signature_phrases: string[]
  metaphor_patterns: string[]
  transition_style: string
  emphasis_patterns: string[]
  punctuation_habits: string
}

export interface TonalRange {
  default_tone: string
  tonal_shifts: Record<string, string>
  emotional_coloring: string
  formality_spectrum: string
}

export interface WritingStyleProfile {
  rhythm: RhythmPattern
  stylistic_markers: StylisticMarkers
  tonal_range: TonalRange
  linguistic_fingerprints: string[]
  vocabulary_character: string
  voice_description: string
  confidence: number
}

// Cognitive Types
export interface ReasoningPatterns {
  primary_mode: string
  logical_style: string
  evidence_preference: string
  abstraction_level: string
}

export interface MentalModels {
  identified_frameworks: string[]
  implicit_models: string[]
  analogical_sources: string[]
}

export interface CognitiveProfile {
  reasoning_patterns: ReasoningPatterns
  mental_models: MentalModels
  problem_solving_style: string
  idea_connection_style: string
  learning_approach: string
  complexity_preference: string
  thinking_description: string
  confidence: number
}

// Emotional Types
export interface EmotionalTriggers {
  excites: string[]
  frustrates: string[]
  motivates: string[]
  calms: string[]
}

export interface PassionMap {
  high_passion: string[]
  moderate_interest: string[]
  emerging_curiosity: string[]
}

export interface EmotionalProfile {
  triggers: EmotionalTriggers
  passion_map: PassionMap
  expression_patterns: string
  emotional_vocabulary: string[]
  values_from_emotion: string[]
  emotional_baseline: string
  emotional_description: string
  confidence: number
}

// Interest Types
export interface Interest {
  topic: string
  depth: number
  evidence: string[]
  context: string
}

export interface InterestProfile {
  genuine_interests: Interest[]
  curiosities: string[]
  aspirations: string[]
  topic_affinities: Record<string, number>
  learning_trajectories: string[]
  interest_description: string
  confidence: number
}

// Worldview Types
export interface CoreBeliefs {
  explicit_beliefs: string[]
  implicit_assumptions: string[]
  values_hierarchy: string[]
}

export interface WorldviewProfile {
  core_beliefs: CoreBeliefs
  philosophical_leanings: string[]
  framing_patterns: string
  unique_perspectives: string[]
  domain_lenses: Record<string, string>
  epistemology: string
  worldview_description: string
  confidence: number
}

// Social Types
export interface CommunicationDynamics {
  initiation_style: string
  response_patterns: string
  engagement_depth: string
  directness_level: string
}

export interface SocialProfile {
  communication_dynamics: CommunicationDynamics
  collaboration_style: string
  authority_positioning: string
  audience_adaptation: Record<string, string>
  relational_patterns: string[]
  conflict_approach: string
  social_description: string
  confidence: number
}

// Analysis Metadata
export interface AnalysisMetadata {
  documents_analyzed: number
  total_tokens_analyzed: number
  analysis_duration_seconds: number
  model_used: string
}

// Complete Personality Profile (v2 - AI-analyzed)
export interface PersonalityProfile {
  version: number
  writing_style: WritingStyleProfile
  cognitive: CognitiveProfile
  emotional: EmotionalProfile
  interests: InterestProfile
  worldview: WorldviewProfile
  social: SocialProfile
  personality_essence: string
  key_characteristics: string[]
  context_variations: Record<string, string>
  analysis_metadata?: AnalysisMetadata
  overall_confidence: number
}

export interface FeedbackRequest {
  messageId: string
  rating: number
  comment?: string
}

// Chat API
export const chatApi = {
  sendMessage: async (data: SendMessageRequest): Promise<SendMessageResponse> => {
    const response = await api.post<SendMessageResponse>('/api/v1/chat/message', {
      message: data.message,
      conversation_id: data.conversationId,
    })
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
  uploadFiles: async (
    files: File[]
  ): Promise<{
    results: Array<{ filename: string; status: string; document_id?: number; message: string }>
  }> => {
    const formData = new FormData()
    for (const file of files) {
      formData.append('files', file)
    }

    const response = await api.post<{
      results: Array<{ filename: string; status: string; document_id?: number; message: string }>
    }>('/api/v1/upload/files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 30000, // Fast upload (files processed in background)
    })
    return response.data
  },

  getProcessingStatus: async (documentId: number): Promise<ApiResponse<ProcessingStatus>> => {
    const response = await api.get<ApiResponse<ProcessingStatus>>(
      `/api/v1/upload/status/${documentId}`
    )
    return response.data
  },

  getDocuments: async (): Promise<Document[]> => {
    const response = await api.get<Document[]>('/api/v1/upload/documents')
    return response.data
  },

  getStats: async (): Promise<UploadStats> => {
    const response = await api.get<UploadStats>('/api/v1/upload/stats')
    return response.data
  },
}

// Personality API
export const personalityApi = {
  getProfile: async (): Promise<PersonalityProfile> => {
    const response = await api.get<PersonalityProfile>('/api/v1/personality/profile')
    return response.data
  },

  updateProfile: async (
    profile: Partial<PersonalityProfile>
  ): Promise<{ status: string; message: string; profile: PersonalityProfile }> => {
    const response = await api.put<{
      status: string
      message: string
      profile: PersonalityProfile
    }>('/api/v1/personality/profile', { profile_data: profile })
    return response.data
  },

  analyzeData: async (): Promise<{
    status: string
    message: string
    profile: PersonalityProfile
  }> => {
    const response = await api.post<{
      status: string
      message: string
      profile: PersonalityProfile
    }>('/api/v1/personality/analyze')
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
  let errorMessage = 'An unexpected error occurred'

  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ error?: string; message?: string }>
    errorMessage =
      axiosError.response?.data?.error ||
      axiosError.response?.data?.message ||
      axiosError.message ||
      'An unexpected error occurred'
  } else if (error instanceof Error) {
    errorMessage = error.message
  }

  logger.error('API error handled', error, { errorMessage })
  return errorMessage
}
