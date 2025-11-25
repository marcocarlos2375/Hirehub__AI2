<template>
  <div class="hb-tooltip-container" @mouseenter="show" @mouseleave="hide" @focus="show" @blur="hide">
    <slot></slot>
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div 
        v-if="isVisible" 
        class="hb-tooltip" 
        :class="[
          `hb-tooltip--${position}`,
          `hb-tooltip--${variant}`,
          { 'hb-tooltip--arrow': arrow }
        ]"
        role="tooltip"
      >
        <div v-if="arrow" class="hb-tooltip__arrow"></div>
        <div class="hb-tooltip__content">
          <slot name="content">{{ content }}</slot>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, onBeforeUnmount, watch } from 'vue'

type TooltipPosition = 'top' | 'bottom' | 'left' | 'right'
type TooltipVariant = 'dark' | 'light' | 'primary' | 'success' | 'danger' | 'warning' | 'info'
type TooltipTrigger = 'hover' | 'click' | 'focus' | 'manual'

interface Props {
  content?: string
  position?: TooltipPosition
  variant?: TooltipVariant
  arrow?: boolean
  delay?: number
  trigger?: TooltipTrigger
  disabled?: boolean
  modelValue?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  content: '',
  position: 'top',
  variant: 'dark',
  arrow: true,
  delay: 200,
  trigger: 'hover',
  disabled: false,
  modelValue: undefined
})

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const emit = defineEmits<Emits>()

const isVisible = ref<boolean>(props.modelValue !== undefined ? props.modelValue : false)
let showTimeout: ReturnType<typeof setTimeout> | null = null
let hideTimeout: ReturnType<typeof setTimeout> | null = null

// Watch for changes to modelValue prop
watch(() => props.modelValue, (newValue: boolean | undefined) => {
  if (newValue !== undefined) {
    isVisible.value = newValue
  }
})

// Watch for changes to isVisible and emit update events
watch(isVisible, (newValue: boolean) => {
  if (props.modelValue !== undefined) {
    emit('update:modelValue', newValue)
  }
})

function show(): void {
  if (props.disabled) return

  if (props.trigger === 'manual') {
    return
  }

  if (hideTimeout !== null) {
    clearTimeout(hideTimeout)
  }

  if (props.delay > 0) {
    showTimeout = setTimeout(() => {
      isVisible.value = true
    }, props.delay)
  } else {
    isVisible.value = true
  }
}

function hide(): void {
  if (props.disabled) return

  if (props.trigger === 'manual') {
    return
  }

  if (showTimeout !== null) {
    clearTimeout(showTimeout)
  }

  if (props.delay > 0) {
    hideTimeout = setTimeout(() => {
      isVisible.value = false
    }, props.delay)
  } else {
    isVisible.value = false
  }
}

function toggle(): void {
  if (props.disabled) return
  isVisible.value = !isVisible.value
}

// Clean up timeouts
onBeforeUnmount(() => {
  if (showTimeout !== null) {
    clearTimeout(showTimeout)
  }
  if (hideTimeout !== null) {
    clearTimeout(hideTimeout)
  }
})

// Expose methods to parent components
defineExpose({
  show,
  hide,
  toggle
})
</script>

<style scoped>
.hb-tooltip-container {
  position: relative;
  display: inline-block;
}

.hb-tooltip {
  position: absolute;
  z-index: 50;
  max-width: 300px;
  padding: 0.5rem;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  pointer-events: none;
}

.hb-tooltip__content {
  font-size: var(--text-xs);
  line-height: 1.4;
  white-space: normal;
  word-wrap: break-word;
}

/* Positions */
.hb-tooltip--top {
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(-0.5rem);
  margin-bottom: 0.5rem;
}

.hb-tooltip--bottom {
  top: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(0.5rem);
  margin-top: 0.5rem;
}

.hb-tooltip--left {
  right: 100%;
  top: 50%;
  transform: translateX(-0.5rem) translateY(-50%);
  margin-right: 0.5rem;
}

.hb-tooltip--right {
  left: 100%;
  top: 50%;
  transform: translateX(0.5rem) translateY(-50%);
  margin-left: 0.5rem;
}

/* Arrows */
.hb-tooltip--arrow .hb-tooltip__arrow {
  position: absolute;
  width: 0.5rem;
  height: 0.5rem;
  transform: rotate(45deg);
}

.hb-tooltip--top.hb-tooltip--arrow .hb-tooltip__arrow {
  bottom: -0.25rem;
  left: 50%;
  margin-left: -0.25rem;
}

.hb-tooltip--bottom.hb-tooltip--arrow .hb-tooltip__arrow {
  top: -0.25rem;
  left: 50%;
  margin-left: -0.25rem;
}

.hb-tooltip--left.hb-tooltip--arrow .hb-tooltip__arrow {
  right: -0.25rem;
  top: 50%;
  margin-top: -0.25rem;
}

.hb-tooltip--right.hb-tooltip--arrow .hb-tooltip__arrow {
  left: -0.25rem;
  top: 50%;
  margin-top: -0.25rem;
}

/* Variants */
.hb-tooltip--dark {
  background-color: var(--gray-800);
  color: white;
}

.hb-tooltip--dark.hb-tooltip--arrow .hb-tooltip__arrow {
  background-color: var(--gray-800);
}

.hb-tooltip--light {
  background-color: white;
  color: var(--gray-800);
  border: 1px solid var(--gray-200);
}

.hb-tooltip--light.hb-tooltip--arrow .hb-tooltip__arrow {
  background-color: white;
  border: 1px solid var(--gray-200);
  border-top: none;
  border-left: none;
}

.hb-tooltip--primary {
  background-color: var(--primary-500);
  color: white;
}

.hb-tooltip--primary.hb-tooltip--arrow .hb-tooltip__arrow {
  background-color: var(--primary-500);
}

.hb-tooltip--success {
  background-color: var(--success-500);
  color: white;
}

.hb-tooltip--success.hb-tooltip--arrow .hb-tooltip__arrow {
  background-color: var(--success-500);
}

.hb-tooltip--danger {
  background-color: var(--danger-500);
  color: white;
}

.hb-tooltip--danger.hb-tooltip--arrow .hb-tooltip__arrow {
  background-color: var(--danger-500);
}

.hb-tooltip--warning {
  background-color: var(--warning-500);
  color: white;
}

.hb-tooltip--warning.hb-tooltip--arrow .hb-tooltip__arrow {
  background-color: var(--warning-500);
}

.hb-tooltip--info {
  background-color: var(--info-500);
  color: white;
}

.hb-tooltip--info.hb-tooltip--arrow .hb-tooltip__arrow {
  background-color: var(--info-500);
}
</style>
