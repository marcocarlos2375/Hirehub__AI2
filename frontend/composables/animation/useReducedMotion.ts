import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Reduced Motion Composable
 *
 * Detects user's motion preferences for accessibility support.
 * Monitors the `prefers-reduced-motion` media query.
 *
 * Usage:
 * ```ts
 * const { prefersReducedMotion } = useReducedMotion()
 *
 * if (prefersReducedMotion.value) {
 *   // Use simplified animations
 * }
 * ```
 */
export const useReducedMotion = () => {
  const prefersReducedMotion = ref(false)
  let mediaQuery: MediaQueryList | null = null

  const updateMotionPreference = (e: MediaQueryListEvent | MediaQueryList) => {
    prefersReducedMotion.value = e.matches
  }

  onMounted(() => {
    // Check if matchMedia is supported
    if (typeof window === 'undefined' || !window.matchMedia) {
      return
    }

    mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    prefersReducedMotion.value = mediaQuery.matches

    // Listen for changes
    mediaQuery.addEventListener('change', updateMotionPreference)
  })

  onUnmounted(() => {
    // Cleanup listener
    if (mediaQuery) {
      mediaQuery.removeEventListener('change', updateMotionPreference)
    }
  })

  return {
    prefersReducedMotion
  }
}
