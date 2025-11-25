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
      <div v-if="modelValue" class="fixed inset-0 modal-fullscreen-wrapper" :style="{ zIndex: props.zIndex }" aria-labelledby="modal-title" role="dialog" aria-modal="true">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-gray-900 bg-opacity-98 transition-opacity modal-fullscreen-overlay" aria-hidden="true" />

        <!-- Fullscreen Modal Content -->
        <div class="fixed inset-0 flex flex-col modal-fullscreen-content">
          <!-- Modal Header -->
          <div class="modal-fullscreen-header">
            <div class="flex items-center justify-between h-full px-6">
              <!-- Left side - Title -->
              <div class="flex items-center gap-4">
                <h2 class="text-xl font-semibold text-white">
                  <slot name="title">{{ title }}</slot>
                </h2>
              </div>

              <!-- Right side - Actions -->
              <div class="flex items-center gap-3">
                <slot name="header-actions"></slot>
                
                <!-- Close button -->
                <button
                  type="button"
                  class="rounded-md bg-gray-800 text-gray-300 hover:text-white hover:bg-gray-700 p-2 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors"
                  @click="closeModal"
                >
                  <span class="sr-only">Close</span>
                  <i class="ri-close-line text-xl"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Modal Body -->
          <div class="modal-fullscreen-body">
            <slot></slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
// @ts-strict

interface Props {
  modelValue?: boolean
  title?: string
  persistent?: boolean
  zIndex?: number
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  title: '',
  persistent: false,
  zIndex: 300
})

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
}

const emit = defineEmits<Emits>()

const closeModal = (): void => {
  if (props.persistent) return

  emit('update:modelValue', false)
  emit('close')
}
</script>

<style scoped lang="scss">
.modal-fullscreen-wrapper {
  pointer-events: none;
}

.modal-fullscreen-overlay {
  pointer-events: none;
}

.modal-fullscreen-content {
  pointer-events: auto;
}

.modal-fullscreen-header {
  height: 64px;
  background: var(--primary-1000);
  border-bottom: 1px solid var(--primary-950);
  flex-shrink: 0;
}

.modal-fullscreen-body {
  flex: 1;
  overflow: hidden;
  background: var(--primary-1000);
}
</style>
