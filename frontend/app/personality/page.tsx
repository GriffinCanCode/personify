'use client'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { personalityApi } from '@/lib/api'
import { useErrorLogger, useLogger } from '@/lib/logger'
import { useQuery } from '@tanstack/react-query'
import {
  Brain,
  ChevronRight,
  Globe,
  Heart,
  Lightbulb,
  MessageSquare,
  Sparkles,
  Users,
} from 'lucide-react'
import Link from 'next/link'
import React from 'react'

function ConfidenceIndicator({ value, label }: { value: number; label: string }) {
  const color = value >= 0.7 ? 'bg-green-500' : value >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground">
      <div className={`w-2 h-2 rounded-full ${color}`} />
      <span>
        {label}: {Math.round(value * 100)}%
      </span>
    </div>
  )
}

function DimensionCard({
  title,
  icon: Icon,
  description,
  confidence,
  children,
}: {
  title: string
  icon: React.ElementType
  description: string
  confidence: number
  children: React.ReactNode
}) {
  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Icon className="w-5 h-5 text-primary" />
            {title}
          </CardTitle>
          <ConfidenceIndicator value={confidence} label="confidence" />
        </div>
        <CardDescription className="text-sm">{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">{children}</CardContent>
    </Card>
  )
}

function TagList({
  items,
  variant = 'secondary',
}: { items: string[]; variant?: 'default' | 'secondary' | 'outline' }) {
  if (!items?.length)
    return <span className="text-sm text-muted-foreground italic">None identified</span>
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.slice(0, 8).map((item) => (
        <Badge key={item} variant={variant} className="text-xs">
          {item}
        </Badge>
      ))}
    </div>
  )
}

function InterestItem({ topic, depth }: { topic: string; depth: number }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span>{topic}</span>
        <span className="text-muted-foreground">{Math.round(depth * 100)}%</span>
      </div>
      <Progress value={depth * 100} className="h-1.5" />
    </div>
  )
}

export default function PersonalityPage() {
  useLogger('PersonalityPage')
  const logError = useErrorLogger('PersonalityPage')

  const {
    data: profile,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['personality'],
    queryFn: personalityApi.getProfile,
  })

  if (error) logError(error, { context: 'profile_fetch' })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background p-4 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="text-muted-foreground">Loading personality profile...</p>
        </div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-background p-4 flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>No Personality Profile</CardTitle>
            <CardDescription>
              Upload documents and analyze them to create your AI-powered personality profile
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/upload">
              <Button className="w-full">Go to Upload</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto p-4 md:p-6 space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Personality Profile</h1>
            <p className="text-muted-foreground">
              AI-analyzed profile v{profile.version} •{' '}
              {Math.round(profile.overall_confidence * 100)}% confidence
            </p>
          </div>
          <div className="flex gap-2">
            <Link href="/chat">
              <Button>
                Chat Now <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </Link>
            <Link href="/">
              <Button variant="outline">Home</Button>
            </Link>
          </div>
        </div>

        {/* Essence Card */}
        <Card className="bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              Personality Essence
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-lg leading-relaxed">{profile.personality_essence}</p>
            {profile.key_characteristics?.length > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {profile.key_characteristics.map((trait) => (
                  <Badge key={trait} variant="default">
                    {trait}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Six Dimensions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Writing Style */}
          <DimensionCard
            title="Writing Style"
            icon={MessageSquare}
            description={profile.writing_style.voice_description}
            confidence={profile.writing_style.confidence}
          >
            <div className="space-y-2">
              <div className="text-sm">
                <span className="font-medium">Rhythm:</span>{' '}
                <span className="text-muted-foreground">
                  {profile.writing_style.rhythm.pacing_description}
                </span>
              </div>
              <div className="text-sm">
                <span className="font-medium">Tone:</span>{' '}
                <span className="text-muted-foreground">
                  {profile.writing_style.tonal_range.default_tone}
                </span>
              </div>
              <div className="text-sm">
                <span className="font-medium">Vocabulary:</span>{' '}
                <span className="text-muted-foreground">
                  {profile.writing_style.vocabulary_character}
                </span>
              </div>
            </div>
            {profile.writing_style.stylistic_markers.signature_phrases?.length > 0 && (
              <div className="pt-2">
                <p className="text-xs font-medium mb-1.5 text-muted-foreground">
                  Signature Phrases
                </p>
                <div className="flex flex-wrap gap-1">
                  {profile.writing_style.stylistic_markers.signature_phrases
                    .slice(0, 5)
                    .map((phrase) => (
                      <Badge key={phrase} variant="outline" className="text-xs">
                        &quot;{phrase}&quot;
                      </Badge>
                    ))}
                </div>
              </div>
            )}
          </DimensionCard>

          {/* Cognitive Patterns */}
          <DimensionCard
            title="Thinking Patterns"
            icon={Brain}
            description={profile.cognitive.thinking_description}
            confidence={profile.cognitive.confidence}
          >
            <div className="space-y-2">
              <div className="text-sm">
                <span className="font-medium">Reasoning:</span>{' '}
                <span className="text-muted-foreground">
                  {profile.cognitive.reasoning_patterns.primary_mode}
                </span>
              </div>
              <div className="text-sm">
                <span className="font-medium">Problem Solving:</span>{' '}
                <span className="text-muted-foreground">
                  {profile.cognitive.problem_solving_style}
                </span>
              </div>
              <div className="text-sm">
                <span className="font-medium">Complexity:</span>{' '}
                <span className="text-muted-foreground">
                  {profile.cognitive.complexity_preference}
                </span>
              </div>
            </div>
            {profile.cognitive.mental_models.identified_frameworks?.length > 0 && (
              <div className="pt-2">
                <p className="text-xs font-medium mb-1.5 text-muted-foreground">
                  Mental Frameworks
                </p>
                <TagList items={profile.cognitive.mental_models.identified_frameworks} />
              </div>
            )}
          </DimensionCard>

          {/* Emotional Patterns */}
          <DimensionCard
            title="Emotional Landscape"
            icon={Heart}
            description={profile.emotional.emotional_description}
            confidence={profile.emotional.confidence}
          >
            <div className="space-y-2">
              <div className="text-sm">
                <span className="font-medium">Baseline:</span>{' '}
                <span className="text-muted-foreground">
                  {profile.emotional.emotional_baseline}
                </span>
              </div>
            </div>
            {profile.emotional.triggers.excites?.length > 0 && (
              <div>
                <p className="text-xs font-medium mb-1 text-green-600">What Excites</p>
                <TagList items={profile.emotional.triggers.excites.slice(0, 4)} variant="outline" />
              </div>
            )}
            {profile.emotional.triggers.motivates?.length > 0 && (
              <div>
                <p className="text-xs font-medium mb-1 text-blue-600">Core Motivations</p>
                <TagList
                  items={profile.emotional.triggers.motivates.slice(0, 4)}
                  variant="outline"
                />
              </div>
            )}
          </DimensionCard>

          {/* Interests */}
          <DimensionCard
            title="Interests & Passions"
            icon={Lightbulb}
            description={profile.interests.interest_description}
            confidence={profile.interests.confidence}
          >
            {profile.interests.genuine_interests?.length > 0 && (
              <div className="space-y-2">
                {profile.interests.genuine_interests.slice(0, 4).map((interest) => (
                  <InterestItem
                    key={interest.topic}
                    topic={interest.topic}
                    depth={interest.depth}
                  />
                ))}
              </div>
            )}
            {profile.interests.aspirations?.length > 0 && (
              <div className="pt-2">
                <p className="text-xs font-medium mb-1.5 text-muted-foreground">Aspirations</p>
                <TagList items={profile.interests.aspirations.slice(0, 4)} />
              </div>
            )}
          </DimensionCard>

          {/* Worldview */}
          <DimensionCard
            title="Worldview & Values"
            icon={Globe}
            description={profile.worldview.worldview_description}
            confidence={profile.worldview.confidence}
          >
            {profile.worldview.core_beliefs.values_hierarchy?.length > 0 && (
              <div>
                <p className="text-xs font-medium mb-1.5 text-muted-foreground">Core Values</p>
                <div className="space-y-1">
                  {profile.worldview.core_beliefs.values_hierarchy.slice(0, 5).map((value, i) => (
                    <div key={value} className="flex items-center gap-2 text-sm">
                      <span className="font-bold text-muted-foreground w-4">{i + 1}</span>
                      <span>{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {profile.worldview.philosophical_leanings?.length > 0 && (
              <div className="pt-2">
                <p className="text-xs font-medium mb-1.5 text-muted-foreground">Philosophy</p>
                <TagList items={profile.worldview.philosophical_leanings.slice(0, 4)} />
              </div>
            )}
          </DimensionCard>

          {/* Social Dynamics */}
          <DimensionCard
            title="Social Dynamics"
            icon={Users}
            description={profile.social.social_description}
            confidence={profile.social.confidence}
          >
            <div className="space-y-2">
              <div className="text-sm">
                <span className="font-medium">Directness:</span>{' '}
                <span className="text-muted-foreground">
                  {profile.social.communication_dynamics.directness_level}
                </span>
              </div>
              <div className="text-sm">
                <span className="font-medium">Collaboration:</span>{' '}
                <span className="text-muted-foreground">{profile.social.collaboration_style}</span>
              </div>
              <div className="text-sm">
                <span className="font-medium">Authority:</span>{' '}
                <span className="text-muted-foreground">
                  {profile.social.authority_positioning}
                </span>
              </div>
            </div>
            {profile.social.relational_patterns?.length > 0 && (
              <div className="pt-2">
                <p className="text-xs font-medium mb-1.5 text-muted-foreground">
                  Relational Patterns
                </p>
                <TagList items={profile.social.relational_patterns.slice(0, 4)} />
              </div>
            )}
          </DimensionCard>
        </div>

        {/* Context Variations */}
        {profile.context_variations && Object.keys(profile.context_variations).length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Context Adaptations</CardTitle>
              <CardDescription>How personality shifts across different contexts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(profile.context_variations).map(([context, description]) => (
                  <div key={context} className="p-3 bg-muted/50 rounded-lg">
                    <p className="font-medium capitalize mb-1">{context}</p>
                    <p className="text-sm text-muted-foreground">{description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Analysis Metadata */}
        {profile.analysis_metadata && (
          <Card className="bg-muted/30">
            <CardContent className="py-4">
              <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
                <span>Documents analyzed: {profile.analysis_metadata.documents_analyzed}</span>
                <span>
                  Tokens processed:{' '}
                  {profile.analysis_metadata.total_tokens_analyzed.toLocaleString()}
                </span>
                <span>
                  Analysis time: {profile.analysis_metadata.analysis_duration_seconds.toFixed(1)}s
                </span>
                <span>Model: {profile.analysis_metadata.model_used}</span>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
