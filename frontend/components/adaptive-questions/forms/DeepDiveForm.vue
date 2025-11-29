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
        <HbInput
          v-if="prompt.type === 'text'"
          :id="prompt.id"
          v-model="formData[prompt.id]"
          type="text"
          :placeholder="prompt.placeholder"
          :required="prompt.required"
          :class="{ 'border-red-300': errors[prompt.id] }"
          @input="clearError(prompt.id)"
        />

        <!-- Textarea Input -->
        <HbInput
          v-else-if="prompt.type === 'textarea'"
          :id="prompt.id"
          v-model="formData[prompt.id]"
          type="textarea"
          :rows="4"
          :placeholder="prompt.placeholder"
          :required="prompt.required"
          :class="{ 'border-red-300': errors[prompt.id] }"
          @input="clearError(prompt.id)"
        />

        <!-- Number Input -->
        <HbInput
          v-else-if="prompt.type === 'number'"
          :id="prompt.id"
          v-model.number="formData[prompt.id]"
          type="number"
          :placeholder="prompt.placeholder"
          :required="prompt.required"
          :class="{ 'border-red-300': errors[prompt.id] }"
          @input="clearError(prompt.id)"
        />

        <!-- Select Input -->
        <HbSelect
          v-else-if="prompt.type === 'select'"
          :id="prompt.id"
          v-model="formData[prompt.id]"
          :options="getSelectOptions(prompt)"
          :required="prompt.required"
          :class="{ 'border-red-300': errors[prompt.id] }"
          @change="clearError(prompt.id)"
        />

        <!-- Multiselect Input -->
        <HbCheckbox
          v-else-if="prompt.type === 'multiselect'"
          v-model="formData[prompt.id]"
          :options="prompt.options || []"
          :error="errors[prompt.id]"
          @update:modelValue="clearError(prompt.id)"
        />

        <!-- Validation Error -->
        <p v-if="errors[prompt.id]" class="text-sm text-red-600 mt-2">
          {{ errors[prompt.id] }}
        </p>
      </div>

      <!-- Form Actions -->
      <div class="flex items-center justify-between pt-4 border-t border-gray-200">
        <HbButton
          type="button"
          @click="resetForm"
          variant="outline"
        >
          Reset Form
        </HbButton>

        <HbButton
          type="submit"
          :disabled="loading"
          :loading="loading"
          variant="primary"
          size="lg"
        >
          <span v-if="loading">Generating Answer...</span>
          <span v-else>Generate Professional Answer</span>
        </HbButton>
      </div>

      <!-- Progress Indicator -->
      <div v-if="loading" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-center gap-3">
          <HbSpinner size="sm" />
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
import type { DeepDiveFormProps, DeepDiveFormEmits } from '~/types/component-props'
import type { DeepDivePrompt } from '~/types/adaptive-questions'

const props = withDefaults(defineProps<DeepDiveFormProps>(), {
  loading: false
})

const emit = defineEmits<DeepDiveFormEmits>()

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

// Transform select options to HbSelect format
const getSelectOptions = (prompt: DeepDivePrompt) => {
  if (!prompt.options || !Array.isArray(prompt.options)) return []

  // Add placeholder as first option
  const options = [
    { value: '', label: prompt.placeholder || 'Select an option' }
  ]

  // Convert array of strings to {value, label} format
  prompt.options.forEach((option: string) => {
    options.push({ value: option, label: option })
  })

  return options
}

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
