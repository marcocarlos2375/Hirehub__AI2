<template>
  <Teleport to="body">
    <TransitionRoot
      as="template"
      :show="show"
      enter="transition ease-out duration-300"
      enter-from="opacity-0 scale-95"
      enter-to="opacity-100 scale-100"
      leave="transition ease-in duration-200"
      leave-from="opacity-100 scale-100"
      leave-to="opacity-0 scale-95"
    >
      <div 
        class="hb-notification"
        :class="{
          'hb-notification--success': type === 'success',
          'hb-notification--error': type === 'error',
          'hb-notification--info': type === 'info',
          'hb-notification--warning': type === 'warning',
          'hb-notification--simplified': variant === 'simplified',
          [`hb-notification--${position}`]: true
        }"
      >
        <div v-if="variant !== 'simplified' && type !== 'success'" class="hb-notification__icon">
          <!-- Error Icon -->
          <svg v-if="type === 'error'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="hb-notification__svg">
            <path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zm-1.72 6.97a.75.75 0 10-1.06 1.06L10.94 12l-1.72 1.72a.75.75 0 101.06 1.06L12 13.06l1.72 1.72a.75.75 0 101.06-1.06L13.06 12l1.72-1.72a.75.75 0 10-1.06-1.06L12 10.94l-1.72-1.72z" clip-rule="evenodd" />
          </svg>
          
          <!-- Warning Icon -->
          <svg v-else-if="type === 'warning'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="hb-notification__svg">
            <path fill-rule="evenodd" d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z" clip-rule="evenodd" />
          </svg>
          
          <!-- Info Icon -->
          <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="hb-notification__svg">
            <path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm8.706-1.442c1.146-.573 2.437.463 2.126 1.706l-.709 2.836.042-.02a.75.75 0 01.67 1.34l-.04.022c-1.147.573-2.438-.463-2.127-1.706l.71-2.836-.042.02a.75.75 0 11-.671-1.34l.041-.022zM12 9a.75.75 0 100-1.5.75.75 0 000 1.5z" clip-rule="evenodd" />
          </svg>
        </div>
        
        <div class="hb-notification__content">
          <!-- Show title only if there's no message -->
          <h4 v-if="variant !== 'simplified' && !message" class="hb-notification__title">{{ title }}</h4>
          <div v-if="variant === 'simplified'" class="hb-notification__simplified-content">
          {{ message ? ' ' + message : '' }}
          </div>
          <!-- When there's a message, show it as main text (no title) -->
          <p v-if="variant !== 'simplified' && message" class="hb-notification__message hb-notification__message--primary">
            {{ message }}
          </p>
        </div>
        
        <button 
          class="hb-notification__close" 
          @click="$emit('close')"
        >
          <span class="sr-only">Close</span>
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="hb-notification__close-icon">
            <path fill-rule="evenodd" d="M5.47 5.47a.75.75 0 011.06 0L12 10.94l5.47-5.47a.75.75 0 111.06 1.06L13.06 12l5.47 5.47a.75.75 0 11-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 01-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 010-1.06z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </TransitionRoot>
  </Teleport>
</template>

<script setup lang="ts">
// @ts-strict
import { TransitionRoot } from '@headlessui/vue'
import { onMounted, onBeforeUnmount } from 'vue'

type NotificationType = 'success' | 'error' | 'info' | 'warning'
type NotificationPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center'
type NotificationVariant = 'default' | 'simplified'

interface Props {
  show?: boolean
  type?: NotificationType
  title: string
  message?: string
  position?: NotificationPosition
  duration?: number
  autoClose?: boolean
  variant?: NotificationVariant
}

const props = withDefaults(defineProps<Props>(), {
  show: false,
  type: 'info',
  message: '',
  position: 'top-center',
  duration: 5000,
  autoClose: true,
  variant: 'default'
})

interface Emits {
  (e: 'close'): void
}

const emit = defineEmits<Emits>()

let autoCloseTimeout: ReturnType<typeof setTimeout> | null = null

onMounted(() => {
  if (props.autoClose && props.duration > 0) {
    autoCloseTimeout = setTimeout(() => {
      emit('close')
    }, props.duration)
  }
})

onBeforeUnmount(() => {
  if (autoCloseTimeout !== null) {
    clearTimeout(autoCloseTimeout)
  }
})
</script>

<style scoped>
.hb-notification {
  position: fixed;
  z-index: 150;
  width: 400px;

  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  margin: 0.5rem;
  border: none;
  font-weight: var(--font-semibold) ;
  font-family: var(--font-heading);
  font-size: var(--text-sm);
  box-sizing: border-box;
}

.hb-notification--success {
  background-color: var(--success-500);
  color: white;
}

.hb-notification--success .hb-notification__icon {
  color: white;
}

.hb-notification--error {
  background-color: var(--danger-500);
  color: white;
}

.hb-notification--error .hb-notification__icon {
  color: white;
}

.hb-notification--warning {
  background-color: var(--warning-500);
  color: white;
}

.hb-notification--warning .hb-notification__icon {
  color: white;
}

.hb-notification--info {
  background-color: var(--primary-500);
  color: white;
}

.hb-notification--info .hb-notification__icon {
  color: white;
}

/* Positioning */
.hb-notification--top-right {
  top: 5rem; /* Account for fixed navbar */
  right: 1rem;
}

.hb-notification--top-left {
  top: 5rem; /* Account for fixed navbar */
  left: 1rem;
}

.hb-notification--bottom-right {
  bottom: 1rem;
  right: 1rem;
}

.hb-notification--bottom-left {
  bottom: 1rem;
  left: 1rem;
}

.hb-notification--top-center {
  top: 26px !important; /* 26px spacing */
  left: 50% !important;
  right: auto !important;
  transform: translateX(-50%) !important;
  margin: 0 !important;
  width: 400px;
}

.hb-notification--bottom-center {
  bottom: 1rem;
  left: 50% !important;
  right: auto !important;
  transform: translateX(-50%) !important;
  margin: 0.5rem 0 !important; /* Only top/bottom margin */
  width: 400px;
}

/* Mobile responsive adjustments */
@media (max-width: 640px) {
  .hb-notification {
    max-width: calc(100vw - 2rem);
    min-width: calc(100vw - 2rem);
  }
  
  .hb-notification--top-right,
  .hb-notification--top-left {
    top: 5rem;
    left: 1rem;
    right: 1rem;
    margin: 0.5rem;
  }
  
  .hb-notification--top-center {
    top: 26px !important; /* 26px spacing */
    left: 50% !important;
    right: auto !important;
    transform: translateX(-50%) !important;
    margin: 0 !important;
    max-width: calc(100vw - 2rem);
    width: 378px; /* Fixed width for mobile */
  }
  
  .hb-notification--bottom-right,
  .hb-notification--bottom-left {
    bottom: 1rem;
    left: 1rem;
    right: 1rem;
    margin: 0.5rem;
  }
  
  .hb-notification--bottom-center {
    bottom: 1rem !important;
    left: 50% !important;
    right: auto !important;
    transform: translateX(-50%) !important;
    margin: 0.5rem 0 !important;
    max-width: calc(100vw - 2rem);
  }
}

.hb-notification__icon {
  flex-shrink: 0;
  margin-right: 0.75rem;
}

.hb-notification__svg {
  width: 1.5rem;
  height: 1.5rem;
}

.hb-notification__content {
  flex: 1;
  min-width: 0;
  text-align: center;
}

.hb-notification__title {
  color: white;
  margin: 0;
}

.hb-notification__message {
  color: white;
  margin: 0.25rem 0 0 0;
}

.hb-notification__message--primary {
  color: white;
  margin: 0;
}

.hb-notification__close {
  background: transparent;
  border: none;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.7);
  padding: 0.25rem;
  margin-left: 0.5rem;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.hb-notification__close:hover {
  color: white;
}

.hb-notification__close-icon {
  width: 1.25rem;
  height: 1.25rem;
}

@keyframes slide-in {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes slide-in-center {
  from {
    transform: translateX(-50%) translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(-50%) translateY(0);
    opacity: 1;
  }
}
/* Simplified variant styles */
.hb-notification--simplified {
  border-left: none;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
}

.hb-notification--simplified.hb-notification--success {
  background-color: var(--success-500);
  color: white;
}

.hb-notification--simplified.hb-notification--error {
  background-color: var(--danger-500);
  color: white;
}

.hb-notification--simplified.hb-notification--warning {
  background-color: var(--warning-500);
  color: white;
}

.hb-notification--simplified.hb-notification--info {
  background-color: var(--primary-500);
  color: white;
}

.hb-notification--simplified .hb-notification__simplified-content {
  color: white;
  font-weight: 400;
  font-size: 13px;
  margin: 0;
  line-height: 1.5;
  font-family: var(--font-heading);
}

.hb-notification--simplified .hb-notification__close {
  color: rgba(255, 255, 255, 0.7);
}

.hb-notification--simplified .hb-notification__close:hover {
  color: white;
}
</style>
