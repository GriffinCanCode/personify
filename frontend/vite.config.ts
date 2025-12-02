import react from '@vitejs/plugin-react-swc'
import { defineConfig } from 'vite'
import checker from 'vite-plugin-checker'
import tsconfigPaths from 'vite-tsconfig-paths'

/**
 * Vite configuration for development tooling
 * Note: Next.js handles the main build, this is for dev tools
 */
export default defineConfig({
  plugins: [
    // Use SWC for faster compilation
    react(),

    // Resolve TypeScript paths from tsconfig
    tsconfigPaths(),

    // Type checking and linting in dev mode
    checker({
      typescript: true,
      eslint: {
        lintCommand: 'eslint --ext .ts,.tsx .',
      },
      overlay: {
        initialIsOpen: false,
      },
    }),
  ],

  resolve: {
    alias: {
      '@': '/src', // Fallback alias
    },
  },

  // Optimize dependencies
  optimizeDeps: {
    include: ['react', 'react-dom', 'axios', '@tanstack/react-query'],
    exclude: ['@biomejs/biome'],
  },

  // Server configuration for storybook or other Vite-based tools
  server: {
    port: 3001,
    strictPort: false,
    open: false,
  },

  // Build configuration
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'query-vendor': ['@tanstack/react-query'],
        },
      },
    },
  },
})
