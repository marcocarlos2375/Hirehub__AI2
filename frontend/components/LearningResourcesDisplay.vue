<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-8 border border-blue-100">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <svg class="h-7 w-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <div class="flex-1">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Learning Resources</h2>
          <p class="text-gray-700">
            We've found <span class="font-semibold text-blue-600">{{ resources.length }}</span> resources to help you develop this skill.
            Select the ones you'd like to pursue and we'll create a personalized learning roadmap.
          </p>
        </div>
      </div>
    </div>

    <!-- Resume Addition Suggestion -->
    <div v-if="resumeAddition" class="bg-green-50 border border-green-200 rounded-lg p-6">
      <div class="flex items-start gap-3">
        <svg class="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="flex-1">
          <h3 class="font-bold text-gray-900 mb-2 flex items-center gap-2">
            Suggested Resume Addition
            <button
              @click="copyToClipboard(resumeAddition)"
              class="ml-auto px-3 py-1 text-sm bg-green-100 text-green-700 border border-green-300 rounded-lg hover:bg-green-200 transition-colors flex items-center gap-1.5"
            >
              <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy
            </button>
          </h3>
          <p class="text-sm text-gray-700 bg-white rounded p-3 border border-green-200">
            {{ resumeAddition }}
          </p>
          <p class="text-xs text-gray-600 mt-2">
            Add this to your resume to show your commitment to learning this skill.
          </p>
        </div>
      </div>
    </div>

    <!-- Selection Summary -->
    <div v-if="selectedResourceIds.length > 0" class="bg-indigo-50 border border-indigo-200 rounded-lg p-5">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center">
            <span class="text-white font-bold text-sm">{{ selectedResourceIds.length }}</span>
          </div>
          <div>
            <h3 class="font-bold text-gray-900">
              {{ selectedResourceIds.length }} resource{{ selectedResourceIds.length !== 1 ? 's' : '' }} selected
            </h3>
            <p class="text-sm text-gray-600">
              Estimated completion time: {{ totalDuration }} days
            </p>
          </div>
        </div>
        <button
          v-if="selectedResourceIds.length > 0"
          @click="clearSelection"
          class="px-4 py-2 text-sm text-indigo-600 hover:text-indigo-700 font-medium"
        >
          Clear All
        </button>
      </div>
    </div>

    <!-- Filter/Sort Options -->
    <div class="bg-white border border-gray-200 rounded-lg p-4">
      <div class="flex flex-wrap gap-4 items-center">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-2">Filter by Type</label>
          <select
            v-model="filterType"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="course">Courses</option>
            <option value="project">Projects</option>
            <option value="certification">Certifications</option>
          </select>
        </div>

        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-2">Filter by Difficulty</label>
          <select
            v-model="filterDifficulty"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option value="all">All Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-2">Filter by Cost</label>
          <select
            v-model="filterCost"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option value="all">All</option>
            <option value="free">Free Only</option>
            <option value="freemium">Freemium</option>
            <option value="paid">Paid</option>
          </select>
        </div>
      </div>

      <div v-if="hasActiveFilters" class="mt-3 flex items-center justify-between">
        <p class="text-sm text-gray-600">
          Showing {{ filteredResources.length }} of {{ resources.length }} resources
        </p>
        <button
          @click="clearFilters"
          class="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
        >
          Clear Filters
        </button>
      </div>
    </div>

    <!-- Resources Grid -->
    <div v-if="filteredResources.length > 0" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div v-for="resource in filteredResources" :key="resource.id" class="relative">
        <!-- Selection Checkbox Overlay -->
        <div class="absolute top-2 right-2 z-10">
          <label class="flex items-center gap-2 bg-white rounded-lg px-3 py-2 shadow-md cursor-pointer hover:bg-gray-50 transition-colors">
            <input
              type="checkbox"
              :value="resource.id"
              v-model="selectedResourceIds"
              @change="handleResourceSelection(resource.id)"
              class="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
            />
            <span class="text-sm font-medium text-gray-700">Select</span>
          </label>
        </div>

        <!-- Resource Card -->
        <LearningResourceCard
          :resource="resource"
          :show-add-button="false"
          class="h-full"
          :class="{ 'ring-2 ring-indigo-500 ring-offset-2': selectedResourceIds.includes(resource.id) }"
        />
      </div>
    </div>

    <!-- No Results -->
    <div v-else class="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
      <svg class="h-16 w-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No resources found</h3>
      <p class="text-gray-600">Try adjusting your filters to see more results.</p>
    </div>

    <!-- Action Button -->
    <div class="bg-white border border-gray-200 rounded-lg p-6">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <h3 class="font-bold text-gray-900 mb-1">Ready to start learning?</h3>
          <p class="text-sm text-gray-600">
            {{ selectedResourceIds.length > 0
              ? `Save your plan with ${selectedResourceIds.length} selected resource${selectedResourceIds.length !== 1 ? 's' : ''}`
              : 'Select resources above to create your learning plan'
            }}
          </p>
        </div>

        <button
          @click="savePlan"
          :disabled="selectedResourceIds.length === 0 || loading"
          class="px-8 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <svg v-if="loading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span v-if="loading">Saving...</span>
          <span v-else>Save Learning Plan</span>
        </button>
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
import type { LearningResource } from '~/types/adaptive-questions'
import LearningResourceCard from './LearningResourceCard.vue'

interface Props {
  resources: LearningResource[]
  resumeAddition?: string
  loading?: boolean
  modelValue?: string[] // For v-model binding of selected IDs
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  modelValue: () => []
})

const emit = defineEmits<{
  'save-plan': [resourceIds: string[]]
  'update:modelValue': [resourceIds: string[]]
}>()

// Filters
const filterType = ref<string>('all')
const filterDifficulty = ref<string>('all')
const filterCost = ref<string>('all')
const copySuccess = ref(false)

// Selected resources (supports v-model)
const selectedResourceIds = ref<string[]>([...props.modelValue])

// Sync with v-model
watch(() => props.modelValue, (newValue) => {
  selectedResourceIds.value = [...newValue]
})

watch(selectedResourceIds, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

// Computed
const filteredResources = computed(() => {
  let filtered = props.resources

  if (filterType.value !== 'all') {
    filtered = filtered.filter(r => r.type === filterType.value)
  }

  if (filterDifficulty.value !== 'all') {
    filtered = filtered.filter(r => r.difficulty === filterDifficulty.value)
  }

  if (filterCost.value !== 'all') {
    filtered = filtered.filter(r => r.cost === filterCost.value)
  }

  return filtered
})

const hasActiveFilters = computed(() => {
  return filterType.value !== 'all' || filterDifficulty.value !== 'all' || filterCost.value !== 'all'
})

const totalDuration = computed(() => {
  const selected = props.resources.filter(r => selectedResourceIds.value.includes(r.id))
  return selected.reduce((sum, r) => sum + r.duration_days, 0)
})

// Methods
const handleResourceSelection = (resourceId: string) => {
  // The v-model will automatically update selectedResourceIds
  // This handler is for any additional logic needed on selection
}

const clearSelection = () => {
  selectedResourceIds.value = []
}

const clearFilters = () => {
  filterType.value = 'all'
  filterDifficulty.value = 'all'
  filterCost.value = 'all'
}

const savePlan = () => {
  if (selectedResourceIds.value.length === 0) return
  emit('save-plan', selectedResourceIds.value)
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
