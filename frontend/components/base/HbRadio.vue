<template>
  <div class="hb-radio-group" :class="{ 'is-vertical': vertical }">
    <label v-if="label" class="hb-radio-group-label">
      {{ label }}<span v-if="required" class="required">*</span>
    </label>
    
    <div class="hb-radio-options" :class="{ 'vertical': vertical }">
      <div 
        v-for="(option, index) in options" 
        :key="index" 
        class="hb-radio-option"
        :class="{ 'selected': isSelected(option) }"
        @click="selectOption(option)"
      >
        <div class="hb-radio-button">
          <div class="outer-circle">
            <div v-if="isSelected(option)" class="inner-circle"></div>
          </div>
        </div>
        
        <div class="hb-radio-content">
          <div class="hb-radio-label">{{ getOptionLabel(option) }}</div>
          <div v-if="getOptionDescription(option)" class="hb-radio-description">
            {{ getOptionDescription(option) }}
          </div>
        </div>
      </div>
    </div>
    
    <span v-if="error" class="error-msg">{{ error }}</span>
    <span v-else-if="helperText" class="helper-text">{{ helperText }}</span>
  </div>
</template>

<script setup lang="ts">
// @ts-strict

interface OptionObject {
  [key: string]: any
  description?: string
}

interface Props {
  modelValue?: string | number | OptionObject | null
  options: (string | number | OptionObject)[]
  label?: string
  optionLabel?: string
  optionValue?: string
  vertical?: boolean
  required?: boolean
  error?: string
  helperText?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  label: '',
  optionLabel: 'label',
  optionValue: 'value',
  vertical: false,
  required: false,
  error: '',
  helperText: ''
});

interface Emits {
  (e: 'update:modelValue', value: string | number | OptionObject): void
}

const emit = defineEmits<Emits>();

const isSelected = (option: string | number | OptionObject): boolean => {
  if (typeof option === 'object' && option !== null) {
    if (typeof props.modelValue === 'object' && props.modelValue !== null) {
      return JSON.stringify((option as OptionObject)[props.optionValue]) === JSON.stringify(props.modelValue);
    }
    return (option as OptionObject)[props.optionValue] === props.modelValue;
  }
  return option === props.modelValue;
};

const selectOption = (option: string | number | OptionObject): void => {
  const value = typeof option === 'object' && option !== null
    ? (option as OptionObject)[props.optionValue]
    : option;

  emit('update:modelValue', value);
};

const getOptionLabel = (option: string | number | OptionObject): string => {
  if (typeof option === 'object' && option !== null) {
    return (option as OptionObject)[props.optionLabel];
  }
  return String(option);
};

const getOptionDescription = (option: string | number | OptionObject): string | null => {
  if (typeof option === 'object' && option !== null && (option as OptionObject).description) {
    return (option as OptionObject).description;
  }
  return null;
};

</script>

<style lang="scss" scoped>
.hb-radio-group {
  margin-bottom: 1rem;
  
  &-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    font-size: 0.875rem;
    color: #1f2937; /* gray-800 */
    
    .required {
      color: #ef4444; /* red-500 */
      margin-left: 0.125rem;
    }
  }
}

.hb-radio-options {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  
  &.vertical {
    flex-direction: column;
  }
}

.hb-radio-option {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: #f9fafb; /* gray-50 */
  }
  
  &.selected {
    .hb-radio-button {
      .outer-circle {
        border-color: #0ea5e9; /* primary-500 */
      }
    }
    
    .hb-radio-label {
      color: #0ea5e9; /* primary-500 */
    }
  }
}

.hb-radio-button {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;
  margin-top: 0.125rem;
  
  .outer-circle {
    width: 1.25rem;
    height: 1.25rem;
    border-radius: 50%;
    border: 1px solid #9ca3af; /* gray-400 */
    display: flex;
    align-items: center;
    justify-content: center;
    transition: border-color 0.2s ease;
  }
  
  .inner-circle {
    width: 0.625rem;
    height: 0.625rem;
    border-radius: 50%;
    background-color: #0ea5e9; /* primary-500 */
    transition: transform 0.2s ease;
    transform-origin: center;
    animation: pulse 0.3s ease-out;
  }
}

.hb-radio-content {
  display: flex;
  flex-direction: column;
}

.hb-radio-label {
  font-weight: 500;
  color: #1f2937; /* gray-800 */
  transition: color 0.2s ease;
}

.hb-radio-description {
  font-size: 0.75rem;
  color: #6b7280; /* gray-500 */
  margin-top: 0.25rem;
}

.error-msg {
  display: block;
  color: #ef4444; /* red-500 */
  font-size: 0.75rem;
  margin-top: 0.5rem;
}

.helper-text {
  display: block;
  color: #6b7280; /* gray-500 */
  font-size: 0.75rem;
  margin-top: 0.5rem;
}

@keyframes pulse {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
