<template>
  <div class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
    <div class="flex min-h-full items-center justify-center p-4">
      <!-- Modal Container -->
      <div class="relative bg-white rounded-2xl shadow-2xl max-w-2xl w-full" @click.stop>
        <!-- Header -->
        <div class="bg-gradient-to-r from-purple-600 to-indigo-600 px-8 py-6">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                <svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Experience Check
              </h2>
              <p class="text-purple-100 text-sm mt-1">Help us understand your background</p>
            </div>
            <button
              @click="$emit('close')"
              class="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="px-8 py-8">
          <!-- Gap Info -->
          <div class="bg-indigo-50 border border-indigo-200 rounded-lg p-6 mb-6">
            <h3 class="font-bold text-xl text-indigo-900 mb-2">{{ gapTitle }}</h3>
            <p class="text-indigo-700 text-sm">{{ gapDescription }}</p>
          </div>

          <!-- Question -->
          <div class="mb-8">
            <p class="text-lg text-gray-800 font-medium text-center">
              Do you have experience with <span class="text-purple-600 font-bold">{{ gapTitle }}</span>?
            </p>
          </div>

          <!-- Buttons -->
          <div class="grid grid-cols-1 gap-4">
            <!-- Yes Button -->
            <button
              @click="handleSelection('yes')"
              class="group relative px-6 py-5 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                  <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                    <svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div class="text-left">
                    <div class="font-bold text-lg">Yes, I have experience</div>
                    <div class="text-green-100 text-sm">We'll ask detailed questions about your experience</div>
                  </div>
                </div>
                <svg class="h-6 w-6 opacity-70 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>

            <!-- No Button -->
            <button
              @click="handleSelection('no')"
              class="group relative px-6 py-5 bg-gradient-to-r from-red-500 to-rose-600 text-white rounded-xl hover:from-red-600 hover:to-rose-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                  <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                    <svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                  <div class="text-left">
                    <div class="font-bold text-lg">No, I don't have experience</div>
                    <div class="text-red-100 text-sm">We'll suggest learning resources for this skill</div>
                  </div>
                </div>
                <svg class="h-6 w-6 opacity-70 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>

            <!-- Willing to Learn Button -->
            <button
              @click="handleSelection('willing_to_learn')"
              class="group relative px-6 py-5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                  <div class="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                    <svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                  <div class="text-left">
                    <div class="font-bold text-lg">Willing to learn</div>
                    <div class="text-blue-100 text-sm">We'll create a learning roadmap for this skill</div>
                  </div>
                </div>
                <svg class="h-6 w-6 opacity-70 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Background Overlay -->
    <div class="fixed inset-0 bg-black/50 -z-10" @click="$emit('close')"></div>
  </div>
</template>

<script setup lang="ts">
import type { ExperienceLevel } from '~/types/adaptive-questions'

interface Props {
  gapTitle: string
  gapDescription: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  'experience-selected': [level: ExperienceLevel]
}>()

const handleSelection = (level: ExperienceLevel) => {
  emit('experience-selected', level)
  emit('close')
}
</script>
