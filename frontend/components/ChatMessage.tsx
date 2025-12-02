'use client'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useInteractionLogger } from '@/lib/logger'
import { cn } from '@/lib/utils'
import { ThumbsDown, ThumbsUp } from 'lucide-react'

interface ChatMessageProps {
  role: 'user' | 'assistant'
  content: string
  confidenceScore?: number
  styleMatch?: number
  messageId?: number
  onFeedback?: (messageId: number, rating: number) => void
}

export function ChatMessage({
  role,
  content,
  confidenceScore,
  styleMatch,
  messageId,
  onFeedback,
}: ChatMessageProps) {
  const isAssistant = role === 'assistant'
  const logInteraction = useInteractionLogger('ChatMessage')

  const handleFeedback = (rating: number) => {
    if (messageId && onFeedback) {
      logInteraction('feedback_clicked', {
        messageId,
        rating,
        confidenceScore,
        styleMatch,
      })
      onFeedback(messageId, rating)
    }
  }

  return (
    <div
      className={cn(
        'flex w-full gap-4 p-4 rounded-lg',
        isAssistant ? 'bg-muted/50' : 'bg-background'
      )}
    >
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold">
        {role === 'user' ? 'Y' : 'VG'}
      </div>

      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <span className="font-semibold">{role === 'user' ? 'You' : 'Virtual Griffin'}</span>
          {isAssistant && confidenceScore !== undefined && (
            <Badge variant={confidenceScore > 0.7 ? 'default' : 'secondary'}>
              {Math.round(confidenceScore * 100)}% confidence
            </Badge>
          )}
          {isAssistant && styleMatch !== undefined && (
            <Badge variant="outline">{Math.round(styleMatch * 100)}% style match</Badge>
          )}
        </div>

        <p className="text-sm whitespace-pre-wrap">{content}</p>

        {isAssistant && messageId && onFeedback && (
          <div className="flex gap-2 pt-2">
            <Button size="sm" variant="ghost" onClick={() => handleFeedback(5)}>
              <ThumbsUp className="w-4 h-4 mr-1" />
              Sounds like me
            </Button>
            <Button size="sm" variant="ghost" onClick={() => handleFeedback(1)}>
              <ThumbsDown className="w-4 h-4 mr-1" />
              Not quite right
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
