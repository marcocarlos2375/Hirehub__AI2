<template>
  <div class=" py-2 bg-white">
    <!-- Header with sidebar-style number -->
    <div class="flex items-start gap-3 mb-3">
      <!-- Sidebar-style step number -->
      <div class="step-number">
        <span class="relative z-10">{{ index + 1 }}</span>
      </div>

      <div class="flex-1">
        <!-- Title with icon for clarity -->
        <div class="flex items-center gap-2 mb-2">

          <p class="text-base text-gray-900 title">
            {{ title }}
          </p>
        </div>


      </div>
    </div>
    <!-- Examples as dash list -->
    <div v-if="examplesList.length > 0" class="space-y-1 mb-2">
      <div v-for="(example, idx) in examplesList" :key="idx" class="example-item">
        <span class="text-xs text-gray-600">{{ example }}</span>
      </div>
    </div>

    <!-- Textarea -->
    <HbInput :model-value="modelValue" @update:model-value="handleInput" type="text" :placeholder="placeholder"
      appearance="white" size="md" :disabled="disabled" class="w-full" />

    <!-- Character counter -->
    <div class="mt-2 flex items-center justify-between text-xs text-gray-500">
      <span>{{ characterCount }} characters</span>

      <span v-if="characterCount < 40" class="text-amber-500 flex items-center gap-1">

        Add more details (min 40 chars)
      </span>

      <span v-else class="text-green-600 flex items-center gap-1">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clip-rule="evenodd" />
        </svg>
        Good detail level
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ImprovementSuggestion } from '~/types/adaptive-questions'

interface Props {
  suggestion: ImprovementSuggestion | string  // Structured suggestion object from AI or legacy string
  index: number                               // 0-based index for numbering
  modelValue: string                          // v-model binding for textarea
  disabled?: boolean                          // Disable during API calls
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

// Check if suggestion is a string (legacy format) or object (new format)
const isLegacyFormat = computed(() => typeof props.suggestion === 'string')

// Get title - handle both formats
const title = computed(() => {
  if (isLegacyFormat.value) {
    // Legacy format: parse string by splitting on first period or colon
    const str = props.suggestion as string
    const periodIndex = str.indexOf('.')
    const colonIndex = str.indexOf(':')

    if (periodIndex > 0 && (colonIndex === -1 || periodIndex < colonIndex)) {
      return str.substring(0, periodIndex).trim()
    } else if (colonIndex > 0) {
      return str.substring(0, colonIndex).trim()
    }
    return str
  } else {
    // New format: get from object
    return (props.suggestion as ImprovementSuggestion).title
  }
})

// Get examples - handle both formats
const detail = computed(() => {
  if (isLegacyFormat.value) {
    // Legacy format: get text after first period or colon
    const str = props.suggestion as string
    const periodIndex = str.indexOf('.')
    const colonIndex = str.indexOf(':')

    if (periodIndex > 0 && periodIndex < str.length - 1 && (colonIndex === -1 || periodIndex < colonIndex)) {
      return str.substring(periodIndex + 1).trim()
    } else if (colonIndex > 0 && colonIndex < str.length - 1) {
      return str.substring(colonIndex + 1).trim()
    }
    return ''
  } else {
    // New format: get from object
    return (props.suggestion as ImprovementSuggestion).examples
  }
})

// Parse examples into list for display
const examplesList = computed(() => {
  if (!detail.value) return []

  // If detail is already an array (new format), return it directly
  if (Array.isArray(detail.value)) {
    return detail.value
  }

  // Legacy string format: split by ' or ' to separate multiple examples
  // Remove leading "Add details like " if present
  const cleanedDetail = detail.value.replace(/^Add details like ['"]?/i, '').replace(/['"]?$/, '')

  // Split on patterns like:
  // - " or '"
  // - "' or '"
  // - "or"
  const examples = cleanedDetail.split(/['"]?\s+or\s+['"]/i)

  return examples
    .map(ex => ex.trim())
    .map(ex => ex.replace(/^['"]|['"]$/g, '')) // Remove leading/trailing quotes
    .filter(ex => ex.length > 0)
})

// Get placeholder from help_text
const placeholder = computed(() => {
  if (isLegacyFormat.value) {
    return 'Share additional relevant information...'
  } else {
    return (props.suggestion as ImprovementSuggestion).help_text || 'Share additional relevant information...'
  }
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

/* Example item with dash before */
.example-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.example-item::before {
  content: "-";
  color: var(--primary-400);
  flex-shrink: 0;
  line-height: 1;
}
.title{
  font-weight: 500;
  margin-top: 2px;
}
</style>
