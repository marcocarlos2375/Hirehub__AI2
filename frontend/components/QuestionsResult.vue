<template>
  <div class="space-y-6">
    <!-- Header with Stats -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div class="flex items-center justify-between mb-4">
        <div class="flex-1">
          <h2 class="text-2xl font-bold text-gray-900">Smart Questions</h2>
          <p class="text-sm text-gray-600 mt-1">
            Answer these questions to potentially improve your score by +15-20%
          </p>
        </div>

        <!-- Mode Toggle -->
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2 mr-4">
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                v-model="useAdaptiveMode"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              <span class="ml-3 text-sm font-medium text-gray-700">
                {{ useAdaptiveMode ? 'Adaptive Mode' : 'Traditional Mode' }}
              </span>
            </label>
          </div>

          <div class="text-right">
            <div class="text-3xl font-bold text-indigo-600">
              {{ questionsData.total_questions }}
            </div>
            <div class="text-sm text-gray-600">Questions</div>
          </div>
        </div>
      </div>

      <!-- Stats Row -->
      <div class="grid grid-cols-3 gap-4">
        <div class="text-center p-3 bg-red-50 rounded-lg">
          <div class="text-2xl font-semibold text-red-700">
            {{ questionsData.critical_count }}
          </div>
          <div class="text-xs text-gray-600">Critical</div>
        </div>
        <div class="text-center p-3 bg-orange-50 rounded-lg">
          <div class="text-2xl font-semibold text-orange-700">
            {{ questionsData.high_count }}
          </div>
          <div class="text-xs text-gray-600">High Priority</div>
        </div>
        <div class="text-center p-3 bg-yellow-50 rounded-lg">
          <div class="text-2xl font-semibold text-yellow-700">
            {{ questionsData.medium_count }}
          </div>
          <div class="text-xs text-gray-600">Medium</div>
        </div>
      </div>

      <!-- RAG Context Indicator -->
      <div v-if="questionsData.rag_context_used" class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div class="flex items-center gap-2 text-sm text-blue-800">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span>
            <span class="font-medium">AI-Enhanced:</span> Questions personalized based on similar successful candidates
          </span>
        </div>
      </div>

      <!-- Generation Time -->
      <div class="mt-3 text-xs text-gray-500 text-right">
        Generated in {{ timeSeconds }}s using {{ questionsData.model }}
      </div>

      <!-- Adaptive Mode Info -->
      <div v-if="useAdaptiveMode" class="mt-4 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
        <div class="flex items-start gap-3">
          <svg class="h-5 w-5 text-indigo-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <div class="flex-1">
            <h4 class="font-semibold text-indigo-900 mb-1">Adaptive Mode Active</h4>
            <p class="text-sm text-indigo-800">
              Each question adapts based on your experience level:
            </p>
            <ul class="text-sm text-indigo-700 mt-2 space-y-1 ml-4 list-disc">
              <li><strong>Have experience:</strong> Answer deep-dive questions for a professional resume bullet</li>
              <li><strong>No experience:</strong> Get personalized learning resources and roadmap</li>
              <li><strong>Willing to learn:</strong> Create a learning plan with timeline</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Traditional Mode: Questions List -->
    <div v-if="!useAdaptiveMode" class="space-y-6">
      <QuestionCard
        v-for="question in questionsData.questions"
        :key="question.id"
        :question="question"
      >
        <AnswerInput
          :placeholder="`Share your experience for: ${question.title}`"
          :disabled="isSubmitting || hasSubmitted"
          :submit-button-text="getAnswerStatus(question.id)"
          @submit="(text, type, time) => handleAnswerSubmit(question.id, text, type, time)"
        />
      </QuestionCard>
    </div>

    <!-- Adaptive Mode: Adaptive Question Flows -->
    <div v-else class="space-y-8">
      <div
        v-for="question in questionsData.questions"
        :key="question.id"
        class="bg-white border-2 border-indigo-200 rounded-lg p-6"
      >
        <!-- Question Header -->
        <div class="mb-6">
          <div class="flex items-center gap-3 mb-3">
            <span
              :class="[
                'px-3 py-1 rounded-full text-xs font-bold uppercase',
                question.priority === 'CRITICAL' ? 'bg-red-100 text-red-700' :
                question.priority === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                'bg-yellow-100 text-yellow-700'
              ]"
            >
              {{ question.priority }}
            </span>
            <span class="text-sm font-medium text-gray-500">Impact: {{ question.impact }}</span>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">{{ question.title }}</h3>
          <p class="text-sm text-gray-600">{{ question.context_why }}</p>
        </div>

        <!-- Adaptive Flow Component -->
        <AdaptiveQuestionFlow
          :question-id="question.id"
          :question-text="question.question_text"
          :question-data="question"
          :gap-info="{ title: question.title, description: question.context_why }"
          :user-id="getUserId()"
          :parsed-cv="parsedCV"
          :parsed-jd="parsedJD"
          :language="language"
          @complete="(state) => handleAdaptiveComplete(question.id, state)"
          @cancel="() => {}"
        />
      </div>
    </div>

    <!-- Submit All Button -->
    <div v-if="allQuestionsAnswered && !hasSubmitted" class="sticky bottom-6 z-10">
      <div class="bg-white rounded-lg shadow-lg border-2 border-indigo-500 p-6">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold text-gray-900">
              All Questions Answered!
            </h3>
            <p class="text-sm text-gray-600">
              Ready to analyze your answers and update your score
            </p>
          </div>
          <button
            @click="submitAllAnswers"
            :disabled="isSubmitting"
            class="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="!isSubmitting">Submit All Answers</span>
            <span v-else class="flex items-center gap-2">
              <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Analyzing...
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Results Section (shown after submission) -->
    <div v-if="hasSubmitted && answersResult" class="space-y-6">
      <!-- Score Improvement Banner -->
      <div :class="[
        'rounded-lg shadow-lg p-8 text-center',
        answersResult.score_improvement > 0
          ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white'
          : 'bg-gradient-to-r from-gray-500 to-gray-600 text-white'
      ]">
        <div class="mb-4">
          <div class="text-6xl font-bold mb-2">
            {{ answersResult.updated_score }}
          </div>
          <div class="text-xl font-medium opacity-90">
            New Compatibility Score
          </div>
        </div>

        <div v-if="answersResult.score_improvement > 0" class="flex items-center justify-center gap-2 text-2xl font-semibold">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
          <span>+{{ answersResult.score_improvement }} points!</span>
        </div>
        <div v-else class="text-xl">
          No change detected
        </div>
      </div>

      <!-- Uncovered Experiences -->
      <div v-if="answersResult.uncovered_experiences.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
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
import type { GenerateQuestionsResult, SubmitAnswersResult, QuestionAnswer } from '~/composables/useAnalysisState'
import type { AdaptiveQuestionState } from '~/types/adaptive-questions'
import { useAnswerSubmitter } from '~/composables/useAnswerSubmitter'
import AdaptiveQuestionFlow from './AdaptiveQuestionFlow.vue'

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

const { useAdaptiveFlow } = useAnalysisState()
const useAdaptiveMode = ref(useAdaptiveFlow.value)

// Watch for changes to global adaptive flow setting
watch(useAdaptiveFlow, (newValue) => {
  useAdaptiveMode.value = newValue
})

const answers = ref<Map<string, QuestionAnswer>>(new Map())
const adaptiveResults = ref<Map<string, AdaptiveQuestionState>>(new Map())
const isSubmitting = ref(false)
const hasSubmitted = ref(false)
const answersResult = ref<SubmitAnswersResult | null>(null)

const { submitAnswers: submitAnswersAPI } = useAnswerSubmitter()

const allQuestionsAnswered = computed(() => {
  if (useAdaptiveMode.value) {
    // In adaptive mode, check if all adaptive flows are complete
    return adaptiveResults.value.size === props.questionsData.questions.length
  } else {
    // In traditional mode, check if all questions have answers
    return answers.value.size === props.questionsData.questions.length
  }
})

const getAnswerStatus = (questionId: string): string => {
  if (hasSubmitted.value) return 'Submitted'
  if (answers.value.has(questionId)) return 'Update Answer'
  return 'Submit Answer'
}

const getUserId = (): string => {
  // Generate a session-based user ID
  return `user-${Date.now()}`
}

const handleAnswerSubmit = (
  questionId: string,
  text: string,
  type: 'text' | 'voice',
  transcriptionTime?: number
) => {
  const answer: QuestionAnswer = {
    question_id: questionId,
    answer_text: text,
    answer_type: type,
    transcription_time: transcriptionTime
  }

  answers.value.set(questionId, answer)
}

const handleAdaptiveComplete = (questionId: string, state: AdaptiveQuestionState) => {
  // Store the completed adaptive state
  adaptiveResults.value.set(questionId, state)

  // Convert to traditional answer format for compatibility
  if (state.finalAnswer) {
    const answer: QuestionAnswer = {
      question_id: questionId,
      answer_text: state.finalAnswer,
      answer_type: 'text'
    }
    answers.value.set(questionId, answer)
  }

  console.log(`Adaptive flow completed for question ${questionId}:`, state)
}

const submitAllAnswers = async () => {
  try {
    isSubmitting.value = true

    const answersArray = Array.from(answers.value.values())

    const result = await submitAnswersAPI(
      props.parsedCV,
      props.parsedJD,
      props.questionsData.questions,
      answersArray,
      props.originalScore,
      props.language
    )

    if (result) {
      answersResult.value = result
      hasSubmitted.value = true
      emit('answers-submitted', result, answersArray, result.updated_cv)
    }
  } catch (error: any) {
    alert(error.message || 'Failed to submit answers')
  } finally {
    isSubmitting.value = false
  }
}
</script>
