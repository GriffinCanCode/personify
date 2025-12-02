'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { personalityApi } from '@/lib/api'
import { Brain, MessageSquare, TrendingUp, Award } from 'lucide-react'
import Link from 'next/link'

export default function PersonalityPage() {
  const { data: profile, isLoading } = useQuery({
    queryKey: ['personality'],
    queryFn: personalityApi.getProfile,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background p-4 flex items-center justify-center">
        <p>Loading personality profile...</p>
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
              Upload documents and analyze them to create your personality profile
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

  const style = profile.communication_style
  const traits = profile.personality_traits

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Virtual Griffin's Personality</h1>
            <p className="text-muted-foreground">
              Your digital twin's personality profile based on your data
            </p>
          </div>
          <Link href="/">
            <Button variant="outline">Back to Home</Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                Communication Style
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm">Formality</span>
                  <span className="text-sm text-muted-foreground">
                    {Math.round(style.formality * 100)}%
                  </span>
                </div>
                <Progress value={style.formality * 100} />
              </div>
              
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm">Directness</span>
                  <span className="text-sm text-muted-foreground">
                    {Math.round(style.directness * 100)}%
                  </span>
                </div>
                <Progress value={style.directness * 100} />
              </div>
              
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm">Verbosity</span>
                  <span className="text-sm text-muted-foreground">
                    {Math.round(style.verbosity * 100)}%
                  </span>
                </div>
                <Progress value={style.verbosity * 100} />
              </div>
              
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm">Humor</span>
                  <span className="text-sm text-muted-foreground">
                    {Math.round(style.humor * 100)}%
                  </span>
                </div>
                <Progress value={style.humor * 100} />
              </div>

              <div>
                <p className="text-sm font-medium mb-2">Vocabulary</p>
                <Badge>{style.vocabulary_level}</Badge>
              </div>
              
              <div>
                <p className="text-sm font-medium mb-2">Average Sentence Length</p>
                <p className="text-2xl font-bold">{style.avg_sentence_length.toFixed(1)} words</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5" />
                Personality Traits
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm">Openness</span>
                  <span className="text-sm text-muted-foreground">
                    {Math.round(traits.openness * 100)}%
                  </span>
                </div>
                <Progress value={traits.openness * 100} />
              </div>
              
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm">Conscientiousness</span>
                  <span className="text-sm text-muted-foreground">
                    {Math.round(traits.conscientiousness * 100)}%
                  </span>
                </div>
                <Progress value={traits.conscientiousness * 100} />
              </div>
              
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm">Extraversion</span>
                  <span className="text-sm text-muted-foreground">
                    {Math.round(traits.extraversion * 100)}%
                  </span>
                </div>
                <Progress value={traits.extraversion * 100} />
              </div>
              
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm">Agreeableness</span>
                  <span className="text-sm text-muted-foreground">
                    {Math.round(traits.agreeableness * 100)}%
                  </span>
                </div>
                <Progress value={traits.agreeableness * 100} />
              </div>
              
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm">Emotional Stability</span>
                  <span className="text-sm text-muted-foreground">
                    {Math.round(traits.emotional_stability * 100)}%
                  </span>
                </div>
                <Progress value={traits.emotional_stability * 100} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Values
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {profile.values_hierarchy.slice(0, 7).map((value: string, idx: number) => (
                  <div key={idx} className="flex items-center gap-2">
                    <span className="text-2xl font-bold text-muted-foreground">
                      {idx + 1}
                    </span>
                    <span className="text-lg">{value}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="w-5 h-5" />
                Knowledge Domains
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {profile.knowledge_domains.expert?.length > 0 && (
                <div>
                  <p className="text-sm font-medium mb-2">Expert</p>
                  <div className="flex flex-wrap gap-2">
                    {profile.knowledge_domains.expert.map((domain: string) => (
                      <Badge key={domain} variant="default">{domain}</Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {profile.knowledge_domains.competent?.length > 0 && (
                <div>
                  <p className="text-sm font-medium mb-2">Competent</p>
                  <div className="flex flex-wrap gap-2">
                    {profile.knowledge_domains.competent.map((domain: string) => (
                      <Badge key={domain} variant="secondary">{domain}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Common Phrases</CardTitle>
            <CardDescription>
              Frequently used expressions in your writing
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {style.common_phrases.slice(0, 15).map((phrase: string) => (
                <Badge key={phrase} variant="outline">"{phrase}"</Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

