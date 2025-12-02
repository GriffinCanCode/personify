'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { FileUploader } from '@/components/FileUploader'
import { uploadApi, personalityApi } from '@/lib/api'
import { FileText, BarChart3, Sparkles } from 'lucide-react'
import Link from 'next/link'

export default function UploadPage() {
  const queryClient = useQueryClient()
  const [analyzing, setAnalyzing] = useState(false)

  const { data: stats } = useQuery({
    queryKey: ['upload-stats'],
    queryFn: uploadApi.getStats,
  })

  const { data: documents } = useQuery({
    queryKey: ['documents'],
    queryFn: uploadApi.getDocuments,
  })

  const uploadMutation = useMutation({
    mutationFn: uploadApi.uploadFiles,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['upload-stats'] })
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })

  const analyzeMutation = useMutation({
    mutationFn: personalityApi.analyzeData,
    onSuccess: () => {
      setAnalyzing(false)
      queryClient.invalidateQueries({ queryKey: ['personality'] })
    },
  })

  const handleUpload = async (files: File[]) => {
    return uploadMutation.mutateAsync(files)
  }

  const handleAnalyze = () => {
    setAnalyzing(true)
    analyzeMutation.mutate()
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Upload Your Data</h1>
            <p className="text-muted-foreground">
              Feed Virtual Griffin with your documents to build your personality profile
            </p>
          </div>
          <Link href="/">
            <Button variant="outline">Back to Home</Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Documents
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {stats?.total_documents || 0}
              </div>
              <p className="text-sm text-muted-foreground">
                {stats?.processed_documents || 0} processed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Chunks
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {stats?.total_chunks || 0}
              </div>
              <p className="text-sm text-muted-foreground">
                Stored in vector database
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                Ready to Analyze
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Button
                onClick={handleAnalyze}
                disabled={!stats?.processed_documents || analyzing}
                className="w-full"
              >
                {analyzing ? 'Analyzing...' : 'Build Profile'}
              </Button>
            </CardContent>
          </Card>
        </div>

        <FileUploader onUpload={handleUpload} />

        {documents && documents.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Uploaded Documents</CardTitle>
              <CardDescription>
                All documents that have been uploaded and processed
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {documents.map((doc: any) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between p-3 border rounded"
                  >
                    <div className="flex-1">
                      <p className="font-medium">{doc.filename}</p>
                      <p className="text-sm text-muted-foreground">
                        {doc.chunk_count} chunks • {doc.source_type}
                      </p>
                    </div>
                    <Badge variant={doc.processed_at ? 'default' : 'secondary'}>
                      {doc.processed_at ? 'Processed' : 'Pending'}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

