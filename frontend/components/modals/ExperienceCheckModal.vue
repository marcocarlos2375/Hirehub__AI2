<template>
  <HbModal
    :modelValue="true"
    @update:modelValue="$emit('close')"
    title="Experience Check"
    size="lg"
  >
    <!-- Gap Info -->
    <div class="  rounded-lg p-3 mb-6">
      <h3 class="font-bold text-lg text-primary-900 mb-1"> Do you have experience with <span class="text-primary-600 font-bold">{{ gapTitle }}</span>?</h3>
      <p class="text-primary-700 text-sm">{{ gapDescription }}</p>
    </div>

    

    <!-- Buttons -->
    <div class="space-y-3">
      <!-- Yes Button -->
      <button
        @click="handleSelection('yes')"
        class="choice-button choice-button--yes"
      >
        <div class="choice-button__content">
          <div class="choice-button__title">Yes, I have experience</div>
          <div class="choice-button__description">We'll ask detailed questions about your experience</div>
        </div>
        <svg class="choice-button__arrow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>

      <!-- No Button -->
      <button
        @click="handleSelection('no')"
        class="choice-button choice-button--no"
      >
        <div class="choice-button__content">
          <div class="choice-button__title">No, I don't have experience</div>
          <div class="choice-button__description">We'll suggest learning resources for this skill</div>
        </div>
        <svg class="choice-button__arrow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>

      <!-- Willing to Learn Button -->
      <button
        @click="handleSelection('willing_to_learn')"
        class="choice-button choice-button--learn"
      >
        <div class="choice-button__content">
          <div class="choice-button__title">Willing to learn</div>
          <div class="choice-button__description">We'll create a learning roadmap for this skill</div>
        </div>
        <svg class="choice-button__arrow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  </HbModal>
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

<style scoped>
.choice-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border: none;
  border-radius: 0.5rem;
  background-color: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}

.choice-button:hover {
  transform: translateX(4px);
}

.choice-button__content {
  flex: 1;
  text-align: left;
}

.choice-button__title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.choice-button__description {
  font-size: 0.75rem;
  opacity: 0.7;
}

.choice-button__arrow {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  opacity: 0.5;
  transition: opacity 0.2s ease;
}

.choice-button:hover .choice-button__arrow {
  opacity: 1;
}

/* Yes variant - Green */
.choice-button--yes {
  color: #10b981;
}

.choice-button--yes:hover {
  color: #059669;
}

/* No variant - Red */
.choice-button--no {
  color: #ef4444;
}

.choice-button--no:hover {
  color: #dc2626;
}

/* Willing to Learn variant - Blue */
.choice-button--learn {
  color: #0ea5e9;
}

.choice-button--learn:hover {
  color: #0284c7;
}
</style>
