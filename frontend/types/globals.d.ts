/**
 * Global Type Definitions
 * Defines global types for libraries and window extensions
 */

// Nuxt/Vue Global Types
declare module '#app' {
  interface NuxtApp {
    $t: (key: string, params?: Record<string, string | number>) => string
    $toast: {
      show(message: string, type?: 'success' | 'error' | 'warning' | 'info', duration?: number): void
      success(message: string, duration?: number): void
      error(message: string, duration?: number): void
      warning(message: string, duration?: number): void
      info(message: string, duration?: number): void
    }
  }
}

// Extend Vue component instance to include $t, $toast, $router, and $route
declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $t: (key: string, params?: Record<string, string | number>) => string
    $toast: {
      show(message: string, type?: 'success' | 'error' | 'warning' | 'info', duration?: number): void
      success(message: string, duration?: number): void
      error(message: string, duration?: number): void
      warning(message: string, duration?: number): void
      info(message: string, duration?: number): void
    }
    $router: import('vue-router').Router
    $route: import('vue-router').RouteLocationNormalizedLoaded
  }
}

// Process/Environment Types
declare global {
  const process: {
    client: boolean
    server: boolean
    dev: boolean
    env: Record<string, string | undefined>
  }
}

// Module declarations for JSON imports
declare module '*.json' {
  const value: any
  export default value
}

// Module declarations for Vue components
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

export {}
