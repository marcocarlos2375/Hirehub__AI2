<template>
  <div class="feedback-submitted-slide">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <HbLoadingOverlay
        :show="true"
        message="Formatting your professional answer..."
      />
    </div>

    <!-- Formatted Answer Display -->
    <div v-else class="answer-display">
      

      <!-- Display Formatted Answer in Read-Only AnswerInput -->
      <div class="formatted-answer-container">
        <label class="block text-sm font-medium text-gray-900 mb-2">
          Formatted Answer
        </label>
        <div class="answer-preview">
          <pre class="whitespace-pre-wrap text-sm text-gray-800">{{ formattedAnswer }}</pre>
        </div>
      </div>

      <!-- Action Button -->
      <div class="flex justify-end mt-6">
        <HbButton @click="handleContinue" variant="primary">
          Continue to Next Question
          <svg class="h-4 w-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </HbButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  formattedAnswer?: string
  loading: boolean
}

interface Emits {
  (e: 'continue'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const handleContinue = () => {
  emit('continue')
}
</script>

<style scoped>
.feedback-submitted-slide {
  padding: 1.5rem;
  min-height: 400px;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.answer-display {
  width: 100%;
}

.formatted-answer-container {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.answer-preview {
  background: #f9fafb;
  border-radius: 0.375rem;
  padding: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.answer-preview pre {
  font-family: inherit;
  margin: 0;
  line-height: 1.6;
}
</style>
