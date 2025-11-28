<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="show"
        class="hb-loading-overlay"
        :class="overlayClasses"
        :style="{ zIndex: zIndex }"
      >
        <div
          class="hb-loading-overlay__content"
          :style="contentStyles"
        >
          <HbSpinner :size="spinnerSize" class="hb-loading-overlay__spinner" />
          <p
            v-if="message"
            class="hb-loading-overlay__message"
            :class="messageClasses"
          >
            {{ message }}
          </p>
          <p
            v-if="shouldShowTimeoutWarning"
            class="hb-loading-overlay__timeout"
          >
            {{ timeoutMessage || 'This is taking longer than expected. Please wait...' }}
          </p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import type { SpinnerSize } from '~/types/components'

interface Props {
  // Visibility
  show: boolean

  // Content
  message?: string

  // Size controls
  spinnerSize?: SpinnerSize
  textSize?: 'sm' | 'md' | 'lg' | 'xl'

  // Background styling
  blur?: boolean
  opacity?: number

  // Timeout warning
  showTimeoutWarning?: boolean
  timeoutThreshold?: number
  timeoutMessage?: string

  // Advanced
  zIndex?: number
}

const props = withDefaults(defineProps<Props>(), {
  message: 'Loading...',
  spinnerSize: 'lg',
  textSize: 'lg',
  blur: false,
  opacity: 0.85,
  showTimeoutWarning: true,
  timeoutThreshold: 10000,
  zIndex: 9999
})

// Timeout warning logic
const startTime = ref<number | null>(null)
const shouldShowTimeoutWarning = computed(() => {
  if (!props.showTimeoutWarning || !startTime.value) return false
  return (Date.now() - startTime.value) > props.timeoutThreshold
})

// Track visibility changes
watch(() => props.show, (isShowing) => {
  if (isShowing) {
    startTime.value = Date.now()
  } else {
    startTime.value = null
  }
})

// Computed classes
const overlayClasses = computed(() => ({
  'hb-loading-overlay--blur': props.blur
}))

const messageClasses = computed(() => ({
  [`hb-loading-overlay__message--${props.textSize}`]: true
}))

// Dynamic styles for content box
const contentStyles = computed(() => ({
  backgroundColor: `rgba(0, 0, 0, ${props.opacity})`
}))
</script>

<style scoped>
.hb-loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;

  &--blur {
    backdrop-filter: blur(4px);
    pointer-events: auto;
  }

  &__content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    width: 250px;
    min-height: 300px;
    padding: 2rem 1.5rem;
    border-radius: 0.75rem;
    pointer-events: auto;
  }

  &__spinner {
    margin-bottom: 0.25rem;
  }

  &__message {
    font-weight: 500;
    color: white;
    text-align: center;
    line-height: 1.4;

    &--sm { font-size: 0.875rem; }
    &--md { font-size: 1rem; }
    &--lg { font-size: 1.125rem; }
    &--xl { font-size: 1.25rem; }
  }

  &__timeout {
    font-size: 0.75rem;
    color: #fb923c;  /* orange-400 for visibility on dark bg */
    text-align: center;
    margin-top: 0.25rem;
    line-height: 1.3;
    animation: pulse 2s ease-in-out infinite;
  }
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
