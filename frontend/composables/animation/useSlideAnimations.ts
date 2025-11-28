import { computed } from 'vue'
import { useReducedMotion } from './useReducedMotion'

/**
 * Slide Animations Composable
 *
 * Provides VueUse Motion animation variants for slider transitions.
 * Automatically adapts animations based on user's motion preferences.
 */
export const useSlideAnimations = () => {
  const { prefersReducedMotion } = useReducedMotion()

  /**
   * Slide Left Animation (Forward: Original → Refinement)
   *
   * - Initial: Enters from right (x: 100)
   * - Enter: Slides to center with spring physics
   * - Leave: Exits to left (x: -100)
   */
  const slideLeft = computed(() => prefersReducedMotion.value ? {
    initial: { opacity: 0 },
    enter: { opacity: 1, transition: { duration: 150 } },
    leave: { opacity: 0, transition: { duration: 150 } }
  } : {
    initial: { opacity: 0, x: 100 },
    enter: {
      opacity: 1,
      x: 0,
      transition: {
        type: 'spring',
        stiffness: 260,
        damping: 20,
        mass: 0.8
      }
    },
    leave: {
      opacity: 0,
      x: -100,
      transition: { duration: 300, ease: 'easeInOut' }
    }
  })

  /**
   * Slide Right Animation (Backward: Refinement → Original)
   *
   * - Initial: Enters from left (x: -100)
   * - Enter: Slides to center with spring physics
   * - Leave: Exits to right (x: 100)
   */
  const slideRight = computed(() => prefersReducedMotion.value ? {
    initial: { opacity: 0 },
    enter: { opacity: 1, transition: { duration: 150 } },
    leave: { opacity: 0, transition: { duration: 150 } }
  } : {
    initial: { opacity: 0, x: -100 },
    enter: {
      opacity: 1,
      x: 0,
      transition: {
        type: 'spring',
        stiffness: 260,
        damping: 20,
        mass: 0.8
      }
    },
    leave: {
      opacity: 0,
      x: 100,
      transition: { duration: 300, ease: 'easeInOut' }
    }
  })

  /**
   * Stagger Children Animation
   *
   * Used for list items (refinement suggestions, quality issues/strengths)
   * - 80ms delay between each child
   * - 100ms initial delay before first child
   */
  const staggerChildren = {
    enter: {
      transition: {
        staggerChildren: 80,
        delayChildren: 100
      }
    }
  }

  /**
   * List Item Animation
   *
   * Used with staggerChildren for individual list items
   * - Slides in from left with fade
   */
  const listItem = {
    initial: { opacity: 0, x: -20 },
    enter: {
      opacity: 1,
      x: 0,
      transition: { duration: 300, ease: 'easeOut' }
    }
  }

  /**
   * Fade In Animation
   *
   * Simple fade in/out for elements that don't need slide effect
   */
  const fadeIn = computed(() => ({
    initial: { opacity: 0 },
    enter: {
      opacity: 1,
      transition: { duration: prefersReducedMotion.value ? 150 : 300 }
    },
    leave: {
      opacity: 0,
      transition: { duration: prefersReducedMotion.value ? 150 : 200 }
    }
  }))

  /**
   * Scale In Animation
   *
   * Used for circle progress and other emphasis elements
   */
  const scaleIn = computed(() => prefersReducedMotion.value ? {
    initial: { opacity: 0 },
    enter: { opacity: 1, transition: { duration: 150 } }
  } : {
    initial: { scale: 0, opacity: 0 },
    enter: {
      scale: 1,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 260,
        damping: 20,
        delay: 0
      }
    }
  })

  return {
    slideLeft,
    slideRight,
    staggerChildren,
    listItem,
    fadeIn,
    scaleIn
  }
}
