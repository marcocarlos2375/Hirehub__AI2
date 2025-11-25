<template>
  <span 
    class="hb-badge" 
    :class="[
      `hb-badge--${variant}`,
      `hb-badge--${size}`,
      { 
        'hb-badge--rounded': rounded,
        'hb-badge--outline': outline,
        'hb-badge--dot': dot,
        'hb-badge--with-icon': $slots.icon
      }
    ]"
  >
    <span v-if="dot" class="hb-badge__dot"></span>
    <slot name="icon"></slot>
    <span v-if="!dot && ($slots.default || label)" class="hb-badge__label">
      <slot>{{ label }}</slot>
    </span>
  </span>
</template>

<script setup lang="ts">
// @ts-strict

type BadgeVariant = 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'light' | 'dark' | 'gray'
type BadgeSize = 'sm' | 'md' | 'lg'

interface Props {
  variant?: BadgeVariant
  size?: BadgeSize
  label?: string
  rounded?: boolean
  outline?: boolean
  dot?: boolean
}

withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  label: '',
  rounded: false,
  outline: false,
  dot: false
});
</script>

<style scoped>
.hb-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-medium);
  white-space: nowrap;
  vertical-align: middle;
  border-radius: var(--radius-md);
}

/* Sizes */
.hb-badge--sm {
  font-size: var(--text-xs);
  padding: 0.125rem 0.375rem;
  line-height: 1.2;
}

.hb-badge--md {
  font-size: var(--text-xs);
  padding: 0.25rem 0.5rem;
  line-height: 1.2;
}

.hb-badge--lg {
  font-size: var(--text-sm);
  padding: 0.375rem 0.75rem;
  line-height: 1.2;
}

/* Rounded variant */
.hb-badge--rounded {
  border-radius: var(--radius-full);
}

/* With icon */
.hb-badge--with-icon {
  gap: 0.25rem;
}

/* Dot variant */
.hb-badge--dot {
  padding: 0;
  height: 0.5rem;
  width: 0.5rem;
  border-radius: 50%;
}

.hb-badge--dot.hb-badge--sm {
  height: 0.375rem;
  width: 0.375rem;
}

.hb-badge--dot.hb-badge--lg {
  height: 0.625rem;
  width: 0.625rem;
}

/* Variants */
/* Primary */
.hb-badge--primary {
  background-color: var(--primary-500);
  color: white;
}

.hb-badge--primary.hb-badge--outline {
  background-color: transparent;
  color: var(--primary-500);
  border: 1px solid var(--primary-500);
}

/* Secondary */
.hb-badge--secondary {
  background-color: var(--secondary-500);
  color: white;
}

.hb-badge--secondary.hb-badge--outline {
  background-color: transparent;
  color: var(--secondary-500);
  border: 1px solid var(--secondary-500);
}

/* Success */
.hb-badge--success {
  background-color: var(--success-500);
  color: white;
}

.hb-badge--success.hb-badge--outline {
  background-color: transparent;
  color: var(--success-500);
  border: 1px solid var(--success-500);
}

/* Danger */
.hb-badge--danger {
  background-color: var(--danger-500);
  color: white;
}

.hb-badge--danger.hb-badge--outline {
  background-color: transparent;
  color: var(--danger-500);
  border: 1px solid var(--danger-500);
}

/* Warning */
.hb-badge--warning {
  background-color: var(--warning-500);
  color: white;
}

.hb-badge--warning.hb-badge--outline {
  background-color: transparent;
  color: var(--warning-500);
  border: 1px solid var(--warning-500);
}

/* Info */
.hb-badge--info {
  background-color: var(--info-500);
  color: white;
}

.hb-badge--info.hb-badge--outline {
  background-color: transparent;
  color: var(--info-500);
  border: 1px solid var(--info-500);
}

/* Light */
.hb-badge--light {
  background-color: var(--gray-100);
  color: var(--gray-800);
}

.hb-badge--light.hb-badge--outline {
  background-color: transparent;
  color: var(--gray-500);
  border: 1px solid var(--gray-200);
}

/* Dark */
.hb-badge--dark {
  background-color: var(--gray-800);
  color: white;
}

.hb-badge--dark.hb-badge--outline {
  background-color: transparent;
  color: var(--gray-800);
  border: 1px solid var(--gray-800);
}

/* Gray */
.hb-badge--gray {
  background-color: var(--gray-500);
  color: white;
}

.hb-badge--gray.hb-badge--outline {
  background-color: transparent;
  color: var(--gray-500);
  border: 1px solid var(--gray-500);
}
</style>
