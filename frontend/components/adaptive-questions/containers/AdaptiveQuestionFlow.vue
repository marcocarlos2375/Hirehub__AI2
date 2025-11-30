<template>
  <div class="space-y-6">
    <!-- Experience Check Modal -->
    <ExperienceCheckModal
      v-if="showExperienceModal"
      :gap-title="gapInfo.title"
      :gap-description="gapInfo.description"
      @experience-selected="handleExperienceSelection"
      @close="$emit('cancel')"
    />

    <!-- Loading State -->
    <HbCard v-if="state.loading && !showExperienceModal" class="p-12">
      <div class="flex flex-col items-center justify-center">
        <HbSpinner size="xl" />
        <h3 class="text-lg font-semibold text-gray-900 mt-4 mb-2">{{ loadingMessage }}</h3>
        <p class="text-sm text-gray-600">This may take a few seconds...</p>
      </div>
    </HbCard>

    <!-- Error State -->
    <div v-if="state.error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <div class="flex items-start gap-3">
        <svg class="h-6 w-6 text-red-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <div class="flex-1">
          <h3 class="font-bold text-gray-900 mb-1">Error</h3>
          <p class="text-sm text-gray-700">{{ state.error }}</p>
        </div>
        <HbButton
          @click="resetFlow"
          variant="danger"
          size="sm"
        >
          Try Again
        </HbButton>
      </div>
    </div>

    <!-- Deep Dive Path: Form -->
    <DeepDiveForm
      v-if="state.currentStep === 'deep_dive' && state.deepDivePrompts"
      :prompts="state.deepDivePrompts"
      :loading="state.loading"
      @submit-inputs="handleDeepDiveSubmit"
    />

    <!-- Deep Dive Path: Quality Evaluation -->
    <!-- Refinement Slider (replaces quality_eval step when score < 7) -->
    <RefinementSlider
      v-if="state.currentStep === 'quality_eval' && state.generatedAnswer && (state.qualityScore || 0) < 7"
      :generated-answer="state.generatedAnswer"
      :quality-score="state.qualityScore || 0"
      :quality-issues="state.qualityIssues"
      :quality-strengths="state.qualityStrengths"
      @submit-refinement="handleRefinementSubmit"
    />

    <!-- Quality Evaluation (only shown if score >= 7) -->
    <AnswerQualityDisplay
      v-if="state.currentStep === 'quality_eval' && state.generatedAnswer && (state.qualityScore || 0) >= 7"
      :generated-answer="state.generatedAnswer"
      :quality-score="state.qualityScore || 0"
      :quality-issues="state.qualityIssues"
      :quality-strengths="state.qualityStrengths"
      :improvement-suggestions="state.improvementSuggestions"
      :is-acceptable="true"
      :show-refine-button="false"
      @accept-answer="handleAcceptAnswer"
    />

    <!-- Black Loading Overlay -->
    <HbLoadingOverlay
      :show="showRefinementLoading"
      message="Formatting your professional answer..."
      text-size="xl"
    />

    <!-- Learning Path: Resources Display -->
    <div v-if="state.currentStep === 'resources' && state.suggestedResources">
      <LearningResourcesDisplay
        :resources="state.suggestedResources"
        :resume-addition="state.resumeAddition"
        :loading="state.loading"
        v-model="state.selectedResourceIds"
        @save-plan="handleSaveLearningPlan"
      />

      <!-- Timeline (shown after resources are selected) -->
      <LearningTimeline
        v-if="state.selectedResourceIds && state.selectedResourceIds.length > 0 && state.timeline"
        :timeline="state.timeline"
        :estimated-completion="calculateEstimatedCompletion()"
        class="mt-6"
      />
    </div>

    <!-- Completion State -->
    <div v-if="state.currentStep === 'complete'" class="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-lg p-8">
      <div class="text-center">
        <div class="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-2">Workflow Complete!</h3>
        <p class="text-gray-700 mb-6">
          {{ state.finalAnswer
            ? 'Your professional answer has been generated and is ready to add to your resume.'
            : 'Your learning plan has been saved successfully.'
          }}
        </p>

        <!-- Final Answer (if applicable) -->
        <div v-if="state.finalAnswer" class="bg-white rounded-lg p-6 border border-green-200 mb-6 text-left">
          <h4 class="font-bold text-gray-900 mb-3 flex items-center gap-2">
            <svg class="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Final Answer for Your Resume
          </h4>
          <p class="text-gray-800 whitespace-pre-wrap">{{ state.finalAnswer }}</p>
        </div>

        <HbButton
          @click="$emit('complete', state)"
          variant="primary"
          size="lg"
        >
          Continue
        </HbButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {
  ExperienceLevel,
  WorkflowStep,
  DeepDivePrompt,
  LearningResource,
  TimelineStep,
  QualityEvaluation,
  AdaptiveQuestionState,
  FormattedAnswer
} from '~/types/adaptive-questions'
import type { QuestionData, GapInfo, ParsedCV, ParsedJobDescription } from '~/types/api-responses'

import ExperienceCheckModal from '../../modals/ExperienceCheckModal.vue'
import DeepDiveForm from '../forms/DeepDiveForm.vue'
import AnswerQualityDisplay from '../cards/AnswerQualityDisplay.vue'
import RefinementSlider from '../sliders/RefinementSlider.vue'
import LearningResourcesDisplay from '../../learning/LearningResourcesDisplay.vue'
import LearningTimeline from '../../learning/LearningTimeline.vue'

interface Props {
  questionId: string
  questionText: string
  questionData: Record<string, any>
  gapInfo: {
    title: string
    description: string
    priority?: string  // Gap priority: CRITICAL, HIGH, IMPORTANT, MEDIUM, NICE_TO_HAVE, LOW, LOGISTICAL
  }
  userId: string
  parsedCv: Record<string, any>
  parsedJd: Record<string, any>
  language?: string
  initialExperienceLevel?: ExperienceLevel | null
}

const props = withDefaults(defineProps<Props>(), {
  language: 'english',
  initialExperienceLevel: null
})

const emit = defineEmits<{
  complete: [state: AdaptiveQuestionState]
  cancel: []
}>()

const { startAdaptiveQuestion, submitStructuredInputs, refineAnswer, saveLearningPlan, formatAnswer } = useAdaptiveQuestions()

// State
const showExperienceModal = ref(!props.initialExperienceLevel)
const showRefinementDialog = ref(false)
const showRefinementLoading = ref(false)
const refinementData = ref<Record<string, any>>({
  duration_detail: '',
  specific_tools: '',
  metrics: ''
})

const state = ref<AdaptiveQuestionState>({
  questionId: props.questionId,
  gapTitle: props.gapInfo.title,
  gapDescription: props.gapInfo.description,
  experienceCheck: null,
  currentStep: 'check',
  refinementIteration: 0,
  loading: false,
  selectedResourceIds: []
})

// Computed
const loadingMessage = computed(() => {
  switch (state.value.currentStep) {
    case 'check': return 'Generating personalized questions...'
    case 'deep_dive': return 'Generating professional answer...'
    case 'quality_eval': return 'Evaluating answer quality...'
    case 'resources': return 'Finding learning resources...'
    default: return 'Processing...'
  }
})

const hasRefinementData = computed(() => {
  return Object.values(refinementData.value).some(v => v && v.trim())
})

// Helper function to convert FormattedAnswer to display text
const formatAnswerToText = (formatted: FormattedAnswer): string => {
  let text = `${formatted.name}\n\n`

  if (formatted.description) text += `${formatted.description}\n\n`

  // Metadata
  if (formatted.company) text += `Company: ${formatted.company}\n`
  if (formatted.provider) text += `Provider: ${formatted.provider}\n`
  if (formatted.duration) text += `Duration: ${formatted.duration}\n`
  if (formatted.team_size) text += `Team Size: ${formatted.team_size}\n`

  text += `\nKey Achievements:\n`
  formatted.bullet_points.forEach((bullet, i) => {
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

// Methods
const handleExperienceSelection = async (level: ExperienceLevel) => {
  showExperienceModal.value = false
  state.value.experienceCheck = level
  state.value.loading = true

  try {
    const response = await startAdaptiveQuestion(
      props.questionId,
      props.questionText,
      props.questionData as QuestionData,
      props.gapInfo as GapInfo,
      props.userId,
      props.parsedCv as ParsedCV,
      props.parsedJd as ParsedJobDescription,
      level,
      props.language
    )

    if (response.error) {
      state.value.error = response.error
      return
    }

    state.value.currentStep = response.current_step as WorkflowStep

    if (response.deep_dive_prompts) {
      state.value.deepDivePrompts = response.deep_dive_prompts as DeepDivePrompt[]
    }

    if (response.suggested_resources) {
      state.value.suggestedResources = response.suggested_resources as LearningResource[]
      state.value.resumeAddition = response.resume_addition
      // Generate timeline for all resources initially
      generateTimeline(response.suggested_resources.map(r => r.id))
    }
  } catch (error: any) {
    state.value.error = error.message || 'Failed to start adaptive workflow'
  } finally {
    state.value.loading = false
  }
}

const handleDeepDiveSubmit = async (data: Record<string, any>) => {
  state.value.loading = true
  state.value.deepDiveData = data

  try {
    const response = await submitStructuredInputs(props.questionId, data)

    if (response.error) {
      state.value.error = response.error
      return
    }

    state.value.generatedAnswer = response.generated_answer
    state.value.qualityScore = response.quality_score
    state.value.qualityIssues = response.quality_issues
    state.value.qualityStrengths = response.quality_strengths
    state.value.improvementSuggestions = response.improvement_suggestions

    if (response.final_answer) {
      state.value.finalAnswer = response.final_answer
      state.value.currentStep = 'complete'
    } else {
      state.value.currentStep = 'quality_eval'
    }
  } catch (error: any) {
    state.value.error = error.message || 'Failed to generate answer'
  } finally {
    state.value.loading = false
  }
}

const showRefinementPrompt = () => {
  showRefinementDialog.value = true
  refinementData.value = {
    duration_detail: '',
    specific_tools: '',
    metrics: ''
  }
}

const cancelRefinement = () => {
  showRefinementDialog.value = false
}

const submitRefinement = async () => {
  if (!hasRefinementData.value || !state.value.generatedAnswer || !state.value.qualityIssues) return

  state.value.loading = true
  showRefinementDialog.value = false

  try {
    const response = await refineAnswer(
      props.questionId,
      props.questionText,
      props.questionData as QuestionData,
      props.gapInfo as { title: string; description: string },
      state.value.generatedAnswer,
      state.value.qualityIssues,
      refinementData.value
    )

    if (response.error) {
      state.value.error = response.error
      return
    }

    state.value.generatedAnswer = response.refined_answer
    state.value.qualityScore = response.quality_score ?? undefined
    state.value.refinementIteration = response.iteration

    // With new flow, refinement always completes the workflow
    state.value.finalAnswer = response.refined_answer
    state.value.currentStep = 'complete'
  } catch (error: any) {
    state.value.error = error.message || 'Failed to refine answer'
  } finally {
    state.value.loading = false
  }
}

const handleRefinementSubmit = async (refinementData: Record<string, any>) => {
  if (!state.value.generatedAnswer || !state.value.qualityIssues) return

  // Show black loading overlay
  showRefinementLoading.value = true

  try {
    // Step 1: Refine the answer
    const response = await refineAnswer(
      props.questionId,
      props.questionText,
      props.questionData as QuestionData,
      props.gapInfo as { title: string; description: string },
      state.value.generatedAnswer,
      state.value.qualityIssues,
      refinementData
    )

    if (response.error) {
      state.value.error = response.error
      showRefinementLoading.value = false
      return
    }

    // Store the AI-rewritten answer
    const rewrittenAnswer = response.refined_answer
    state.value.generatedAnswer = rewrittenAnswer

    // Step 2: Format the answer with AI
    const formattedAnswer = await formatAnswer(
      props.questionText,
      rewrittenAnswer,
      props.gapInfo as { title: string; description: string },
      refinementData,
      props.language
    )

    // Store formatted answer in state
    state.value.formattedAnswer = formattedAnswer

    // Convert to readable text for display
    const formattedText = formatAnswerToText(formattedAnswer)

    // Hide loading overlay
    showRefinementLoading.value = false

    // Complete the workflow with formatted answer
    state.value.refinementIteration = 1  // Mark as refined (blocks further refinement)
    state.value.finalAnswer = formattedText
    state.value.currentStep = 'complete'

  } catch (error: any) {
    state.value.error = error.message || 'Failed to refine answer'
    showRefinementLoading.value = false
  }
}

const handleAcceptAnswer = (answer: string) => {
  state.value.finalAnswer = answer
  state.value.currentStep = 'complete'
}

const generateTimeline = (resourceIds: string[]) => {
  if (!state.value.suggestedResources) return

  const selected = state.value.suggestedResources.filter(r => resourceIds.includes(r.id))
  let currentDay = 1
  const timeline: TimelineStep[] = []

  selected.forEach(resource => {
    timeline.push({
      resource_id: resource.id,
      resource_title: resource.title,
      type: resource.type,
      start_day: currentDay,
      end_day: currentDay + resource.duration_days - 1,
      duration_days: resource.duration_days
    })
    currentDay += resource.duration_days
  })

  state.value.timeline = timeline
}

// Watch for selected resources changes to update timeline
watch(() => state.value.selectedResourceIds, (newIds) => {
  if (newIds && newIds.length > 0) {
    generateTimeline(newIds)
  } else {
    state.value.timeline = []
  }
}, { deep: true })

const calculateEstimatedCompletion = () => {
  if (!state.value.timeline || state.value.timeline.length === 0) return ''

  const totalDays = Math.max(...state.value.timeline.map(step => step.end_day))
  const weeks = Math.floor(totalDays / 7)
  const days = totalDays % 7

  if (weeks > 0 && days > 0) return `~${weeks} weeks ${days} days`
  if (weeks > 0) return `~${weeks} week${weeks !== 1 ? 's' : ''}`
  return `${days} day${days !== 1 ? 's' : ''}`
}

const handleSaveLearningPlan = async (resourceIds: string[]) => {
  state.value.loading = true

  try {
    const response = await saveLearningPlan(
      props.userId,
      props.gapInfo as GapInfo,
      resourceIds,
      `Learning plan for ${props.gapInfo.title}`
    )

    if (response.error) {
      state.value.error = response.error
      return
    }

    state.value.planId = response.plan_id
    state.value.currentStep = 'complete'
  } catch (error: any) {
    state.value.error = error.message || 'Failed to save learning plan'
  } finally {
    state.value.loading = false
  }
}

const resetFlow = () => {
  showExperienceModal.value = true
  state.value = {
    questionId: props.questionId,
    gapTitle: props.gapInfo.title,
    gapDescription: props.gapInfo.description,
    experienceCheck: null,
    currentStep: 'check',
    refinementIteration: 0,
    loading: false,
    selectedResourceIds: []
  }
}

// Auto-start workflow if initialExperienceLevel is provided
onMounted(() => {
  if (props.initialExperienceLevel) {
    handleExperienceSelection(props.initialExperienceLevel)
  }
})
</script>

<style scoped>
/* Styles removed - using HbLoadingOverlay component */
</style>
