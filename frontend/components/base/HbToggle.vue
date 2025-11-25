<template>
  <div class="hb-toggle" :class="{ 'is-checked': modelValue }">
    <div class="toggle-container" @click="toggle" :class="{ 'disabled': disabled }">
      <div class="toggle-track">
        <div class="toggle-thumb"></div>
      </div>
      <label v-if="label" class="hb-toggle-label text-sm">
        {{ label }}<span v-if="required" class="required">*</span>
      </label>
    </div>
    
    <span v-if="error" class="error-msg text-sm">{{ error }}</span>
    <span v-else-if="helperText" class="helper-text text-sm">{{ helperText }}</span>
  </div>
</template>

<script setup lang="ts">
// @ts-strict

interface Props {
  modelValue?: boolean
  label?: string
  onText?: string
  offText?: string
  required?: boolean
  disabled?: boolean
  error?: string
  helperText?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  label: '',
  onText: 'Yes',
  offText: 'No',
  required: false,
  disabled: false,
  error: '',
  helperText: ''
});

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const emit = defineEmits<Emits>();

const toggle = (): void => {
  if (props.disabled) return;
  emit('update:modelValue', !props.modelValue);
};
</script>

<style lang="scss" scoped>
.hb-toggle {
  display: flex;
  flex-direction: column;
  margin-bottom: var(--spacing-4);
  
  &-label {
    display: block;
    font-weight: var(--font-medium);
    font-size: 13px;
    color: var(--gray-700);
    margin-left: var(--spacing-3);
    
    .required {
      color: var(--error-500);
      margin-left: 2px;
    }
  }
  
  .toggle-container {
    display: flex;
    align-items: center;
    cursor: pointer;
    
    &.disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }
  
  .toggle-track {
    position: relative;
    width: 40px;
    height: 22px;
    background-color: var(--gray-300);
    border-radius: 34px;
    margin-right: var(--spacing-3);
    transition: background-color 0.3s ease;
    
    .toggle-thumb {
      position: absolute;
      top: 2px;
      left: 2px;
      width: 18px;
      height: 18px;
      background-color: white;
      border-radius: 50%;
      transition: transform 0.3s ease;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
  }
  
  .toggle-text {
    font-size: var(--text-sm);
    color: var(--gray-700);
  }
  
  &.is-checked {
    .toggle-track {
      background-color: var(--primary-500);
      
      .toggle-thumb {
        transform: translateX(18px);
      }
    }
  }
  
  .error-msg {
    display: block;
    color: var(--error-500);
    font-size: var(--text-xs);
    margin-top: var(--spacing-1);
  }
  
  .helper-text {
    display: block;
    color: var(--gray-500);
    font-size: var(--text-xs);
    margin-top: var(--spacing-1);
  }
}
</style>
