import { vi } from 'vitest'
import { ref, computed, watch, readonly } from 'vue'
import { setActivePinia, createPinia } from 'pinia'

// Create and activate Pinia instance for testing
setActivePinia(createPinia())

// Mock Nuxt composables
;(global as any).useRuntimeConfig = vi.fn(() => ({
  public: {
    apiBase: 'http://localhost:8001'
  }
}))

;(global as any).$fetch = vi.fn() as any

// Mock useState (Nuxt's server-safe ref)
// useState creates a shared state that persists across components
const stateMap = new Map<string, any>()

;(global as any).useState = vi.fn((key: string, init?: () => any) => {
  if (!stateMap.has(key)) {
    stateMap.set(key, ref(init ? init() : undefined))
  }
  return stateMap.get(key)
})

// Helper to clear state between tests
;(global as any).clearAllState = () => {
  stateMap.clear()
}

// Make Vue reactivity APIs globally available
;(global as any).ref = ref
;(global as any).computed = computed
;(global as any).watch = watch
;(global as any).readonly = readonly
