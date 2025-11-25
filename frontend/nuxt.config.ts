// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt'],

  // Global CSS imports
  css: [
    '~/assets/css/var.css',   // HireHub UI CSS variables (design system)
    '~/assets/css/main.css'   // HireHub UI base styles and components
  ],

  // Component auto-import configuration
  components: [
    {
      path: '~/components',
      pathPrefix: false
    },
    {
      path: '~/components/base',
      prefix: 'Hb',
      pathPrefix: false,
      global: true
    }
  ],

  // Configure auto-imports to scan nested directories
  imports: {
    dirs: [
      'composables/**',  // Scan all nested composable directories
      'stores/**',       // Scan all nested store directories
      'utils/**'         // Scan utils directory
    ]
  },

  // App configuration
  app: {
    head: {
      link: [
        // Google Fonts for HireHub UI Components
        {
          rel: 'preconnect',
          href: 'https://fonts.googleapis.com'
        },
        {
          rel: 'preconnect',
          href: 'https://fonts.gstatic.com',
          crossorigin: 'anonymous'
        },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Gabarito:wght@400;500;600;700;800;900&family=Outfit:wght@100;200;300;400;500;600;700;800;900&family=Wix+Madefor+Text:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,500;1,600;1,700;1,800&display=swap'
        }
      ]
    }
  },

  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8001',
      // HireHub UI Components configuration
      apiBaseUrl: process.env.VITE_API_BASE_URL || 'http://localhost:8001',
      apiUrl: process.env.VITE_API_URL || 'http://localhost:8001/api',
      languageToolApiUrl: process.env.VITE_LANGUAGETOOL_API_URL || 'https://api.languagetool.org/v2/check'
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
