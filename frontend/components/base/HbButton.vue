<template>
  <!-- Regular Button -->
  <button
    v-if="!to && !href"
    :type="type"
    :class="buttonClasses"
    :disabled="disabled || loading"
    v-bind="$attrs"
    @click="$emit('click', $event)"
  >
    <Transition name="fade" mode="in-out">
      <div v-if="loading" class="hb-button__spinner">
        <HbSpinner :size="spinnerSize" :color="spinnerColor" />
      </div>
    </Transition>
    <span :class="{ 'invisible': loading }" class="hb-button__content">
      <!-- Leading Icon Slot -->
      <span v-if="$slots['leading-icon']" class="hb-button__leading-icon">
        <slot name="leading-icon" />
      </span>
      
      <!-- Default Slot (Button Text) -->
      <slot />
      
      <!-- Trailing Icon Slot -->
      <span v-if="$slots['trailing-icon']" class="hb-button__trailing-icon">
        <slot name="trailing-icon" />
      </span>
    </span>
  </button>
  
  <!-- Navigation Link (Internal) -->
  <!-- NOTE: Replace NuxtLink with your router component (RouterLink for vue-router, <a> for plain HTML) -->
  <NuxtLink
    v-else-if="to && !href"
    :to="to"
    :class="buttonClasses"
    v-bind="$attrs"
    @click="$emit('click', $event)"
  >
    <Transition name="fade" mode="in-out">
      <div v-if="loading" class="hb-button__spinner">
        <HbSpinner :size="spinnerSize" :color="spinnerColor" />
      </div>
    </Transition>
    <span :class="{ 'invisible': loading }" class="hb-button__content">
      <!-- Leading Icon Slot -->
      <span v-if="$slots['leading-icon']" class="hb-button__leading-icon">
        <slot name="leading-icon" />
      </span>
      
      <!-- Default Slot (Button Text) -->
      <slot />
      
      <!-- Trailing Icon Slot -->
      <span v-if="$slots['trailing-icon']" class="hb-button__trailing-icon">
        <slot name="trailing-icon" />
      </span>
    </span>
  </NuxtLink>
  
  <!-- External Link -->
  <a
    v-else-if="!to && href"
    :href="href"
    :target="target"
    :download="download"
    :class="buttonClasses"
    v-bind="$attrs"
    @click="$emit('click', $event)"
  >
    <Transition name="fade" mode="in-out">
      <div v-if="loading" class="hb-button__spinner">
        <HbSpinner :size="spinnerSize" :color="spinnerColor" />
      </div>
    </Transition>
    <span :class="{ 'invisible': loading }" class="hb-button__content">
      <!-- Leading Icon Slot -->
      <span v-if="$slots['leading-icon']" class="hb-button__leading-icon">
        <slot name="leading-icon" />
      </span>
      
      <!-- Default Slot (Button Text) -->
      <slot />
      
      <!-- Trailing Icon Slot -->
      <span v-if="$slots['trailing-icon']" class="hb-button__trailing-icon">
        <slot name="trailing-icon" />
      </span>
    </span>
  </a>
</template>

<script setup lang="ts">
// @ts-strict
import { computed } from 'vue'
import type { HbButtonProps, HbButtonEmits } from '~/types/components'
import HbSpinner from './HbSpinner.vue'

const props = withDefaults(defineProps<HbButtonProps>(), {
  variant: 'primary',
  size: 'md',
  rounded: 'default',
  fullWidth: false,
  disabled: false,
  loading: false,
  type: 'button',
  to: undefined,
  href: undefined,
  target: '_self',
  download: false,
  border: true,
  iconOnly: false
})

const emit = defineEmits<HbButtonEmits>()

// Computed button classes
const buttonClasses = computed(() => [
  'hb-button',
  `hb-button--${props.variant}`,
  `hb-button--${props.size}`,
  `hb-button--rounded-${props.rounded}`,
  { 'hb-button--full-width': props.fullWidth },
  { 'hb-button--disabled': props.disabled },
  { 'hb-button--loading': props.loading },
  { 'hb-button--no-border': !props.border },
  { 'hb-button--icon-only': props.iconOnly }
])

// Determine appropriate spinner size based on button size
const spinnerSize = computed(() => {
  switch (props.size) {
    case 'sm': return 'xs' as const
    case 'md': return 'sm' as const
    case 'lg': return 'md' as const
    default: return 'sm' as const
  }
})

// Determine appropriate spinner color based on button variant
const spinnerColor = computed((): 'primary' | 'secondary' | 'white' | 'black' | 'danger' => {
  switch (props.variant) {
    case 'primary':
    case 'secondary':
    case 'danger':
      return 'white'
    case 'white':
    case 'light':
      return 'primary'
    case 'light-gray':
      return 'black' // Changed from 'gray' to match HbSpinner's type
    case 'outline':
    case 'ghost':
    case 'link':
    case 'transparent':
      return 'primary'
    default:
      return 'white'
  }
})
</script>

<style lang="scss" scoped>
.hb-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-medium);
  font-family: var(--font-heading) !important;
  transition: all var(--transition-normal) var(--transition-ease);
  position: relative;
  cursor: pointer;

  /* Rounded variants */
  &--rounded-default {
    border-radius: var(--button-border-radius);
  }

  &--rounded-pill {
    border-radius: 9999px;
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.8), 0 0 0 4px var(--primary-500);
  }
  
  /* Size variants */
  &--sm {
    height: 32px;
    padding: 0 12px;
    font-size: 0.875rem; // 14px
    line-height: 1.25rem;
  }
  
  &--md {
    height: 44px;
    padding: 0 16px;
    font-size: 0.875rem; // 14px
    line-height: 1.25rem;
  }
  
  &--lg {
    height: 48px;
    padding: 0 24px;
    font-size: 1rem; // 16px
    line-height: 1.5rem;
  }
  
  /* Icon-only variant */
  &--icon-only {
    &.hb-button--sm {
      width: 32px;
      padding: 0;
    }
    
    &.hb-button--md {
      width: 44px;
      padding: 0;
    }
    
    &.hb-button--lg {
      width: 48px;
      padding: 0;
    }
    
    .hb-button__leading-icon {
      margin-right: 0;
    }
    
    .hb-button__trailing-icon {
      margin-left: 0;
    }
  }
  
  /* Color variants */
  &--primary {
    color: var(--white);
    background-color: var(--primary-500);
    
    &:hover:not(.hb-button--disabled) {
      background-color: var(--primary-600);
    }
    
    &:focus {
      box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.8), 0 0 0 4px var(--primary-500);
    }
  }
  
  &--secondary {
    color: var(--white);
    background-color: var(--secondary-500);
    
    &:hover:not(.hb-button--disabled) {
      background-color: var(--secondary-700);
    }
    
    &:focus {
      box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.8), 0 0 0 4px var(--gray-500);
    }
  }
  
  &--outline {
    color: var(--gray-700);
    background-color: var(--white);
    border: 1px solid var(--gray-300);
    
    &:hover:not(.hb-button--disabled) {
      background-color: var(--gray-50);
    }
    
    &:focus {
      box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.8), 0 0 0 4px var(--primary-500);
    }
  }
  
  &--ghost {
    color: var(--gray-700);
    background-color: transparent;
    
    &:hover:not(.hb-button--disabled) {
      background-color: var(--gray-100);
    }
    
    &:focus {
      box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.8), 0 0 0 4px var(--gray-500);
    }
  }
  
  &--dark-ghost {
    color: var(--gray-300);
    background-color: transparent;
    border: 1px solid var(--gray-600);
    
    &:hover:not(.hb-button--disabled) {
      color: var(--primary-400);
      background-color: var(--gray-700);
      border-color: var(--primary-400);
    }
    
    &:focus {
      box-shadow: 0 0 0 2px var(--gray-800), 0 0 0 4px var(--primary-500);
    }
  }
  
  &--danger {
    color: var(--white);
    background-color: var(--danger-600);
    
    &:hover:not(.hb-button--disabled) {
      background-color: var(--danger-700);
    }
    
    &:focus {
      box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.8), 0 0 0 4px var(--danger-500);
    }
  }
  
  &--white {
    color: var(--primary-500);
    background-color: var(--white);
    
    &:hover:not(.hb-button--disabled) {
      background-color: var(--gray-50);
    }
    
    &:focus {
      box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.8), 0 0 0 4px var(--primary-500);
    }
  }
  
  &--light {
    color: var(--primary-500);
    background-color: var(--primary-50);
    border: 1px solid var(--primary-100);
    
    &:hover:not(.hb-button--disabled) {
      background-color: var(--primary-100);
      border-color: var(--primary-200);
    }
    
    &:focus {
      box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.8), 0 0 0 4px var(--primary-200);
    }
    
    &.hb-button--no-border {
      border: none;
      
      &:hover:not(.hb-button--disabled) {
        border: none;
      }
    }
  }
  
  &--light-gray {
    color: var(--gray-700);
    background-color: var(--gray-50);
    border: 1px solid var(--gray-200);
    
    &:hover:not(.hb-button--disabled) {
      background-color: var(--gray-100);
      border-color: var(--gray-300);
    }
    
    &:focus {
      box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.8), 0 0 0 4px var(--gray-300);
    }
    
    &.hb-button--no-border {
      border: none;
      
      &:hover:not(.hb-button--disabled) {
        border: none;
      }
    }
  }
  
  &--link {
    color: var(--primary-500);
    background-color: transparent;
    padding: 0;
    height: auto;
    text-decoration: none;
    font-weight: var(--font-normal);
    
    &:hover:not(.hb-button--disabled) {
      color: var(--primary-700);
      text-decoration: none;
    }
    
    &:focus {
      box-shadow: none;
      text-decoration: none;
    }
  }
  
  &--transparent {
    color: var(--primary-500);
    background-color: transparent;
    border: none;
    
    &:hover:not(.hb-button--disabled) {
      color: var(--primary-600);
      background-color: var(--primary-50);
    }
    
    &:focus {
      box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.8), 0 0 0 4px var(--primary-500);
    }
  }
  
  /* States */
  &--full-width:not([class*='w-']) {
    width: 100%;
  }
  
  &--disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  }
  
  &--loading {
    color: transparent;
    
    &:hover {
      color: transparent;
    }
  }
  
  &__spinner {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  /* Icon styles */
  &__content {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  &__leading-icon {
    display: inline-flex;
    margin-right: 0.5rem;
  }
  
  &__trailing-icon {
    display: inline-flex;
    margin-left: 0.5rem;
  }
  
  /* Size-specific icon adjustments */
  &--sm {
    .hb-button__leading-icon,
    .hb-button__trailing-icon {
      svg, img {
        width: 1rem;
        height: 1rem;
      }
    }
  }
  
  &--md {
    .hb-button__leading-icon,
    .hb-button__trailing-icon {
      svg, img {
        width: 1.25rem;
        height: 1.25rem;
      }
    }
  }
  
  &--lg {
    .hb-button__leading-icon,
    .hb-button__trailing-icon {
      svg, img {
        width: 1.5rem;
        height: 1.5rem;
      }
    }
  }
}

/* Fade transition for loading spinner */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.invisible {
  opacity: 0;
}
</style>
