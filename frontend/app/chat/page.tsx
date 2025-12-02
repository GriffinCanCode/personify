'use client'

import { useState, useRef, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { ChatMessage } from '@/components/ChatMessage'
import { chatApi, feedbackApi } from '@/lib/api'
import { Send, Loader2 } from 'lucide-react'
import Link from 'next/link'

interface Message {
  id?: number
  role: 'user' | 'assistant'
  content: string
  confidence_score?: number
  style_match?: number
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState<number | undefined>()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const chatMutation = useMutation({
    mutationFn: (message: string) =>
      chatApi.sendMessage(message, conversationId),
    onSuccess: (data) => {
      setConversationId(data.conversation_id)
      setMessages(prev => [
        ...prev,
        {
          id: data.message_id,
          role: 'assistant',
          content: data.response,
          confidence_score: data.confidence_score,
          style_match: data.style_match,
        },
      ])
    },
  })

  const feedbackMutation = useMutation({
    mutationFn: ({ messageId, rating }: { messageId: number; rating: number }) =>
      feedbackApi.submitFeedback(messageId, rating),
  })

  const handleSend = () => {
    if (!input.trim()) return

    const userMessage = {
      role: 'user' as const,
      content: input,
    }

    setMessages(prev => [...prev, userMessage])
    chatMutation.mutate(input)
    setInput('')
  }

  const handleFeedback = (messageId: number, rating: number) => {
    feedbackMutation.mutate({ messageId, rating })
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-4xl mx-auto space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Chat with Virtual Griffin</h1>
            <p className="text-muted-foreground">
              Your identical digital twin, powered by your own data
            </p>
          </div>
          <Link href="/">
            <Button variant="outline">Back to Home</Button>
          </Link>
        </div>

        <Card className="h-[600px] flex flex-col">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center text-center text-muted-foreground">
                <div>
                  <p className="text-lg mb-2">Start a conversation with Virtual Griffin</p>
                  <p className="text-sm">
                    Ask anything - Virtual Griffin will respond exactly as you would
                  </p>
                </div>
              </div>
            ) : (
              messages.map((message, idx) => (
                <ChatMessage
                  key={idx}
                  {...message}
                  messageId={message.id}
                  onFeedback={handleFeedback}
                />
              ))
            )}
            
            {chatMutation.isPending && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Virtual Griffin is thinking...</span>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t p-4">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Type your message..."
                disabled={chatMutation.isPending}
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || chatMutation.isPending}
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

