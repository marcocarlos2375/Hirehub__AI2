<template>
  <div class="space-y-6">
    <!-- Form Header -->
    <div class="bg-indigo-50 border border-indigo-200 rounded-lg p-6">
      <div class="flex items-start gap-3">
        <svg class="h-6 w-6 text-indigo-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
        <div>
          <h3 class="font-bold text-lg text-indigo-900">Tell us about your experience</h3>
          <p class="text-indigo-700 text-sm mt-1">
            Please provide detailed information to help us generate a professional answer for your resume.
          </p>
        </div>
      </div>
    </div>

    <!-- Dynamic Form Fields -->
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <div
        v-for="prompt in prompts"
        :key="prompt.id"
        class="bg-white border border-gray-200 rounded-lg p-6 hover:border-indigo-300 transition-colors"
      >
        <!-- Field Label -->
        <label :for="prompt.id" class="block text-sm font-medium text-gray-900 mb-2">
          {{ prompt.question }}
          <span v-if="prompt.required" class="text-red-500 ml-1">*</span>
        </label>

        <!-- Help Text -->
        <p v-if="prompt.help_text" class="text-sm text-gray-500 mb-3">
          {{ prompt.help_text }}
        </p>

        <!-- Text Input -->
        <input
          v-if="prompt.type === 'text'"
          :id="prompt.id"
          v-model="formData[prompt.id]"
          type="text"
          :placeholder="prompt.placeholder"
          :required="prompt.required"
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          :class="{ 'border-red-300 focus:ring-red-500': errors[prompt.id] }"
          @input="clearError(prompt.id)"
        />

        <!-- Textarea Input -->
        <textarea
          v-else-if="prompt.type === 'textarea'"
          :id="prompt.id"
          v-model="formData[prompt.id]"
          rows="4"
          :placeholder="prompt.placeholder"
          :required="prompt.required"
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
          :class="{ 'border-red-300 focus:ring-red-500': errors[prompt.id] }"
          @input="clearError(prompt.id)"
        />

        <!-- Number Input -->
        <input
          v-else-if="prompt.type === 'number'"
          :id="prompt.id"
          v-model.number="formData[prompt.id]"
          type="number"
          :placeholder="prompt.placeholder"
          :required="prompt.required"
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          :class="{ 'border-red-300 focus:ring-red-500': errors[prompt.id] }"
          @input="clearError(prompt.id)"
        />

        <!-- Select Input -->
        <select
          v-else-if="prompt.type === 'select'"
          :id="prompt.id"
          v-model="formData[prompt.id]"
          :required="prompt.required"
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          :class="{ 'border-red-300 focus:ring-red-500': errors[prompt.id] }"
          @change="clearError(prompt.id)"
        >
          <option value="" disabled selected>{{ prompt.placeholder || 'Select an option' }}</option>
          <option v-for="option in prompt.options" :key="option" :value="option">
            {{ option }}
          </option>
        </select>

        <!-- Multiselect Input -->
        <div v-else-if="prompt.type === 'multiselect'" class="space-y-2">
          <div class="max-h-60 overflow-y-auto border border-gray-300 rounded-lg p-3 space-y-2"
               :class="{ 'border-red-300': errors[prompt.id] }">
            <label
              v-for="option in prompt.options"
              :key="option"
              class="flex items-center gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer"
            >
              <input
                type="checkbox"
                :value="option"
                v-model="formData[prompt.id]"
                class="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                @change="clearError(prompt.id)"
              />
              <span class="text-sm text-gray-700">{{ option }}</span>
            </label>
          </div>
          <p v-if="Array.isArray(formData[prompt.id]) && formData[prompt.id].length > 0" class="text-xs text-gray-500">
            {{ formData[prompt.id].length }} selected
          </p>
        </div>

        <!-- Validation Error -->
        <p v-if="errors[prompt.id]" class="text-sm text-red-600 mt-2">
          {{ errors[prompt.id] }}
        </p>
      </div>

      <!-- Form Actions -->
      <div class="flex items-center justify-between pt-4 border-t border-gray-200">
        <button
          type="button"
          @click="resetForm"
          class="px-6 py-2.5 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
        >
          Reset Form
        </button>

        <button
          type="submit"
          :disabled="loading"
          class="px-8 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <svg v-if="loading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span v-if="loading">Generating Answer...</span>
          <span v-else>Generate Professional Answer</span>
        </button>
      </div>

      <!-- Progress Indicator -->
      <div v-if="loading" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-center gap-3">
          <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          <div class="text-sm text-blue-900">
            <p class="font-medium">AI is analyzing your responses...</p>
            <p class="text-blue-700 text-xs mt-1">This may take 3-5 seconds</p>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import type { DeepDivePrompt } from '~/types/adaptive-questions'

interface Props {
  prompts: DeepDivePrompt[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<{
  'submit-inputs': [data: Record<string, any>]
}>()

// Initialize form data based on prompts
const formData = ref<Record<string, any>>({})
const errors = ref<Record<string, string>>({})

// Initialize form data with proper types for each field
const initializeFormData = () => {
  const data: Record<string, any> = {}

  props.prompts.forEach(prompt => {
    if (prompt.type === 'multiselect') {
      data[prompt.id] = []
    } else if (prompt.type === 'number') {
      data[prompt.id] = ''
    } else {
      data[prompt.id] = ''
    }
  })

  formData.value = data
}

// Initialize on mount
onMounted(() => {
  initializeFormData()
})

// Reinitialize if prompts change
watch(() => props.prompts, () => {
  initializeFormData()
}, { deep: true })

const clearError = (fieldId: string) => {
  if (errors.value[fieldId]) {
    delete errors.value[fieldId]
  }
}

const validateForm = (): boolean => {
  errors.value = {}
  let isValid = true

  props.prompts.forEach(prompt => {
    if (prompt.required) {
      const value = formData.value[prompt.id]

      if (prompt.type === 'multiselect') {
        if (!Array.isArray(value) || value.length === 0) {
          errors.value[prompt.id] = 'Please select at least one option'
          isValid = false
        }
      } else if (prompt.type === 'number') {
        if (value === '' || value === null || value === undefined) {
          errors.value[prompt.id] = 'This field is required'
          isValid = false
        }
      } else {
        if (!value || (typeof value === 'string' && !value.trim())) {
          errors.value[prompt.id] = 'This field is required'
          isValid = false
        }
      }
    }
  })

  return isValid
}

const handleSubmit = () => {
  if (!validateForm()) {
    // Scroll to first error
    const firstErrorField = Object.keys(errors.value)[0]
    if (firstErrorField) {
      const element = document.getElementById(firstErrorField)
      element?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
    return
  }

  // Clean up the data before emitting
  const cleanData: Record<string, any> = {}
  Object.entries(formData.value).forEach(([key, value]) => {
    // Convert empty strings to actual empty strings, keep arrays as-is
    cleanData[key] = value
  })

  emit('submit-inputs', cleanData)
}

const resetForm = () => {
  initializeFormData()
  errors.value = {}
}
</script>
