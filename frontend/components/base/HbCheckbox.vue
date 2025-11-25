<template>
  <div class="hb-checkbox-group" :class="{ 'is-vertical': vertical }">
    <label v-if="label" class="hb-checkbox-group-label">
      {{ label }}<span v-if="required" class="required">*</span>
    </label>
    
    <div class="hb-checkbox-options" :class="{ 'vertical': vertical }">
      <div 
        v-for="(option, index) in options" 
        :key="index" 
        class="hb-checkbox-option"
        :class="{ 'selected': isSelected(option) }"
        @click="toggleOption(option)"
      >
        <div class="hb-checkbox-button">
          <div class="checkbox-square" :class="{ 'checked': isSelected(option) }">
            <svg v-if="isSelected(option)" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="check-icon">
              <path fill-rule="evenodd" d="M19.916 4.626a.75.75 0 01.208 1.04l-9 13.5a.75.75 0 01-1.154.114l-6-6a.75.75 0 011.06-1.06l5.353 5.353 8.493-12.739a.75.75 0 011.04-.208z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>
        
        <div class="hb-checkbox-content">
          <div class="hb-checkbox-label">{{ getOptionLabel(option) }}</div>
          <div v-if="getOptionDescription(option)" class="hb-checkbox-description">
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
  modelValue?: any[]
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
  modelValue: () => [],
  label: '',
  optionLabel: 'label',
  optionValue: 'value',
  vertical: false,
  required: false,
  error: '',
  helperText: ''
});

interface Emits {
  (e: 'update:modelValue', value: any[]): void
}

const emit = defineEmits<Emits>();

const getOptionValue = (option: string | number | OptionObject): any => {
  if (typeof option === 'object' && option !== null) {
    return (option as OptionObject)[props.optionValue];
  }
  return option;
};

const isSelected = (option: string | number | OptionObject): boolean => {
  const value = getOptionValue(option);
  return props.modelValue.some(item => {
    if (typeof item === 'object' && item !== null && typeof value === 'object' && value !== null) {
      return JSON.stringify(item) === JSON.stringify(value);
    }
    return item === value;
  });
};

const toggleOption = (option: string | number | OptionObject): void => {
  const value = getOptionValue(option);
  const newValue = [...props.modelValue];

  const index = newValue.findIndex(item => {
    if (typeof item === 'object' && item !== null && typeof value === 'object' && value !== null) {
      return JSON.stringify(item) === JSON.stringify(value);
    }
    return item === value;
  });

  if (index === -1) {
    newValue.push(value);
  } else {
    newValue.splice(index, 1);
  }

  emit('update:modelValue', newValue);
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
.hb-checkbox-group {
  margin-bottom: 1rem;
  
  &-label {
    display: block;
    margin-bottom: 0.5rem;
    font-size: var(--text-sm);
    color: var(--gray-900); /* gray-800 */
    
    .required {
      color: #ef4444; /* red-500 */
      margin-left: 0.125rem;
    }
  }
}

.hb-checkbox-options {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  
  &.vertical {
    flex-direction: column;
  }
}

.hb-checkbox-option {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: background-color 0.2s ease;
  
  &:hover {
  
    
    .checkbox-square {
      border-color: #0ea5e9; /* primary-500 */
    }
  }
  
  
}

.hb-checkbox-button {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;
  margin-top: 0.125rem;
  
  .checkbox-square {
    width: 1.25rem;
    height: 1.25rem;
    border-radius: 0.25rem;
    border: 1px solid #9ca3af; /* gray-400 */
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    position: relative;
    
    &.checked {
      background-color: #0ea5e9; /* primary-500 */
      border-color: #0ea5e9; /* primary-500 */
      
      .check-icon {
        color: white;
        animation: scale-in 0.2s ease-out forwards;
      }
    }
    
    .check-icon {
      width: 0.875rem;
      height: 0.875rem;
    }
  }
}

.hb-checkbox-content {
  display: flex;
  flex-direction: column;
}

.hb-checkbox-label {
  color: #1f2937; /* gray-800 */
  transition: color 0.2s ease;
  font-size: var(--text-sm);
}

.hb-checkbox-description {
  font-size: var(--text-xs);
  color: #6b7280; /* gray-500 */
  margin-top: 0.25rem;
}

.error-msg {
  display: block;
  color: #ef4444; /* red-500 */
  font-size: var(--text-xs);
  margin-top: 0.5rem;
}

.helper-text {
  display: block;
  color: #6b7280; /* gray-500 */
  font-size: var(--text-xs);
  margin-top: 0.5rem;
}

@keyframes scale-in {
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
