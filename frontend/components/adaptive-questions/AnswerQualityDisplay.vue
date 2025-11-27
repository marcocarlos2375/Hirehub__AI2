<template>
  <div>
    <!-- Two-column grid layout (desktop: 35/65 split) / stack (mobile) -->
    <div class="grid grid-cols-1 md:grid-cols-[35%_65%] gap-6 mb-6">
      <!-- Left Column: Quality Score Header (35%) -->
      <div class="flex items-center justify-center">
        <div>
          <!-- Circle Progress -->
          <circleProgress :score="qualityScore" label="Quality" :size="'sm'" class="mb-4" />

          <!-- Status Message -->
          <div :class="['text-xl font-bold mb-2', qualityScoreClasses(qualityScore).text]">
            {{ getQualityStatus(qualityScore) }}
          </div>

          <p class="text-gray-700 text-sm max-w-md mx-auto">
            {{ getQualityMessage(qualityScore) }}
          </p>
        </div>
      </div>

      <!-- Right Column: Strengths + Issues (50%) -->
      <div class="space-y-4">
        <!-- Quality Strengths -->
        <div v-if="qualityStrengths && qualityStrengths.length > 0">
          <div class="flex items-center mb-2">
            <h3 class="text-lg font-semibold text-gray-900">Strengths & Issues Found</h3>
          </div>
          <div>
            <ul class="space-y-1">
              <li v-for="(strength, index) in qualityStrengths" :key="index" class="flex items-start gap-3">
                <svg class="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor"
                  viewBox="0 0 24 24" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                <span class="text-sm text-gray-700">{{ strength }}</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Quality Issues -->
        <div v-if="qualityIssues && qualityIssues.length > 0">

          <div class="">
            <ul class="space-y-1">
              <li v-for="(issue, index) in qualityIssues" :key="index" class="flex items-start gap-3">
                <svg class="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor"
                  viewBox="0 0 24 24" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span class="text-sm text-gray-700">{{ issue }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { QualityEvaluation } from '~/types/adaptive-questions'
import { usePriorityStyles } from '~/composables/ui/usePriorityStyles'

interface Props {
  generatedAnswer: string
  qualityScore: number
  qualityIssues?: string[]
  qualityStrengths?: string[]
  improvementSuggestions?: Array<{
    issue: string
    suggestion: string
    priority: string
  }>
  isAcceptable: boolean
  showRefineButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showRefineButton: true
})

const emit = defineEmits<{
  'refine-answer': []
  'accept-answer': [answer: string]
}>()

const { qualityScoreClasses } = usePriorityStyles()
const copySuccess = ref(false)

// Convert markdown-style formatting to HTML
const formattedAnswer = computed(() => {
  let html = props.generatedAnswer

  // Convert **bold** to <strong>bold</strong>
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // Convert newlines to <br> tags
  html = html.replace(/\n/g, '<br>')

  return html
})

const getQualityStatus = (score: number) => {
  if (score >= 9) return 'Excellent Quality!'
  if (score >= 7) return 'Good Quality'
  if (score >= 5) return 'Needs Improvement'
  return 'Requires Refinement'
}

const getQualityMessage = (score: number) => {
  if (score >= 9) return 'Your answer is outstanding with specific details, metrics, and professional language.'
  if (score >= 7) return 'Your answer meets professional standards and is ready to use.'
  if (score >= 5) return 'Your answer has potential but could benefit from more specifics and details.'
  return 'Your answer needs significant improvement. Please add more context, details, and metrics.'
}




</script>
