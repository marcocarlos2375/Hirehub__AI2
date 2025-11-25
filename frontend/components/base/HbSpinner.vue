<template>
  <div
    class="hb-spinner"
    :class="[size, color]"
  />
</template>

<script setup lang="ts">
// @ts-strict

interface Props {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl' | 'xxxl'
  color?: 'primary' | 'secondary' | 'white' | 'black' | 'danger'
}

withDefaults(defineProps<Props>(), {
  size: 'md',
  color: 'primary'
})
</script>

<style lang="scss" scoped>
.hb-spinner {
  flex-shrink: 0;
  flex-grow: 0;
  border: 3px rgba(var(--primary-500-rgb), 0.25) solid;
  border-top: 3px rgba(var(--primary-500-rgb), 1) solid;
  border-radius: 50%;
  animation: spinnerRotation 0.6s infinite linear;
  width: 18px;
  height: 18px;

  // Colors
  &.primary {
    border: 3px rgba(var(--primary-500-rgb), 0.25) solid;
    border-top: 3px rgba(var(--primary-500-rgb), 1) solid;
  }

  &.secondary {
    border: 3px rgba(var(--secondary-500-rgb), 0.25) solid;
    border-top: 3px rgba(var(--secondary-500-rgb), 1) solid;
  }

  &.danger {
    border: 3px rgba(var(--danger-500-rgb), 0.25) solid;
    border-top: 3px rgba(var(--danger-500-rgb), 1) solid;
  }

  &.white {
    border: 3px rgba(255, 255, 255, 0.25) solid;
    border-top: 3px rgba(255, 255, 255, 1) solid;
  }

  &.black {
    border: 3px rgba(0, 0, 0, 0.25) solid;
    border-top: 3px rgba(0, 0, 0, 1) solid;
  }

  // Sizes
  &.xs {
    width: 12px;
    height: 12px;
    border-width: 2px;
  }
  
  &.sm {
    width: 14px;
    height: 14px;
    border-width: 2px;
  }

  &.md {
    width: 18px;
    height: 18px;
    border-width: 3px;
  }

  &.lg {
    width: 26px;
    height: 26px;
    border-width: 3px;
  }

  &.xl {
    width: 34px;
    height: 34px;
    border-width: 4px;
  }

  &.xxl {
    width: 44px;
    height: 44px;
    border-width: 4px;
  }

  &.xxxl {
    width: 60px;
    height: 60px;
    border-width: 5px;
  }
}

@keyframes spinnerRotation {
  from { transform: rotate(0deg); }
  to { transform: rotate(359deg); }
}
</style>
