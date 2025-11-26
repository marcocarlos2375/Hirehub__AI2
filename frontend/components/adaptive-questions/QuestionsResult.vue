<template>
  <div class="space-y-6" ref="containerRef">
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
      orientation="horizontal"
      size="md"
      :allowSkip="true"
      :showNavigation="true"
      nextLabel="Next Question"
      backLabel="Previous"
      finishLabel="Submit All Answers"
      @update:modelValue="handleStepChange"
      @complete="submitAllAnswers"
    >
      <template #default="{ index }">
        <div class="min-h-[400px]">
          <!-- Get the current question based on index -->
          <div v-if="currentQuestion" class="space-y-4">
            <!-- BEFORE Evaluation: Show QuestionCard with AnswerInput -->
            <QuestionCard
              v-if="!activeAdaptiveFlows.has(currentQuestion.id) && !answerEvaluations.has(currentQuestion.id)"
              :question="currentQuestion"
              @need-help="handleNeedHelp(currentQuestion)"
            >
              <AnswerInput
                :modelValue="questionsStore.getAnswerDraft(currentQuestion!.id)"
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
            </QuestionCard>

            <!-- AFTER Evaluation: Show Single Tab "Answer Refinement" -->
            <div v-if="answerEvaluations.has(currentQuestion.id)" class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
              <!-- Tab Header -->
              <div class="flex gap-2 border-b border-gray-200 bg-gray-50 px-4">
                <div class="px-4 py-3 font-medium text-sm text-green-600 border-b-2 border-green-600 bg-white">
                  ✨ Answer Refinement
                </div>
              </div>

              <!-- Tab Content -->
              <div class="p-6 space-y-6">
                <!-- Question Context -->
                <div class="bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-200 rounded-lg p-5">
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex-1">
                      <div class="flex items-center gap-3 mb-2">
                        <span class="text-sm font-semibold text-gray-500">Q{{ currentQuestion.number }}</span>
                        <span
                          :class="[
                            'px-2.5 py-0.5 rounded-full text-xs font-medium',
                            currentQuestion.priority === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                            currentQuestion.priority === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                            currentQuestion.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          ]"
                        >
                          {{ currentQuestion.priority }}
                        </span>
                        <span class="text-xs text-green-600 font-medium">
                          {{ currentQuestion.impact }}
                        </span>
                      </div>
                      <h3 class="text-lg font-semibold text-gray-900 mb-2">
                        {{ currentQuestion.title }}
                      </h3>
                      <p class="text-sm text-gray-700 leading-relaxed">
                        {{ currentQuestion.question_text }}
                      </p>
                    </div>
                  </div>
                </div>

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
                <div v-if="!answerEvaluations.get(currentQuestion.id)!.is_acceptable && refinementData.has(currentQuestion.id)" class="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-300 rounded-lg p-6">
                  <h3 class="text-xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                    <svg class="h-6 w-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                   Improve Your Answer
                  </h3>
                  <p class="text-sm text-gray-700 mb-6">
                    Answer the questions below to address the specific issues identified in your response:
                  </p>

                  <div class="space-y-4">
                    <div
                      v-for="(suggestion, index) in answerEvaluations.get(currentQuestion.id)?.improvement_suggestions || []"
                      :key="index"
                      :class="[
                        'p-5 rounded-lg border shadow-sm transition-all',
                        getSuggestionPriorityClass(suggestion, index)
                      ]"
                    >
                      <div class="flex items-start gap-3 mb-3">
                        <span :class="[
                          'inline-flex items-center justify-center w-7 h-7 rounded-full font-bold text-sm flex-shrink-0',
                          getSuggestionBadgeClass(suggestion, index)
                        ]">
                          {{ index + 1 }}
                        </span>
                        <div class="flex-1">
                          <p class="text-sm text-gray-800 mb-1">
                            {{ getSuggestionPriorityIcon(suggestion, index) }}
                            <span class="font-medium">{{ extractSuggestionTitle(suggestion) }}</span>
                          </p>
                          <p class="text-xs text-gray-600">{{ extractSuggestionDetail(suggestion) }}</p>
                        </div>
                      </div>
                      <textarea
                        v-model="refinementData.get(currentQuestion.id)![`suggestion_${index}`]"
                        :placeholder="getSuggestionPlaceholder(suggestion, index)"
                        :rows="getSuggestionRows(suggestion)"
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-vertical text-sm"
                        @input="updateRefinementField(currentQuestion.id, `suggestion_${index}`, ($event.target as HTMLTextAreaElement).value)"
                      ></textarea>
                      <div class="mt-2 flex items-center justify-between text-xs text-gray-500">
                        <span>
                          {{ (refinementData.get(currentQuestion.id)?.[`suggestion_${index}`] || '').length }} characters
                        </span>
                        <span v-if="(refinementData.get(currentQuestion.id)?.[`suggestion_${index}`] || '').length < 20" class="text-amber-600">
                          Add more details (min 20 chars)
                        </span>
                        <span v-else class="text-green-600">
                          Good detail level
                        </span>
                      </div>
                    </div>

                    <div class="flex gap-3 pt-4">
                      <HbButton
                        @click="submitRefinement(currentQuestion.id)"
                        :disabled="evaluatingQuestionId === currentQuestion.id"
                        :loading="evaluatingQuestionId === currentQuestion.id"
                        variant="secondary"
                        size="lg"
                        class="flex-1"
                      >
                        <template #leading-icon>
                          <svg v-if="!evaluatingQuestionId" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </template>
                        {{ evaluatingQuestionId === currentQuestion.id ? 'Submitting Improvements...' : 'Submit Improvements' }}
                      </HbButton>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Evaluation Loading with Enhanced UI -->
            <div v-if="evaluatingQuestionId === currentQuestion.id" class="ml-4 pl-4 border-l-4 border-blue-300">
              <div class="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
                <!-- Main Loading Message -->
                <div class="flex items-center gap-3 mb-4">
                  <HbSpinner size="lg" />
                  <div class="flex-1">
                    <h4 class="font-semibold text-gray-900 flex items-center gap-2">
                      <span>Evaluating Your Answer</span>
                      <span class="animate-pulse">...</span>
                    </h4>
                    <p class="text-sm text-gray-600">AI is analyzing quality and generating feedback</p>
                  </div>
                </div>

                <!-- Timeout Warning (if taking longer than 10s) -->
                <div v-if="showTimeoutWarning" class="mb-4 p-3 bg-yellow-50 border border-yellow-300 rounded-lg">
                  <div class="flex items-start gap-2">
                    <svg class="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <div class="flex-1">
                      <p class="text-sm font-medium text-yellow-800">This is taking longer than usual</p>
                      <p class="text-xs text-yellow-700 mt-1">The AI is conducting a thorough analysis. Please wait a moment longer.</p>
                    </div>
                  </div>
                </div>

                <!-- Progress Steps -->
                <div class="space-y-2 pl-13">
                  <div class="flex items-center gap-2 text-sm">
                    <div class="w-4 h-4 rounded-full bg-green-500 flex items-center justify-center text-white text-xs">✓</div>
                    <span class="text-gray-700">Answer received</span>
                  </div>
                  <div class="flex items-center gap-2 text-sm">
                    <div class="w-4 h-4 rounded-full bg-blue-500 animate-pulse"></div>
                    <span class="text-gray-700 font-medium">Analyzing content...</span>
                  </div>
                  <div class="flex items-center gap-2 text-sm text-gray-400">
                    <div class="w-4 h-4 rounded-full border-2 border-gray-300"></div>
                    <span>Generating improvements</span>
                  </div>
                </div>

                <!-- Skeleton Loader for Expected Output -->
                <div class="mt-4 pt-4 border-t border-blue-200">
                  <div class="space-y-3 animate-pulse">
                    <div class="h-4 bg-blue-200 rounded w-3/4"></div>
                    <div class="h-4 bg-blue-200 rounded w-1/2"></div>
                    <div class="h-4 bg-blue-200 rounded w-5/6"></div>
                  </div>
                </div>
              </div>
            </div>

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
  </div>
</template>

<script setup lang="ts">
import type { GenerateQuestionsResult, QuestionAnswer, QuestionItem } from '~/composables/analysis/useAnalysisState'
import type { AdaptiveQuestionState, ExperienceLevel } from '~/types/adaptive-questions'
import { useAnswerSubmitter } from '~/composables/adaptive-questions/useAnswerSubmitter'
import { useQuestionsStore } from '~/stores/questions/useQuestionsStore'
import ExperienceCheckModal from '../modals/ExperienceCheckModal.vue'
import AdaptiveQuestionFlow from './AdaptiveQuestionFlow.vue'
import AnswerQualityDisplay from './AnswerQualityDisplay.vue'
import AnswerInput from './AnswerInput.vue'
import QuestionCard from './QuestionCard.vue'

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

const questionSteps = computed(() => {
  return props.questionsData.questions.map((q, idx) => ({
    title: `Q${idx + 1}`,
    description: q.title.length > 40 ? q.title.substring(0, 40) + '...' : q.title
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

// Dynamic refinement UI helpers
const getSuggestionPriorityClass = (suggestion: string, index: number): string => {
  // Determine priority from suggestion text or position (first = critical, last = nice-to-have)
  const suggestionLower = suggestion.toLowerCase()

  if (suggestionLower.includes('critical') || suggestionLower.includes('must') || suggestionLower.includes('required')) {
    return 'bg-red-50 border-red-300'
  } else if (suggestionLower.includes('important') || suggestionLower.includes('should') || index === 0) {
    return 'bg-orange-50 border-orange-300'
  } else {
    return 'bg-white border-gray-200'
  }
}

const getSuggestionBadgeClass = (suggestion: string, index: number): string => {
  const suggestionLower = suggestion.toLowerCase()

  if (suggestionLower.includes('critical') || suggestionLower.includes('must') || suggestionLower.includes('required')) {
    return 'bg-red-100 text-red-700'
  } else if (suggestionLower.includes('important') || suggestionLower.includes('should') || index === 0) {
    return 'bg-orange-100 text-orange-700'
  } else {
    return 'bg-amber-100 text-amber-700'
  }
}

const getSuggestionPriorityIcon = (suggestion: string, index: number): string => {
  const suggestionLower = suggestion.toLowerCase()

  if (suggestionLower.includes('critical') || suggestionLower.includes('must') || suggestionLower.includes('required')) {
    return '🔴'
  } else if (suggestionLower.includes('important') || suggestionLower.includes('should') || index === 0) {
    return '🟠'
  } else {
    return '💡'
  }
}

const extractSuggestionTitle = (suggestion: string): string => {
  // Extract title before first colon or period
  const colonIndex = suggestion.indexOf(':')
  const periodIndex = suggestion.indexOf('.')

  if (colonIndex > 0 && colonIndex < 80) {
    return suggestion.substring(0, colonIndex).trim()
  } else if (periodIndex > 0 && periodIndex < 80) {
    return suggestion.substring(0, periodIndex).trim()
  }

  return suggestion.length > 60 ? suggestion.substring(0, 60) + '...' : suggestion
}

const extractSuggestionDetail = (suggestion: string): string => {
  // Extract detail after first colon or period
  const colonIndex = suggestion.indexOf(':')
  const periodIndex = suggestion.indexOf('.')

  if (colonIndex > 0 && colonIndex < 80) {
    return suggestion.substring(colonIndex + 1).trim()
  } else if (periodIndex > 0 && periodIndex < 80) {
    return suggestion.substring(periodIndex + 1).trim()
  }

  return ''
}

const getSuggestionPlaceholder = (suggestion: string, index: number): string => {
  const title = extractSuggestionTitle(suggestion)
  return `Provide specific details about ${title.toLowerCase()}...`
}

const getSuggestionRows = (suggestion: string): number => {
  // More rows for complex suggestions
  const suggestionLower = suggestion.toLowerCase()

  if (suggestionLower.includes('example') || suggestionLower.includes('detail') || suggestionLower.includes('explain')) {
    return 4
  } else if (suggestionLower.includes('specific') || suggestionLower.includes('describe')) {
    return 3
  } else {
    return 2
  }
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
    const response = await refineAnswer(
      questionId,
      question.question_text,
      question,
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
        updated_cv: result.updated_cv,
        time_seconds: result.time_seconds,
        model: result.model
      }

      // Store results using store action
      questionsStore.setAnswersResult(transformedResult)
      emit('answers-submitted', transformedResult, answersArray, result.updated_cv)
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
</style>
