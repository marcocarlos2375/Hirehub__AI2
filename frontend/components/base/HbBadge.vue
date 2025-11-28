<template>
  <span
    class="hb-badge"
    :class="[
      `hb-badge--${variant}`,
      `hb-badge--${size}`,
      `hb-badge--${mode}`,
      `hb-badge--rounded-${rounded}`,
      props.class,
      {
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
type BadgeMode = 'solid' | 'light'
type BadgeRounded = 'sm' | 'md' | 'lg' | 'full'

interface Props {
  variant?: BadgeVariant
  size?: BadgeSize
  mode?: BadgeMode
  label?: string
  rounded?: BadgeRounded
  outline?: boolean
  dot?: boolean
  class?: string | object | any[]
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  mode: 'solid',
  label: '',
  rounded: 'md',
  outline: false,
  dot: false,
  class: ''
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
}

/* Sizes */
.hb-badge--sm {
  font-size: var(--text-xs);
  padding: 0.25rem 0.5rem;
  line-height: 1.2;
}

.hb-badge--md {
  font-size: var(--text-xs);
  padding: 0.375rem 0.625rem;
  line-height: 1.2;
}

.hb-badge--lg {
  font-size: var(--text-sm);
  padding: 0.5rem 0.875rem;
  line-height: 1.2;
}

/* Rounded variants */
.hb-badge--rounded-sm {
  border-radius: 0.25rem; /* 4px - subtle rounded */
}

.hb-badge--rounded-md {
  border-radius: var(--radius-md); /* default from var.css */
}

.hb-badge--rounded-lg {
  border-radius: 0.5rem; /* 8px - large rounded */
}

.hb-badge--rounded-full {
  border-radius: var(--radius-full); /* 9999px - pill shape */
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

/* ============================================ */
/* Light Mode Variants */
/* ============================================ */

/* Primary - Light Mode */
.hb-badge--primary.hb-badge--light {
  background-color: var(--primary-50, #f5f3ff);
  color: var(--primary-500, #8b5cf6);
}

.hb-badge--primary.hb-badge--light.hb-badge--outline {
  background-color: transparent;
  color: var(--primary-500, #8b5cf6);
  border: 1px solid var(--primary-500, #8b5cf6);
}

/* Secondary - Light Mode */
.hb-badge--secondary.hb-badge--light {
  background-color: var(--secondary-50, #fdf4ff);
  color: var(--secondary-500, #d946ef);
}

.hb-badge--secondary.hb-badge--light.hb-badge--outline {
  background-color: transparent;
  color: var(--secondary-500, #d946ef);
  border: 1px solid var(--secondary-500, #d946ef);
}

/* Success - Light Mode */
.hb-badge--success.hb-badge--light {
  background-color: #f0fdf4; /* green-50 */
  color: #22c55e; /* green-500 */
}

.hb-badge--success.hb-badge--light.hb-badge--outline {
  background-color: transparent;
  color: #22c55e;
  border: 1px solid #22c55e;
}

/* Danger - Light Mode */
.hb-badge--danger.hb-badge--light {
  background-color: #fef2f2; /* red-50 */
  color: #ef4444; /* red-500 */
}

.hb-badge--danger.hb-badge--light.hb-badge--outline {
  background-color: transparent;
  color: #ef4444;
  border: 1px solid #ef4444;
}

/* Warning - Light Mode */
.hb-badge--warning.hb-badge--light {
  background-color: #fff7ed; /* orange-50 */
  color: #f97316; /* orange-500 */
}

.hb-badge--warning.hb-badge--light.hb-badge--outline {
  background-color: transparent;
  color: #f97316;
  border: 1px solid #f97316;
}

/* Info - Light Mode */
.hb-badge--info.hb-badge--light {
  background-color: #eff6ff; /* blue-50 */
  color: #3b82f6; /* blue-500 */
}

.hb-badge--info.hb-badge--light.hb-badge--outline {
  background-color: transparent;
  color: #3b82f6;
  border: 1px solid #3b82f6;
}
</style>
