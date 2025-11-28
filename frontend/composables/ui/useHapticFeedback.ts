/**
 * Haptic Feedback Composable
 *
 * Provides mobile haptic feedback (vibration) as progressive enhancement.
 * Falls back gracefully when Vibration API is not available.
 *
 * Usage:
 * ```ts
 * const { triggerHaptic } = useHapticFeedback()
 *
 * // Light haptic (10ms) - for subtle feedback
 * triggerHaptic('light')
 *
 * // Medium haptic (20ms) - for button presses
 * triggerHaptic('medium')
 *
 * // Heavy haptic (30ms-10ms-30ms) - for important actions
 * triggerHaptic('heavy')
 * ```
 */
export const useHapticFeedback = () => {
  /**
   * Trigger haptic feedback
   *
   * @param type - Haptic intensity: 'light', 'medium', or 'heavy'
   */
  const triggerHaptic = (type: 'light' | 'medium' | 'heavy' = 'light') => {
    // Check if Vibration API is supported
    if (typeof navigator === 'undefined' || !('vibrate' in navigator)) {
      return
    }

    const patterns = {
      light: [10],
      medium: [20],
      heavy: [30, 10, 30]
    }

    try {
      navigator.vibrate(patterns[type])
    } catch (error) {
      // Silently fail if vibration is not supported
      console.debug('Haptic feedback not available:', error)
    }
  }

  /**
   * Check if haptic feedback is available
   */
  const isHapticSupported = () => {
    return typeof navigator !== 'undefined' && 'vibrate' in navigator
  }

  return {
    triggerHaptic,
    isHapticSupported
  }
}
