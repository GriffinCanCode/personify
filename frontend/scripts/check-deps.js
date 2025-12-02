#!/usr/bin/env node

/**
 * Check for outdated dependencies and security vulnerabilities
 * Run with: node scripts/check-deps.js
 */

const { execSync } = require('node:child_process')

console.log('🔍 Checking for outdated dependencies...\n')

try {
  // Check for outdated packages
  console.log('📦 Outdated packages:')
  execSync('npm outdated', { stdio: 'inherit' })
} catch (_error) {
  // npm outdated exits with code 1 if there are outdated packages
  // This is expected behavior, so we don't throw
}

console.log('\n🔒 Checking for security vulnerabilities...\n')

try {
  // Check for security vulnerabilities
  execSync('npm audit --production', { stdio: 'inherit' })
} catch (_error) {
  console.error('⚠️  Security vulnerabilities found!')
  console.log('Run "npm audit fix" to fix them automatically')
  process.exit(1)
}

console.log('\n✅ Dependency check complete!')
