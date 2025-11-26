<template>
  <div class="bg-white rounded-lg px-1 mb-4">
    <!-- Header -->
    <div class="flex items-start justify-between mb-2">
      <div class="flex-1">
        <div class="flex items-center gap-3 mb-2">
          <span class="text-sm font-semibold text-gray-500">Q{{ question.number }}</span>
          <span
            :class="[
              'px-2.5 py-0.5 rounded text-xs font-medium',
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
    <div class="mb-2">
      <p class="text-gray-700 leading text-sm/6 whitespace-pre-line">
        {{ question.question_text }}
      </p>
    </div>

    <!-- Context Why -->
    <div class=" mb-2">
      <p class="text-xs bg-primary-50 rounded-lg p-2 text-primary-800">
        {{ question.context_why }}
      </p>
    </div>

    <!-- Examples (collapsible) -->
    <div v-if="question.examples && question.examples.length > 0" class="">
      <HbButton
        @click="showExamples = !showExamples"
        variant="link"
        size="sm"
      >
        Examples
        <template #trailing-icon>
          <svg
            v-if="showExamples"
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
          </svg>
          <svg
            v-else
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
        </template>
      </HbButton>

      <transition name="slide-fade">
        <div v-if="showExamples" class="mt-3 pl-2">
          <ul class="space-y-2">
            <li
              v-for="(example, index) in question.examples"
              :key="index"
              class="text-sm text-gray-600 flex items-start gap-2"
            >
              <HbIcon name="asterix" :width="10" :height="10" class="flex-shrink-0 mt-1" />
              <span>{{ example }}</span>
            </li>
          </ul>

          <!-- Zero Experience Button -->
          <div class="mt-2 mb-2">
            <HbButton
              @click="$emit('need-help')"
              variant="link"
              size="sm"
            >
              I have no experience
            </HbButton>

          </div>
        </div>
      </transition>
    </div>

    <!-- Answer Slot -->
    <div class="pt-1">
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

const showExamples = ref(true)

const priorityColorClass = computed(() => {
  switch (props.question.priority) {
    case 'CRITICAL':
      return 'bg-red-100 text-red-600'
    case 'HIGH':
      return 'bg-orange-100 text-orange-600'
    case 'MEDIUM':
      return 'bg-yellow-100 text-yellow-600'
    default:
      return 'bg-gray-100 text-gray-600'
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
