export interface Agent {
  name: string
  display_name: string
  description: string
}

export interface Message {
  id: string
  content: string
  sender: 'user' | 'agent'
  timestamp: Date
}

export interface ChatResponse {
  response: string
  agent_name: string
  conversation_id: number
}

export interface NoteRequest {
  content: string
  metadata?: Record<string, any>
}

export interface SearchResult {
  content: string
  score: number
  source: string
  created_at: string
} 