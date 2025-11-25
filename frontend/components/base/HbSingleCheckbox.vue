<template>
  <div class="hb-single-checkbox">
    <div 
      class="hb-checkbox-option"
      :class="{ 'selected': modelValue }"
      @click="toggle"
    >
      <div class="hb-checkbox-button">
        <div class="checkbox-square" :class="{ 'checked': modelValue, 'indeterminate': indeterminate }">
          <svg v-if="indeterminate" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="check-icon">
            <path fill-rule="evenodd" d="M4.25 12a.75.75 0 01.75-.75h14a.75.75 0 010 1.5H5a.75.75 0 01-.75-.75z" clip-rule="evenodd" />
          </svg>
          <svg v-else-if="modelValue" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="check-icon">
            <path fill-rule="evenodd" d="M19.916 4.626a.75.75 0 01.208 1.04l-9 13.5a.75.75 0 01-1.154.114l-6-6a.75.75 0 011.06-1.06l5.353 5.353 8.493-12.739a.75.75 0 011.04-.208z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
      
      <div class="hb-checkbox-content">
        <slot>
          <div class="hb-checkbox-label">{{ label }}</div>
        </slot>
      </div>
    </div>
    
    <span v-if="error" class="error-msg">{{ error }}</span>
  </div>
</template>

<script setup lang="ts">
// @ts-strict

interface Props {
  modelValue?: boolean
  label?: string
  error?: string
  indeterminate?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  label: '',
  error: '',
  indeterminate: false
});

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const emit = defineEmits<Emits>();

const toggle = (): void => {
  emit('update:modelValue', !props.modelValue);
};
</script>

<style lang="scss" scoped>
.hb-single-checkbox {
  margin-bottom: 1rem;
}

.hb-checkbox-option {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: var(--spacing-2);
  border-radius: var(--radius-2xl);
  transition: background-color var(--transition-normal) var(--transition-ease);
  
  &:hover {
    background-color: var(--gray-50);
    
    .checkbox-square {
      border-color: var(--primary-500);
    }
  }
  
  /* No special styling for selected state - only the checkbox itself changes */
}

.hb-checkbox-button {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: var(--spacing-3);
  flex-shrink: 0;
  
  .checkbox-square {
    width: 1.25rem;
    height: 1.25rem;
    border-radius: var(--radius-sm);
    border: 1px solid var(--gray-400);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-normal) var(--transition-ease);
    position: relative;
    
    &.checked, &.indeterminate {
      background-color: var(--primary-500);
      border-color: var(--primary-500);
      
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
  flex: 1;
  padding-top: 1px; /* Slight adjustment for perfect vertical alignment */
}

.hb-checkbox-label {
  font-weight: 500;
  font-size: var(--text-xs);
  color: var(--gray-600);
  transition: color 0.2s ease;
  
  a {
    color: var(--primary-500);
    text-decoration: underline;
    
    &:hover {
      color: var(--primary-600);
    }
  }
}

.error-msg {
  display: block;
  color: var(--danger-500);
  font-size: var(--text-xs);
  margin-top: var(--spacing-2);
  padding-left: 2rem;
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
