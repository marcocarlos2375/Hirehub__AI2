// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt'],

  // Configure auto-imports to scan nested directories
  imports: {
    dirs: [
      'composables/**',  // Scan all nested composable directories
      'stores/**',       // Scan all nested store directories
      'utils/**'         // Scan utils directory
    ]
  },

  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8001'
    }
  },

  // Proxy API requests to avoid CORS issues in development
  nitro: {
    devProxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true
      }
    }
  }
})
