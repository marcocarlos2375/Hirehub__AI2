<template>
  <div class="refinement-slider">
    <HbSlider
      mode="carousel"
      v-model="currentSlide"
      :loop="false"
      :showArrows="false"
      dotPosition="bottom"
      dotAlignment="center"
      :swipeable="false"
    >
      <!-- Slide 1: Quality Evaluation -->
      <div class="slide">
        <AnswerQualityDisplay
          :generated-answer="generatedAnswer"
          :quality-score="qualityScore"
          :quality-issues="qualityIssues"
          :quality-strengths="qualityStrengths"
          :is-acceptable="false"
          :show-refine-button="false"
        />
        <div class="flex justify-end mt-4">
          <HbButton @click="nextSlide" variant="primary">
            Next: Add Details
            <svg class="h-4 w-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </HbButton>
        </div>
      </div>

      <!-- Slide 2: Refinement Form -->
      <div class="slide">
        <!-- Form Header -->
        <div class="bg-indigo-50 border border-indigo-200 rounded-lg p-6 mb-6">
          <div class="flex items-start gap-3">
            <svg class="h-6 w-6 text-indigo-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            <div>
              <h3 class="font-bold text-lg text-indigo-900">Improve Your Answer</h3>
              <p class="text-indigo-700 text-sm mt-1">
                Provide additional details to enhance your answer quality
              </p>
            </div>
          </div>
        </div>

        <!-- Refinement Form Fields -->
        <div class="space-y-6">
          <!-- Duration Detail -->
          <div class="bg-white border border-gray-200 rounded-lg p-6">
            <label for="duration_detail" class="block text-sm font-medium text-gray-900 mb-2">
              How long did you work on this? (timeframe)
            </label>
            <p class="text-sm text-gray-500 mb-3">
              e.g., "2 years", "6 months", "from 2020 to 2022"
            </p>
            <HbInput
              id="duration_detail"
              v-model="refinementData.duration_detail"
              type="text"
              placeholder="Enter duration..."
            />
          </div>

          <!-- Specific Tools -->
          <div class="bg-white border border-gray-200 rounded-lg p-6">
            <label for="specific_tools" class="block text-sm font-medium text-gray-900 mb-2">
              What specific tools or technologies did you use?
            </label>
            <p class="text-sm text-gray-500 mb-3">
              e.g., "Django, FastAPI, PostgreSQL, Redis"
            </p>
            <HbInput
              id="specific_tools"
              v-model="refinementData.specific_tools"
              type="textarea"
              :rows="3"
              placeholder="List specific tools and technologies..."
            />
          </div>

          <!-- Metrics -->
          <div class="bg-white border border-gray-200 rounded-lg p-6">
            <label for="metrics" class="block text-sm font-medium text-gray-900 mb-2">
              What measurable results did you achieve?
            </label>
            <p class="text-sm text-gray-500 mb-3">
              e.g., "Reduced response time by 30%", "Increased throughput by 50%", "Served 10k users"
            </p>
            <HbInput
              id="metrics"
              v-model="refinementData.metrics"
              type="textarea"
              :rows="3"
              placeholder="Describe quantifiable achievements..."
            />
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-between mt-6">
          <HbButton @click="prevSlide" variant="outline">
            <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </HbButton>
          <HbButton @click="submitRefinement" variant="primary" :disabled="!hasRefinementData">
            Generate Improved Answer
          </HbButton>
        </div>
      </div>
    </HbSlider>
  </div>
</template>

<script setup lang="ts">
interface Props {
  generatedAnswer: string
  qualityScore: number
  qualityIssues?: string[]
  qualityStrengths?: string[]
}

interface RefinementData {
  duration_detail: string
  specific_tools: string
  metrics: string
}

interface Emits {
  (e: 'submit-refinement', data: RefinementData): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const currentSlide = ref(0)
const refinementData = ref<RefinementData>({
  duration_detail: '',
  specific_tools: '',
  metrics: ''
})

const hasRefinementData = computed(() => {
  return Object.values(refinementData.value).some(v => v.trim().length > 0)
})

const nextSlide = () => {
  if (currentSlide.value < 1) currentSlide.value++
}

const prevSlide = () => {
  if (currentSlide.value > 0) currentSlide.value--
}

const submitRefinement = () => {
  emit('submit-refinement', refinementData.value)
}
</script>

<style scoped>
.refinement-slider {
  position: relative;
}

.slide {
  padding: 1.5rem;
}
</style>
