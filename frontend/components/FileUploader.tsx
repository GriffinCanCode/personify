'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, CheckCircle, XCircle } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'

interface FileUploaderProps {
  onUpload: (files: File[]) => Promise<any>
  onComplete?: () => void
}

interface UploadFile {
  file: File
  status: 'pending' | 'uploading' | 'success' | 'error'
  message?: string
}

export function FileUploader({ onUpload, onComplete }: FileUploaderProps) {
  const [files, setFiles] = useState<UploadFile[]>([])
  const [uploading, setUploading] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      status: 'pending' as const,
    }))
    setFiles(prev => [...prev, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
  })

  const handleUpload = async () => {
    setUploading(true)
    
    const filesToUpload = files
      .filter(f => f.status === 'pending')
      .map(f => f.file)

    try {
      const result = await onUpload(filesToUpload)
      
      // Update file statuses based on results
      setFiles(prev =>
        prev.map(f => {
          const uploadResult = result.results?.find(
            (r: any) => r.filename === f.file.name
          )
          
          if (uploadResult) {
            return {
              ...f,
              status: uploadResult.status === 'success' ? 'success' : 'error',
              message: uploadResult.message,
            }
          }
          return f
        })
      )

      onComplete?.()
    } catch (error) {
      console.error('Upload error:', error)
      setFiles(prev =>
        prev.map(f => ({
          ...f,
          status: 'error' as const,
          message: 'Upload failed',
        }))
      )
    } finally {
      setUploading(false)
    }
  }

  const clearCompleted = () => {
    setFiles(prev => prev.filter(f => f.status === 'pending'))
  }

  const pendingCount = files.filter(f => f.status === 'pending').length
  const successCount = files.filter(f => f.status === 'success').length

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="pt-6">
          <div
            {...getRootProps()}
            className={cn(
              'border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors',
              isDragActive
                ? 'border-primary bg-primary/5'
                : 'border-muted-foreground/25 hover:border-primary/50'
            )}
          >
            <input {...getInputProps()} />
            <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            {isDragActive ? (
              <p className="text-lg">Drop files here...</p>
            ) : (
              <div>
                <p className="text-lg mb-2">
                  Drag & drop files here, or click to select
                </p>
                <p className="text-sm text-muted-foreground">
                  Supports: .txt, .pdf, .docx, .md, .json, audio files
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {files.length > 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-2">
              {files.map((fileItem, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 p-2 rounded border"
                >
                  <div className="flex-shrink-0">
                    {fileItem.status === 'success' && (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    )}
                    {fileItem.status === 'error' && (
                      <XCircle className="w-5 h-5 text-red-500" />
                    )}
                    {fileItem.status === 'pending' && (
                      <File className="w-5 h-5 text-muted-foreground" />
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {fileItem.file.name}
                    </p>
                    {fileItem.message && (
                      <p className="text-xs text-muted-foreground">
                        {fileItem.message}
                      </p>
                    )}
                  </div>
                  
                  <div className="text-sm text-muted-foreground">
                    {(fileItem.file.size / 1024).toFixed(1)} KB
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-2 mt-4">
              <Button
                onClick={handleUpload}
                disabled={uploading || pendingCount === 0}
                className="flex-1"
              >
                {uploading ? 'Uploading...' : `Upload ${pendingCount} file(s)`}
              </Button>
              {successCount > 0 && (
                <Button variant="outline" onClick={clearCompleted}>
                  Clear completed
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

