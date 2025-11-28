<template>
  <div class="flex items-center justify-between mb-2">
    <div class="flex-1">
      <h2 class="text-2xl font-bold text-gray-900">{{ title }}</h2>
      <p class="text-sm text-gray-600 mt-1">{{ subtitle }}</p>
    </div>

    <div class="text-right">
      <!-- Stats Row -->
      <div class="flex gap-3">
        <div class="flex items-center gap-1.5 px-2 py-1 bg-red-50 rounded-lg">
          <div class="text-lg font-semibold text-red-600">{{ criticalCount }}</div>
          <div class="text-xs text-red-600">Critical</div>
        </div>
        <div class="flex items-center gap-1.5 px-2 py-1 bg-orange-50 rounded-lg">
          <div class="text-lg font-semibold text-orange-600">{{ highCount }}</div>
          <div class="text-xs text-orange-600">High</div>
        </div>
        <div class="flex items-center gap-1.5 px-2 py-1 bg-yellow-50 rounded-lg">
          <div class="text-lg font-semibold text-yellow-600">{{ mediumCount }}</div>
          <div class="text-xs text-yellow-600">Medium</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  subtitle: string
  criticalCount: number
  highCount: number
  mediumCount: number
}

const props = defineProps<Props>()
</script>
