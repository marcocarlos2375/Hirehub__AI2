<template>
  <div class="hb-slider" :class="rootClasses">
    <!-- Label (shared across modes) -->
    <div v-if="label" class="hb-slider__label">
      {{ label }}<span v-if="required" class="required">*</span>
    </div>

    <!-- Helper Text (shared) -->
    <div v-if="helperText && !error" class="hb-slider__helper">
      {{ helperText }}
    </div>

    <!-- CAROUSEL MODE -->
    <div v-if="mode === 'carousel'" class="hb-slider__carousel" :class="carouselClasses">
      <!-- Arrow Navigation (Left/Previous) -->
      <button
        v-if="showArrows"
        class="hb-slider__arrow hb-slider__arrow--prev"
        @click="prev"
        :disabled="disabled || (!loop && currentSlide === 0)"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <!-- Slides Container -->
      <div class="hb-slider__container" :style="containerStyle">
        <div
          class="hb-slider__track"
          :class="trackClasses"
          :style="trackStyle"
          @touchstart="handleTouchStart"
          @touchmove="handleTouchMove"
          @touchend="handleTouchEnd"
          @mouseenter="isHovering = true"
          @mouseleave="isHovering = false"
        >
          <slot />
        </div>
      </div>

      <!-- Arrow Navigation (Right/Next) -->
      <button
        v-if="showArrows"
        class="hb-slider__arrow hb-slider__arrow--next"
        @click="next"
        :disabled="disabled || (!loop && currentSlide === props.slideCount - 1)"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>

      <!-- Dot Navigation -->
      <div
        v-if="showDots"
        class="hb-slider__dots"
        :class="[
          `hb-slider__dots--${dotPosition}`,
          `hb-slider__dots--${dotAlignment}`
        ]"
      >
        <button
          v-for="(_, index) in props.slideCount"
          :key="index"
          class="hb-slider__dot"
          :class="{ 'hb-slider__dot--active': currentSlide === index }"
          @click="goToSlide(index)"
          :disabled="disabled"
        />
      </div>
    </div>

    <!-- RANGE MODE -->
    <div v-else class="hb-slider__range" :class="rangeClasses">
      <div v-if="showValue && !range" class="hb-slider__value">
        {{ displayValue }}
      </div>
      <div v-if="showValue && range" class="hb-slider__value-range">
        <span>{{ displayValueLower }}</span>
        <span>{{ displayValueUpper }}</span>
      </div>

      <div class="hb-slider__range-container">
        <!-- Native input(s) for accessibility -->
        <input
          v-if="!range"
          type="range"
          :id="inputId"
          :min="min"
          :max="max"
          :step="step"
          :disabled="disabled"
          :value="numericValue"
          @input="updateRangeValue"
          class="hb-slider__range-input"
        />

        <!-- Dual inputs for range mode -->
        <template v-else>
          <input
            type="range"
            :id="`${inputId}-lower`"
            :min="min"
            :max="max"
            :step="step"
            :disabled="disabled"
            :value="numericValueLower"
            @input="updateRangeLower"
            class="hb-slider__range-input hb-slider__range-input--lower"
          />
          <input
            type="range"
            :id="`${inputId}-upper`"
            :min="min"
            :max="max"
            :step="step"
            :disabled="disabled"
            :value="numericValueUpper"
            @input="updateRangeUpper"
            class="hb-slider__range-input hb-slider__range-input--upper"
          />
        </template>

        <!-- Custom track -->
        <div class="hb-slider__range-track">
          <div
            class="hb-slider__range-progress"
            :style="progressStyle"
          ></div>

          <!-- Thumb(s) -->
          <div
            v-if="!range"
            class="hb-slider__thumb"
            :style="{ left: thumbPosition }"
          ></div>
          <template v-else>
            <div class="hb-slider__thumb" :style="{ left: thumbPositionLower }"></div>
            <div class="hb-slider__thumb" :style="{ left: thumbPositionUpper }"></div>
          </template>
        </div>

        <!-- Ticks -->
        <div v-if="showTicks" class="hb-slider__ticks">
          <div
            v-for="tick in ticksArray"
            :key="tick.value"
            class="hb-slider__tick"
            :class="{ 'hb-slider__tick--active': isTickActive(tick.value) }"
            :style="{ left: `${calculateTickPosition(tick.value)}%` }"
          >
            <div class="hb-slider__tick-mark"></div>
            <div v-if="tick.label" class="hb-slider__tick-label">{{ tick.label }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Message (shared) -->
    <div v-if="error" class="hb-slider__error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'

interface SliderTick {
  value: number
  label?: string
}

interface Props {
  // Core mode selector
  mode?: 'carousel' | 'range'
  modelValue?: number | number[]

  // CAROUSEL MODE PROPS
  slideCount?: number
  autoplay?: boolean
  interval?: number
  loop?: boolean
  transition?: 'slide' | 'fade' | 'scale'
  direction?: 'horizontal' | 'vertical'
  navigation?: 'dots' | 'arrows' | 'both' | 'none'
  showDots?: boolean
  showArrows?: boolean
  dotPosition?: 'bottom' | 'top' | 'left' | 'right'
  dotAlignment?: 'start' | 'center' | 'end'
  arrowPosition?: 'inside' | 'outside'
  pauseOnHover?: boolean
  swipeable?: boolean
  height?: string | number

  // RANGE MODE PROPS
  min?: number
  max?: number
  step?: number
  range?: boolean
  variant?: 'default' | 'gradient' | 'segmented'
  size?: 'sm' | 'md' | 'lg'
  showValue?: boolean
  showTicks?: boolean
  ticks?: SliderTick[]
  valueFormat?: (value: number) => string
  marks?: Record<number, string>

  // SHARED PROPS
  disabled?: boolean
  label?: string
  helperText?: string
  error?: string
  required?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'carousel',
  modelValue: 0,

  // Carousel defaults
  slideCount: 0,
  autoplay: false,
  interval: 3000,
  loop: true,
  transition: 'slide',
  direction: 'horizontal',
  navigation: 'both',
  showDots: true,
  showArrows: true,
  dotPosition: 'bottom',
  dotAlignment: 'center',
  arrowPosition: 'inside',
  pauseOnHover: true,
  swipeable: true,

  // Range defaults
  min: 0,
  max: 100,
  step: 1,
  range: false,
  variant: 'default',
  size: 'md',
  showValue: true,
  showTicks: false,
  ticks: () => [],
  valueFormat: (value: number) => value.toString(),
  marks: () => ({}),

  // Shared defaults
  disabled: false,
  required: false
})

interface Emits {
  (e: 'update:modelValue', value: number | number[]): void
  (e: 'change', value: number | number[]): void
  (e: 'before-change', from: number, to: number): void
  (e: 'after-change', index: number): void
  (e: 'input', value: number | number[]): void
}

const emit = defineEmits<Emits>()

// ===== CAROUSEL STATE =====
const currentSlide = ref(props.mode === 'carousel' ? (props.modelValue as number) : 0)
const autoplayTimer = ref<number | null>(null)
const isHovering = ref(false)
const touchStartX = ref(0)
const touchStartY = ref(0)

// ===== RANGE STATE =====
const inputId = ref(`slider-${Math.random().toString(36).substring(2, 9)}`)

// ===== COMPUTED: Shared =====
const rootClasses = computed(() => ({
  [`hb-slider--${props.mode}`]: true,
  'hb-slider--disabled': props.disabled,
  'has-error': !!props.error
}))

// ===== COMPUTED: Carousel =====
const carouselClasses = computed(() => ({
  [`hb-slider--${props.transition}`]: true,
  [`hb-slider--${props.direction}`]: true,
  [`hb-slider--arrow-${props.arrowPosition}`]: props.showArrows
}))

const trackClasses = computed(() => ({
  'hb-slider__track--sliding': props.transition === 'slide'
}))

const trackStyle = computed(() => {
  if (props.mode !== 'carousel') return {}

  const isHorizontal = props.direction === 'horizontal'
  const translateValue = -currentSlide.value * 100
  const transform = isHorizontal
    ? `translateX(${translateValue}%)`
    : `translateY(${translateValue}%)`

  return {
    transform,
    transition: `transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)`
  }
})

const containerStyle = computed(() => {
  if (props.mode !== 'carousel' || !props.height) return {}
  const height = typeof props.height === 'number' ? `${props.height}px` : props.height
  return { height }
})

// ===== COMPUTED: Range =====
const rangeClasses = computed(() => ({
  [`hb-slider__range--${props.variant}`]: true,
  [`hb-slider__range--${props.size}`]: true,
  'hb-slider__range--dual': props.range
}))

const numericValue = computed<number>(() => {
  if (props.mode !== 'range' || props.range) return 0
  return Number(props.modelValue)
})

const numericValueLower = computed<number>(() => {
  if (props.mode !== 'range' || !props.range) return 0
  const values = props.modelValue as number[]
  return values?.[0] ?? props.min ?? 0
})

const numericValueUpper = computed<number>(() => {
  if (props.mode !== 'range' || !props.range) return 0
  const values = props.modelValue as number[]
  return values?.[1] ?? props.max ?? 100
})

const displayValue = computed<string>(() => {
  if (props.mode !== 'range') return ''
  return props.valueFormat(numericValue.value)
})

const displayValueLower = computed<string>(() => {
  if (props.mode !== 'range') return ''
  return props.valueFormat(numericValueLower.value)
})

const displayValueUpper = computed<string>(() => {
  if (props.mode !== 'range') return ''
  return props.valueFormat(numericValueUpper.value)
})

const thumbPosition = computed<string>(() => {
  if (props.mode !== 'range' || props.range) return '0%'
  const percentage = ((numericValue.value - props.min) / (props.max - props.min)) * 100
  return `${percentage}%`
})

const thumbPositionLower = computed<string>(() => {
  if (props.mode !== 'range' || !props.range) return '0%'
  const min = props.min ?? 0
  const max = props.max ?? 100
  const percentage = ((numericValueLower.value - min) / (max - min)) * 100
  return `${percentage}%`
})

const thumbPositionUpper = computed<string>(() => {
  if (props.mode !== 'range' || !props.range) return '0%'
  const min = props.min ?? 0
  const max = props.max ?? 100
  const percentage = ((numericValueUpper.value - min) / (max - min)) * 100
  return `${percentage}%`
})

const progressStyle = computed(() => {
  if (props.mode !== 'range') return {}

  if (!props.range) {
    return { width: thumbPosition.value }
  } else {
    return {
      left: thumbPositionLower.value,
      width: `calc(${thumbPositionUpper.value} - ${thumbPositionLower.value})`
    }
  }
})

const ticksArray = computed<SliderTick[]>(() => {
  if (props.mode !== 'range') return []

  if (props.ticks.length > 0) return props.ticks

  // Auto-generate ticks from marks
  const marksArray = Object.entries(props.marks).map(([value, label]) => ({
    value: Number(value),
    label
  }))

  return marksArray
})

// ===== METHODS: Carousel =====
const next = () => {
  if (props.disabled || props.mode !== 'carousel') return
  const nextIndex = currentSlide.value + 1
  if (nextIndex < props.slideCount) {
    goToSlide(nextIndex)
  } else if (props.loop) {
    goToSlide(0)
  }
}

const prev = () => {
  if (props.disabled || props.mode !== 'carousel') return
  const prevIndex = currentSlide.value - 1
  if (prevIndex >= 0) {
    goToSlide(prevIndex)
  } else if (props.loop) {
    goToSlide(props.slideCount - 1)
  }
}

const goToSlide = (index: number) => {
  if (props.disabled || props.mode !== 'carousel' || index === currentSlide.value) return
  emit('before-change', currentSlide.value, index)
  currentSlide.value = index
  emit('update:modelValue', index)
  emit('change', index)
  emit('after-change', index)
}

const startAutoplay = () => {
  if (props.mode !== 'carousel' || !props.autoplay || props.disabled) return
  stopAutoplay()
  autoplayTimer.value = window.setInterval(() => {
    if (!isHovering.value || !props.pauseOnHover) {
      next()
    }
  }, props.interval)
}

const stopAutoplay = () => {
  if (autoplayTimer.value) {
    clearInterval(autoplayTimer.value)
    autoplayTimer.value = null
  }
}

const handleTouchStart = (e: TouchEvent) => {
  if (props.mode !== 'carousel' || !props.swipeable || props.disabled) return
  const touch = e.touches[0]
  if (!touch) return
  touchStartX.value = touch.clientX
  touchStartY.value = touch.clientY
}

const handleTouchMove = (_e: TouchEvent) => {
  // Could prevent scrolling here
}

const handleTouchEnd = (e: TouchEvent) => {
  if (props.mode !== 'carousel' || !props.swipeable || props.disabled) return
  const touch = e.changedTouches[0]
  if (!touch) return
  const touchEndX = touch.clientX
  const touchEndY = touch.clientY
  const diffX = touchStartX.value - touchEndX
  const diffY = touchStartY.value - touchEndY

  if (props.direction === 'horizontal' && Math.abs(diffX) > 50) {
    if (diffX > 0) next()
    else prev()
  } else if (props.direction === 'vertical' && Math.abs(diffY) > 50) {
    if (diffY > 0) next()
    else prev()
  }
}

// ===== METHODS: Range =====
const updateRangeValue = (event: Event): void => {
  if (props.mode !== 'range' || props.range) return
  const target = event.target as HTMLInputElement
  const newValue = Number(target.value)
  emit('update:modelValue', newValue)
  emit('change', newValue)
  emit('input', newValue)
}

const updateRangeLower = (event: Event): void => {
  if (props.mode !== 'range' || !props.range) return
  const target = event.target as HTMLInputElement
  const newLower = Number(target.value)
  const upper = numericValueUpper.value

  // Prevent crossing
  if (newLower <= upper) {
    emit('update:modelValue', [newLower, upper])
    emit('change', [newLower, upper])
    emit('input', [newLower, upper])
  }
}

const updateRangeUpper = (event: Event): void => {
  if (props.mode !== 'range' || !props.range) return
  const target = event.target as HTMLInputElement
  const newUpper = Number(target.value)
  const lower = numericValueLower.value

  // Prevent crossing
  if (newUpper >= lower) {
    emit('update:modelValue', [lower, newUpper])
    emit('change', [lower, newUpper])
    emit('input', [lower, newUpper])
  }
}

const calculateTickPosition = (value: number): number => {
  if (props.mode !== 'range') return 0
  return ((value - props.min) / (props.max - props.min)) * 100
}

const isTickActive = (value: number): boolean => {
  if (props.mode !== 'range') return false

  if (!props.range) {
    return numericValue.value >= value
  } else {
    return value >= numericValueLower.value && value <= numericValueUpper.value
  }
}

// ===== LIFECYCLE =====
onMounted(() => {
  if (props.mode === 'carousel') {
    startAutoplay()
  }
})

onUnmounted(() => {
  stopAutoplay()
})

watch(() => props.modelValue, (newVal) => {
  if (props.mode === 'carousel') {
    currentSlide.value = newVal as number
  }
})

watch(() => props.autoplay, (newVal) => {
  if (props.mode === 'carousel') {
    if (newVal) startAutoplay()
    else stopAutoplay()
  }
})
</script>

<style lang="scss" scoped>
.hb-slider {
  width: 100%;
  margin-bottom: var(--spacing-4);
  position: relative;

  &__label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: var(--font-medium);
    font-size: var(--text-sm);
    margin-bottom: var(--spacing-2);

    .required {
      color: var(--danger-500);
      margin-left: var(--spacing-0-5);
    }
  }

  &__helper {
    font-size: var(--text-xs);
    color: var(--gray-500);
    margin-bottom: var(--spacing-2);
  }

  &__error {
    margin-top: var(--spacing-1);
    font-size: var(--text-xs);
    color: var(--danger-500);
  }

  // ===== CAROUSEL MODE =====
  &__carousel {
    position: relative;
    overflow: hidden;
  }

  &__container {
    position: relative;
    overflow: hidden;
    width: 100%;
    height: 100%;
  }

  &__track {
    display: flex;
    height: 100%;

    &--sliding {
      transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    :deep(> *) {
      flex-shrink: 0;
      width: 100%;
    }
  }

  &--vertical &__track {
    flex-direction: column;
  }

  &__arrow {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    z-index: 10;
    background: rgba(255, 255, 255, 0.9);
    border: none;
    width: 40px;
    height: 40px;
    border-radius: var(--radius-full);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all var(--transition-fast);

    &:hover:not(:disabled) {
      background: var(--white);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }

    &:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }

    &--prev {
      left: var(--spacing-2);
    }

    &--next {
      right: var(--spacing-2);
    }
  }

  &--arrow-outside {
    .hb-slider__arrow--prev {
      left: calc(-40px - var(--spacing-2));
    }
    .hb-slider__arrow--next {
      right: calc(-40px - var(--spacing-2));
    }
  }

  &__dots {
    display: flex;
    gap: var(--spacing-2);
    padding: var(--spacing-3) 0;

    // Position variants
    &--top {
      order: -1;
    }

    &--bottom {
      /* Default positioning */
    }

    &--left {
      position: absolute;
      left: var(--spacing-4);
      top: 50%;
      transform: translateY(-50%);
      flex-direction: column;
      padding: 0;
    }

    &--right {
      position: absolute;
      right: var(--spacing-4);
      top: 50%;
      transform: translateY(-50%);
      flex-direction: column;
      padding: 0;
    }

    // Alignment variants (for top/bottom positions)
    &--start {
      justify-content: flex-start;
    }

    &--center {
      justify-content: center;
    }

    &--end {
      justify-content: flex-end;
    }

    // For left/right positions, alignment affects vertical positioning
    &--left {
      &.hb-slider__dots--start {
        top: var(--spacing-4);
        transform: none;
      }

      &.hb-slider__dots--end {
        top: auto;
        bottom: var(--spacing-4);
        transform: none;
      }
    }

    &--right {
      &.hb-slider__dots--start {
        top: var(--spacing-4);
        transform: none;
      }

      &.hb-slider__dots--end {
        top: auto;
        bottom: var(--spacing-4);
        transform: none;
      }
    }
  }

  &__dot {
    width: 10px;
    height: 10px;
    border-radius: var(--radius-full);
    background: var(--gray-300);
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    padding: 0;

    &:hover:not(:disabled) {
      background: var(--primary-300);
    }

    &--active {
      background: var(--primary-500);
      transform: scale(1.2);
    }

    &:disabled {
      cursor: not-allowed;
      opacity: 0.5;
    }
  }

  // ===== RANGE MODE =====
  &__range {
    position: relative;
  }

  &__value,
  &__value-range {
    font-weight: var(--font-medium);
    color: var(--gray-700);
    font-size: var(--text-sm);
    margin-bottom: var(--spacing-2);
  }

  &__value-range {
    display: flex;
    justify-content: space-between;
  }

  &__range-container {
    position: relative;
    height: 36px;
    display: flex;
    align-items: center;
  }

  &__range-input {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
    z-index: 2;

    &:disabled {
      cursor: not-allowed;
    }
  }

  &__range-track {
    position: relative;
    width: 100%;
    height: 6px;
    background-color: var(--gray-200);
    border-radius: var(--radius-full);
  }

  &__range-progress {
    position: absolute;
    height: 100%;
    background-color: var(--primary-500);
    border-radius: var(--radius-full);
    transition: all var(--transition-fast);
  }

  &__thumb {
    position: absolute;
    width: 20px;
    height: 20px;
    border-radius: var(--radius-md);
    background-color: var(--primary-500);
    border: 2px solid var(--primary-500);
    top: 50%;
    transform: translate(-50%, -50%);
    transition: all var(--transition-fast);
    z-index: 1;

    &:hover {
      transform: translate(-50%, -50%) scale(1.1);
    }
  }

  &__ticks {
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    margin-top: var(--spacing-2);
    height: 30px;
  }

  &__tick {
    position: absolute;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;

    &-mark {
      width: 2px;
      height: 8px;
      background-color: var(--gray-300);
      border-radius: var(--radius-full);
    }

    &-label {
      margin-top: var(--spacing-1);
      font-size: var(--text-xs);
      color: var(--gray-500);
      white-space: nowrap;
    }

    &--active {
      .hb-slider__tick-mark {
        background-color: var(--primary-500);
      }

      .hb-slider__tick-label {
        color: var(--primary-700);
        font-weight: var(--font-medium);
      }
    }
  }

  // Size variants (range mode)
  &__range--sm {
    .hb-slider__range-track {
      height: 4px;
    }
    .hb-slider__thumb {
      width: 16px;
      height: 16px;
    }
  }

  &__range--lg {
    .hb-slider__range-track {
      height: 8px;
    }
    .hb-slider__thumb {
      width: 24px;
      height: 24px;
    }
  }

  // Gradient variant
  &__range--gradient &__range-progress {
    background: linear-gradient(90deg, var(--primary-400), var(--primary-600));
  }

  // Disabled state
  &--disabled {
    opacity: 0.6;
    pointer-events: none;
  }

  // Error state
  &.has-error {
    .hb-slider__range-progress {
      background-color: var(--danger-500);
    }

    .hb-slider__thumb {
      border-color: var(--danger-500);
      background-color: var(--danger-500);
    }
  }
}
</style>
