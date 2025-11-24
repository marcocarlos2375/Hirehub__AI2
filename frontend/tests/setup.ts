import { vi } from 'vitest'
import { ref, computed, watch } from 'vue'

// Mock Nuxt composables
global.useRuntimeConfig = vi.fn(() => ({
  public: {
    apiBase: 'http://localhost:8001'
  }
}))

global.$fetch = vi.fn()

// Make Vue reactivity APIs globally available
global.ref = ref
global.computed = computed
global.watch = watch
