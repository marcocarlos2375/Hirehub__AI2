<template>
  <div class="hb-img" :class="[sizeClass, { 'hb-img--loading': loading, 'hb-img--error': hasError }]">
    <!-- Placeholder shown while loading or on error -->
    <div v-if="loading || hasError" class="hb-img__placeholder">
      <div v-if="loading" class="hb-img__loading">
        <svg class="hb-img__spinner" viewBox="0 0 50 50">
          <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
        </svg>
      </div>
      <div v-else-if="hasError" class="hb-img__error-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <circle cx="8.5" cy="8.5" r="1.5"></circle>
          <polyline points="21 15 16 10 5 21"></polyline>
        </svg>
        <span v-if="errorText" class="hb-img__error-text">{{ errorText }}</span>
      </div>
    </div>
    
    <!-- Actual image -->
    <img
      v-show="!loading && !hasError"
      :src="src"
      :alt="alt"
      :width="width"
      :height="height"
      @load="onLoad"
      @error="onError"
      class="hb-img__image"
      :class="{ 'hb-img__image--rounded': rounded, 'hb-img__image--circle': circle }"
    />
    
    <!-- Optional caption -->
    <figcaption v-if="caption" class="hb-img__caption">{{ caption }}</figcaption>
    
    <!-- Overlay for hover effects -->
    <div v-if="overlay && !loading && !hasError" class="hb-img__overlay">
      <slot name="overlay">
        <div class="hb-img__overlay-content">
          <slot name="overlay-content"></slot>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed } from 'vue'

interface Props {
  src: string
  alt?: string
  width?: number | string | null
  height?: number | string | null
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'full'
  caption?: string
  rounded?: boolean
  circle?: boolean
  overlay?: boolean
  errorText?: string
  lazyLoad?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  alt: '',
  width: null,
  height: null,
  size: 'md',
  caption: '',
  rounded: false,
  circle: false,
  overlay: false,
  errorText: 'Failed to load image',
  lazyLoad: true
})

const loading = ref<boolean>(true)
const hasError = ref<boolean>(false)

const sizeClass = computed<string>(() => {
  return `hb-img--${props.size}`
})

function onLoad(): void {
  loading.value = false
}

function onError(): void {
  loading.value = false
  hasError.value = true
}
</script>

<style lang="scss" scoped>
.hb-img {
  position: relative;
  display: inline-block;
  overflow: hidden;
  
  // Size variants
  &--xs {
    width: var(--size-16);
    height: var(--size-16);
  }
  
  &--sm {
    width: var(--size-24);
    height: var(--size-24);
  }
  
  &--md {
    width: var(--size-32);
    height: var(--size-32);
  }
  
  &--lg {
    width: var(--size-48);
    height: var(--size-48);
  }
  
  &--xl {
    width: var(--size-64);
    height: var(--size-64);
  }
  
  &--full {
    width: 100%;
    height: auto;
  }
  
  &__image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform var(--transition-normal) var(--transition-ease);
    
    &--rounded {
      border-radius: var(--radius-md);
    }
    
    &--circle {
      border-radius: var(--radius-full);
    }
  }
  
  &__placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--gray-100);
    color: var(--gray-500);
    border-radius: var(--radius-md);
  }
  
  &__loading {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  &__spinner {
    animation: rotate 2s linear infinite;
    width: 30px;
    height: 30px;
    
    & .path {
      stroke: var(--primary-500);
      stroke-linecap: round;
      animation: dash 1.5s ease-in-out infinite;
    }
  }
  
  &__error-icon {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--danger-500);
  }
  
  &__error-text {
    margin-top: var(--spacing-2);
    font-size: var(--text-xs);
    text-align: center;
    max-width: 80%;
  }
  
  &__caption {
    margin-top: var(--spacing-2);
    font-size: var(--text-sm);
    color: var(--gray-600);
    text-align: center;
  }
  
  &__overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.4);
    opacity: 0;
    transition: opacity var(--transition-normal) var(--transition-ease);
    display: flex;
    align-items: center;
    justify-content: center;
    
    .hb-img:hover & {
      opacity: 1;
    }
  }
  
  &__overlay-content {
    color: var(--white);
    text-align: center;
    padding: var(--spacing-2);
  }
}

@keyframes rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}
</style>
