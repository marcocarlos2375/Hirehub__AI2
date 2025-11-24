<template>
  <div class="space-y-6">
    <!-- Header with selection counter -->
    <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-200">
      <div class="flex items-center gap-3">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800">
          <svg class="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          {{ domains.length }} Domains Found
        </span>
        <span v-if="timeSeconds" class="text-sm text-gray-600">
          <span class="font-medium">{{ timeSeconds }}s</span>
        </span>
      </div>
      <div class="text-sm font-medium" :class="selectedDomains.length === 6 ? 'text-green-600' : 'text-gray-600'">
        {{ selectedDomains.length }}/6 Selected
      </div>
    </div>

    <!-- Instruction message -->
    <div v-if="selectedDomains.length === 0" class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
      <p class="text-sm text-blue-800">
        <strong>Select up to 6 domains</strong> you'd like to explore. Click on any card to select it, then click "Expand" to see detailed skill gap analysis.
      </p>
    </div>

    <!-- Domains grid -->
    <div class="grid grid-cols-1 gap-4">
      <div
        v-for="domain in domains"
        :key="domain.rank"
        class="bg-white rounded-lg border-2 transition-all cursor-pointer hover:shadow-md"
        :class="{
          'border-indigo-500 bg-indigo-50': isSelected(domain),
          'border-gray-200': !isSelected(domain),
          'opacity-50': selectedDomains.length >= 6 && !isSelected(domain)
        }"
        @click="toggleDomain(domain)"
      >
        <!-- Domain card header -->
        <div class="p-6">
          <div class="flex justify-between items-start mb-3">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <span class="text-xs font-semibold text-gray-500 uppercase">Rank #{{ domain.rank }}</span>
                <span
                  class="px-2 py-1 rounded-full text-xs font-medium"
                  :class="{
                    'bg-green-100 text-green-800': domain.fit_score >= 75,
                    'bg-yellow-100 text-yellow-800': domain.fit_score >= 55 && domain.fit_score < 75,
                    'bg-orange-100 text-orange-800': domain.fit_score < 55
                  }"
                >
                  {{ domain.fit_score }}% Fit
                </span>
              </div>
              <h3 class="text-xl font-bold text-gray-900 mb-2">{{ domain.domain_name }}</h3>

              <!-- Role and Industry Tags -->
              <div class="flex flex-wrap gap-2 mb-3">
                <span class="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs font-semibold">
                  Role: {{ domain.technical_role }}
                </span>
                <span class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-semibold">
                  Industry: {{ domain.industry }}
                </span>
              </div>

              <p class="text-sm text-gray-600 leading-relaxed mb-2">
                <strong>Role Fit:</strong> {{ domain.reasoning }}
              </p>
              <p class="text-sm text-gray-600 leading-relaxed">
                <strong>Industry Match:</strong> {{ domain.industry_rationale }}
              </p>
            </div>
            <div class="ml-4">
              <div class="flex items-center justify-center w-16 h-16 rounded-full" :class="{
                'bg-green-100': domain.fit_score >= 75,
                'bg-yellow-100': domain.fit_score >= 55 && domain.fit_score < 75,
                'bg-orange-100': domain.fit_score < 55
              }">
                <span class="text-2xl font-bold" :class="{
                  'text-green-700': domain.fit_score >= 75,
                  'text-yellow-700': domain.fit_score >= 55 && domain.fit_score < 75,
                  'text-orange-700': domain.fit_score < 55
                }">{{ domain.fit_score }}</span>
              </div>
            </div>
          </div>

          <!-- Expand/collapse button -->
          <button
            @click.stop="toggleExpand(domain.rank)"
            class="text-sm font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-1 mt-3"
          >
            <svg
              class="h-4 w-4 transition-transform"
              :class="{ 'rotate-180': expanded[domain.rank] }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            {{ expanded[domain.rank] ? 'Collapse Details' : 'Expand Details' }}
          </button>

          <!-- Expandable details -->
          <div v-if="expanded[domain.rank]" class="mt-6 space-y-6 border-t border-gray-200 pt-6">
            <!-- Matching Skills -->
            <div>
              <h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                <svg class="h-5 w-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Skills You Already Have ({{ domain.matching_skills.length }})
              </h4>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="skill in domain.matching_skills"
                  :key="skill"
                  class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                >
                  {{ skill }}
                </span>
              </div>
            </div>

            <!-- Role Skills to Learn -->
            <div v-if="domain.role_skills_to_learn && domain.role_skills_to_learn.length > 0">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-sm font-semibold text-gray-700 flex items-center">
                  <svg class="h-5 w-5 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  Technical Role Skills to Learn ({{ domain.role_skills_to_learn.length }})
                </h4>
                <span
                  class="px-2 py-1 rounded-full text-xs font-semibold"
                  :class="{
                    'bg-red-100 text-red-800': domain.learning_priority === 'HIGH',
                    'bg-yellow-100 text-yellow-800': domain.learning_priority === 'MEDIUM',
                    'bg-blue-100 text-blue-800': domain.learning_priority === 'LOW'
                  }"
                >
                  {{ domain.learning_priority }} Priority
                </span>
              </div>
              <div class="flex flex-wrap gap-2 mb-4">
                <span
                  v-for="skill in domain.role_skills_to_learn"
                  :key="skill"
                  class="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm font-medium"
                >
                  {{ skill }}
                </span>
              </div>
            </div>

            <!-- Industry Domain Knowledge to Learn -->
            <div v-if="domain.industry_skills_to_learn && domain.industry_skills_to_learn.length > 0">
              <h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                <svg class="h-5 w-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                Industry Domain Knowledge to Learn ({{ domain.industry_skills_to_learn.length }})
              </h4>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="skill in domain.industry_skills_to_learn"
                  :key="skill"
                  class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium"
                >
                  {{ skill }}
                </span>
              </div>
            </div>

            <!-- Time to Ready -->
            <div class="bg-gray-50 rounded-lg p-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <svg class="h-5 w-5 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span class="text-sm font-semibold text-gray-700">Estimated Time to Job-Ready</span>
                </div>
                <span class="text-lg font-bold text-indigo-600">{{ domain.time_to_ready }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Selection limit message -->
    <div v-if="selectedDomains.length >= 6" class="bg-green-50 border border-green-200 rounded-lg p-4 mt-4">
      <p class="text-sm text-green-800 flex items-center">
        <svg class="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <strong>Maximum 6 domains selected.</strong> You can deselect a domain to choose a different one.
      </p>
    </div>

    <!-- Generate Job Search Queries Button -->
    <div v-if="selectedDomains.length > 0" class="mt-8 flex justify-center">
      <button
        @click="showQueryModal = true"
        class="px-8 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold rounded-xl hover:shadow-2xl hover:scale-105 transition-all flex items-center gap-3 text-lg"
      >
        <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        Generate Job Search Queries
        <span class="px-3 py-1 bg-white/20 rounded-full text-sm font-semibold">
          {{ selectedDomains.length }} domains
        </span>
      </button>
    </div>

    <!-- Job Search Queries Modal -->
    <JobSearchQueriesModal
      v-if="showQueryModal"
      :domains="selectedDomains"
      @close="showQueryModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import type { DomainMatch } from '~/composables/useDomainFinder'

interface Props {
  domains: DomainMatch[]
  timeSeconds?: number
}

const props = defineProps<Props>()

const selectedDomains = ref<DomainMatch[]>([])
const expanded = ref<Record<number, boolean>>({})
const showQueryModal = ref(false)

const isSelected = (domain: DomainMatch): boolean => {
  return selectedDomains.value.some(d => d.rank === domain.rank)
}

const toggleDomain = (domain: DomainMatch) => {
  const index = selectedDomains.value.findIndex(d => d.rank === domain.rank)

  if (index >= 0) {
    // Already selected - remove it
    selectedDomains.value.splice(index, 1)
  } else if (selectedDomains.value.length < 6) {
    // Not selected and under limit - add it
    selectedDomains.value.push(domain)
  }
  // If at limit and not selected, do nothing (user must deselect first)
}

const toggleExpand = (rank: number) => {
  expanded.value[rank] = !expanded.value[rank]
}

// Export selected domains for parent component
defineExpose({
  selectedDomains
})
</script>
