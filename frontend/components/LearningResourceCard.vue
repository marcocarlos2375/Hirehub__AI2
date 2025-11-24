<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
    <!-- Header with type badge -->
    <div class="flex items-start justify-between mb-3">
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-2">
          <span
            :class="[
              'px-2.5 py-1 rounded-full text-xs font-medium',
              typeColorClass
            ]"
          >
            {{ resource.type }}
          </span>
          <span
            :class="[
              'px-2 py-0.5 rounded text-xs font-medium',
              difficultyColorClass
            ]"
          >
            {{ resource.difficulty }}
          </span>
          <span
            :class="[
              'px-2 py-0.5 rounded text-xs font-medium',
              costColorClass
            ]"
          >
            {{ resource.cost }}
          </span>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-1">
          {{ resource.title }}
        </h3>
        <p class="text-sm text-gray-600">
          by {{ resource.provider }}
        </p>
      </div>
    </div>

    <!-- Description -->
    <p class="text-gray-700 text-sm mb-4 line-clamp-3">
      {{ resource.description }}
    </p>

    <!-- Meta information -->
    <div class="flex flex-wrap gap-4 mb-4">
      <div class="flex items-center gap-1.5 text-sm text-gray-600">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ resource.duration_days }} days</span>
      </div>

      <div v-if="resource.rating" class="flex items-center gap-1.5 text-sm text-gray-600">
        <svg class="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
        <span>{{ resource.rating.toFixed(1) }}</span>
      </div>

      <div v-if="showCertificate" class="flex items-center gap-1.5 text-sm text-green-600">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
        </svg>
        <span>Certificate</span>
      </div>
    </div>

    <!-- Skills covered -->
    <div class="mb-4">
      <p class="text-xs font-medium text-gray-700 mb-2">Skills covered:</p>
      <div class="flex flex-wrap gap-1.5">
        <span
          v-for="skill in resource.skills_covered.slice(0, 5)"
          :key="skill"
          class="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-md"
        >
          {{ skill }}
        </span>
        <span
          v-if="resource.skills_covered.length > 5"
          class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md"
        >
          +{{ resource.skills_covered.length - 5 }} more
        </span>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex gap-2 mt-4 pt-4 border-t border-gray-200">
      <a
        :href="resource.url"
        target="_blank"
        rel="noopener noreferrer"
        class="flex-1 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors text-center"
      >
        View Resource
      </a>
      <button
        v-if="showAddButton"
        @click="$emit('add-to-plan', resource.id)"
        class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
      >
        Add to Plan
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LearningResourceItem } from '~/composables/useAdaptiveQuestions'

interface Props {
  resource: LearningResourceItem
  showAddButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showAddButton: true
})

defineEmits<{
  'add-to-plan': [resourceId: string]
}>()

const showCertificate = computed(() => {
  return props.resource.type === 'certification' ||
         props.resource.title.toLowerCase().includes('certification') ||
         props.resource.title.toLowerCase().includes('certificate')
})

const typeColorClass = computed(() => {
  switch (props.resource.type) {
    case 'course':
      return 'bg-purple-100 text-purple-800'
    case 'project':
      return 'bg-green-100 text-green-800'
    case 'certification':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
})

const difficultyColorClass = computed(() => {
  switch (props.resource.difficulty) {
    case 'beginner':
      return 'bg-green-50 text-green-700 border border-green-200'
    case 'intermediate':
      return 'bg-yellow-50 text-yellow-700 border border-yellow-200'
    case 'advanced':
      return 'bg-red-50 text-red-700 border border-red-200'
    default:
      return 'bg-gray-50 text-gray-700 border border-gray-200'
  }
})

const costColorClass = computed(() => {
  switch (props.resource.cost) {
    case 'free':
      return 'bg-green-50 text-green-700 border border-green-200'
    case 'freemium':
      return 'bg-blue-50 text-blue-700 border border-blue-200'
    case 'paid':
      return 'bg-orange-50 text-orange-700 border border-orange-200'
    default:
      return 'bg-gray-50 text-gray-700 border border-gray-200'
  }
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
