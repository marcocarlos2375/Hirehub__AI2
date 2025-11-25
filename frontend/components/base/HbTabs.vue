<template>
  <div class="hb-tabs">
    <!-- Tab Navigation -->
    <div class="hb-tabs__nav" :class="[`hb-tabs__nav--${variant}`, `hb-tabs__nav--${size}`]">
      <button
        v-for="(tab, index) in tabs"
        :key="index"
        class="hb-tabs__tab"
        :class="{
          'hb-tabs__tab--active': modelValue === index,
          'hb-tabs__tab--disabled': tab.disabled
        }"
        :disabled="tab.disabled"
        @click="!tab.disabled && updateTab(index)"
      >
        <div class="hb-tabs__tab-content">
          <div v-if="tab.icon" class="hb-tabs__tab-icon">
            <component :is="tab.icon" />
          </div>
          <span class="hb-tabs__tab-label">{{ tab.label }}</span>
          <div v-if="tab.badge" class="hb-tabs__tab-badge">
            {{ tab.badge }}
          </div>
        </div>
      </button>
    </div>
    
    <!-- Tab Content -->
    <div class="hb-tabs__content" :class="{ 'hb-tabs__content--with-border': bordered }">
      <div v-if="loading" class="hb-tabs__loading">
        <HbSpinner :size="spinnerSize" :color="spinnerColor" />
      </div>
      <div v-else class="hb-tabs__panel">
        <slot :active-tab="modelValue" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { computed } from 'vue'
import HbSpinner from './HbSpinner.vue'

interface Tab {
  label: string
  icon?: unknown
  badge?: string | number
  disabled?: boolean
}

interface Props {
  tabs?: Tab[]
  modelValue?: number
  variant?: 'default' | 'pills' | 'underline'
  size?: 'sm' | 'md' | 'lg'
  bordered?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  tabs: () => [],
  modelValue: 0,
  variant: 'default',
  size: 'md',
  bordered: true,
  loading: false
})

const emit = defineEmits<{
  'update:modelValue': [index: number]
}>()

const updateTab = (index: number): void => {
  emit('update:modelValue', index)
}

const spinnerSize = computed<'sm' | 'md' | 'lg'>(() => {
  const sizeMap: Record<string, 'sm' | 'md' | 'lg'> = {
    sm: 'sm',
    md: 'md',
    lg: 'lg'
  }
  return sizeMap[props.size] || 'md'
})

const spinnerColor = computed<'primary' | 'secondary' | 'danger' | 'white' | 'black'>(() => {
  return 'primary'
})
</script>

<style>
.hb-tabs {
  width: 100%;
}

.hb-tabs__nav {
  display: flex;
  border-bottom: 1px solid var(--gray-200);
  margin-bottom: var(--spacing-4);
}

/* Variant Styles */
.hb-tabs__nav--default {
  gap: var(--spacing-1);
}

.hb-tabs__nav--pills {
  gap: var(--spacing-2);
  border-bottom: none;
}

.hb-tabs__nav--underline {
  gap: var(--spacing-4);
}

/* Size Styles */
.hb-tabs__nav--sm .hb-tabs__tab {
  padding: var(--spacing-1) var(--spacing-2);
  font-size: var(--text-sm);
}

.hb-tabs__nav--md .hb-tabs__tab {
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--text-base);
}

.hb-tabs__nav--lg .hb-tabs__tab {
  padding: var(--spacing-3) var(--spacing-4);
  font-size: var(--text-lg);
}

.hb-tabs__tab {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-medium);
  color: var(--gray-600);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-duration) var(--transition-ease);
}

.hb-tabs__tab:hover:not(.hb-tabs__tab--disabled) {
  color: var(--primary-600);
}

.hb-tabs__tab--active {
  color: var(--primary-500);
}

.hb-tabs__nav--default .hb-tabs__tab--active {
  color: var(--primary-500);
}

.hb-tabs__nav--default .hb-tabs__tab--active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--primary-500);
}

.hb-tabs__nav--pills .hb-tabs__tab--active {
  color: var(--primary-500);
  background-color: var(--primary-50);
}

.hb-tabs__nav--underline .hb-tabs__tab--active {
  color: var(--primary-500);
  border-bottom: 2px solid var(--primary-500);
}

.hb-tabs__tab--disabled {
  color: var(--gray-400);
  cursor: not-allowed;
}

.hb-tabs__tab-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.hb-tabs__tab-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.hb-tabs__tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.5rem;
  height: 1.5rem;
  padding: 0 var(--spacing-1);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: white;
  background-color: var(--primary-500);
  border-radius: var(--radius-full);
}

.hb-tabs__content {
  padding: var(--spacing-4) 0;
}

.hb-tabs__content--with-border {
  padding: var(--spacing-4);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-md);
}

.hb-tabs__loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100px;
}
</style>
