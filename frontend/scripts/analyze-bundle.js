#!/usr/bin/env node

/**
 * Analyze bundle size
 * Run after build: node scripts/analyze-bundle.js
 */

const fs = require('node:fs')
const path = require('node:path')

const buildDir = path.join(__dirname, '../.next')

if (!fs.existsSync(buildDir)) {
  console.error('❌ Build directory not found. Run "npm run build" first.')
  process.exit(1)
}

console.log('📊 Analyzing bundle size...\n')

// This is a simple analyzer. For more detailed analysis, use @next/bundle-analyzer
const getDirectorySize = (dir) => {
  let size = 0
  const files = fs.readdirSync(dir)

  for (const file of files) {
    const filePath = path.join(dir, file)
    const stats = fs.statSync(filePath)

    if (stats.isDirectory()) {
      size += getDirectorySize(filePath)
    } else {
      size += stats.size
    }
  }

  return size
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${Math.round((bytes / k ** i) * 100) / 100} ${sizes[i]}`
}

try {
  const totalSize = getDirectorySize(buildDir)
  console.log(`Total build size: ${formatBytes(totalSize)}`)

  const staticDir = path.join(buildDir, 'static')
  if (fs.existsSync(staticDir)) {
    const staticSize = getDirectorySize(staticDir)
    console.log(`Static files size: ${formatBytes(staticSize)}`)
  }

  console.log('\n💡 Tip: Use @next/bundle-analyzer for detailed analysis')
  console.log('   npm install --save-dev @next/bundle-analyzer')
} catch (error) {
  console.error('❌ Error analyzing bundle:', error.message)
  process.exit(1)
}
