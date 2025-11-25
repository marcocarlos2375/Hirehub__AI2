/**
 * Global Type Definitions
 * Defines global types for libraries and window extensions
 */

// jQuery Global Types
declare global {
  interface Window {
    $: JQueryStatic
    jQuery: JQueryStatic
  }

  // jQuery Core
  interface JQueryStatic {
    (selector: string | Element | Document | JQuery): JQuery
    (html: string, ownerDocument?: Document): JQuery
    (callback: () => void): JQuery
    (): JQuery
    // Plugin registry
    fn: JQuery
  }

  interface JQuery {
    // Core
    length: number
    [index: number]: Element
    each(callback: (index: number, element: Element) => void | boolean): JQuery
    map(callback: (index: number, element: Element) => any): JQuery
    eq(index: number): JQuery
    first(): JQuery
    last(): JQuery
    get(index?: number): Element | Element[]
    index(selector?: string | JQuery | Element): number

    // DOM Manipulation
    html(htmlString?: string): JQuery | string
    text(textString?: string): JQuery | string
    append(content: string | Element | JQuery): JQuery
    prepend(content: string | Element | JQuery): JQuery
    after(content: string | Element | JQuery): JQuery
    before(content: string | Element | JQuery): JQuery
    remove(): JQuery
    empty(): JQuery

    // Attributes
    attr(attributeName: string): string | undefined
    attr(attributeName: string, value: string | number | null): JQuery
    attr(attributes: Record<string, string | number>): JQuery
    removeAttr(attributeName: string): JQuery
    addClass(className: string | ((index: number, currentClassName: string) => string)): JQuery
    removeClass(className?: string | ((index: number, currentClassName: string) => string)): JQuery
    toggleClass(className: string, state?: boolean): JQuery
    hasClass(className: string): boolean

    // CSS
    css(propertyName: string): string
    css(propertyName: string, value: string | number): JQuery
    css(properties: Record<string, string | number>): JQuery
    height(value?: number | string): JQuery | number
    width(value?: number | string): JQuery | number

    // Traversing
    find(selector: string): JQuery
    children(selector?: string): JQuery
    parent(selector?: string): JQuery
    parents(selector?: string): JQuery
    closest(selector: string): JQuery
    siblings(selector?: string): JQuery
    next(selector?: string): JQuery
    prev(selector?: string): JQuery

    // Events
    on(events: string, selector?: string | null, handler?: (event: JQueryEventObject) => void): JQuery
    off(events?: string, selector?: string | null, handler?: (event: JQueryEventObject) => void): JQuery
    trigger(eventType: string, extraParameters?: any[] | Record<string, any>): JQuery
    click(handler?: (event: JQueryEventObject) => void): JQuery

    // jQuery Columnizer Plugin
    columnize(options?: {
      columns?: number
      width?: number
      buildOnce?: boolean
      target?: string | JQuery
      overflow?: {
        height?: number
        id?: string
        doneFunc?: () => void
      }
      ignoreImageLoading?: boolean
      accuracy?: number
      precise?: boolean
      lastNeverTallest?: boolean
    }): JQuery
  }

  interface JQueryEventObject {
    type: string
    target: Element
    currentTarget: Element
    preventDefault(): void
    stopPropagation(): void
    stopImmediatePropagation(): void
    which: number
    metaKey: boolean
    pageX: number
    pageY: number
  }
}

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
