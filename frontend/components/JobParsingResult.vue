<template>
  <div class="space-y-6">
    <!-- Header with stats -->
    <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-200">
      <div class="flex items-center gap-3">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
          <svg class="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          Parsed Successfully
        </span>
        <span v-if="timeSeconds" class="text-sm text-gray-600">
          <span class="font-medium">{{ timeSeconds }}s</span>
        </span>
      </div>
    </div>

    <!-- Two-Column Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Column: Key Information (30%) -->
      <div class="lg:col-span-1 space-y-4">
        <!-- Company & Position Card -->
        <div class="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg p-6 border border-indigo-100">
          <div class="mb-4">
            <h2 class="text-2xl font-bold text-gray-900 mb-1">{{ data.position_title || 'N/A' }}</h2>
            <p class="text-lg text-indigo-700 font-medium">{{ data.company_name || 'Company not specified' }}</p>
          </div>

          <!-- Location & Work Mode -->
          <div class="space-y-2 text-sm">
            <div v-if="data.location" class="flex items-center text-gray-700">
              <svg class="h-4 w-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {{ data.location }}
            </div>
            <div v-if="data.work_mode" class="flex items-center text-gray-700">
              <svg class="h-4 w-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              {{ data.work_mode }}
            </div>
          </div>
        </div>

        <!-- Salary & Experience Card -->
        <div class="bg-white rounded-lg p-6 border border-gray-200 space-y-4">
          <div v-if="data.salary_range">
            <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Salary Range</h3>
            <p class="text-lg font-bold text-green-600">{{ data.salary_range }}</p>
          </div>

          <div v-if="data.experience_years_required || data.experience_level">
            <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Experience</h3>
            <div class="text-sm text-gray-700">
              <p v-if="data.experience_years_required">{{ data.experience_years_required }}+ years</p>
              <p v-if="data.experience_level" class="capitalize">{{ data.experience_level }} level</p>
            </div>
          </div>
        </div>

        <!-- Quick Stats Card -->
        <div class="bg-white rounded-lg p-6 border border-gray-200">
          <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Quick Stats</h3>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div>
              <p class="text-2xl font-bold text-indigo-600">{{ data.hard_skills_required?.length || 0 }}</p>
              <p class="text-gray-600">Skills</p>
            </div>
            <div>
              <p class="text-2xl font-bold text-indigo-600">{{ data.responsibilities?.length || 0 }}</p>
              <p class="text-gray-600">Tasks</p>
            </div>
            <div>
              <p class="text-2xl font-bold text-indigo-600">{{ data.tech_stack?.length || 0 }}</p>
              <p class="text-gray-600">Tech</p>
            </div>
            <div>
              <p class="text-2xl font-bold text-indigo-600">{{ data.soft_skills_required?.length || 0 }}</p>
              <p class="text-gray-600">Soft Skills</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Detailed Sections (70%) -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Hard Skills Section -->
        <div v-if="data.hard_skills_required?.length" class="bg-white rounded-lg p-6 border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Technical Skills</h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="skill in data.hard_skills_required"
              :key="skill.skill"
              :class="getSkillBadgeClass(skill.priority)"
              class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border"
            >
              <span :class="getPriorityDotClass(skill.priority)" class="w-2 h-2 rounded-full mr-2"></span>
              {{ skill.skill }}
            </span>
          </div>
          <div class="mt-4 flex gap-4 text-xs text-gray-500">
            <div class="flex items-center">
              <span class="w-2 h-2 rounded-full bg-red-500 mr-1"></span> Critical
            </div>
            <div class="flex items-center">
              <span class="w-2 h-2 rounded-full bg-amber-500 mr-1"></span> Important
            </div>
            <div class="flex items-center">
              <span class="w-2 h-2 rounded-full bg-green-500 mr-1"></span> Nice-to-have
            </div>
          </div>
        </div>

        <!-- Soft Skills Section -->
        <div v-if="data.soft_skills_required?.length" class="bg-white rounded-lg p-6 border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Soft Skills & Qualities</h3>
          <ul class="space-y-2">
            <li v-for="(skill, index) in data.soft_skills_required" :key="index" class="flex items-start text-sm text-gray-700">
              <svg class="h-5 w-5 text-indigo-500 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              {{ skill }}
            </li>
          </ul>
        </div>

        <!-- Responsibilities Section -->
        <div v-if="data.responsibilities?.length" class="bg-white rounded-lg p-6 border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Key Responsibilities</h3>
          <ol class="space-y-3">
            <li v-for="(task, index) in data.responsibilities" :key="index" class="flex items-start text-sm text-gray-700">
              <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 text-xs font-semibold mr-3 mt-0.5 flex-shrink-0">
                {{ index + 1 }}
              </span>
              {{ task }}
            </li>
          </ol>
        </div>

        <!-- Tech Stack Section -->
        <div v-if="data.tech_stack?.length" class="bg-white rounded-lg p-6 border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Technology Stack</h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="tech in data.tech_stack"
              :key="tech"
              class="inline-flex items-center px-3 py-1 rounded-md text-sm font-medium bg-blue-50 text-blue-700 border border-blue-200"
            >
              {{ tech }}
            </span>
          </div>
        </div>

        <!-- Domain Expertise Section -->
        <div v-if="data.domain_expertise" class="bg-white rounded-lg p-6 border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Domain Expertise</h3>
          <div class="space-y-4">
            <div v-if="data.domain_expertise.industry?.length">
              <h4 class="text-sm font-semibold text-gray-700 mb-2">Industry</h4>
              <div class="flex flex-wrap gap-2">
                <span v-for="ind in data.domain_expertise.industry" :key="ind" class="px-3 py-1 rounded-md text-sm bg-purple-50 text-purple-700 border border-purple-200">
                  {{ ind }}
                </span>
              </div>
            </div>
            <div v-if="data.domain_expertise.specific_knowledge?.length">
              <h4 class="text-sm font-semibold text-gray-700 mb-2">Specific Knowledge</h4>
              <ul class="space-y-1">
                <li v-for="knowledge in data.domain_expertise.specific_knowledge" :key="knowledge" class="text-sm text-gray-600 flex items-start">
                  <span class="text-purple-500 mr-2">•</span>
                  {{ knowledge }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Implicit Requirements Section -->
        <div v-if="data.implicit_requirements?.length" class="bg-white rounded-lg p-6 border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Implicit Requirements</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
            <div v-for="req in data.implicit_requirements" :key="req" class="flex items-start text-sm text-gray-600">
              <span class="text-indigo-400 mr-2">▸</span>
              {{ req }}
            </div>
          </div>
        </div>

        <!-- Company Culture Section -->
        <div v-if="data.company_culture_signals?.length" class="bg-white rounded-lg p-6 border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Company Culture & Benefits</h3>
          <div class="space-y-2">
            <div v-for="culture in data.company_culture_signals" :key="culture" class="flex items-start text-sm text-gray-700">
              <span class="text-xl mr-2">✨</span>
              {{ culture }}
            </div>
          </div>
        </div>

        <!-- ATS Keywords Section -->
        <div v-if="data.ats_keywords?.length" class="bg-white rounded-lg p-6 border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">ATS Keywords</h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="keyword in data.ats_keywords"
              :key="keyword"
              class="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700 border border-gray-300"
            >
              {{ keyword }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ParsedJobResult } from '~/composables/useAnalysisState'

interface Props {
  data: ParsedJobResult
  timeSeconds?: number
}

defineProps<Props>()

const getSkillBadgeClass = (priority: string) => {
  const classes = {
    critical: 'bg-red-50 text-red-700 border-red-200',
    important: 'bg-amber-50 text-amber-700 border-amber-200',
    nice: 'bg-green-50 text-green-700 border-green-200'
  }
  return classes[priority.toLowerCase() as keyof typeof classes] || 'bg-gray-50 text-gray-700 border-gray-200'
}

const getPriorityDotClass = (priority: string) => {
  const classes = {
    critical: 'bg-red-500',
    important: 'bg-amber-500',
    nice: 'bg-green-500'
  }
  return classes[priority.toLowerCase() as keyof typeof classes] || 'bg-gray-500'
}
</script>
