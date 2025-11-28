import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * Animation Store
 *
 * Centralized animation state and timing coordination for the slider-based question flow.
 * Manages animation sequences and queuing to prevent conflicts.
 */
export const useAnimationStore = defineStore('animation', () => {
  // State
  const isSliding = ref(false)
  const slideDirection = ref<'left' | 'right'>('left')
  const isEvaluating = ref(false)
  const stepperHeaderVisible = ref(true)
  const answerInputVisible = ref(true)

  // Animation queue to prevent conflicts
  const animationQueue = ref<Array<() => Promise<void>>>([])
  const isProcessingQueue = ref(false)

  // Helper function for delays
  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

  /**
   * Queue an animation to prevent conflicts
   */
  const queueAnimation = (animation: () => Promise<void>) => {
    animationQueue.value.push(animation)
    if (!isProcessingQueue.value) {
      processQueue()
    }
  }

  /**
   * Process the animation queue sequentially
   */
  const processQueue = async () => {
    isProcessingQueue.value = true
    while (animationQueue.value.length > 0) {
      const animation = animationQueue.value.shift()
      if (animation) {
        await animation()
      }
    }
    isProcessingQueue.value = false
  }

  /**
   * Orchestrated sequence: Original → Refinement (Slide Left)
   *
   * Timeline:
   * T=0ms:     AnswerInput fades out (200ms)
   * T=150ms:   HbLoadingOverlay fades in (300ms)
   * T=150ms:   API evaluation starts
   * T=API:     HbLoadingOverlay fades out (300ms)
   * T=API+200: HbStepper header slides up + fades out (250ms)
   * T=API+250: HbSlider transitions LEFT (600ms)
   */
  const slideToRefinement = async () => {
    await queueAnimation(async () => {
      // Hide AnswerInput
      answerInputVisible.value = false
      await delay(200)

      // Show loading state
      isEvaluating.value = true
      await delay(300)

      // API call happens externally - will set isEvaluating to false

      // Wait for API to complete (set externally)
      // This function is called after API completes

      // Hide HbStepper header
      stepperHeaderVisible.value = false
      await delay(250)

      // Set slide direction
      slideDirection.value = 'left'
      isSliding.value = true

      // Slide index changed by QuestionSlider component
      await delay(600)

      isSliding.value = false
    })
  }

  /**
   * Orchestrated sequence: Refinement → Original (Slide Right)
   *
   * Timeline:
   * T=0ms:     Refinement form fades out (200ms)
   * T=150ms:   HbLoadingOverlay fades in (300ms)
   * T=150ms:   API re-evaluation starts
   * T=API:     HbLoadingOverlay fades out (300ms)
   * T=API+200: HbSlider transitions RIGHT (600ms)
   * T=API+400: HbStepper header slides down + fades in (250ms)
   * T=API+600: AnswerInput fades in with improved text (300ms)
   */
  const slideToOriginal = async () => {
    await queueAnimation(async () => {
      await delay(200)

      // Show loading state
      isEvaluating.value = true
      await delay(300)

      // API call happens externally - will set isEvaluating to false

      // Wait for API to complete (set externally)
      // This function is called after API completes

      // Set slide direction
      slideDirection.value = 'right'
      isSliding.value = true

      // Slide index changed by QuestionSlider component
      await delay(600)

      // Show HbStepper header
      stepperHeaderVisible.value = true
      await delay(250)

      // Show AnswerInput
      answerInputVisible.value = true
      await delay(300)

      isSliding.value = false
    })
  }

  /**
   * Reset animation state (useful when navigating between questions)
   */
  const resetAnimationState = () => {
    isSliding.value = false
    isEvaluating.value = false
    stepperHeaderVisible.value = true
    answerInputVisible.value = true
    slideDirection.value = 'left'
  }

  /**
   * Clear animation queue (useful for cleanup)
   */
  const clearQueue = () => {
    animationQueue.value = []
    isProcessingQueue.value = false
  }

  return {
    // State
    isSliding,
    slideDirection,
    isEvaluating,
    stepperHeaderVisible,
    answerInputVisible,

    // Methods
    slideToRefinement,
    slideToOriginal,
    resetAnimationState,
    clearQueue
  }
})
