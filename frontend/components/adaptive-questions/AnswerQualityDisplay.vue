<template>
  <div class="quality-display-card">
    <!-- Header: Score + Verdict -->
    <div class="header p-4 bg-gray-50 rounded-lg">
      <div class="score-wrapper">
        <circleProgress :score="qualityScore" label="Quality" :size="'xs'" />
      </div>
      <div class="verdict border-l pl-4">
        <h2>{{ getQualityStatus(qualityScore) }}</h2>
        <p class="text-sm">{{ getQualityMessage(qualityScore) }}</p>
      </div>
    </div>

    <!-- Two-column Grid: Strengths | Issues -->
    <div class="feedback-grid  mt-4 rounded-lg">
      <!-- Left: Strengths -->
      <div v-if="qualityStrengths && qualityStrengths.length > 0" class="column positive">
        <div class="column-header">Strengths</div>
        <div v-for="(item, index) in qualityStrengths" :key="index" class="feedback-item">
          <div class="flex items-start gap-3">
            <!-- Check icon with green background -->
            <div class="icon-wrapper bg-green-50 rounded-full p-1.5 flex-shrink-0">
              <svg class="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div class="flex-1">
              <strong v-if="item.label">{{ item.label }}</strong>
              <span>{{ item.description }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Issues -->
      <div v-if="qualityIssues && qualityIssues.length > 0" class="column negative">
        <div class="column-header">Opportunities for Growth</div>
        <div v-for="(item, index) in qualityIssues" :key="index" class="feedback-item">
          <div class="flex items-start gap-3">
            <!-- Warning triangle icon with red background -->
            <div class="icon-wrapper bg-red-50 rounded-full p-1.5 flex-shrink-0">
              <svg class="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div class="flex-1">
              <strong v-if="item.label">{{ item.label }}</strong>
              <span>{{ item.description }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { QualityEvaluation, QualityFeedbackItem } from '~/types/adaptive-questions'
import { usePriorityStyles } from '~/composables/ui/usePriorityStyles'

interface Props {
  generatedAnswer: string
  qualityScore: number
  qualityIssues?: QualityFeedbackItem[]
  qualityStrengths?: QualityFeedbackItem[]
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
  if (score >= 9) return 'your answer is outstanding with specific details, metrics, and professional language.'
  if (score >= 7) return 'your answer meets professional standards and is ready to use.'
  if (score >= 5) return 'your answer has potential but could benefit from more specifics and details.'
  return 'your answer needs significant improvement. Please add more context, details, and metrics.'
}
</script>

<style scoped>
/* Card container */
.quality-display-card {
  background: white;
  border-radius: 12px;
}

/* Header Section */
.header {
  display: flex;
  align-items: center;
  gap: 32px;

}

.score-wrapper {
  flex-shrink: 0;
}

.verdict h2 {
  margin: 0 0 1px 0;
  color: #1f2937; /* gray-800 */
  font-size: 20px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1.5px;
}

.verdict p {
  margin: 0;
  color: #6b7280; /* gray-500 */
  line-height: 1.6;
  max-width: 650px;
}

/* Two-column Grid */
.feedback-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
}

/* Column Headers */
.column-header {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 24px;
  font-weight: 700;
  color: #6b7280; /* gray-500 */
}

/* Feedback Items */
.feedback-item {
  margin-bottom: 16px;
}

/* Icon wrapper for circular backgrounds */
.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  min-height: 28px;
}



/* Text styling */
.feedback-item strong {
  display: block;
  color: #1f2937; /* gray-800 */
  margin-bottom: 4px;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.feedback-item span {
  color: #6b7280; /* gray-500 */
  font-size: 13px;
  line-height: 1.5;
  display: block;
}

/* Responsive */
@media (max-width: 768px) {
  .feedback-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }

  .header {
    flex-direction: column;
    text-align: center;
    gap: 24px;
  }

  .quality-display-card {
    padding: 24px;
  }
}
</style>
