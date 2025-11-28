<template>
  <div class="questions-wrapper" ref="containerRef">
    <div class="questions-content">
    <!-- Header with Stats (animated with VueUse Motion) -->
    <div
      v-if="currentQuestionStepState === 'initial' && currentQuestionIndex === 0 && showHeader"
      v-motion
      :initial="{ opacity: 1, height: 'auto' }"
      :enter="{ opacity: 1, height: 'auto', transition: { duration: 250 } }"
      :leave="{ opacity: 0, height: 0, transition: { duration: 250 } }"
      class="bg-white overflow-hidden"
    >
      <QuestionsHeader
        :title="`Land your dream job in ${questionsData.total_questions} steps`"
        subtitle="Answer to improve your score by +15-25%"
        :critical-count="questionsData.critical_count"
        :high-count="questionsData.high_count"
        :medium-count="questionsData.medium_count"
      />
    </div>

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
      :showHeader="currentQuestionStepState === 'initial'"
      @update:modelValue="handleStepChange"
      @complete="submitAllAnswers"
    >
      <template #default="{ index }">
        <div class="min-h-[400px]">
          <!-- QuestionSlider with 2 slides (Original + Refinement) -->
          <QuestionSlider
            v-if="currentQuestion"
            :question="currentQuestion"
            :question-index="currentQuestionIndex"
            :is-active="true"
            :parsed-cv="parsedCV"
            :parsed-jd="parsedJD"
            :language="language"
            @need-help="handleNeedHelp"
            @navigate="handleNavigation"
            @submit-all="submitAllAnswers"
            @slide-changed="handleSlideChanged"
            @refinement-submitted="handleRefinementSubmitted"
          />
        </div>
      </template>
    </HbStepper>
    </div>

    <!-- Fixed AnswerInput Footer (animated with VueUse Motion) -->
    <div
      v-if="currentQuestion && !hasSubmitted && !activeAdaptiveFlows.has(currentQuestion.id) && !answerEvaluations.has(currentQuestion.id) && currentQuestionStepState === 'initial'"
      v-motion
      :initial="{ opacity: 1, y: 0 }"
      :enter="{ opacity: 1, y: 0, transition: { duration: 300 } }"
      :leave="{ opacity: 0, y: 20, transition: { duration: 200 } }"
      class="questions-footer"
    >
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

    <!-- Evaluation Loading Overlay -->
    <HbLoadingOverlay
      :show="evaluatingQuestionId === currentQuestion?.id"
      message="Evaluating your answer..."
    />

  </div>
</template>

<script setup lang="ts">
import type { GenerateQuestionsResult, QuestionAnswer, QuestionItem } from '~/composables/analysis/useAnalysisState'
import type { AdaptiveQuestionState, ExperienceLevel } from '~/types/adaptive-questions'
import type { QuestionData } from '~/types/api-responses'
import type { QuestionStepState } from '~/types/question-state'
import { useAnswerSubmitter } from '~/composables/adaptive-questions/useAnswerSubmitter'
import { useAdaptiveQuestions } from '~/composables/adaptive-questions/useAdaptiveQuestions'
import { useQuestionsStore } from '~/stores/questions/useQuestionsStore'
import ExperienceCheckModal from '../modals/ExperienceCheckModal.vue'
import AdaptiveQuestionFlow from './AdaptiveQuestionFlow.vue'
import AnswerQualityDisplay from './AnswerQualityDisplay.vue'
import AnswerInput from './AnswerInput.vue'
import QuestionContextCard from './QuestionContextCard.vue'
import RefinementSuggestionCard from './RefinementSuggestionCard.vue'
import QuestionSlider from './QuestionSlider.vue'
import QuestionsHeader from './QuestionsHeader.vue'
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

// Use Pinia stores
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
const { evaluateAnswer, refineAnswer, formatAnswer } = useAdaptiveQuestions()

const allQuestionsAnswered = computed(() => {
  return questionsStore.allQuestionsAnswered(props.questionsData.questions.length)
})

// Stepper state management
const currentQuestionIndex = ref(0)

// Header visibility control (auto-hide after 3s)
const showHeader = ref(true)


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

const containerRef = ref<HTMLElement | null>(null)

// Keyboard navigation for steps
const handleKeyDown = (event: KeyboardEvent) => {
  // Block navigation if current question is in feedback state
  if (currentQuestionStepState.value === 'feedback') {
    return // Don't allow keyboard navigation in feedback state
  }

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

// Initialize answer drafts and keyboard navigation on mount
onMounted(() => {
  // Initialize answer drafts for all questions
  const questionIds = props.questionsData.questions.map(q => q.id)
  questionsStore.initializeAnswerDrafts(questionIds)

  // Add keyboard navigation
  window.addEventListener('keydown', handleKeyDown)

  // Auto-hide header after 3 seconds
  setTimeout(() => {
    showHeader.value = false
  }, 3000)
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

// Get current question step state (for header visibility)
const currentQuestionStepState = computed<QuestionStepState>(() => {
  if (!currentQuestion.value) return 'initial'
  return questionsStore.getQuestionState(currentQuestion.value.id)
})

// Handle navigation from arrow buttons
const handleNavigation = (direction: 'previous' | 'next') => {
  // Block navigation if current question is in feedback state
  if (currentQuestionStepState.value === 'feedback') {
    return // Don't allow navigation in feedback state
  }

  if (direction === 'previous' && currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  } else if (direction === 'next' && currentQuestionIndex.value < props.questionsData.questions.length - 1) {
    currentQuestionIndex.value++
  }
}

// Handle slide changed event from QuestionSlider
const handleSlideChanged = (questionId: string, slideIndex: number) => {
  console.log(`Slide changed for question ${questionId} to slide ${slideIndex}`)
}

// Handle refinement submitted event from QuestionSlider
const handleRefinementSubmitted = (questionId: string, refinementData: Record<string, any>) => {
  // Delegate to existing submitRefinement function
  submitRefinement(questionId)
}

// Handle step navigation
const handleStepChange = (newIndex: number) => {
  // Block navigation if current question is in feedback state
  if (currentQuestionStepState.value === 'feedback') {
    return // Don't allow step changes in feedback state
  }

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


const handleAnswerSubmit = async (
  questionId: string,
  text: string,
  type: 'text' | 'voice',
  transcriptionTime?: number
) => {
  // Find the question
  const question = props.questionsData.questions.find(q => q.id === questionId)
  if (!question) return

  // Set evaluating state using store
  questionsStore.startEvaluation(questionId)

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

    // Only store answer if evaluation was successful and quality is acceptable
    // User will need to accept the answer before it counts
  } catch (error: any) {
    console.error('Failed to evaluate answer:', error)
    alert('Failed to evaluate answer. Please try again.')
    questionsStore.clearEvaluation()
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

  // Start evaluation using store
  questionsStore.startEvaluation(questionId)

  try {
    // Get question data
    const question = props.questionsData.questions.find(q => q.id === questionId)
    if (!question) {
      alert('Question not found')
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
      evaluation!.quality_issues.map(qi => qi.label),  // Convert objects to strings
      labeledRefinement
    )

    if (response.error) {
      alert('Failed to refine answer: ' + response.error)
      questionsStore.clearEvaluation()
      return
    }

    // Store the refined answer
    const refinedAnswerText = response.refined_answer || evaluation!.answer_text

    // Format the refined answer with AI
    const formattedAnswer = await formatAnswer(
      question.question_text,
      refinedAnswerText,
      { title: question.title, description: question.context_why },
      labeledRefinement,
      props.language
    )

    // Convert formatted answer to readable text
    const formatAnswerToText = (formatted: any): string => {
      let text = `${formatted.name}\n\n`
      if (formatted.description) text += `${formatted.description}\n\n`
      if (formatted.company) text += `Company: ${formatted.company}\n`
      if (formatted.provider) text += `Provider: ${formatted.provider}\n`
      if (formatted.duration) text += `Duration: ${formatted.duration}\n`
      if (formatted.team_size) text += `Team Size: ${formatted.team_size}\n`
      text += `\nKey Achievements:\n`
      formatted.bullet_points.forEach((bullet: string, i: number) => {
        text += `${i + 1}. ${bullet}\n`
      })
      if (formatted.technologies.length > 0) {
        text += `\nTechnologies: ${formatted.technologies.join(', ')}\n`
      }
      if (formatted.skills_gained && formatted.skills_gained.length > 0) {
        text += `\nSkills Gained: ${formatted.skills_gained.join(', ')}\n`
      }
      return text
    }

    const formattedText = formatAnswerToText(formattedAnswer)

    // Store the formatted answer in the store for display
    questionsStore.setImprovedResponse(questionId, formattedText)

    // Update evaluation with refined answer
    if (evaluation) {
      const updatedEvaluation = {
        ...evaluation,
        answer_text: refinedAnswerText,
        quality_score: response.quality_score || evaluation.quality_score,
        is_acceptable: (response.quality_score || 0) >= 7
      }
      questionsStore.setEvaluation(questionId, updatedEvaluation)
    }

    // Increment refinement iteration counter
    questionsStore.incrementRefinementIteration(questionId)

    console.log(`Answer refined and formatted successfully for question ${questionId}`)
  } catch (error: any) {
    console.error('Failed to refine answer:', error)
    alert('Failed to refine answer. Please try again.')
    questionsStore.clearEvaluation()
  } finally {
    questionsStore.clearEvaluation()
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
  padding: 2px;  /* Restore padding (removed from parent .content) */

  /* Add spacing between elements inside */
  > * + * {
    margin-top: 5px;  /* space-y-6 equivalent */
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
