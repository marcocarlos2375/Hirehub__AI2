<template>
  <div class="hb-pills" :class="{ 'hb-pills--vertical': vertical }">
    <button
      v-for="(option, index) in options"
      :key="index"
      class="hb-pill"
      :class="[
        `hb-pill--${size}`,
        `hb-pill--${variant}`,
        {
          'hb-pill--active': modelValue === option.value,
          'hb-pill--disabled': option.disabled
        }
      ]"
      :disabled="option.disabled"
      @click="handleSelect(option.value)"
    >
      <slot name="icon" :option="option" v-if="$slots.icon"></slot>
      <span class="hb-pill__label">{{ option.label }}</span>
      <slot name="suffix" :option="option" v-if="$slots.suffix"></slot>
    </button>
  </div>
</template>

<script setup lang="ts">
// @ts-strict

interface Option {
  label: string
  value: string | number | boolean
  disabled?: boolean
}

interface Props {
  modelValue?: string | number | boolean | Record<string, unknown> | null
  options?: Option[]
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'gray'
  size?: 'sm' | 'md' | 'lg'
  vertical?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  options: () => [],
  variant: 'primary',
  size: 'md',
  vertical: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number | boolean | Record<string, unknown>]
  'change': [value: string | number | boolean | Record<string, unknown>]
}>()

const handleSelect = (value: string | number | boolean): void => {
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<style scoped>
.hb-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.hb-pills--vertical {
  flex-direction: column;
}

.hb-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  font-family: var(--font-body);
  font-weight: var(--font-medium);
  white-space: nowrap;
  border-radius: var(--radius-full);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.hb-pill:focus {
  outline: none;
  box-shadow: 0 0 0 2px var(--white), 0 0 0 4px var(--primary-300);
}

.hb-pill--disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Sizes */
.hb-pill--sm {
  font-size: var(--text-xs);
  padding: 0.25rem 0.625rem;
  line-height: 1.2;
}

.hb-pill--md {
  font-size: var(--text-xs);
  padding: 0.375rem 0.75rem;
  line-height: 1.2;
}

.hb-pill--lg {
  font-size: var(--text-sm);
  padding: 0.5rem 1rem;
  line-height: 1.2;
}

/* Variants */
/* Primary */
.hb-pill--primary {
  background-color: var(--gray-100);
  color: var(--gray-700);
  border-color: var(--gray-200);
}

.hb-pill--primary:hover:not(.hb-pill--disabled) {
  background-color: var(--gray-200);
  color: var(--gray-800);
}

.hb-pill--primary.hb-pill--active {
  background-color: var(--primary-100);
  color: var(--primary-700);
  border-color: var(--primary-200);
}

/* Secondary */
.hb-pill--secondary {
  background-color: var(--gray-100);
  color: var(--gray-700);
  border-color: var(--gray-200);
}

.hb-pill--secondary:hover:not(.hb-pill--disabled) {
  background-color: var(--gray-200);
  color: var(--gray-800);
}

.hb-pill--secondary.hb-pill--active {
  background-color: var(--secondary-100);
  color: var(--secondary-700);
  border-color: var(--secondary-200);
}

/* Success */
.hb-pill--success {
  background-color: var(--gray-100);
  color: var(--gray-700);
  border-color: var(--gray-200);
}

.hb-pill--success:hover:not(.hb-pill--disabled) {
  background-color: var(--gray-200);
  color: var(--gray-800);
}

.hb-pill--success.hb-pill--active {
  background-color: var(--success-100);
  color: var(--success-700);
  border-color: var(--success-200);
}

/* Danger */
.hb-pill--danger {
  background-color: var(--gray-100);
  color: var(--gray-700);
  border-color: var(--gray-200);
}

.hb-pill--danger:hover:not(.hb-pill--disabled) {
  background-color: var(--gray-200);
  color: var(--gray-800);
}

.hb-pill--danger.hb-pill--active {
  background-color: var(--danger-100);
  color: var(--danger-700);
  border-color: var(--danger-200);
}

/* Warning */
.hb-pill--warning {
  background-color: var(--gray-100);
  color: var(--gray-700);
  border-color: var(--gray-200);
}

.hb-pill--warning:hover:not(.hb-pill--disabled) {
  background-color: var(--gray-200);
  color: var(--gray-800);
}

.hb-pill--warning.hb-pill--active {
  background-color: var(--warning-100);
  color: var(--warning-700);
  border-color: var(--warning-200);
}

/* Info */
.hb-pill--info {
  background-color: var(--gray-100);
  color: var(--gray-700);
  border-color: var(--gray-200);
}

.hb-pill--info:hover:not(.hb-pill--disabled) {
  background-color: var(--gray-200);
  color: var(--gray-800);
}

.hb-pill--info.hb-pill--active {
  background-color: var(--info-100);
  color: var(--info-700);
  border-color: var(--info-200);
}

/* Gray */
.hb-pill--gray {
  background-color: var(--gray-100);
  color: var(--gray-700);
  border-color: var(--gray-200);
}

.hb-pill--gray:hover:not(.hb-pill--disabled) {
  background-color: var(--gray-200);
  color: var(--gray-800);
}

.hb-pill--gray.hb-pill--active {
  background-color: var(--gray-200);
  color: var(--gray-800);
  border-color: var(--gray-300);
}
</style>
