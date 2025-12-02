import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center space-y-8">
        <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Personify
        </h1>
        <p className="text-2xl text-muted-foreground">
          Virtual Griffin - Your Identical Digital Twin
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/chat">
            <Button size="lg">Start Conversation</Button>
          </Link>
          <Link href="/upload">
            <Button size="lg" variant="outline">
              Upload Data
            </Button>
          </Link>
          <Link href="/personality">
            <Button size="lg" variant="outline">
              View Personality
            </Button>
          </Link>
        </div>
      </div>
    </main>
  )
}
