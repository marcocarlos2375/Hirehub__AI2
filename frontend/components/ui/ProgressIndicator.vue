<template>
  <div class="flex items-center gap-2">
    <!-- Circular progress -->
    <div class="relative" :style="{ width: size + 'px', height: size + 'px' }">
      <svg class="transform -rotate-90" :width="size" :height="size">
        <!-- Background circle -->
        <circle
          :cx="size / 2"
          :cy="size / 2"
          :r="radius"
          stroke="#e5e7eb"
          :stroke-width="strokeWidth"
          fill="none"
        />
        <!-- Progress circle -->
        <circle
          :cx="size / 2"
          :cy="size / 2"
          :r="radius"
          :stroke="progressColor"
          :stroke-width="strokeWidth"
          fill="none"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="dashOffset"
          stroke-linecap="round"
          class="transition-all duration-300 ease-in-out"
        />
      </svg>
      <!-- Center icon or percentage -->
      <div class="absolute inset-0 flex items-center justify-center">
        <!-- Loading spinner -->
        <svg
          v-if="status === 'loading'"
          class="animate-spin h-3 w-3 text-primary-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
        <!-- Checkmark -->
        <svg
          v-else-if="status === 'complete'"
          class="h-3 w-3 text-green-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
        </svg>
        <!-- Pending clock -->
        <svg
          v-else-if="status === 'pending'"
          class="h-3 w-3 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <circle cx="12" cy="12" r="10" stroke-width="2" />
          <path stroke-linecap="round" stroke-width="2" d="M12 6v6l4 2" />
        </svg>
        <!-- Error -->
        <svg
          v-else-if="status === 'error'"
          class="h-3 w-3 text-red-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
    </div>

    <!-- Percentage text (only show if loading or complete) -->
    <span v-if="showPercentage && (status === 'loading' || status === 'complete')" class="text-xs font-medium text-gray-700">
      {{ Math.round(percentage) }}%
    </span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  percentage: number
  status: 'pending' | 'loading' | 'complete' | 'error'
  size?: number
  showPercentage?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 24,
  showPercentage: true
})

const strokeWidth = computed(() => props.size / 8)
const radius = computed(() => (props.size - strokeWidth.value) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const dashOffset = computed(() => {
  return circumference.value - (props.percentage / 100) * circumference.value
})

const progressColor = computed(() => {
  if (props.status === 'complete') return '#10b981' // green-500
  if (props.status === 'error') return '#ef4444' // red-500
  if (props.status === 'loading') return '#0ea5e9' // primary-500 (sky blue)
  return '#d1d5db' // gray-300
})
</script>
