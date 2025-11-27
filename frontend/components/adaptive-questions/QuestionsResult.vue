<template>
  <div class="questions-wrapper" ref="containerRef">
    <div class="questions-content">
    <!-- Header with Stats -->
    <transition name="slide-up">
      <div v-if="!hideHeader" class="bg-white">
        <div class="flex items-center justify-between mb-2">
          <div class="flex-1">
            <h2 class="text-2xl font-bold text-gray-900">Land your dream job in {{ questionsData.total_questions }} steps</h2>
            <p class="text-sm text-gray-600 mt-1">
             Answer to improve your score by +15-25%
            </p>
          </div>

          <div class="text-right">
           <!-- Stats Row -->
        <div class="flex gap-3">
          <div class="flex items-center gap-1.5 px-2 py-1 bg-red-50 rounded-lg">
            <div class="text-lg font-semibold text-red-600">{{ questionsData.critical_count }}</div>
            <div class="text-xs text-red-600">Critical</div>
          </div>
          <div class="flex items-center gap-1.5 px-2 py-1 bg-orange-50 rounded-lg">
            <div class="text-lg font-semibold text-orange-600">{{ questionsData.high_count }}</div>
            <div class="text-xs text-orange-600">High</div>
          </div>
          <div class="flex items-center gap-1.5 px-2 py-1 bg-yellow-50 rounded-lg">
            <div class="text-lg font-semibold text-yellow-600">{{ questionsData.medium_count }}</div>
            <div class="text-xs text-yellow-600">Medium</div>
          </div>
          <!-- Debug button -->
          <button @click="hideHeader = true" class="text-xs px-2 py-1 bg-gray-200 rounded">Hide (test)</button>
        </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Questions Stepper -->
    <HbStepper
      v-model="currentQuestionIndex"
      :steps="questionSteps"
      stepper-type="border"
      transition="slide-fade"
      orientation="horizontal"
      size="md"
      :allowSkip="true"
      :showNavigation="false"
      @update:modelValue="handleStepChange"
      @complete="submitAllAnswers"
    >
      <template #default="{ index }">
        <div class="min-h-[400px]">
          <!-- Get the current question based on index -->
          <div v-if="currentQuestion" class="space-y-4">
            <!-- BEFORE Evaluation: Show Question Context -->
            <QuestionContextCard
              v-if="!activeAdaptiveFlows.has(currentQuestion.id) && !answerEvaluations.has(currentQuestion.id)"
              :question="currentQuestion"
              variant="full"
              :show-impact="true"
              :show-context-why="true"
              :show-examples="true"
              :show-previous="currentQuestionIndex > 0"
              :show-next="currentQuestionIndex < questionsData.questions.length - 1"
              :is-last-question="currentQuestionIndex === questionsData.questions.length - 1"
              :all-answered="allQuestionsAnswered"
              @need-help="handleNeedHelp(currentQuestion)"
              @navigate="handleNavigation"
              @submit-all="submitAllAnswers"
            />


            <!-- AFTER Evaluation: Show Single Tab "Answer Refinement" -->
            <div v-if="answerEvaluations.has(currentQuestion.id)" class="bg-white overflow-hidden">
              

              <!-- Tab Content -->
              <div class="space-y-6">
              
                <!-- Answer Quality Display -->
                <AnswerQualityDisplay
                    :generated-answer="answerEvaluations.get(currentQuestion.id)!.answer_text"
                    :quality-score="answerEvaluations.get(currentQuestion.id)!.quality_score"
                    :quality-issues="answerEvaluations.get(currentQuestion.id)!.quality_issues"
                    :quality-strengths="answerEvaluations.get(currentQuestion.id)!.quality_strengths"
                    :improvement-suggestions="answerEvaluations.get(currentQuestion.id)!.improvement_suggestions.map(s => ({ issue: s, suggestion: s, priority: 'medium' }))"
                    :is-acceptable="answerEvaluations.get(currentQuestion.id)!.is_acceptable"
                    :show-refine-button="false"
                    @accept-answer="handleAcceptAnswer(currentQuestion.id)"
                  />

                <!-- Improvement Questions Section (only if score < 7) -->
                <div v-if="!answerEvaluations.get(currentQuestion.id)!.is_acceptable && refinementData.has(currentQuestion.id)" class="bg-white ">
                  <h3 class="text-xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                   
                   Improve Your Answer
                  </h3>
                  <p class="text-sm text-gray-700 mb-3">
                    Answer the questions below to address the specific issues identified in your response:
                  </p>

                  <div class="space-y-4">
                    <RefinementSuggestionCard
                      v-for="(suggestion, index) in answerEvaluations.get(currentQuestion.id)?.improvement_suggestions || []"
                      :key="index"
                      :suggestion="suggestion"
                      :index="index"
                      :model-value="refinementData.get(currentQuestion.id)?.[`suggestion_${index}`] || ''"
                      @update:model-value="updateRefinementField(currentQuestion.id, `suggestion_${index}`, $event)"
                      :disabled="evaluatingQuestionId === currentQuestion.id"
                    />

                    <div class="flex gap-3 pt-4">
                      <HbButton
                        @click="submitRefinement(currentQuestion.id)"
                        :disabled="evaluatingQuestionId === currentQuestion.id"
                        :loading="evaluatingQuestionId === currentQuestion.id"
                        variant="primary"
                        size="lg"
                        class="flex-1"
                      >
                        
                        {{ evaluatingQuestionId === currentQuestion.id ? 'Submitting Improvements...' : 'Submit Improvements' }}
                      </HbButton>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Evaluation loading now handled by AnswerEvaluationModal -->
            <!-- Adaptive Flow (shown inline after modal choice) -->
            <div v-if="activeAdaptiveFlows.has(currentQuestion.id)" class="ml-4 pl-4 border-l-4 border-indigo-300">
              <AdaptiveQuestionFlow
                :question-id="currentQuestion.id"
                :question-text="currentQuestion.question_text"
                :question-data="currentQuestion"
                :gap-info="{ title: currentQuestion.title, description: currentQuestion.context_why }"
                :user-id="getUserId()"
                :parsed-cv="parsedCV"
                :parsed-jd="parsedJD"
                :language="language"
                :initial-experience-level="activeAdaptiveFlows.get(currentQuestion.id)"
                @complete="(state) => handleAdaptiveComplete(currentQuestion!.id, state)"
                @cancel="() => cancelAdaptiveFlow(currentQuestion!.id)"
              />
            </div>
          </div>

        </div>
      </template>
    </HbStepper>
    </div>

    <!-- Fixed AnswerInput Footer - Only show when answering -->
    <div v-if="currentQuestion && !hasSubmitted && !activeAdaptiveFlows.has(currentQuestion.id) && !answerEvaluations.has(currentQuestion.id)"
         class="questions-footer">
        <AnswerInput
          :modelValue="questionsStore.getAnswerDraft(currentQuestion.id)"
          @update:modelValue="(val) => questionsStore.setAnswerDraft(currentQuestion!.id, val)"
          :question-id="currentQuestion.id"
          :question-text="currentQuestion.question_text"
          :placeholder="`Share your experience for: ${currentQuestion.title}`"
          :disabled="isSubmitting || hasSubmitted || evaluatingQuestionId === currentQuestion.id"
          :submit-button-text="evaluatingQuestionId === currentQuestion.id ? 'Evaluating...' : 'Submit Answer'"
          :show-examples="!!currentQuestion.examples"
          :examples="currentQuestion.examples"
          @submit="(text, type, time) => handleAnswerSubmit(currentQuestion!.id, text, type, time)"
        />
    </div>

    <!-- Adaptive Modal (opens when user clicks "Zero Experience" button) -->
    <ExperienceCheckModal
      v-if="showAdaptiveModal && currentAdaptiveQuestion"
      :gap-title="currentAdaptiveQuestion.title"
      :gap-description="currentAdaptiveQuestion.context_why"
      @experience-selected="handleExperienceSelection"
      @close="closeAdaptiveModal"
    />

    <!-- Results Section (shown after submission) -->
    <div v-if="hasSubmitted && answersResult" class="space-y-6">
      <!-- Score Improvement Banner -->
      <div :class="[
        'rounded-lg shadow-lg p-8 text-center',
        answersResult.score_improvement.absolute_change > 0
          ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white'
          : 'bg-gradient-to-r from-gray-500 to-gray-600 text-white'
      ]">
        <div class="mb-4">
          <div class="text-6xl font-bold mb-2">
            {{ answersResult.score_improvement.after }}
          </div>
          <div class="text-xl font-medium opacity-90">
            New Compatibility Score
          </div>
        </div>

        <div v-if="answersResult.score_improvement.absolute_change > 0" class="flex items-center justify-center gap-2 text-2xl font-semibold">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
          <span>+{{ answersResult.score_improvement.absolute_change }} points!</span>
        </div>
        <div v-else class="text-xl">
          No change detected
        </div>
      </div>

      <!-- Uncovered Experiences -->
      <div v-if="answersResult.uncovered_experiences && answersResult.uncovered_experiences.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Hidden Experience Uncovered
        </h3>
        <ul class="space-y-3">
          <li
            v-for="(experience, index) in answersResult.uncovered_experiences"
            :key="index"
            class="flex items-start gap-3 p-3 bg-green-50 rounded-lg"
          >
            <span class="text-green-600 font-semibold mt-0.5">✓</span>
            <span class="text-gray-800">{{ experience }}</span>
          </li>
        </ul>
      </div>

      <!-- Category Improvements -->
      <div v-if="Object.keys(answersResult.category_improvements).length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">
          Score Improvements by Category
        </h3>
        <div class="grid grid-cols-2 gap-4">
          <div
            v-for="(points, category) in answersResult.category_improvements"
            :key="category"
            class="p-4 bg-gray-50 rounded-lg"
          >
            <div class="text-2xl font-bold text-indigo-600">+{{ points }}</div>
            <div class="text-sm text-gray-600 capitalize">{{ category }}</div>
          </div>
        </div>
      </div>

      <!-- Metadata -->
      <div class="text-xs text-gray-500 text-center">
        Analysis completed in {{ answersResult.time_seconds }}s using {{ answersResult.model }}
      </div>
    </div>

    <!-- Evaluation Loading Box (Centered, Voice-Modal Style) -->
    <Transition name="fade">
      <div v-if="showLoadingBox" class="evaluation-loading-box">
        <HbSpinner size="lg" class="loading-spinner" />
        <p class="loading-text">Evaluating your answer...</p>
        <p v-if="showTimeoutWarning" class="timeout-warning">
          This is taking longer than expected. Please wait...
        </p>
      </div>
    </Transition>

    <!-- Evaluation Slider (2 Slides: Evaluation + Improved Answer) -->
    <Transition name="fade">
      <div v-if="showEvaluationSlider" class="evaluation-slider">
        <div class="slider-container">
          <div
            class="slides-wrapper"
            :style="{ transform: `translateX(-${currentSlide * 100}%)` }"
            @touchstart="handleTouchStart"
            @touchmove="handleTouchMove"
            @touchend="handleTouchEnd"
          >
            <!-- Slide 1: Evaluation + Refinement -->
            <div class="slide">
              <div class="slide-inner">
                <h3 class="slide-title">Answer Evaluation</h3>
                <p class="text-sm text-gray-500 mb-4">Review your answer quality and refine if needed</p>

                <div v-if="currentEvaluation" class="evaluation-container">
                  <!-- Quality Score Badge -->
                  <div class="quality-score-badge">
                    <div :class="['score-circle', scoreColorClass]">
                      <span class="score-number">{{ currentEvaluation.quality_score }}</span>
                      <span class="score-max">/10</span>
                    </div>
                    <p class="score-label">{{ scoreLabel }}</p>
                  </div>

                  <!-- Quality Strengths -->
                  <div v-if="currentEvaluation.quality_strengths?.length" class="quality-section strengths">
                    <h4 class="section-title">✓ Strengths</h4>
                    <ul class="quality-list">
                      <li v-for="(strength, index) in currentEvaluation.quality_strengths" :key="index">
                        {{ strength }}
                      </li>
                    </ul>
                  </div>

                  <!-- Quality Issues -->
                  <div v-if="currentEvaluation.quality_issues?.length" class="quality-section issues">
                    <h4 class="section-title">✗ Areas to Improve</h4>
                    <ul class="quality-list">
                      <li v-for="(issue, index) in currentEvaluation.quality_issues" :key="index">
                        {{ issue }}
                      </li>
                    </ul>
                  </div>

                  <!-- Refinement Form -->
                  <div v-if="!currentEvaluation.is_acceptable" class="refinement-form">
                    <h4 class="form-title">Help us improve your answer:</h4>

                    <div class="form-field">
                      <label>Duration/Timeline Details:</label>
                      <textarea
                        v-model="refinementFields.duration_detail"
                        placeholder="e.g., 'Led this project for 18 months from Jan 2022 to June 2023'"
                        rows="2"
                        :disabled="isRefining"
                      ></textarea>
                    </div>

                    <div class="form-field">
                      <label>Specific Tools/Technologies:</label>
                      <textarea
                        v-model="refinementFields.specific_tools"
                        placeholder="e.g., 'Used React, Node.js, PostgreSQL, Docker, AWS ECS'"
                        rows="2"
                        :disabled="isRefining"
                      ></textarea>
                    </div>

                    <div class="form-field">
                      <label>Metrics/Measurable Outcomes:</label>
                      <textarea
                        v-model="refinementFields.metrics"
                        placeholder="e.g., 'Increased page load speed by 40%, reduced bounce rate from 35% to 18%'"
                        rows="2"
                        :disabled="isRefining"
                      ></textarea>
                    </div>

                    <HbButton
                      variant="primary"
                      @click="handleRefinementSubmit"
                      :disabled="isRefining || !hasRefinementData"
                      class="mt-4"
                    >
                      {{ isRefining ? 'Improving...' : 'Submit Improvements →' }}
                    </HbButton>
                  </div>
                </div>
              </div>
            </div>

            <!-- Slide 2: AI-Improved Response -->
            <div class="slide">
              <div class="slide-inner">
                <h3 class="slide-title">Improved Answer</h3>
                <p class="text-sm text-gray-500 mb-4">AI-enhanced version based on your refinements</p>

                <div class="improved-answer-display">
                  <label class="answer-label">Enhanced Response:</label>
                  <div class="answer-box improved">
                    {{ currentImprovedAnswer }}
                  </div>
                </div>

                <div class="action-buttons">
                  <HbButton
                    variant="secondary"
                    @click="currentSlide = 0"
                  >
                    ← Edit More
                  </HbButton>
                  <HbButton
                    variant="primary"
                    @click="handleUseImprovedAnswer"
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
            v-for="index in 2"
            :key="index"
            :class="['dot', { active: currentSlide === index - 1 }]"
            @click="currentSlide = index - 1"
            :disabled="isRefining"
          ></button>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
import type { GenerateQuestionsResult, QuestionAnswer, QuestionItem } from '~/composables/analysis/useAnalysisState'
import type { AdaptiveQuestionState, ExperienceLevel } from '~/types/adaptive-questions'
import type { QuestionData } from '~/types/api-responses'
import { useAnswerSubmitter } from '~/composables/adaptive-questions/useAnswerSubmitter'
import { useAdaptiveQuestions } from '~/composables/adaptive-questions/useAdaptiveQuestions'
import { useQuestionsStore } from '~/stores/questions/useQuestionsStore'
import ExperienceCheckModal from '../modals/ExperienceCheckModal.vue'
import AdaptiveQuestionFlow from './AdaptiveQuestionFlow.vue'
import AnswerQualityDisplay from './AnswerQualityDisplay.vue'
import AnswerInput from './AnswerInput.vue'
import QuestionContextCard from './QuestionContextCard.vue'
import RefinementSuggestionCard from './RefinementSuggestionCard.vue'
import HbStepper from '~/components/base/HbStepper.vue'
import HbButton from '~/components/base/HbButton.vue'
import HbSpinner from '~/components/base/HbSpinner.vue'

// Import types from store for consistency
import type { AnswerEvaluation, SubmitAnswersResult } from '~/stores/questions/useQuestionsStore'

interface Props {
  questionsData: GenerateQuestionsResult
  parsedCV: any
  parsedJD: any
  originalScore: number
  timeSeconds: number
  language?: string
}

interface Emits {
  (e: 'answers-submitted', result: SubmitAnswersResult, answers: QuestionAnswer[], updatedCV: any): void
}

const props = withDefaults(defineProps<Props>(), {
  language: 'english'
})

const emit = defineEmits<Emits>()

// Use Pinia store instead of local refs
const questionsStore = useQuestionsStore()

// Computed properties from store
const answers = computed(() => questionsStore.answers)
const answerEvaluations = computed(() => questionsStore.answerEvaluations)
const activeAdaptiveFlows = computed(() => questionsStore.activeAdaptiveFlows)
const refinementData = computed(() => questionsStore.refinementData)
const activeQuestionTab = computed(() => questionsStore.activeQuestionTab)
const evaluatingQuestionId = computed(() => questionsStore.evaluatingQuestionId)
const isSubmitting = computed(() => questionsStore.isSubmitting)
const hasSubmitted = computed(() => questionsStore.hasSubmitted)
const answersResult = computed(() => questionsStore.answersResult)
const showAdaptiveModal = computed(() => questionsStore.showAdaptiveModal)
const currentAdaptiveQuestion = computed(() => questionsStore.currentAdaptiveQuestion)

const { submitAnswers: submitAnswersAPI } = useAnswerSubmitter()
const { evaluateAnswer, refineAnswer } = useAdaptiveQuestions()

// Timeout tracking for loading states
const evaluationStartTime = ref<number | null>(null)
const showTimeoutWarning = computed(() => {
  if (!evaluationStartTime.value) return false
  return (Date.now() - evaluationStartTime.value) > 10000 // 10 seconds
})

const allQuestionsAnswered = computed(() => {
  return questionsStore.allQuestionsAnswered(props.questionsData.questions.length)
})

// Stepper state management
const currentQuestionIndex = ref(0)
const currentSlide = ref(0)
const showLoadingBox = ref(false)
const showEvaluationSlider = ref(false)
const refinementFields = ref({
  duration_detail: '',
  specific_tools: '',
  metrics: ''
})
const isRefining = ref(false)
const currentImprovedAnswer = ref('')

// Touch handling for slider
const touchStartX = ref(0)
const touchEndX = ref(0)

const handleTouchStart = (e: TouchEvent) => {
  if (e.changedTouches.length > 0) {
    touchStartX.value = e.changedTouches[0]?.screenX ?? 0
  }
}

const handleTouchMove = (e: TouchEvent) => {
  if (e.changedTouches.length > 0) {
    touchEndX.value = e.changedTouches[0]?.screenX ?? 0
  }
}

const handleTouchEnd = () => {
  if (touchStartX.value - touchEndX.value > 50) {
    // Swipe left
    if (currentSlide.value < 1) currentSlide.value++
  }
  if (touchEndX.value - touchStartX.value > 50) {
    // Swipe right
    if (currentSlide.value > 0) currentSlide.value--
  }
}

// Computed properties for evaluation display
const currentEvaluation = computed(() => {
  if (!currentQuestion.value) return null
  return answerEvaluations.value.get(currentQuestion.value.id)
})

const scoreColorClass = computed(() => {
  const score = currentEvaluation.value?.quality_score || 0
  if (score >= 8) return 'bg-green-100 text-green-800'
  if (score >= 5) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
})

const scoreLabel = computed(() => {
  const score = currentEvaluation.value?.quality_score || 0
  if (score >= 8) return 'Excellent'
  if (score >= 5) return 'Average'
  return 'Needs Improvement'
})

const hasRefinementData = computed(() => {
  return refinementFields.value.duration_detail || refinementFields.value.specific_tools || refinementFields.value.metrics
})

const handleRefinementSubmit = async () => {
  if (!currentQuestion.value) return
  isRefining.value = true
  
  try {
    // Simulate API call or use store action
    await new Promise(resolve => setTimeout(resolve, 1500))
    currentImprovedAnswer.value = "This is a simulated improved answer based on your refinements. It incorporates the details about duration, tools, and metrics you provided."
    currentSlide.value = 1 // Move to improved answer slide
  } catch (e) {
    console.error(e)
  } finally {
    isRefining.value = false
  }
}

const handleUseImprovedAnswer = () => {
  if (!currentQuestion.value) return
  questionsStore.setAnswer(currentQuestion.value.id, currentImprovedAnswer.value, 'text')
  showEvaluationSlider.value = false
}

const questionSteps = computed(() => {
  return props.questionsData.questions.map((q, idx) => ({
    label: `Q${idx + 1}`,
    description: q.title.length > 40 ? q.title.substring(0, 40) + '...' : q.title,
    id: q.id
  }))
})

const currentQuestion = computed(() => {
  return props.questionsData.questions[currentQuestionIndex.value]
})

// Hide header on any user interaction
const hideHeader = ref(false)
const containerRef = ref<HTMLElement | null>(null)

// Simple approach: hide header when user starts answering or after first step
const handleUserInteraction = () => {
  if (!hideHeader.value) {
    console.log('User interaction detected - hiding header')
    hideHeader.value = true
  }
}

// Watch for step changes - hide header after moving past first question
watch(currentQuestionIndex, (newIndex) => {
  if (newIndex > 0) {
    hideHeader.value = true
  }
})

// Keyboard navigation for steps
const handleKeyDown = (event: KeyboardEvent) => {
  // Arrow Right or Arrow Down = Next question
  if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
    if (currentQuestionIndex.value < props.questionsData.questions.length - 1) {
      event.preventDefault()
      currentQuestionIndex.value++
    }
  }
  // Arrow Left or Arrow Up = Previous question
  else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
    if (currentQuestionIndex.value > 0) {
      event.preventDefault()
      currentQuestionIndex.value--
    }
  }
}

// Also hide on mount after a short delay to detect any scroll
onMounted(() => {
  // Initialize answer drafts for all questions
  const questionIds = props.questionsData.questions.map(q => q.id)
  questionsStore.initializeAnswerDrafts(questionIds)

  nextTick(() => {
    console.log('Setting up scroll detection...')

    // Approach 1: Listen to wheel events (mouse scroll) globally
    window.addEventListener('wheel', handleUserInteraction, { once: true, passive: true })
    console.log('Wheel listener attached to window')

    // Approach 2: Listen to any scroll event on document
    document.addEventListener('scroll', handleUserInteraction, { once: true, passive: true })
    console.log('Scroll listener attached to document')

    // Approach 3: Listen on the container
    if (containerRef.value) {
      containerRef.value.addEventListener('wheel', handleUserInteraction, { once: true, passive: true })
      console.log('Wheel listener attached to container')
    }

    // Approach 4: Listen to parent scroll
    const contentParent = document.querySelector('.content')
    if (contentParent) {
      contentParent.addEventListener('scroll', handleUserInteraction, { once: true, passive: true })
      contentParent.addEventListener('wheel', handleUserInteraction, { once: true, passive: true })
      console.log('Scroll and wheel listeners attached to .content parent')
    }

    // Approach 5: Find all scrollable elements
    const allElements = document.querySelectorAll('*')
    allElements.forEach(el => {
      const style = window.getComputedStyle(el)
      if (style.overflowY === 'auto' || style.overflowY === 'scroll') {
        el.addEventListener('scroll', handleUserInteraction, { once: true, passive: true })
        console.log('Scroll listener attached to scrollable element:', el.className)
      }
    })

    // Add keyboard navigation
    window.addEventListener('keydown', handleKeyDown)
    console.log('Keyboard navigation enabled')
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

const currentQuestionState = computed(() => {
  const qId = currentQuestion.value?.id
  if (!qId) return 'unanswered'

  if (activeAdaptiveFlows.value.has(qId)) return 'adaptive'
  if (evaluatingQuestionId.value === qId) return 'evaluating'
  if (answerEvaluations.value.has(qId)) {
    const evaluation = answerEvaluations.value.get(qId)
    return evaluation?.is_acceptable ? 'answered' : 'needs_refinement'
  }
  return 'unanswered'
})

// Handle navigation from arrow buttons
const handleNavigation = (direction: 'previous' | 'next') => {
  if (direction === 'previous' && currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  } else if (direction === 'next' && currentQuestionIndex.value < props.questionsData.questions.length - 1) {
    currentQuestionIndex.value++
  }
}

// Handle step navigation
const handleStepChange = (newIndex: number) => {
  const oldIndex = currentQuestionIndex.value
  const oldQuestion = props.questionsData.questions[oldIndex]

  // Allow backward navigation always
  if (newIndex < oldIndex) {
    currentQuestionIndex.value = newIndex
    return
  }

  // Forward navigation - validate current question is answered
  if (newIndex > oldIndex && oldQuestion) {
    const isAnswered = questionsStore.isQuestionAnswered(oldQuestion.id)
    const isAdaptiveActive = activeAdaptiveFlows.value.has(oldQuestion.id)
    const isEvaluating = evaluatingQuestionId.value === oldQuestion.id

    if (!isAnswered && !isAdaptiveActive && !isEvaluating) {
      // Allow skipping by not blocking navigation
      console.warn('Skipping question:', oldQuestion.id)
    }
  }

  currentQuestionIndex.value = newIndex
}

const getUserId = (): string => {
  // Generate a session-based user ID
  return `user-${Date.now()}`
}

// Helper to convert QuestionItem to QuestionData format
const convertQuestionItemToQuestionData = (question: QuestionItem): QuestionData => {
  return {
    id: question.id,
    text: question.question_text,
    gap_info: {
      title: question.title,
      description: question.context_why,
      category: 'hard_skill', // Default category
      impact: question.priority.toLowerCase() as 'critical' | 'important' | 'nice-to-have'
    },
    context: question.context_why,
    examples: question.examples,
    expected_answer_length: 'medium'
  }
}

const getAnswerStatus = (questionId: string): string => {
  if (hasSubmitted.value) return 'Submitted'
  if (questionsStore.isQuestionAnswered(questionId)) return 'Update Answer'
  return 'Submit Answer'
}

// Tab management helpers - now use store getters/actions
const getActiveTab = (questionId: string): 'original' | 'followup' => {
  return questionsStore.getActiveTab(questionId)
}

const setActiveTab = (questionId: string, tab: 'original' | 'followup') => {
  questionsStore.setActiveTab(questionId, tab)
}

const getFollowupCount = (questionId: string): number => {
  const evaluation = questionsStore.getEvaluationById(questionId)
  if (!evaluation || evaluation.is_acceptable) return 0
  return evaluation.improvement_suggestions?.length || 0
}

const handleAnswerSubmit = async (
  questionId: string,
  text: string,
  type: 'text' | 'voice',
  transcriptionTime?: number
) => {
  // Find the question
  const question = props.questionsData.questions.find(q => q.id === questionId)
  if (!question) return

  // Set evaluating state using store and start timeout tracking
  questionsStore.startEvaluation(questionId)
  evaluationStartTime.value = Date.now()

  try {
    // Call evaluation API
    const evaluation = await evaluateAnswer(
      questionId,
      question.question_text,
      text,
      {
        title: question.title,
        description: question.context_why
      },
      props.language
    )

    // Store evaluation using store action (handles refinement init automatically)
    questionsStore.setEvaluation(questionId, evaluation)

    // Clear the answer draft after successful evaluation
    questionsStore.clearAnswerDraft(questionId)

    // Initialize tab to 'original' when evaluation completes
    questionsStore.setActiveTab(questionId, 'original')

    // Clear timeout tracking
    evaluationStartTime.value = null

    // Only store answer if evaluation was successful and quality is acceptable
    // User will need to accept the answer before it counts
  } catch (error: any) {
    console.error('Failed to evaluate answer:', error)
    alert('Failed to evaluate answer. Please try again.')
    questionsStore.clearEvaluation()
    evaluationStartTime.value = null
  }
}

// Handle "Zero Experience" button click - use store
const handleNeedHelp = (question: QuestionItem) => {
  questionsStore.openAdaptiveModal(question)
}

const closeAdaptiveModal = () => {
  questionsStore.closeAdaptiveModal()
}

// Modal choice handler - unified for all three buttons - use store
const handleExperienceSelection = (level: ExperienceLevel) => {
  if (!questionsStore.currentAdaptiveQuestion) return

  // Start adaptive flow with the selected experience level using store
  questionsStore.startAdaptiveFlow(questionsStore.currentAdaptiveQuestion.id, level)
  questionsStore.closeAdaptiveModal()
}

const cancelAdaptiveFlow = (questionId: string) => {
  questionsStore.completeAdaptiveFlow(questionId)
}

const handleAdaptiveComplete = (questionId: string, state: AdaptiveQuestionState) => {
  // Remove from active flows using store
  questionsStore.completeAdaptiveFlow(questionId)

  // Store the final answer using store
  if (state.finalAnswer) {
    questionsStore.setAnswer(questionId, state.finalAnswer, 'text')
  }

  console.log(`Adaptive flow completed for question ${questionId}:`, state)
}

// Handle accepting an evaluated answer - use store
const handleAcceptAnswer = (questionId: string) => {
  const evaluation = questionsStore.getEvaluationById(questionId)
  if (!evaluation) return

  // Store the accepted answer using store
  questionsStore.setAnswer(questionId, evaluation.answer_text, 'text')
  questionsStore.acceptAnswer(questionId) // Clears refinement data

  console.log(`Answer accepted for question ${questionId}`)
}

// Helper to extract label from suggestion (the part before the colon)
const extractLabelFromSuggestion = (suggestion: string): string => {
  const colonIndex = suggestion.indexOf(':')
  if (colonIndex > 0) {
    return suggestion.substring(0, colonIndex).trim()
  }
  return suggestion.length > 50 ? suggestion.substring(0, 50) + '...' : suggestion
}

const updateRefinementField = (questionId: string, field: string, value: string) => {
  questionsStore.updateRefinementField(questionId, field, value)
}

const submitRefinement = async (questionId: string) => {
  const refinement = questionsStore.getRefinementData(questionId)
  if (!refinement) return

  // Check if user provided any refinement data using store getter
  if (!questionsStore.hasRefinementData(questionId)) {
    alert('Please provide at least one additional detail to improve your answer.')
    return
  }

  // Map suggestion indices to labels for better backend processing
  const evaluation = questionsStore.getEvaluationById(questionId)
  const labeledRefinement: Record<string, string> = {}

  if (evaluation?.improvement_suggestions) {
    evaluation.improvement_suggestions.forEach((suggestion, index) => {
      const key = `suggestion_${index}`
      if (refinement[key] && refinement[key].trim()) {
        const label = extractLabelFromSuggestion(suggestion)
        labeledRefinement[label] = refinement[key]
      }
    })
  }

  // Start evaluation using store and start timeout tracking
  questionsStore.startEvaluation(questionId)
  evaluationStartTime.value = Date.now()

  try {
    // Get question data
    const question = props.questionsData.questions.find(q => q.id === questionId)
    if (!question) {
      alert('Question not found')
      evaluationStartTime.value = null
      return
    }

    // Call refine answer API with labeled data and required context
    const questionData = convertQuestionItemToQuestionData(question)
    const response = await refineAnswer(
      questionId,
      question.question_text,
      questionData,
      { title: question.title, description: question.context_why },
      evaluation!.answer_text,
      evaluation!.quality_issues,
      labeledRefinement
    )

    if (response.error) {
      alert('Failed to refine answer: ' + response.error)
      evaluationStartTime.value = null
      return
    }

    // Update evaluation with refined answer and new score
    if (evaluation) {
      const updatedEvaluation = {
        ...evaluation,
        answer_text: response.refined_answer || evaluation.answer_text,
        quality_score: response.quality_score || evaluation.quality_score,
        is_acceptable: (response.quality_score || 0) >= 7
      }

      // Update the evaluation using store
      questionsStore.setEvaluation(questionId, updatedEvaluation)
    }

    // Increment refinement iteration counter
    questionsStore.incrementRefinementIteration(questionId)

    // Clear timeout tracking
    evaluationStartTime.value = null

    console.log(`Answer refined successfully for question ${questionId}`)
  } catch (error: any) {
    console.error('Failed to refine answer:', error)
    alert('Failed to refine answer. Please try again.')
  } finally {
    questionsStore.clearEvaluation()
    evaluationStartTime.value = null
  }
}

const submitAllAnswers = async () => {
  try {
    // Set submitting state using store
    questionsStore.setSubmitting(true)

    // Get answers array from store
    const answersArray = questionsStore.answersArray

    const result = await submitAnswersAPI(
      props.parsedCV,
      props.parsedJD,
      props.questionsData.questions,
      answersArray,
      props.originalScore,
      props.language
    )

    if (result) {
      // Transform result to match store's expected structure
      const transformedResult: SubmitAnswersResult = {
        success: result.success,
        score_improvement: {
          before: props.originalScore,
          after: result.updated_score,
          absolute_change: result.score_improvement,
          percentage_change: (result.score_improvement / props.originalScore) * 100
        },
        category_improvements: Object.entries(result.category_improvements || {}).map(([category, change]) => ({
          category,
          before: 0, // Not available in old format
          after: 0,  // Not available in old format
          change: change as number
        })),
        uncovered_experiences: result.uncovered_experiences,
        updated_cv: result.updated_cv as any, // Type assertion needed due to legacy API format
        time_seconds: result.time_seconds,
        model: result.model
      }

      // Store results using store action
      questionsStore.setAnswersResult(transformedResult)
      emit('answers-submitted', transformedResult, answersArray, result.updated_cv as any)
    }
  } catch (error: any) {
    alert(error.message || 'Failed to submit answers')
    questionsStore.setSubmitting(false)
  }
}
</script>

<style scoped>
.slide-up-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 1, 1);
}

.slide-up-enter-from {
  transform: translateY(-30px);
  opacity: 0;
  margin-bottom: -100px;
}

.slide-up-leave-to {
  transform: translateY(-30px);
  opacity: 0;
  margin-bottom: -100px;
}

.slide-up-enter-to,
.slide-up-leave-from {
  transform: translateY(0);
  opacity: 1;
  margin-bottom: 0;
}

/* Flex container matching jetable.vue pattern */
.questions-wrapper {
  display: flex;
  flex-direction: column;
  height: 85vh;      /* Exact height constraint */
  max-height: 85vh;  /* Prevent overflow */
}

/* Scrollable content area */
.questions-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;  /* Restore padding (removed from parent .content) */

  /* Add spacing between elements inside */
  > * + * {
    margin-top: 1.5rem;  /* space-y-6 equivalent */
  }
}

/* Footer - Desktop (static positioning) */
.questions-footer {
  display: flex;
  flex-direction: column;
  padding: 1rem 0;
  margin-bottom: 1.5rem;  /* Add spacing from bottom edge */
  background-color: white;
  flex-shrink: 0;
  width: 100%;
}

/* Footer - Mobile (fixed positioning) */
@media (max-width: 768px) {
  .questions-content {
    padding-bottom: 80px;  /* Reserve space for fixed footer */
  }

  .questions-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 1rem;
    z-index: 50;
  }
}
</style>
