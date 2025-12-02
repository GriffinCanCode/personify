/**
 * Type-safe environment variables
 * Validates at build time
 */

const envSchema = {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  NEXT_PUBLIC_ENABLE_ANALYTICS:
    process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true',
  NEXT_PUBLIC_ENABLE_DEBUG: process.env.NEXT_PUBLIC_ENABLE_DEBUG === 'true',
} as const

// Validate required env vars
const requiredEnvVars = ['NEXT_PUBLIC_API_URL'] as const

for (const key of requiredEnvVars) {
  if (!envSchema[key]) {
    throw new Error(`Missing required environment variable: ${key}`)
  }
}

export const env = envSchema

