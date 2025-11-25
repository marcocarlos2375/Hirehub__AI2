<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-4">
    <!-- Header -->
    <div class="flex items-start justify-between mb-4">
      <div class="flex-1">
        <div class="flex items-center gap-3 mb-2">
          <span class="text-sm font-semibold text-gray-500">Q{{ question.number }}</span>
          <span
            :class="[
              'px-2.5 py-0.5 rounded-full text-xs font-medium',
              priorityColorClass
            ]"
          >
            {{ question.priority }}
          </span>
          <span class="text-xs text-green-600 font-medium">
            {{ question.impact }}
          </span>
        </div>
        <h3 class="text-lg font-semibold text-gray-900">
          {{ question.title }}
        </h3>
      </div>
    </div>

    <!-- Question Text -->
    <div class="mb-4">
      <p class="text-gray-700 leading-relaxed whitespace-pre-line">
        {{ question.question_text }}
      </p>
    </div>

    <!-- Context Why -->
    <div class="bg-blue-50 border-l-4 border-blue-400 p-3 mb-4">
      <p class="text-sm text-blue-800">
        <span class="font-medium">Why we're asking:</span> {{ question.context_why }}
      </p>
    </div>

    <!-- Examples (collapsible) -->
    <div v-if="question.examples && question.examples.length > 0" class="mb-4">
      <HbButton
        @click="showExamples = !showExamples"
        variant="link"
        size="sm"
      >
        <template #leading-icon>
          <svg
            :class="['w-4 h-4 transition-transform', showExamples ? 'rotate-90' : '']"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </template>
        {{ showExamples ? 'Hide' : 'Show' }} examples
      </HbButton>

      <transition name="slide-fade">
        <div v-if="showExamples" class="mt-3 pl-6">
          <ul class="space-y-2">
            <li
              v-for="(example, index) in question.examples"
              :key="index"
              class="text-sm text-gray-600 flex items-start gap-2"
            >
              <span class="text-gray-400 mt-0.5">•</span>
              <span>{{ example }}</span>
            </li>
          </ul>

          <!-- Zero Experience Button -->
          <div class="mt-4 pt-3 border-t border-gray-200">
            <HbButton
              @click="$emit('need-help')"
              variant="secondary"
              size="lg"
              class="w-full"
            >
              <template #leading-icon>
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </template>
              I have zero experience/projects with this skill
            </HbButton>
            <p class="text-xs text-gray-500 text-center mt-2">
              Get personalized learning resources and create a learning plan
            </p>
          </div>
        </div>
      </transition>
    </div>

    <!-- Answer Slot -->
    <div class="pt-4 border-t border-gray-200">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { QuestionItem } from '~/composables/analysis/useAnalysisState'

interface Props {
  question: QuestionItem
}

const props = defineProps<Props>()

const showExamples = ref(false)

const priorityColorClass = computed(() => {
  switch (props.question.priority) {
    case 'CRITICAL':
      return 'bg-red-100 text-red-800'
    case 'HIGH':
      return 'bg-orange-100 text-orange-800'
    case 'MEDIUM':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
})
</script>

<style scoped>
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
