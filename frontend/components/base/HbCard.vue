<template>
  <div
    class="hb-card"
    :class="[
      `shadow-${shadow}`,
      { 'hover': hover },
      { 'selectable': selectable },
      { 'selected': selected },
      { 'interactive': interactive || selectable || hover },
      { 'border': border },
      { 'rounded': rounded },
      { [`padding-${padding}`]: padding },
      variant,
      $attrs.class
    ]"
    :style="{ backgroundColor: bgColor }"
    v-bind="{ ...$attrs, class: undefined }"
    @click="handleClick"
  >
    <div v-if="$slots.header" class="hb-card-header">
      <slot name="header"></slot>
    </div>
    
    <div class="hb-card-body">
      <slot></slot>
    </div>
    
    <div v-if="$slots.footer" class="hb-card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict

type CardVariant = 'default' | 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info'
type CardShadow = 'none' | 'sm' | 'md' | 'lg' | 'xl'
type CardPadding = 'none' | 'sm' | 'md' | 'lg'

interface Props {
  variant?: CardVariant
  shadow?: CardShadow
  hover?: boolean
  selectable?: boolean
  selected?: boolean
  interactive?: boolean
  border?: boolean
  rounded?: boolean
  padding?: CardPadding
  /** Background color - allows parent components to override. Defaults to white. Set to 'transparent' for no background. */
  bgColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  shadow: 'none',
  hover: false,
  selectable: false,
  selected: false,
  interactive: false,
  border: true,
  rounded: true,
  padding: 'md',
  bgColor: '#ffffff'
});

interface Emits {
  (e: 'click', event: MouseEvent): void
}

const emit = defineEmits<Emits>();

const handleClick = (event: MouseEvent): void => {
  emit('click', event);
}

defineOptions({
  inheritAttrs: false
});
</script>

<style lang="scss" scoped>
.hb-card {
  /* Background color now controlled via bgColor prop (defaults to #ffffff) */
  transition: all 0.2s ease;
  width: 100%;
  
  &.border {
    border: 1px solid #e5e7eb; /* gray-200 */
  }
  
  &.rounded {
    border-radius: 0.5rem; /* rounded-lg */
    overflow: hidden;
  }
  
  &.shadow-none {
    box-shadow: none;
  }
  
  &.shadow-sm {
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  }
  
  &.shadow-md {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  }
  
  &.shadow-lg {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  }
  
  &.shadow-xl {
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  }
  
  &.hover {
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
  }
  
  &.interactive {
    cursor: pointer;
  }
  
  &.selectable {
    cursor: pointer;
    
    &:hover {
      border-color: #0ea5e9; /* primary-500 */
    }
  }
  
  &.selected {
    border: 1px solid #0ea5e9; /* primary-500 */
    box-shadow: none;
  }
  
  &.primary {
    border: 1px solid #0ea5e9; /* primary-500 */
  }
  
  &.secondary {
    border: 1px solid #6b7280; /* gray-500 */
  }
  
  &.success {
    border: 1px solid #10b981; /* green-500 */
  }
  
  &.danger {
    border: 1px solid #ef4444; /* red-500 */
  }
  
  &.warning {
    border: 1px solid #f59e0b; /* amber-500 */
  }
  
  &.info {
    border: 1px solid #3b82f6; /* blue-500 */
  }
  
  &.padding-none {
    .hb-card-body {
      padding: 0;
    }
  }
  
  &.padding-sm {
    .hb-card-body {
      padding: 0.75rem;
    }
  }
  
  &.padding-md {
    .hb-card-body {
      padding: 1.25rem;
    }
  }
  
  &.padding-lg {
    .hb-card-body {
      padding: 2rem;
    }
  }
  
  .hb-card-header {
    padding: 1rem 1.25rem;
    border-bottom: 1px solid #e5e7eb; /* gray-200 */
    font-weight: 500;
  }
  
  .hb-card-footer {
    padding: 1rem 1.25rem;
    border-top: 1px solid #e5e7eb; /* gray-200 */
    background-color: #f9fafb; /* gray-50 */
  }
}
</style>
