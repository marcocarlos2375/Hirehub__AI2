<template>
  <div class="space-y-6">
    <!-- Quality Score Header -->
    <div class="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-8 border border-indigo-100">
      <div class="text-center">
        <!-- Quality Badge -->
        <div class="inline-flex items-center justify-center w-24 h-24 rounded-full mb-4"
             :class="getScoreBackgroundClass(qualityScore)">
          <div class="text-center">
            <div class="text-3xl font-bold" :class="getScoreTextClass(qualityScore)">
              {{ qualityScore }}
            </div>
            <div class="text-xs font-medium text-gray-600">/ 10</div>
          </div>
        </div>

        <!-- Status Message -->
        <div class="text-2xl font-bold mb-2" :class="getScoreTextClass(qualityScore)">
          {{ getQualityStatus(qualityScore) }}
        </div>

        <p class="text-gray-700 text-sm max-w-2xl mx-auto">
          {{ getQualityMessage(qualityScore) }}
        </p>
      </div>
    </div>

    <!-- Generated Answer -->
  

    <!-- Quality Strengths -->
    <div v-if="qualityStrengths && qualityStrengths.length > 0" class="bg-green-50 border border-green-200 rounded-lg p-6">
      <div class="flex items-center mb-4">
        <svg class="h-5 w-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <h3 class="text-lg font-semibold text-gray-900">Strengths</h3>
      </div>
      <ul class="space-y-2">
        <li v-for="(strength, index) in qualityStrengths" :key="index" class="flex items-start gap-3">
          <svg class="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          <span class="text-sm text-gray-700">{{ strength }}</span>
        </li>
      </ul>
    </div>

    <!-- Quality Issues -->
    <div v-if="qualityIssues && qualityIssues.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <div class="flex items-center mb-4">
        <svg class="h-5 w-5 text-red-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <h3 class="text-lg font-semibold text-gray-900">Issues Found</h3>
      </div>
      <ul class="space-y-2">
        <li v-for="(issue, index) in qualityIssues" :key="index" class="flex items-start gap-3">
          <svg class="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <span class="text-sm text-gray-700">{{ issue }}</span>
        </li>
      </ul>
    </div>

    <!-- Improvement Suggestions -->
    <div v-if="improvementSuggestions && improvementSuggestions.length > 0" class="space-y-4">
      <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
        <svg class="h-5 w-5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
          <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
        </svg>
        Suggestions for Improvement
      </h3>

     
    </div>

    <!-- Action Buttons -->
    <div class="bg-white border border-gray-200 rounded-lg p-6">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <h3 class="font-bold text-gray-900 mb-1">Ready to finalize your answer?</h3>
          <p class="text-sm text-gray-600">
            {{ isAcceptable ? 'Your answer meets quality standards.' : 'Consider refining with more details.' }}
          </p>
        </div>

        <div class="flex gap-3">
          <button
            v-if="showRefineButton && !isAcceptable && qualityScore < 10"
            @click="$emit('refine-answer')"
            class="px-6 py-3 bg-amber-500 text-white font-medium rounded-lg hover:bg-amber-600 transition-colors flex items-center gap-2"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refine Answer
          </button>

          <button
            @click="$emit('accept-answer', generatedAnswer)"
            :class="[
              'px-6 py-3 font-medium rounded-lg transition-colors flex items-center gap-2',
              isAcceptable
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-indigo-600 text-white hover:bg-indigo-700'
            ]"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            {{ isAcceptable ? 'Accept Answer' : 'Accept Anyway' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Copy Success Toast -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div
        v-if="copySuccess"
        class="fixed bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 z-50"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <span class="font-medium">Copied to clipboard!</span>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import type { QualityEvaluation } from '~/types/adaptive-questions'

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

const getScoreBackgroundClass = (score: number) => {
  if (score >= 9) return 'bg-green-100'
  if (score >= 7) return 'bg-blue-100'
  if (score >= 5) return 'bg-amber-100'
  return 'bg-red-100'
}

const getScoreTextClass = (score: number) => {
  if (score >= 9) return 'text-green-700'
  if (score >= 7) return 'text-blue-700'
  if (score >= 5) return 'text-amber-700'
  return 'text-red-700'
}

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

const getPriorityBorderClass = (priority: string | undefined) => {
  if (!priority) return 'border-l-4 border-blue-500'
  const p = priority.toLowerCase()
  if (p === 'high' || p === 'critical') return 'border-l-4 border-red-500'
  if (p === 'medium' || p === 'important') return 'border-l-4 border-amber-500'
  return 'border-l-4 border-blue-500'
}

const getPriorityBadgeClass = (priority: string | undefined) => {
  if (!priority) return 'bg-blue-100 text-blue-700'
  const p = priority.toLowerCase()
  if (p === 'high' || p === 'critical') return 'bg-red-100 text-red-700'
  if (p === 'medium' || p === 'important') return 'bg-amber-100 text-amber-700'
  return 'bg-blue-100 text-blue-700'
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    copySuccess.value = true
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
  }
}
</script>
