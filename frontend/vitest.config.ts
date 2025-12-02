import path from 'node:path'
import react from '@vitejs/plugin-react-swc'
import tsconfigPaths from 'vite-tsconfig-paths'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [
    react(),
    tsconfigPaths(), // Automatically resolve tsconfig paths
  ],

  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: ['./vitest.setup.tsx'],
    include: ['**/*.{test,spec}.{ts,tsx}'],
    exclude: ['node_modules', '.next', 'e2e', 'dist', 'build'],

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules',
        '.next',
        'coverage',
        '**/*.config.*',
        '**/*.d.ts',
        '**/types/**',
        'e2e/**',
        '**/__tests__/**',
        '**/test-utils.tsx',
      ],
      thresholds: {
        lines: 60,
        functions: 60,
        branches: 60,
        statements: 60,
      },
    },

    // Performance
    mockReset: true,
    restoreMocks: true,
    clearMocks: true,

    // Reporter configuration
    reporters: process.env.CI ? ['verbose', 'json'] : ['verbose'],

    // Watch mode
    watch: false,

    // Parallel execution
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
      },
    },

    // Timeouts
    testTimeout: 10000,
    hookTimeout: 10000,
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
    },
  },

  // Optimize deps for faster startup
  optimizeDeps: {
    include: ['react', 'react-dom', '@testing-library/react', '@testing-library/user-event'],
  },
})
