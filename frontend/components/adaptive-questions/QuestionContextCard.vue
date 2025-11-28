<template>
  <div :class="variantClasses.padding">
    <!-- Header Row -->
    <div class="flex items-start justify-between mb-2">
      <!-- Left: Question Metadata -->
      <div class="flex-1">
        <div class="flex items-center gap-3 mb-2">
          <!-- Q Number -->
          <span :class="variantClasses.qNumber">
            Q{{ question.number }}
          </span>

          <!-- Priority Badge -->
          <HbBadge
            :variant="priorityBadgeVariant(question.priority)"
            mode="light"
            size="sm"
            rounded="md"
            class="p-1"
          >
            {{ question.priority }}
          </HbBadge>

          <!-- Impact (optional) -->
          <span
            v-if="showImpact"
            :class="variantClasses.impact"
          >
            {{ question.impact }}
          </span>
        </div>

        <!-- Title -->
        <h3 :class="variantClasses.title">
          {{ question.title }}
        </h3>
      </div>

      <!-- Right: Navigation (optional) -->
      <div v-if="showPrevious || showNext || (isLastQuestion && !showNext)" class="flex items-center gap-2 ml-4">
        <HbButton
          v-if="showPrevious"
          @click="emit('navigate', 'previous')"
          variant="ghost"
          size="sm"
          class="!p-2"
          title="Previous question"
        >
          <template #leading-icon>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </template>
        </HbButton>

        <HbButton
          v-if="isLastQuestion && !showNext"
          @click="emit('submit-all')"
          variant="primary"
          size="sm"
          :disabled="!allAnswered"
        >
          Submit All
        </HbButton>

        <HbButton
          v-else-if="showNext"
          @click="emit('navigate', 'next')"
          variant="ghost"
          size="sm"
          class="!p-2"
          title="Next question"
        >
          <template #leading-icon>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </template>
        </HbButton>
      </div>
    </div>

    <!-- Question Text -->
    <div :class="variantClasses.questionTextWrapper">
      <p :class="variantClasses.questionText">
        {{ question.question_text }}
      </p>
    </div>

    <!-- Context Why (optional) -->
    <div
      v-if="showContextWhy && question.context_why"
      :class="variantClasses.contextWhy"
    >
      <p class="text-xs bg-primary-50 rounded-lg p-2 text-primary-800">
        {{ question.context_why }}
      </p>
    </div>

    <!-- Examples (optional, collapsible) -->
    <div
      v-if="showExamples && question.examples && question.examples.length > 0"
      :class="variantClasses.examples"
    >
      <HbButton
        @click="examplesExpanded = !examplesExpanded"
        variant="link"
        size="sm"
      >
        Examples
        <template #trailing-icon>
          <svg
            v-if="examplesExpanded"
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
        <div v-if="examplesExpanded" class="mt-3 pl-2">
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

          <!-- "Need Help" Button -->
          <div class="mt-2 mb-2">
            <HbButton
              @click="emit('need-help')"
              variant="link"
              size="sm"
            >
              I have no experience
            </HbButton>
          </div>
        </div>
      </transition>
    </div>

    <!-- Default Slot (for answer input) -->
    <div v-if="$slots.default" :class="variantClasses.slotWrapper">
      <slot />
    </div>

    <!-- Actions Slot (for custom buttons) -->
    <div v-if="$slots.actions" class="pt-3">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { QuestionItem } from '~/composables/analysis/useAnalysisState'
import { usePriorityStyles } from '~/composables/ui/usePriorityStyles'

interface Props {
  question: QuestionItem                 // Required question data
  variant?: 'compact' | 'default' | 'full'  // Layout density

  // Optional sections (granular control)
  showImpact?: boolean                   // Show impact label
  showContextWhy?: boolean               // Show context_why section
  showExamples?: boolean                 // Show collapsible examples

  // Navigation (for QuestionCard replacement)
  showPrevious?: boolean                 // Show previous arrow
  showNext?: boolean                     // Show next arrow
  isLastQuestion?: boolean               // Show "Submit All" button
  allAnswered?: boolean                  // Enable "Submit All"
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  showImpact: true,
  showContextWhy: false,
  showExamples: false,
  showPrevious: false,
  showNext: false,
  isLastQuestion: false,
  allAnswered: false
})

const emit = defineEmits<{
  (e: 'navigate', direction: 'previous' | 'next'): void
  (e: 'submit-all'): void
  (e: 'need-help'): void
}>()

const { priorityBadgeVariant } = usePriorityStyles()
const examplesExpanded = ref(true)

const variantClasses = computed(() => {
  const variants = {
    compact: {
      padding: 'px-3 py-2',
      qNumber: 'text-xs font-semibold text-gray-500',
      impact: 'text-xs text-green-600 font-medium',
      title: 'text-base font-semibold text-gray-900',
      questionTextWrapper: 'mb-1',
      questionText: 'text-sm text-gray-700 leading-relaxed',
      contextWhy: 'mb-1',
      examples: '',
      slotWrapper: 'pt-1'
    },
    default: {
      padding: 'px-1 py-5',
      qNumber: 'text-sm font-semibold text-gray-500',
      impact: 'text-xs text-green-600 font-medium',
      title: 'text-lg font-semibold text-gray-900 mb-2',
      questionTextWrapper: 'mb-3',
      questionText: 'text-sm text-gray-700 leading-relaxed',
      contextWhy: 'mb-2',
      examples: '',
      slotWrapper: 'pt-1'
    },
    full: {
      padding: 'px-1',
      qNumber: 'text-sm font-semibold text-gray-500',
      impact: 'text-xs text-green-600 font-medium',
      title: 'text-lg font-semibold text-gray-900',
      questionTextWrapper: 'mb-2',
      questionText: 'text-gray-700 leading text-sm/6 whitespace-pre-line',
      contextWhy: 'mb-2',
      examples: '',
      slotWrapper: 'pt-1'
    }
  }

  return variants[props.variant]
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
