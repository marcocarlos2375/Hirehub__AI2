<template>
  <div class="w-64 bg-gray-50 border-r border-gray-200 min-h-screen p-4">
    <div class="space-y-2">
      <button
        v-for="step in steps"
        :key="step.id"
        @click="$emit('select-step', step.id)"
        :class="[
          'w-full flex items-center justify-between p-4 rounded-lg transition-all duration-200',
          selectedStepId === step.id
            ? 'bg-indigo-600 text-white shadow-lg'
            : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
        ]"
      >
        <div class="flex items-center gap-3 flex-1">
          <!-- Progress Indicator -->
          <ProgressIndicator
            :percentage="step.progress"
            :status="step.status"
            :size="32"
            :show-percentage="false"
          />

          <!-- Step Info -->
          <div class="flex flex-col items-start">
            <span class="font-medium text-sm">{{ step.label }}</span>
            <span
              v-if="step.status === 'loading' || step.status === 'complete'"
              :class="selectedStepId === step.id ? 'text-indigo-200' : 'text-gray-500'"
              class="text-xs"
            >
              {{ Math.round(step.progress) }}%
            </span>
            <span
              v-else-if="step.status === 'pending'"
              :class="selectedStepId === step.id ? 'text-indigo-200' : 'text-gray-500'"
              class="text-xs"
            >
              Waiting...
            </span>
            <span
              v-else-if="step.status === 'error'"
              :class="selectedStepId === step.id ? 'text-red-200' : 'text-red-500'"
              class="text-xs"
            >
              Error
            </span>
          </div>
        </div>

        <!-- Chevron indicator for selected -->
        <svg
          v-if="selectedStepId === step.id"
          class="h-5 w-5 flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AnalysisStep } from '~/composables/analysis/useAnalysisState'

interface Props {
  steps: AnalysisStep[]
  selectedStepId: string
}

defineProps<Props>()
defineEmits<{
  'select-step': [stepId: string]
}>()
</script>
