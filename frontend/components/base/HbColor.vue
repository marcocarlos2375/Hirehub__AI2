<template>
  <div class="hb-color" :class="{ 'has-error': error, 'is-disabled': disabled }">
    <div v-if="label" class="hb-color__label">
      {{ label }}<span v-if="required" class="required">*</span>
    </div>
    
    <div v-if="helperText && !error" class="hb-color__helper hb-color__helper--top">{{ helperText }}</div>
    
    <div class="hb-color__container" @click.stop>
      <HbColorPicker
        v-model="inputValue"
        :disabled="disabled"
        @update:modelValue="updateColor"
      />
    </div>
    
   
    
    <div v-if="error" class="hb-color__error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, watch } from 'vue';
import HbInput from './HbInput.vue';
import HbColorPicker from './HbColorPicker.vue';

interface Props {
  modelValue?: string
  label?: string
  required?: boolean
  disabled?: boolean
  error?: string
  helperText?: string
  showPalette?: boolean
  presetColors?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: '',
  required: false,
  disabled: false,
  error: '',
  helperText: '',
  showPalette: false,
  presetColors: () => []
});

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'focus'): void
  (e: 'blur'): void
}

const emit = defineEmits<Emits>();

const colorInput = ref<HTMLInputElement | null>(null);
const isFocused = ref<boolean>(false);
const inputValue = ref<string>(props.modelValue);

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue: string) => {
  inputValue.value = newValue;
});

// Watch for changes to inputValue
watch(inputValue, (newValue: string) => {
  // Basic validation for hex color
  if (newValue === '' || /^#([0-9A-F]{3}){1,2}$/i.test(newValue)) {
    emit('update:modelValue', newValue);
  }
});

const updateColor = (color: string): void => {
  emit('update:modelValue', color);
  inputValue.value = color;
};

const clearColor = (): void => {
  emit('update:modelValue', '');
  inputValue.value = '';
};

const openPicker = (): void => {
  colorInput.value?.click();
};

const onFocus = (): void => {
  isFocused.value = true;
  emit('focus');
};

const onBlur = (): void => {
  isFocused.value = false;
  emit('blur');
};
</script>

<style lang="scss" scoped>
.hb-color {
  width: 100%;
  margin-bottom: var(--spacing-4);
  
  &__label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: var(--font-medium);
    font-size: var(--text-sm);
    margin-bottom: var(--spacing-2);
    
    .required {
      color: var(--danger-500);
      margin-left: var(--spacing-0-5);
    }
  }
  
  &__helper {
    margin-top: var(--spacing-1);
    font-size: var(--text-xs);
    color: var(--gray-500);
    
    &--top {
      margin-top: var(--spacing-1);
      margin-bottom: var(--spacing-2);
    }
  }
  
  &__container {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
  }
  
  &__preview {
    @apply h-8 w-8 rounded-lg;
    border-radius: var(--radius-lg);
    border: 1px solid var(--gray-300);
    cursor: pointer;
    position: relative;
    overflow: hidden;
    flex-shrink: 0;
    
    .is-disabled & {
      cursor: not-allowed;
      opacity: 0.6;
    }
  }
  
  &__no-color {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(to top right, transparent calc(50% - 1px), red, transparent calc(50% + 1px));
  }
  
  &__input-wrapper {
    position: relative;
    flex: 1;
    
    :deep(.hb-input) {
      margin-bottom: 0;
    }
  }
  
  &__native-input {
    position: absolute;
    width: 0;
    height: 0;
    opacity: 0;
    visibility: hidden;
  }
  
  &__clear-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: none;
    background: none;
    color: var(--gray-500);
    cursor: pointer;
    border-radius: 8px;
    transition: all var(--transition-fast) var(--transition-ease);
    
    &:hover {
      background-color: var(--gray-100);
      color: var(--danger-500);
    }
  }
  
  &__palette {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-2);
    margin-top: var(--spacing-3);
  }
  
  &__palette-item {
    width: 24px;
    height: 24px;
    border-radius: var(--radius-pill);
    border: 1px solid var(--gray-300);
    cursor: pointer;
    transition: transform var(--transition-fast) var(--transition-ease);
    position: relative;
    
    &:hover {
      transform: scale(1.1);
    }
    
    &--selected {
      z-index: 1;
    }
    
    &-ring {
      position: absolute;
      top: -4px;
      left: -4px;
      right: -4px;
      bottom: -4px;
      border-radius: calc(var(--radius-md) + 4px);
      border: 2px solid transparent;
      pointer-events: none;
    }
    
    .is-disabled & {
      cursor: not-allowed;
      opacity: 0.6;
      
      &:hover {
        transform: none;
      }
    }
  }
  
  &__error {
    margin-top: var(--spacing-2);
    font-size: var(--text-xs);
    color: var(--danger-500);
  }
}
</style>
