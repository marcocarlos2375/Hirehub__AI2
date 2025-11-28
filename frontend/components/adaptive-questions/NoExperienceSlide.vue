<template>
  <div
    class="no-experience-slide"
    v-motion
    :initial="slideAnimations.slideLeft.value.initial"
    :enter="slideAnimations.slideLeft.value.enter"
    :leave="slideAnimations.slideLeft.value.leave"
  >
    <div class="content-wrapper">
      <!-- Title -->
      <h3 class="title">
        No Experience with {{ question.title }}?
      </h3>

      <!-- Subtitle -->
      <p class="subtitle">
        Let us know your learning intentions so we can better assist you
      </p>

      <!-- Card Selection -->
      <div class="card-selection">
        <HbCardSelect
          v-model="selectedOption"
          :options="learningOptions"
          :columns="1"
          option-label="label"
          option-value="value"
        >
          <template #card="{ option }">
            <div class="option-content">
              <!-- Left: Icon -->
              <div class="option-icon">
                <HbIcon :name="(option as LearningOption).icon" :width="32" :height="32" />
              </div>

              <!-- Middle: Text content -->
              <div class="option-text">
                <div class="option-label">{{ (option as LearningOption).label }}</div>
                <div class="option-description">{{ (option as LearningOption).description }}</div>
              </div>

              <!-- Right: Check icon (only shown when selected) -->
              <div v-if="isSelected(option as LearningOption)" class="option-check">
                <HbIcon name="check-circle" :width="24" :height="24" />
              </div>
            </div>
          </template>
        </HbCardSelect>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useSlideAnimations } from '~/composables/animation/useSlideAnimations'
import type { QuestionItem } from '~/composables/analysis/useAnalysisState'

interface Props {
  question: QuestionItem
  isActive: boolean
}

interface LearningOption {
  value: string
  label: string
  description: string
  icon: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'learning-choice', questionId: string, choice: 'learn-now' | 'open-later'): void
}>()

const slideAnimations = useSlideAnimations()

// Selected option (v-model for HbCardSelect)
const selectedOption = ref<string | null>(null)

// Learning options for card selection
const learningOptions: LearningOption[] = [
  {
    value: 'learn-now',
    label: 'I want to learn this now',
    description: 'Get personalized course recommendations and add "Currently Learning" to your resume',
    icon: 'graduation-cap'
  },
  {
    value: 'open-later',
    label: 'Open to learning later',
    description: 'Add "Willing to Learn" to your resume for this skill',
    icon: 'clock'
  }
]

// Check if option is selected
const isSelected = (option: LearningOption) => {
  // Handle both cases: selectedOption could be a string (value) or the whole object
  if (typeof selectedOption.value === 'string') {
    return selectedOption.value === option.value
  }
  if (typeof selectedOption.value === 'object' && selectedOption.value !== null) {
    return (selectedOption.value as any).value === option.value
  }
  return false
}

// Watch for selection changes and emit to parent
watch(selectedOption, (newValue) => {
  if (newValue) {
    emit('learning-choice', props.question.id, newValue as 'learn-now' | 'open-later')
  }
})
</script>

<style scoped>
.no-experience-slide {
  will-change: transform, opacity;
  transform: translateZ(0);
  backface-visibility: hidden;
  padding: 1.7rem 0.8rem;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827; /* gray-900 */
  margin-bottom: 0.75rem;
}

.subtitle {
  font-size: 1rem;
  color: #6b7280; /* gray-500 */
  margin-bottom: 2rem;
  max-width: 600px;
}

.card-selection {
  width: 100%;
  max-width: 700px;
}

/* Remove box shadow from cards */
.card-selection :deep(.hb-card-select-option) {
  box-shadow: none !important;
}

.option-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
}

.option-icon {
  flex-shrink: 0;
  color: var(--primary-500);
}

.option-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  text-align: left;
}

.option-label {
  font-size: 1rem;
  font-weight: 600;
  color: #111827; /* gray-900 */
  line-height: 1.3;
}

.option-description {
  font-size: 0.875rem;
  color: #6b7280; /* gray-500 */
  line-height: 1.4;
}

.option-check {
  flex-shrink: 0;
  color: var(--primary-500);
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .title {
    font-size: 1.25rem;
  }

  .subtitle {
    font-size: 0.875rem;
  }

  .option-content {
    padding: 0.75rem;
  }

  .option-label {
    font-size: 0.9375rem;
  }

  .option-description {
    font-size: 0.8125rem;
  }
}
</style>
