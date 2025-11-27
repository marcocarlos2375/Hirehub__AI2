<template>
  <div class=" py-4 bg-white border-b ">
    <!-- Header with sidebar-style number -->
    <div class="flex items-start gap-3 mb-3">
      <!-- Sidebar-style step number -->
      <div class="step-number">
        <span class="relative z-10">{{ index + 1 }}</span>
      </div>

      <div class="flex-1">
        <p class="text-base text-gray-800 font-medium mb-1">
          {{ title }}
        </p>

        <p v-if="detail" class="text-xs text-gray-600">
          {{ detail }}
        </p>
      </div>
    </div>

    <!-- Textarea -->
    <HbInput
      :model-value="modelValue"
      @update:model-value="handleInput"
      type="textarea"
      :placeholder="placeholder"
      appearance="white"
      size="md"
      :disabled="disabled"
      class="w-full"
    />

    <!-- Character counter -->
    <div class="mt-2 flex items-center justify-between text-xs text-gray-500">
      <span>{{ characterCount }} characters</span>

      <span v-if="characterCount < 40" class="text-amber-500 flex items-center gap-1">
       
        Add more details (min 40 chars)
      </span>

      <span v-else class="text-green-600 flex items-center gap-1">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        Good detail level
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  suggestion: string        // Full suggestion text from AI
  index: number            // 0-based index for numbering
  modelValue: string       // v-model binding for textarea
  disabled?: boolean       // Disable during API calls
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

// Parse suggestion into title and detail
const title = computed(() => {
  const colonIndex = props.suggestion.indexOf(':')
  if (colonIndex > 0) {
    return props.suggestion.substring(0, colonIndex).trim()
  }
  return props.suggestion
})

const detail = computed(() => {
  const colonIndex = props.suggestion.indexOf(':')
  if (colonIndex > 0 && colonIndex < props.suggestion.length - 1) {
    return props.suggestion.substring(colonIndex + 1).trim()
  }
  return ''
})

// Simple placeholder
const placeholder = computed(() => {
  return 'Share additional relevant information...'
})

// Character count
const characterCount = computed(() => {
  return props.modelValue?.length || 0
})

// Handle textarea input
const handleInput = (value: string | number) => {
  emit('update:modelValue', String(value))
}
</script>

<style scoped>
/* Sidebar-style step number (matching analyze.vue active state) */
.step-number {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
  background-color: var(--primary-400);
  color: white;
  flex-shrink: 0;
  position: relative;
}
</style>
