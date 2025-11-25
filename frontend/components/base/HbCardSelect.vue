<template>
  <div class="hb-card-select">
    <label v-if="label" class="hb-card-select-label">
      {{ label }}<span v-if="required">*</span>
    </label>
    
    <div class="hb-card-select-grid" :class="{ 'grid-cols-2': columns === 2, 'grid-cols-3': columns === 3, 'grid-cols-4': columns === 4 }">
      <HbCard
        v-for="(option, index) in options"
        :key="index"
        selectable
        hover
        @click="selectOption(option)"
        class="hb-card-select-option"
        :class="{
          'selected-card': isSelected(option)
        }"
      >
        <slot name="card" :option="option" :selected="isSelected(option)">
          <div class="card-option-content">
            <div v-if="getOptionProperty(option, 'icon') || getOptionProperty(option, 'image')" class="card-option-media">
              <img v-if="getOptionProperty(option, 'image')" :src="getOptionProperty(option, 'image')" :alt="getOptionLabel(option)" class="card-option-image">
              <div v-else-if="getOptionProperty(option, 'icon')" class="card-option-icon" v-html="getOptionProperty(option, 'icon')"></div>
            </div>
            <div class="card-option-label">{{ getOptionLabel(option) }}</div>
            <div v-if="getOptionProperty(option, 'description')" class="card-option-description">{{ getOptionProperty(option, 'description') }}</div>
          </div>
        </slot>
      </HbCard>
    </div>
    
    <span v-if="error" class="error-msg">
      {{ error }}
    </span>
    <span v-else-if="helperText" class="helper-text">
      {{ helperText }}
    </span>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { onMounted } from 'vue'
import HbCard from './HbCard.vue'

type ModelValue = string | number | object | any[]

interface OptionObject {
  [key: string]: any
}

interface Props {
  modelValue?: ModelValue | null
  options: (string | number | OptionObject)[]
  label?: string
  optionLabel?: string
  optionValue?: string
  multiple?: boolean
  required?: boolean
  columns?: 1 | 2 | 3 | 4
  error?: string
  helperText?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  label: '',
  optionLabel: 'label',
  optionValue: 'value',
  multiple: false,
  required: false,
  columns: 3,
  error: '',
  helperText: ''
});

interface Emits {
  (e: 'update:modelValue', value: ModelValue): void
}

const emit = defineEmits<Emits>();

onMounted(() => {
  // Select first option by default if none selected
  if (!props.modelValue && props.options && props.options.length > 0) {
    const firstOption = props.options[0];
    const value = typeof firstOption === 'object' ? (firstOption as OptionObject)[props.optionValue] : firstOption;
    emit('update:modelValue', value);
  }
});

const isSelected = (option: string | number | OptionObject): boolean => {
  if (props.multiple && Array.isArray(props.modelValue)) {
    if (typeof option === 'object' && option !== null) {
      return props.modelValue.some(val =>
        val === option ||
        (typeof val === 'object' && val !== null && (val as OptionObject)[props.optionValue] === (option as OptionObject)[props.optionValue])
      );
    }
    return props.modelValue.includes(option);
  }

  if (typeof option === 'object' && option !== null && props.modelValue !== null) {
    if (typeof props.modelValue === 'object') {
      return (props.modelValue as OptionObject)[props.optionValue] === (option as OptionObject)[props.optionValue];
    }
    return props.modelValue === (option as OptionObject)[props.optionValue];
  }

  return props.modelValue === option;
};

const selectOption = (option: string | number | OptionObject): void => {
  if (props.multiple) {
    let newValue: any[] = Array.isArray(props.modelValue) ? [...props.modelValue] : [];

    if (typeof option === 'object' && option !== null) {
      const optionValue = (option as OptionObject)[props.optionValue];
      const index = newValue.findIndex(val =>
        (typeof val === 'object' && val !== null && (val as OptionObject)[props.optionValue] === optionValue) ||
        val === optionValue
      );

      if (index > -1) {
        newValue.splice(index, 1);
      } else {
        newValue.push(option);
      }
    } else {
      const index = newValue.indexOf(option);
      if (index > -1) {
        newValue.splice(index, 1);
      } else {
        newValue.push(option);
      }
    }

    emit('update:modelValue', newValue);
  } else {
    const value = typeof option === 'object' && option !== null ?
      (props.optionValue ? (option as OptionObject)[props.optionValue] : option) :
      option;

    if (!isSelected(option)) {
      emit('update:modelValue', option);
    }
  }
};

const getOptionLabel = (option: string | number | OptionObject): string => {
  if (typeof option === 'object' && option !== null) {
    return (option as OptionObject)[props.optionLabel] || '';
  }
  return String(option);
};

const isOptionObject = (option: string | number | OptionObject): option is OptionObject => {
  return typeof option === 'object' && option !== null;
};

const getOptionProperty = (option: string | number | OptionObject, property: string): any => {
  if (isOptionObject(option)) {
    return (option as OptionObject)[property];
  }
  return undefined;
};

</script>

<style lang="scss" scoped>
.hb-card-select {
  width: 100%;

  .selected-card {
    border: 2px solid var(--primary-500);
  }

  
  &-label {
    display: block;
    margin-bottom: 0.5rem;
    color: #1f2937; /* gray-800 */
    font-weight: 500;
    font-size: 0.875rem;
    
    span {
      color: #ef4444; /* red-500 */
    }
  }
  
  &-grid {
    display: grid;
    gap: 1rem;
    
    &.grid-cols-2 {
      grid-template-columns: repeat(2, 1fr);
    }
    
    &.grid-cols-3 {
      grid-template-columns: repeat(3, 1fr);
    }
    
    &.grid-cols-4 {
      grid-template-columns: repeat(4, 1fr);
    }
    
    @media (max-width: 768px) {
      &.grid-cols-3, &.grid-cols-4 {
        grid-template-columns: repeat(2, 1fr);
      }
    }
    
    @media (max-width: 480px) {
      grid-template-columns: 1fr;
    }
  }
  
  &-option {
    height: 100%;
    
    &.selected-card {
      border: 2px solid #0ea5e9 !important; /* primary-500 */
    }
    
    .card-option-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: 1rem;
    }
    
    .card-option-media {
      margin-bottom: 0.75rem;
    }
    
    .card-option-image {
      width: 64px;
      height: 64px;
      object-fit: cover;
      border-radius: 0.375rem;
    }
    
    .card-option-icon {
      width: 48px;
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--primary-500); /* primary-500 */
      
      svg {
        width: 100%;
        height: 100%;
      }
    }
    
    .card-option-label {
      font-weight: 500;
      margin-bottom: 0.25rem;
    }
    
    .card-option-description {
      font-size: 0.875rem;
      color: #6b7280; /* gray-500 */
    }
  }
  
  .error-msg {
    display: block;
    color: var(--red-500); /* red-500 */
    font-size: 0.875rem;
    margin-top: 0.5rem;
  }
  
  .helper-text {
    display: block;
    color: var(--gray-500); /* gray-500 */
    font-size: 0.75rem;
    margin-top: 0.25rem;
  }
}
</style>
