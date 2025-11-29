<template>
  <div
    class="refinement-slide"
    v-motion
    :initial="slideAnimations.slideLeft.value.initial"
    :enter="slideAnimations.slideLeft.value.enter"
    :leave="slideAnimations.slideLeft.value.leave"
  >
    <div v-if="evaluation" class="bg-white  space-y-6">
      <!-- Answer Quality Display with Stagger Animation -->
      <AnswerQualityDisplay
        :generated-answer="evaluation.answer_text"
        :quality-score="evaluation.quality_score"
        :quality-issues="evaluation.quality_issues"
        :quality-strengths="evaluation.quality_strengths"
        :improvement-suggestions="improvementSuggestionsFormatted"
        :is-acceptable="evaluation.is_acceptable"
        :show-refine-button="false"
        @accept-answer="handleAcceptAnswer"
      />

      <!-- Refinement Form (if not acceptable) -->
      <div
        v-if="!evaluation.is_acceptable"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 400 } }"
        class="bg-white"
      >
        <h3 class="text-xl font-semibold text-gray-900 mb-2 flex items-center gap-2">
          Improve Your Answer
        </h3>
        <p class="text-sm text-gray-700 mb-3">
          Answer the questions below to address the specific issues identified in your response:
        </p>

        <!-- Refinement Suggestion Cards with Stagger -->
        <div
          class="space-y-4"
          v-motion
          :enter="{ transition: { staggerChildren: 80, delayChildren: 200 } }"
        >
          <RefinementSuggestionCard
            v-for="(suggestion, index) in evaluation.improvement_suggestions"
            :key="index"
            v-motion
            :initial="{ opacity: 0, x: -20 }"
            :enter="{ opacity: 1, x: 0, transition: { duration: 300 } }"
            :suggestion="suggestion"
            :index="index"
            :model-value="refinementData[`suggestion_${index}`] || ''"
            @update:model-value="updateRefinementField(`suggestion_${index}`, $event)"
            :disabled="isSubmitting"
          />

          <!-- Validation Error Message -->
          <div v-if="validationError" class="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
            <svg class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <p class="text-sm text-red-700">{{ validationError }}</p>
          </div>

          <!-- Submit Button -->
          <div class="flex gap-3 pt-4">
            <HbButton
              @click="handleSubmitRefinement"
              :disabled="isSubmitting || !hasRefinementData"
              :loading="isSubmitting"
              variant="primary"
              size="lg"
              class="flex-1"
            >
              {{ isSubmitting ? 'Submitting Improvements...' : 'Submit Improvements' }}
            </HbButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQuestionsStore } from '~/stores/questions/useQuestionsStore'
import { useSlideAnimations } from '~/composables/animation/useSlideAnimations'
import { useHapticFeedback } from '~/composables/ui/useHapticFeedback'
import type { QuestionItem } from '~/composables/analysis/useAnalysisState'
import AnswerQualityDisplay from '../cards/AnswerQualityDisplay.vue'
import RefinementSuggestionCard from '../forms/RefinementSuggestionCard.vue'

interface Props {
  question: QuestionItem
  evaluation: any | undefined
  isActive: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'submit-refinement': [questionId: string, refinementData: Record<string, any>]
  'accept-answer': [questionId: string]
}>()

const questionsStore = useQuestionsStore()
const slideAnimations = useSlideAnimations()
const { triggerHaptic } = useHapticFeedback()

// Refinement data for this question
const refinementData = ref<Record<string, string>>({})

// Validation error message
const validationError = ref('')

// Submitting state
const isSubmitting = computed(() => {
  return questionsStore.evaluatingQuestionId === props.question.id
})

// Format improvement suggestions for AnswerQualityDisplay
const improvementSuggestionsFormatted = computed(() => {
  if (!props.evaluation?.improvement_suggestions) return []

  return props.evaluation.improvement_suggestions.map((s: string) => ({
    issue: s,
    suggestion: s,
    priority: 'medium'
  }))
})

// Check if ALL refinement fields have been filled
const hasRefinementData = computed(() => {
  // Get total number of refinement fields (based on improvement suggestions)
  const totalFields = props.evaluation?.improvement_suggestions?.length || 0

  // Get filled fields
  const filledFields = Object.values(refinementData.value).filter(v => v && v.trim())

  // All fields must be filled
  return totalFields > 0 && filledFields.length === totalFields
})

// Update refinement field
const updateRefinementField = (field: string, value: string) => {
  // Force reactivity by creating new object
  refinementData.value = {
    ...refinementData.value,
    [field]: value
  }

  // Debug log to verify updates
  console.log('Refinement field updated:', field, value)
  console.log('Current refinementData:', refinementData.value)
  console.log('hasRefinementData:', hasRefinementData.value)

  // Clear validation error when user types
  if (validationError.value) {
    validationError.value = ''
  }
}

// Handle submit refinement
const handleSubmitRefinement = () => {
  // Explicit validation with error message
  if (!hasRefinementData.value) {
    validationError.value = 'Please fill in all refinement fields before submitting.'
    return
  }

  // Clear any previous errors
  validationError.value = ''

  // Trigger haptic feedback
  triggerHaptic('medium')

  // Emit to parent
  emit('submit-refinement', props.question.id, refinementData.value)
}

// Handle accept answer
const handleAcceptAnswer = () => {
  emit('accept-answer', props.question.id)
}
</script>

<style scoped>
.refinement-slide {
  /* Container for refinement content */
}
</style>
