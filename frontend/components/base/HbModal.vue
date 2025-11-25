<template>
  <Teleport to="body">
    <Transition
      enter-active-class="ease-out duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="props.modelValue || props.show" class="fixed inset-0 z-[200]" aria-labelledby="modal-title" role="dialog" aria-modal="true">
        <div class="modal-container">
          <!-- Background overlay -->
          <div
            class="fixed inset-0 bg-gray-500 bg-opacity-95 transition-opacity modal-overlay"
            aria-hidden="true"
            @click="closeModal"
          />

          <!-- This element is to trick the browser into centering the modal contents. -->
          <span class="hidden sm:inline-block sm:h-screen sm:align-middle" aria-hidden="true">&#8203;</span>

          <Transition
            enter-active-class="ease-out duration-300"
            enter-from-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to-class="opacity-100 translate-y-0 sm:scale-100"
            leave-active-class="ease-in duration-200"
            leave-from-class="opacity-100 translate-y-0 sm:scale-100"
            leave-to-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <div
              v-if="props.modelValue || props.show"
              class="relative inline-block transform overflow-hidden rounded-lg text-left shadow-xl transition-all my-8 w-full mx-auto modal-content" :class="[customClass, appearanceClass, {
                'px-4 pt-5 pb-4': !customClass || (typeof customClass === 'string' && !customClass.includes('px-') && !customClass.includes('p-')),
                'sm:max-w-sm': props.size === 'sm',
                'sm:max-w-md': props.size === 'md',
                'sm:max-w-lg': props.size === 'lg',
                'sm:max-w-xl': props.size === 'xl',
                'sm:max-w-2xl': props.size === '2xl',
                'sm:max-w-3xl': props.size === '3xl',
                'sm:max-w-4xl': props.size === '4xl',
                'sm:max-w-5xl': props.size === '5xl',
                'sm:max-w-6xl': props.size === '6xl',
                'sm:max-w-7xl': props.size === '7xl',
                'sm:p-6': !props.noPadding && (!customClass || (typeof customClass === 'string' && !customClass.includes('px-') && !customClass.includes('p-'))),
              }]"
            >
              <!-- Close button -->
              <div v-if="props.showCloseButton" class="absolute top-0 right-0 pt-4 pr-4">
                <button
                  type="button"
                  :class="[`rounded-md ${props.appearance === 'dark' ? 'bg-gray-700 text-gray-300 hover:text-white' : 'bg-white text-gray-400 hover:text-gray-500'}`, 'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2']"
                  @click="closeModal"
                >
                  <span class="sr-only">Close</span>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <!-- Header/Title -->
              <div v-if="props.title || $slots.header" class="mb-4">
                <h3 v-if="props.title" class="text-lg font-medium leading-6" :class="props.appearance === 'dark' ? 'text-white' : 'text-gray-900'">
                  {{ props.title }}
                </h3>
                <slot v-else name="header"></slot>
              </div>

              <!-- Content -->
              <div :class="{ 'mt-2': props.title || $slots.header }">
                <slot></slot>
              </div>

              <!-- Footer -->
              <div v-if="$slots.footer" class="mt-5 flex justify-end gap-3">
                <slot name="footer"></slot>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
// @ts-strict
import { computed, onMounted, onUnmounted, watch } from 'vue'
import type { HbModalProps, HbModalEmits } from '~/types/components'

const props = withDefaults(defineProps<HbModalProps>(), {
  modelValue: false,
  show: false,
  title: '',
  appearance: 'white',
  size: 'lg',
  showCloseButton: true,
  noPadding: false,
  persistent: false,
  class: ''
})

const emit = defineEmits<HbModalEmits>()

const customClass = computed(() => props.class)

const appearanceClass = computed(() => {
  switch(props.appearance) {
    case 'dark':
      return 'bg-gray-800 text-white'
    case 'light':
      return 'bg-gray-100 text-gray-800'
    case 'white':
    default:
      return 'bg-white text-gray-900'
  }
})

const closeModal = () => {
  if (props.persistent) return

  if (props.modelValue) {
    emit('update:modelValue', false)
  }

  emit('close')
}

// Handle ESC key press
const handleEscKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' || event.key === 'Esc') {
    closeModal()
  }
}

// Add/remove ESC key listener when modal opens/closes
watch(() => props.modelValue || props.show, (isOpen) => {
  if (isOpen) {
    document.addEventListener('keydown', handleEscKey)
  } else {
    document.removeEventListener('keydown', handleEscKey)
  }
})

// Cleanup on unmount
onUnmounted(() => {
  document.removeEventListener('keydown', handleEscKey)
})
</script>

<style scoped>
.modal-container {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  pointer-events: none;
}

.modal-overlay {
  pointer-events: auto;
}

.modal-content {
  max-height: calc(100vh - 2rem);
  margin: 1rem;
  overflow-y: auto;
  pointer-events: auto;
}
</style>
