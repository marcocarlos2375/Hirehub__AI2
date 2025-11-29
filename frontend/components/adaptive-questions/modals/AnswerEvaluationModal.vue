<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="modelValue"
        class="modal-overlay"
        @click.self="handleOverlayClick"
      >
        <!-- Loading State -->
        <div v-if="modalState === 'loading'" class="modal-content loading-content">
          <HbSpinner size="lg" />
          <p class="loading-text">{{ loadingMessage }}</p>
          <p v-if="showTimeoutWarning" class="timeout-warning">
            This is taking longer than expected. Please wait...
          </p>
        </div>

        <!-- Slider State -->
        <div v-else-if="modalState === 'slider'" class="modal-content slider-content">
          <!-- Slider Container -->
          <div class="slider-container" ref="sliderContainer">
            <div
              class="slides-wrapper"
              :style="{ transform: `translateX(-${currentSlide * 100}%)` }"
            >
              <!-- Slide 1: Question Context -->
              <div class="slide">
                <div class="slide-inner">
                  <h3 class="slide-title">Question Context</h3>
                  <p class="text-sm text-gray-500 mb-4">Review what you were asked and your original answer</p>

                  <!-- Question Display -->
                  <div v-if="question" class="question-display">
                    <div class="question-header">
                      <span class="question-number">Q{{ question.number }}</span>
                      <span :class="['priority-badge', priorityClass]">
                        {{ question.priority }}
                      </span>
                    </div>
                    <h4 class="question-title">{{ question.title }}</h4>
                    <p class="question-text">{{ question.question_text }}</p>
                  </div>

                  <!-- User's Original Answer -->
                  <div class="answer-display">
                    <label class="answer-label">Your Answer:</label>
                    <div class="answer-box">
                      {{ userAnswer }}
                    </div>
                  </div>

                  <HbButton
                    variant="primary"
                    @click="nextSlide"
                    class="mt-6"
                  >
                    Review Feedback →
                  </HbButton>
                </div>
              </div>

              <!-- Slide 2: Evaluation + Refinement -->
              <div class="slide">
                <div class="slide-inner">
                  <h3 class="slide-title">Answer Evaluation</h3>
                  <p class="text-sm text-gray-500 mb-4">Review your answer quality and refine if needed</p>

                  <!-- Evaluation Display Placeholder -->
                  <div v-if="evaluation" class="evaluation-container">
                    <!-- Quality Score -->
                    <div class="quality-score-badge">
                      <div :class="['score-circle', scoreColorClass]">
                        <span class="score-number">{{ evaluation.quality_score }}</span>
                        <span class="score-max">/10</span>
                      </div>
                      <p class="score-label">{{ scoreLabel }}</p>
                    </div>

                    <!-- Quality Strengths -->
                    <div v-if="evaluation.quality_strengths?.length" class="quality-section strengths">
                      <h4 class="section-title">Strengths</h4>
                      <ul class="quality-list">
                        <li v-for="(strength, index) in evaluation.quality_strengths" :key="index">
                          {{ strength }}
                        </li>
                      </ul>
                    </div>

                    <!-- Quality Issues -->
                    <div v-if="evaluation.quality_issues?.length" class="quality-section issues">
                      <h4 class="section-title">Areas to Improve</h4>
                      <ul class="quality-list">
                        <li v-for="(issue, index) in evaluation.quality_issues" :key="index">
                          {{ issue }}
                        </li>
                      </ul>
                    </div>

                    <!-- Refinement Form -->
                    <div v-if="!evaluation.is_acceptable" class="refinement-form">
                      <h4 class="section-title">Improve Your Answer</h4>
                      <p class="text-sm text-gray-600 mb-4">
                        Provide more details to strengthen your answer:
                      </p>

                      <div class="refinement-fields">
                        <div class="field-group">
                          <label class="field-label">Duration & Timeline Details</label>
                          <textarea
                            v-model="refinementData.duration_detail"
                            class="refinement-textarea"
                            rows="2"
                            placeholder="How long? When? Timeframes?"
                          ></textarea>
                        </div>

                        <div class="field-group">
                          <label class="field-label">Specific Tools & Technologies</label>
                          <textarea
                            v-model="refinementData.specific_tools"
                            class="refinement-textarea"
                            rows="2"
                            placeholder="Which tools, frameworks, or technologies?"
                          ></textarea>
                        </div>

                        <div class="field-group">
                          <label class="field-label">Metrics & Results</label>
                          <textarea
                            v-model="refinementData.metrics"
                            class="refinement-textarea"
                            rows="2"
                            placeholder="Numbers, outcomes, achievements?"
                          ></textarea>
                        </div>
                      </div>

                      <HbButton
                        variant="primary"
                        @click="submitRefinement"
                        :disabled="isRefining || !hasRefinementData"
                        class="mt-4"
                      >
                        <HbSpinner v-if="isRefining" size="sm" class="mr-2" />
                        {{ isRefining ? 'Improving...' : 'Submit Improvements' }}
                      </HbButton>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Slide 3: AI-Improved Response -->
              <div class="slide">
                <div class="slide-inner">
                  <h3 class="slide-title">Improved Answer</h3>
                  <p class="text-sm text-gray-500 mb-4">AI has enhanced your answer with the details you provided</p>

                  <div class="improved-answer-display">
                    <label class="answer-label">Enhanced Answer:</label>
                    <div class="improved-answer-box">
                      {{ improvedAnswer }}
                    </div>
                  </div>

                  <div class="action-buttons">
                    <HbButton
                      variant="ghost"
                      @click="prevSlide"
                    >
                      ← Edit More
                    </HbButton>
                    <HbButton
                      variant="primary"
                      @click="useImprovedAnswer"
                    >
                      Use This Answer
                    </HbButton>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Dot Navigation -->
          <div class="dot-navigation">
            <button
              v-for="index in 3"
              :key="index"
              :class="['dot', { active: currentSlide === index - 1 }]"
              @click="goToSlide(index - 1)"
              :aria-label="`Go to slide ${index}`"
            ></button>
          </div>

          <!-- Close Button -->
          <button class="close-button" @click="closeModal" aria-label="Close modal">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import type { AnswerEvaluationModalProps, AnswerEvaluationModalEmits } from '~/types/component-props'

const props = defineProps<AnswerEvaluationModalProps>()
const emit = defineEmits<AnswerEvaluationModalEmits>()

// Modal state
const modalState = ref<'loading' | 'slider' | 'closed'>('loading')
const currentSlide = ref(0)
const isRefining = ref(false)
const improvedAnswer = ref('')
const showTimeoutWarning = ref(false)

// Refinement data
const refinementData = reactive({
  duration_detail: '',
  specific_tools: '',
  metrics: ''
})

// Slider ref
const sliderContainer = ref<HTMLElement | null>(null)

// Touch/swipe state
const touchStartX = ref(0)
const touchEndX = ref(0)

// Computed
const loadingMessage = computed(() => {
  return isRefining.value ? 'Improving your answer...' : 'Evaluating your answer...'
})

const hasRefinementData = computed(() => {
  return Object.values(refinementData).some(val => val.trim().length > 0)
})

const priorityClass = computed(() => {
  if (!props.question) return ''
  const priority = props.question.priority?.toUpperCase()
  return {
    'CRITICAL': 'priority-critical',
    'HIGH': 'priority-high',
    'MEDIUM': 'priority-medium',
    'LOW': 'priority-low'
  }[priority] || ''
})

const scoreColorClass = computed(() => {
  if (!props.evaluation) return 'score-gray'
  const score = props.evaluation.quality_score
  if (score >= 8) return 'score-green'
  if (score >= 6) return 'score-yellow'
  return 'score-red'
})

const scoreLabel = computed(() => {
  if (!props.evaluation) return ''
  const score = props.evaluation.quality_score
  if (score >= 8) return 'Excellent'
  if (score >= 6) return 'Good - Could be improved'
  return 'Needs improvement'
})

// Watch for evaluation changes
watch(() => props.evaluation, (newEval) => {
  if (newEval && modalState.value === 'loading') {
    // Transition from loading to slider
    modalState.value = 'slider'
    currentSlide.value = 0
  }
}, { immediate: true })

// Timeout warning (10 seconds)
let timeoutTimer: NodeJS.Timeout | null = null
watch(() => props.modelValue, (isOpen) => {
  if (isOpen && modalState.value === 'loading') {
    timeoutTimer = setTimeout(() => {
      showTimeoutWarning.value = true
    }, 10000)
  } else {
    if (timeoutTimer) {
      clearTimeout(timeoutTimer)
      timeoutTimer = null
    }
    showTimeoutWarning.value = false
  }
})

// Slide navigation
const nextSlide = () => {
  if (currentSlide.value < 2) {
    currentSlide.value++
  }
}

const prevSlide = () => {
  if (currentSlide.value > 0) {
    currentSlide.value--
  }
}

const goToSlide = (index: number) => {
  if (index >= 0 && index <= 2 && !isRefining.value) {
    currentSlide.value = index
  }
}

// Touch/swipe handlers
const handleTouchStart = (e: TouchEvent) => {
  touchStartX.value = e.touches[0]?.clientX ?? 0
}

const handleTouchMove = (e: TouchEvent) => {
  touchEndX.value = e.touches[0]?.clientX ?? 0
}

const handleTouchEnd = () => {
  const diff = touchStartX.value - touchEndX.value
  const threshold = 50

  if (Math.abs(diff) > threshold) {
    if (diff > 0) {
      // Swipe left - next slide
      nextSlide()
    } else {
      // Swipe right - previous slide
      prevSlide()
    }
  }
}

// Keyboard navigation
const handleKeydown = (e: KeyboardEvent) => {
  if (modalState.value !== 'slider') return

  if (e.key === 'ArrowLeft') {
    prevSlide()
  } else if (e.key === 'ArrowRight') {
    nextSlide()
  } else if (e.key === 'Escape') {
    closeModal()
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)

  if (sliderContainer.value) {
    sliderContainer.value.addEventListener('touchstart', handleTouchStart)
    sliderContainer.value.addEventListener('touchmove', handleTouchMove)
    sliderContainer.value.addEventListener('touchend', handleTouchEnd)
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)

  if (sliderContainer.value) {
    sliderContainer.value.removeEventListener('touchstart', handleTouchStart)
    sliderContainer.value.removeEventListener('touchmove', handleTouchMove)
    sliderContainer.value.removeEventListener('touchend', handleTouchEnd)
  }

  if (timeoutTimer) {
    clearTimeout(timeoutTimer)
  }
})

// Actions
const handleOverlayClick = () => {
  // Don't close while loading
  if (modalState.value === 'loading') return
  closeModal()
}

const closeModal = () => {
  emit('update:modelValue', false)
  // Reset state
  setTimeout(() => {
    modalState.value = 'loading'
    currentSlide.value = 0
    isRefining.value = false
    improvedAnswer.value = ''
    Object.keys(refinementData).forEach(key => {
      refinementData[key as keyof typeof refinementData] = ''
    })
  }, 300)
}

const submitRefinement = async () => {
  if (!props.question || isRefining.value) return

  isRefining.value = true

  try {
    // TODO: Call refineAnswer API
    // For now, simulate with timeout
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Mock improved answer
    improvedAnswer.value = `${props.userAnswer}\n\nEnhanced with:\n- ${refinementData.duration_detail}\n- ${refinementData.specific_tools}\n- ${refinementData.metrics}`

    // Navigate to slide 3
    currentSlide.value = 2
  } catch (error) {
    console.error('Refinement failed:', error)
    alert('Failed to improve answer. Please try again.')
  } finally {
    isRefining.value = false
  }
}

const useImprovedAnswer = () => {
  if (!props.question) return
  emit('use-improved-answer', props.question.id, improvedAnswer.value)
  closeModal()
}
</script>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 250;
  padding: 1rem;
}

/* Modal Content */
.modal-content {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  position: relative;
}

/* Loading Content */
.loading-content {
  max-width: 400px;
  padding: 3rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loading-text {
  font-size: 1.125rem;
  font-weight: 500;
  color: #111827;
  text-align: center;
}

.timeout-warning {
  font-size: 0.875rem;
  color: #ea580c;
  text-align: center;
  margin-top: 0.5rem;
}

/* Slider Content */
.slider-content {
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.slider-container {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.slides-wrapper {
  display: flex;
  height: 100%;
  transition: transform 300ms ease-in-out;
}

.slide {
  min-width: 100%;
  height: 100%;
  overflow-y: auto;
  padding: 2rem;
}

.slide-inner {
  max-width: 700px;
  margin: 0 auto;
}

.slide-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.5rem;
}

/* Question Display */
.question-display {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.question-number {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
}

.priority-badge {
  padding: 0.25rem 0.625rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.priority-critical {
  background: #fee2e2;
  color: #dc2626;
}

.priority-high {
  background: #fed7aa;
  color: #ea580c;
}

.priority-medium {
  background: #fef3c7;
  color: #d97706;
}

.priority-low {
  background: #e5e7eb;
  color: #6b7280;
}

.question-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.5rem;
}

.question-text {
  font-size: 0.875rem;
  color: #4b5563;
  line-height: 1.5;
}

/* Answer Display */
.answer-display {
  margin-bottom: 1.5rem;
}

.answer-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.answer-box {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  padding: 1rem;
  font-size: 0.875rem;
  color: #111827;
  line-height: 1.6;
  white-space: pre-wrap;
}

.improved-answer-box {
  background: #ecfdf5;
  border: 2px solid #10b981;
  border-radius: 0.5rem;
  padding: 1rem;
  font-size: 0.875rem;
  color: #111827;
  line-height: 1.6;
  white-space: pre-wrap;
  max-height: 300px;
  overflow-y: auto;
}

/* Evaluation Container */
.evaluation-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.quality-score-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.score-green {
  background: #d1fae5;
  border: 3px solid #10b981;
}

.score-yellow {
  background: #fef3c7;
  border: 3px solid #f59e0b;
}

.score-red {
  background: #fee2e2;
  border: 3px solid #ef4444;
}

.score-gray {
  background: #f3f4f6;
  border: 3px solid #9ca3af;
}

.score-number {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
}

.score-max {
  font-size: 1rem;
  color: #6b7280;
}

.score-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

/* Quality Sections */
.quality-section {
  padding: 1rem;
  border-radius: 0.5rem;
  border-left: 4px solid;
}

.strengths {
  background: #ecfdf5;
  border-color: #10b981;
}

.issues {
  background: #fef2f2;
  border-color: #ef4444;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.5rem;
}

.quality-list {
  list-style: disc;
  padding-left: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.quality-list li {
  font-size: 0.875rem;
  color: #374151;
  line-height: 1.5;
}

/* Refinement Form */
.refinement-form {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.refinement-fields {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field-group {
  display: flex;
  flex-direction: column;
}

.field-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.refinement-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  resize: vertical;
  font-family: inherit;
}

.refinement-textarea:focus {
  outline: none;
  border-color: var(--primary-400);
  ring: 2px;
  ring-color: var(--primary-100);
}

.refinement-textarea::placeholder {
  color: #9ca3af;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

/* Dot Navigation */
.dot-navigation {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #d1d5db;
  border: none;
  cursor: pointer;
  transition: all 200ms ease;
  padding: 0;
}

.dot:hover {
  transform: scale(1.1);
  background: #9ca3af;
}

.dot.active {
  width: 12px;
  height: 12px;
  background: var(--primary-400);
}

/* Close Button */
.close-button {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: #6b7280;
  cursor: pointer;
  transition: all 200ms ease;
}

.close-button:hover {
  background: #f3f4f6;
  color: #111827;
}

/* Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 300ms ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .slider-content {
    max-width: 100%;
    height: 85vh;
    max-height: 85vh;
    border-radius: 0.5rem 0.5rem 0 0;
  }

  .slide {
    padding: 1.5rem 1rem;
  }

  .slide-title {
    font-size: 1.25rem;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
