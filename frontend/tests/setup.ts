import { vi } from 'vitest'
import { ref, computed, watch } from 'vue'

// Mock Nuxt composables
;(global as any).useRuntimeConfig = vi.fn(() => ({
  public: {
    apiBase: 'http://localhost:8001'
  }
}))

;(global as any).$fetch = vi.fn() as any

// Make Vue reactivity APIs globally available
;(global as any).ref = ref
;(global as any).computed = computed
;(global as any).watch = watch
