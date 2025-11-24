<template>
  <div class="space-y-6">
    <!-- Timeline Header -->
    <div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-8 border border-purple-100">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <svg class="h-7 w-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        </div>
        <div class="flex-1">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Your Learning Roadmap</h2>
          <div class="flex flex-wrap gap-4 text-sm">
            <div class="flex items-center gap-2">
              <svg class="h-5 w-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-gray-700">
                <span class="font-semibold text-purple-600">{{ totalDays }}</span> total days
              </span>
            </div>
            <div class="flex items-center gap-2">
              <svg class="h-5 w-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <span class="text-gray-700">
                <span class="font-semibold text-purple-600">{{ timeline.length }}</span> learning steps
              </span>
            </div>
            <div class="flex items-center gap-2">
              <svg class="h-5 w-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span class="text-gray-700">
                Completion: <span class="font-semibold text-purple-600">{{ estimatedCompletion }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Visual Timeline -->
    <div class="bg-white border border-gray-200 rounded-lg p-8">
      <div class="relative">
        <!-- Timeline Line -->
        <div class="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-purple-200 via-blue-200 to-green-200"></div>

        <!-- Timeline Steps -->
        <div class="space-y-8">
          <div
            v-for="(step, index) in timeline"
            :key="step.resource_id"
            class="relative pl-20"
          >
            <!-- Timeline Dot -->
            <div class="absolute left-5 top-2 w-7 h-7 rounded-full border-4 border-white shadow-lg flex items-center justify-center"
                 :class="getTypeBackgroundClass(step.type)">
              <svg v-if="step.type === 'course'" class="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
              </svg>
              <svg v-else-if="step.type === 'project'" class="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
              </svg>
              <svg v-else class="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>

            <!-- Step Card -->
            <div class="bg-gradient-to-br from-gray-50 to-white rounded-lg p-6 border border-gray-200 hover:shadow-md transition-shadow">
              <div class="flex items-start justify-between mb-3">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="text-xs font-semibold text-gray-500">STEP {{ index + 1 }}</span>
                    <span
                      class="px-2 py-0.5 rounded-full text-xs font-medium capitalize"
                      :class="getTypeBadgeClass(step.type)"
                    >
                      {{ step.type }}
                    </span>
                  </div>
                  <h3 class="text-lg font-bold text-gray-900 mb-1">{{ step.resource_title }}</h3>
                </div>
              </div>

              <!-- Timeline Info -->
              <div class="grid grid-cols-3 gap-4 mb-4">
                <div class="bg-blue-50 rounded-lg p-3 border border-blue-100">
                  <div class="text-xs text-blue-600 font-medium mb-1">Start Day</div>
                  <div class="text-lg font-bold text-blue-900">{{ step.start_day }}</div>
                </div>
                <div class="bg-purple-50 rounded-lg p-3 border border-purple-100">
                  <div class="text-xs text-purple-600 font-medium mb-1">Duration</div>
                  <div class="text-lg font-bold text-purple-900">{{ step.duration_days }}d</div>
                </div>
                <div class="bg-green-50 rounded-lg p-3 border border-green-100">
                  <div class="text-xs text-green-600 font-medium mb-1">End Day</div>
                  <div class="text-lg font-bold text-green-900">{{ step.end_day }}</div>
                </div>
              </div>

              <!-- Progress Bar -->
              <div class="relative">
                <div class="flex items-center justify-between text-xs text-gray-600 mb-1">
                  <span>Day {{ step.start_day }}</span>
                  <span class="font-medium">{{ formatDateRange(step.start_day, step.end_day) }}</span>
                  <span>Day {{ step.end_day }}</span>
                </div>
                <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :class="getTypeProgressClass(step.type)"
                    :style="{ width: `${(step.duration_days / totalDays) * 100}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Completion Badge -->
        <div class="relative pl-20 mt-8">
          <div class="absolute left-5 top-2 w-7 h-7 rounded-full bg-gradient-to-br from-green-400 to-emerald-500 border-4 border-white shadow-lg flex items-center justify-center">
            <svg class="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>

          <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-6 border-2 border-green-200">
            <div class="flex items-center gap-3">
              <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 class="text-lg font-bold text-gray-900">Learning Path Complete!</h3>
                <p class="text-sm text-gray-600">You'll have mastered this skill in {{ totalDays }} days</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary Card -->
    <div class="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg p-6 border border-indigo-200">
      <h3 class="font-bold text-gray-900 mb-4 flex items-center gap-2">
        <svg class="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        Summary by Type
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-if="courseCount > 0" class="bg-white rounded-lg p-4 border border-purple-100">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm text-gray-600">Courses</div>
              <div class="text-2xl font-bold text-purple-600">{{ courseCount }}</div>
            </div>
            <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
              <svg class="h-6 w-6 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3z" />
              </svg>
            </div>
          </div>
        </div>

        <div v-if="projectCount > 0" class="bg-white rounded-lg p-4 border border-green-100">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm text-gray-600">Projects</div>
              <div class="text-2xl font-bold text-green-600">{{ projectCount }}</div>
            </div>
            <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="h-6 w-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div v-if="certificationCount > 0" class="bg-white rounded-lg p-4 border border-blue-100">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm text-gray-600">Certifications</div>
              <div class="text-2xl font-bold text-blue-600">{{ certificationCount }}</div>
            </div>
            <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="h-6 w-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TimelineStep } from '~/types/adaptive-questions'

interface Props {
  timeline: TimelineStep[]
  estimatedCompletion?: string
}

const props = withDefaults(defineProps<Props>(), {
  estimatedCompletion: ''
})

// Computed properties
const totalDays = computed(() => {
  if (props.timeline.length === 0) return 0
  return Math.max(...props.timeline.map(step => step.end_day))
})

const courseCount = computed(() => {
  return props.timeline.filter(step => step.type === 'course').length
})

const projectCount = computed(() => {
  return props.timeline.filter(step => step.type === 'project').length
})

const certificationCount = computed(() => {
  return props.timeline.filter(step => step.type === 'certification').length
})

// Helper functions
const getTypeBackgroundClass = (type: string) => {
  switch (type) {
    case 'course': return 'bg-purple-500'
    case 'project': return 'bg-green-500'
    case 'certification': return 'bg-blue-500'
    default: return 'bg-gray-500'
  }
}

const getTypeBadgeClass = (type: string) => {
  switch (type) {
    case 'course': return 'bg-purple-100 text-purple-700'
    case 'project': return 'bg-green-100 text-green-700'
    case 'certification': return 'bg-blue-100 text-blue-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

const getTypeProgressClass = (type: string) => {
  switch (type) {
    case 'course': return 'bg-gradient-to-r from-purple-400 to-purple-600'
    case 'project': return 'bg-gradient-to-r from-green-400 to-green-600'
    case 'certification': return 'bg-gradient-to-r from-blue-400 to-blue-600'
    default: return 'bg-gradient-to-r from-gray-400 to-gray-600'
  }
}

const formatDateRange = (startDay: number, endDay: number) => {
  const weeks = Math.floor(endDay / 7)
  const days = endDay % 7
  if (weeks > 0 && days > 0) return `~${weeks}w ${days}d`
  if (weeks > 0) return `~${weeks} week${weeks !== 1 ? 's' : ''}`
  return `${days} day${days !== 1 ? 's' : ''}`
}
</script>
