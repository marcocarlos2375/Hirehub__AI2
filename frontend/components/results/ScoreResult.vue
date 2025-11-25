<template>
  <div class="space-y-8">
    <!-- Overall Score Header - AI-Generated Encouraging Message -->
    <div class="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-8 border border-indigo-100">
      <div class="text-center">
        <!-- Status Label (Excellent/Good/Moderate/Needs Work) -->
        <div class="text-xl font-semibold mb-3" :class="getStatusColorClass(data.overall_score)">
          {{ data.overall_status }}
        </div>

        <!-- AI-Generated Title -->
        <div class="text-3xl font-bold mb-3 text-gray-900">
          {{ data.score_message.title }}
        </div>

        <!-- AI-Generated Subtitle -->
        <div class="text-lg text-gray-700 mb-4 max-w-3xl mx-auto">
          {{ data.score_message.subtitle }}
        </div>

        <div v-if="timeSeconds" class="text-sm text-gray-600">
          Analysis completed in <span class="font-medium">{{ timeSeconds }}s</span>
        </div>
      </div>
    </div>

    <!-- Category Scores -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900 mb-4">Category Breakdown</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="(category, key) in data.category_scores"
          :key="key"
          class="bg-white rounded-lg p-5 border border-gray-200"
        >
          <div class="flex justify-between items-start mb-3">
            <h3 class="text-sm font-semibold text-gray-700 capitalize">
              {{ key.replace(/_/g, ' ') }}
            </h3>
            <span :class="getCategoryBadgeClass(category.status)" class="text-xs px-2 py-1 rounded-full font-medium">
              {{ category.status }}
            </span>
          </div>
          <div class="flex items-end justify-between">
            <div class="text-3xl font-bold" :class="getScoreColorClass(category.score)">
              {{ category.score }}
            </div>
            <div class="text-sm text-gray-500">
              Weight: {{ Math.round(category.weight * 100) }}%
            </div>
          </div>
          <div class="mt-2 bg-gray-200 rounded-full h-2">
            <div
              class="h-2  transition-all duration-500"
              :class="getScoreBarClass(category.score)"
              :style="{ width: category.score + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Gaps Section -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900 mb-4">Gap Analysis</h2>

      <!-- Critical Gaps -->
      <div v-if="data.gaps.critical.length" class="mb-6">
        <div class="flex items-center mb-3">
          <svg class="h-5 w-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <h3 class="text-lg font-semibold text-gray-900">Critical Gaps ({{ data.gaps.critical.length }})</h3>
        </div>
        <div class="space-y-3">
          <GapCard
            v-for="gap in data.gaps.critical"
            :key="gap.id"
            variant="critical"
            :gap="gap"
          />
        </div>
      </div>

      <!-- Important Gaps -->
      <div v-if="data.gaps.important.length" class="mb-6">
        <div class="flex items-center mb-3">
          <svg class="h-5 w-5 text-amber-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          <h3 class="text-lg font-semibold text-gray-900">Important Gaps ({{ data.gaps.important.length }})</h3>
        </div>
        <div class="space-y-3">
          <GapCard
            v-for="gap in data.gaps.important"
            :key="gap.id"
            variant="important"
            :gap="gap"
          />
        </div>
      </div>

      <!-- Nice-to-Have Gaps -->
      <div v-if="data.gaps.nice_to_have.length" class="mb-6">
        <div class="flex items-center mb-3">
          <svg class="h-5 w-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
          <h3 class="text-lg font-semibold text-gray-900">Nice-to-Have Gaps ({{ data.gaps.nice_to_have.length }})</h3>
        </div>
        <div class="space-y-3">
          <GapCard
            v-for="gap in data.gaps.nice_to_have"
            :key="gap.id"
            variant="nice-to-have"
            :gap="gap"
          />
        </div>
      </div>

      <!-- Logistical Gaps -->
      <div v-if="data.gaps.logistical.length" class="mb-6">
        <div class="flex items-center mb-3">
          <svg class="h-5 w-5 text-gray-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
          </svg>
          <h3 class="text-lg font-semibold text-gray-900">Logistical Gaps ({{ data.gaps.logistical.length }})</h3>
        </div>
        <div class="space-y-3">
          <GapCard
            v-for="gap in data.gaps.logistical"
            :key="gap.id"
            variant="logistical"
            :gap="gap"
          />
        </div>
      </div>

      <!-- No Gaps -->
      <div v-if="!data.gaps.critical.length && !data.gaps.important.length && !data.gaps.nice_to_have.length && !data.gaps.logistical.length" class="text-center py-8 text-gray-500">
        No gaps identified - Excellent match!
      </div>
    </div>

    <!-- Strengths Section -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900 mb-4">Strengths</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="(strength, index) in data.strengths"
          :key="index"
          class="bg-blue-50 border border-blue-200 rounded-lg p-5"
        >
          <div class="flex items-start">
            <svg class="h-6 w-6 text-blue-600 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <div>
              <h3 class="font-semibold text-gray-900 mb-1">{{ strength.title }}</h3>
              <p class="text-sm text-gray-700 mb-2">{{ strength.description }}</p>
              <p class="text-xs text-gray-600 bg-white px-2 py-1 rounded inline-block">{{ strength.evidence }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Application Viability -->
    <div class="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Application Viability</h2>
      <div class="mb-4">
        <span class="text-sm font-semibold text-gray-700">Current Likelihood:</span>
        <span class="ml-2 text-2xl font-bold text-purple-700">{{ data.application_viability.current_likelihood }}</span>
      </div>
      <div>
        <h3 class="text-sm font-semibold text-gray-700 mb-2">Key Blockers:</h3>
        <ul class="space-y-2">
          <li
            v-for="(blocker, index) in data.application_viability.key_blockers"
            :key="index"
            class="flex items-start text-sm text-gray-700"
          >
            <span class="text-purple-500 mr-2 mt-1">▸</span>
            {{ blocker }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ScoreResponse } from '~/composables/analysis/useScoreCalculator'
import GapCard from '~/components/cards/GapCard.vue'

interface Props {
  data: ScoreResponse
  timeSeconds?: number
}

defineProps<Props>()

const getStatusColorClass = (score: number) => {
  if (score >= 75) return 'text-primary-700'       // Dark text (6.1:1 contrast)
  if (score >= 60) return 'text-primary-700'       // Dark text
  if (score >= 40) return 'text-primary-800'       // Darker text (7.9:1)
  if (score >= 25) return 'text-primary-900'       // Darkest text (9.2:1)
  return 'text-primary-950'                         // Near-black (13:1)
}

const getScoreColorClass = (score: number) => {
  if (score >= 75) return 'text-primary-700'       // Dark text (6.1:1 contrast)
  if (score >= 60) return 'text-primary-700'       // Dark text
  if (score >= 40) return 'text-primary-800'       // Darker text (7.9:1)
  if (score >= 25) return 'text-primary-900'       // Darkest text (9.2:1)
  return 'text-primary-950'                         // Near-black (13:1)
}

const getScoreBarClass = (score: number) => {
  if (score >= 75) return 'bg-primary-200'         // Lightest bar (best)
  if (score >= 60) return 'bg-primary-400'         // Light bar
  if (score >= 40) return 'bg-primary-600'         // Medium bar
  if (score >= 25) return 'bg-primary-700'         // Dark bar
  return 'bg-primary-800'                           // Darkest bar (worst)
}

const getCategoryBadgeClass = (status: string) => {
  const classes = {
    'Strong': 'bg-primary-50 text-primary-700',        // Very light bg, dark text
    'Good': 'bg-primary-50 text-primary-700',          // Same (consistency)
    'Fair': 'bg-primary-50 text-primary-700',          // Same
    'Below Target': 'bg-primary-50 text-primary-800',  // Slightly darker text
    'Poor': 'bg-primary-50 text-primary-900'           // Darkest text
  }
  return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800'
}
</script>
