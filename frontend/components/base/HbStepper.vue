<template>
  <div class="hb-stepper" :class="rootClasses">
    <!-- Stepper Header (steps navigation) - controlled by showHeader prop -->
    <div v-if="showHeader">
      <!-- Label -->
      <div v-if="label" class="hb-stepper__label">{{ label }}</div>

      <!-- Progress Bar (optional) -->
      <div v-if="showProgress" class="hb-stepper__progress-wrapper">
        <slot name="progress" :current="currentIndex" :total="visibleSteps.length" :percentage="progressPercentage">
          <HbProgressBar :value="progressPercentage" size="sm" />
        </slot>
      </div>

      <!-- Step Count (optional) -->
      <div v-if="showStepCount" class="hb-stepper__count">
        Step {{ currentStepNumber }} of {{ totalSteps }}
      </div>

      <!-- Steps Container -->
      <div class="hb-stepper__steps" :class="stepsClasses">
        <div
          v-for="(step, index) in visibleSteps"
          :key="step.id || index"
          class="hb-stepper__step"
          :class="getStepClasses(index)"
        >
          <!-- BORDER TYPE: Border-top indicator + label below -->
          <template v-if="stepperType === 'border'">
            <button
              class="hb-stepper__border-step"
              :class="getBorderStepClasses(index)"
              :disabled="!isStepClickable(index)"
              @click="handleStepClick(index)"
              :aria-current="index === currentIndex ? 'step' : undefined"
            >
              <div class="hb-stepper__border-top"></div>
              <div class="hb-stepper__content">
                <slot name="step-label" :step="step" :index="index">
                  <div class="hb-stepper__title">{{ step.label }}</div>
                  <div v-if="step.description" class="hb-stepper__description">
                    {{ step.description }}
                  </div>
                </slot>
              </div>
            </button>
          </template>

          <!-- NUMBER TYPE: Original circular indicator style -->
          <template v-else>
            <!-- Step Indicator -->
            <button
              class="hb-stepper__indicator"
              :disabled="!isStepClickable(index)"
              @click="handleStepClick(index)"
              :aria-current="index === currentIndex ? 'step' : undefined"
            >
              <slot name="step-number" :step="step" :index="index" :state="getStepState(index)">
                <span class="hb-stepper__number">
                  <HbIcon v-if="step.icon" :name="step.icon" />
                  <template v-else-if="step.completed">
                    <svg class="hb-stepper__check" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                  </template>
                  <template v-else-if="showStepNumber">{{ index + 1 }}</template>
                </span>
              </slot>
            </button>

            <!-- Step Label -->
            <div class="hb-stepper__content">
              <slot name="step-label" :step="step" :index="index">
                <div class="hb-stepper__title">{{ step.label }}</div>
                <div v-if="step.description" class="hb-stepper__description">{{ step.description }}</div>
              </slot>
            </div>

            <!-- Connector (only for number type) -->
            <div v-if="index < visibleSteps.length - 1 && showConnector" class="hb-stepper__connector">
              <slot name="connector" :fromStep="step" :toStep="visibleSteps[index + 1]" :completed="step.completed">
                <div class="hb-stepper__connector-line" :class="{ 'is-completed': step.completed }"></div>
              </slot>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="hb-stepper__body">
      <div
        :key="currentIndex"
        v-motion
        :initial="motionVariants.initial"
        :enter="motionVariants.enter"
      >
        <slot
          name="default"
          :index="currentIndex"
          :step="currentStep"
          :canGoNext="canGoNext"
          :canGoBack="canGoBack"
          :goNext="goToNext"
          :goBack="goToPrevious"
          :isFirstStep="isFirstStep"
          :isLastStep="isLastStep"
        />
      </div>
    </div>

    <!-- Built-in Navigation Footer -->
    <div v-if="showNavigation" class="hb-stepper__navigation mt-6 pt-4 border-t border-gray-200">
      <HbButton
        v-if="!isFirstStep"
        variant="outline"
        :disabled="!canGoBack || disabled || loading"
        @click="goToPrevious"
      >
        {{ backLabel }}
      </HbButton>

      <div v-else></div>

      <HbButton
        variant="primary"
        :disabled="isLastStep ? false : (!canGoNext || disabled || loading)"
        @click="isLastStep ? handleComplete() : goToNext()"
      >
        {{ isLastStep ? finishLabel : nextLabel }}
      </HbButton>
    </div>

    <!-- Custom Footer Navigation (optional slot) -->
    <div v-else-if="$slots.footer" class="hb-stepper__footer">
      <slot
        name="footer"
        :canGoNext="canGoNext"
        :canGoBack="canGoBack"
        :goNext="goToNext"
        :goBack="goToPrevious"
        :isFirstStep="isFirstStep"
        :isLastStep="isLastStep"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { computed, ref, watch } from 'vue'

interface Step {
  label: string
  description?: string
  completed?: boolean
  disabled?: boolean
  error?: boolean | string
  hidden?: boolean
  icon?: string
  id?: string
}

type StepValidator = (
  fromIndex: number,
  toIndex: number,
  steps: Step[]
) => boolean | Promise<boolean>

export type StepperType = 'number' | 'border'
export type StepperTransition = 'none' | 'fade' | 'slide' | 'slide-fade' | 'zoom'

interface Props {
  modelValue: number
  steps: Step[]
  stepperType?: StepperType
  transition?: StepperTransition
  orientation?: 'horizontal' | 'vertical'
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'compact' | 'pills'
  allowSkip?: boolean
  allowBack?: boolean
  linear?: boolean
  clickable?: boolean
  showNavigation?: boolean
  showHeader?: boolean
  nextLabel?: string
  backLabel?: string
  finishLabel?: string
  validator?: StepValidator
  showConnector?: boolean
  showProgress?: boolean
  showStepCount?: boolean
  showStepNumber?: boolean
  editable?: boolean
  disabled?: boolean
  loading?: boolean
  label?: string
}

const props = withDefaults(defineProps<Props>(), {
  stepperType: 'number',
  transition: 'slide',
  orientation: 'horizontal',
  size: 'md',
  variant: 'default',
  allowSkip: false,
  allowBack: true,
  linear: false,
  clickable: true,
  showNavigation: false,
  showHeader: true,
  nextLabel: 'Next',
  backLabel: 'Back',
  finishLabel: 'Finish',
  showConnector: true,
  showProgress: false,
  showStepCount: false,
  showStepNumber: true,
  editable: true,
  disabled: false,
  loading: false
})

interface Emits {
  (e: 'update:modelValue', index: number): void
  (e: 'before-change', from: number, to: number): void
  (e: 'after-change', index: number): void
  (e: 'change', index: number): void
  (e: 'step-complete', index: number): void
  (e: 'complete'): void
  (e: 'validation-failed', from: number, to: number): void
}

const emit = defineEmits<Emits>()

// ===== STATE =====
const currentIndex = ref(props.modelValue)
const previousIndex = ref(props.modelValue)
const transitionDirection = ref<'forward' | 'backward'>('forward')

// ===== COMPUTED: Visible Steps =====
const visibleSteps = computed(() => {
  return props.steps.filter(step => !step.hidden)
})

const currentStep = computed(() => {
  return visibleSteps.value[currentIndex.value]
})

// Transition name based on animation type and direction
const transitionName = computed(() => {
  if (props.transition === 'none') return ''
  if (props.transition === 'slide') {
    return transitionDirection.value === 'forward' ? 'slide-left' : 'slide-right'
  }
  if (props.transition === 'slide-fade') {
    return transitionDirection.value === 'forward' ? 'slide-fade-left' : 'slide-fade-right'
  }
  return `stepper-${props.transition}`
})

// VueUse Motion variants
const motionVariants = computed(() => {
  const isForward = transitionDirection.value === 'forward'

  if (props.transition === 'none') {
    return {
      initial: {},
      enter: {}
    }
  }

  if (props.transition === 'slide') {
    return {
      initial: {
        opacity: 0,
        x: isForward ? 100 : -100
      },
      enter: {
        opacity: 1,
        x: 0,
        transition: {
          type: 'spring',
          stiffness: 250,
          damping: 25
        }
      }
    }
  }

  if (props.transition === 'fade') {
    return {
      initial: { opacity: 0 },
      enter: {
        opacity: 1,
        transition: { duration: 300 }
      }
    }
  }

  if (props.transition === 'zoom') {
    return {
      initial: { opacity: 0, scale: 0.9 },
      enter: {
        opacity: 1,
        scale: 1,
        transition: { duration: 300 }
      }
    }
  }

  // slide-fade
  return {
    initial: {
      opacity: 0,
      x: isForward ? 120 : -120
    },
    enter: {
      opacity: 1,
      x: 0,
      transition: {
        type: 'spring',
        stiffness: 200,
        damping: 20
      }
    }
  }
})

// ===== COMPUTED: Navigation State =====
const isFirstStep = computed(() => currentIndex.value === 0)
const isLastStep = computed(() => currentIndex.value === visibleSteps.value.length - 1)

const canGoBack = computed(() => {
  if (isFirstStep.value) return false
  if (!props.allowBack) return false
  if (props.disabled || props.loading) return false
  return true
})

const canGoNext = computed(() => {
  if (isLastStep.value) return false
  if (props.disabled || props.loading) return false

  const nextStep = visibleSteps.value[currentIndex.value + 1]
  if (nextStep?.disabled) return false

  if (props.linear && !currentStep.value?.completed) return false

  return true
})

// ===== COMPUTED: Progress =====
const progressPercentage = computed(() => {
  const completed = visibleSteps.value.filter(s => s.completed).length
  return Math.round((completed / visibleSteps.value.length) * 100)
})

const currentStepNumber = computed(() => currentIndex.value + 1)
const totalSteps = computed(() => visibleSteps.value.length)

// ===== COMPUTED: Classes =====
const rootClasses = computed(() => ({
  [`hb-stepper--${props.orientation}`]: true,
  [`hb-stepper--${props.size}`]: true,
  [`hb-stepper--${props.variant}`]: true,
  [`hb-stepper--${props.stepperType}`]: true,
  'hb-stepper--disabled': props.disabled,
  'hb-stepper--loading': props.loading
}))

const stepsClasses = computed(() => ({
  'hb-stepper__steps--horizontal': props.orientation === 'horizontal',
  'hb-stepper__steps--vertical': props.orientation === 'vertical',
  'hb-stepper__steps--border': props.stepperType === 'border'
}))

// ===== METHODS: Step State =====
const getStepState = (index: number): string => {
  const step = visibleSteps.value[index]
  if (!step) return 'pending'

  if (index === currentIndex.value) return 'active'
  if (step.error) return 'error'
  if (step.completed || index < currentIndex.value) return 'completed'  // Mark previous steps as completed
  if (step.disabled) return 'disabled'

  return 'pending'
}

const getStepClasses = (index: number) => {
  const state = getStepState(index)
  return {
    [`hb-stepper__step--${state}`]: true,
    'hb-stepper__step--clickable': isStepClickable(index)
  }
}

const isStepClickable = (index: number): boolean => {
  if (!props.clickable) return false
  if (index === currentIndex.value) return false
  if (props.disabled || props.loading) return false

  const step = visibleSteps.value[index]
  if (step?.disabled) return false

  // Can't click future steps in linear mode unless they're completed
  if (props.linear && index > currentIndex.value && !step?.completed) {
    return false
  }

  // Can't click completed steps if not editable
  if (!props.editable && step?.completed && index < currentIndex.value) {
    return false
  }

  return true
}

const getBorderStepClasses = (index: number) => {
  const state = getStepState(index)
  return {
    'hb-stepper__border-step--active': state === 'active',
    'hb-stepper__border-step--completed': state === 'completed',
    'hb-stepper__border-step--pending': state === 'pending',
    'hb-stepper__border-step--error': state === 'error',
    'hb-stepper__border-step--disabled': state === 'disabled',
    'hb-stepper__border-step--clickable': isStepClickable(index)
  }
}

// ===== METHODS: Navigation =====
const canNavigateTo = async (targetIndex: number): Promise<boolean> => {
  if (props.disabled || props.loading) return false

  const targetStep = visibleSteps.value[targetIndex]
  if (!targetStep || targetStep.disabled) return false

  // Linear mode validation
  if (props.linear && targetIndex > currentIndex.value) {
    const allPreviousCompleted = visibleSteps.value
      .slice(0, targetIndex)
      .every(step => step.completed)

    if (!allPreviousCompleted) return false
  }

  // Check allowBack
  if (!props.allowBack && targetIndex < currentIndex.value) return false

  // Check allowSkip
  if (!props.allowSkip && targetIndex > currentIndex.value + 1) return false

  // Custom validator
  if (props.validator) {
    try {
      const result = await props.validator(currentIndex.value, targetIndex, props.steps)
      if (!result) {
        emit('validation-failed', currentIndex.value, targetIndex)
        return false
      }
    } catch (error) {
      console.error('Step validation error:', error)
      return false
    }
  }

  return true
}

const goToStep = async (index: number) => {
  if (index === currentIndex.value) return

  const canNavigate = await canNavigateTo(index)
  if (!canNavigate) return

  // Track direction for transition
  transitionDirection.value = index > currentIndex.value ? 'forward' : 'backward'
  previousIndex.value = currentIndex.value

  emit('before-change', currentIndex.value, index)
  currentIndex.value = index
  emit('update:modelValue', index)
  emit('change', index)
  emit('after-change', index)

  // Check if all steps completed
  if (visibleSteps.value.every(s => s.completed)) {
    emit('complete')
  }
}

const goToNext = async () => {
  if (canGoNext.value) {
    await goToStep(currentIndex.value + 1)
  }
}

const goToPrevious = async () => {
  if (canGoBack.value) {
    await goToStep(currentIndex.value - 1)
  }
}

const handleStepClick = async (index: number) => {
  if (isStepClickable(index)) {
    await goToStep(index)
  }
}

const handleComplete = () => {
  emit('complete')
}

// ===== WATCHERS =====
watch(() => props.modelValue, (newVal) => {
  if (newVal !== currentIndex.value) {
    // Track direction for transition
    transitionDirection.value = newVal > currentIndex.value ? 'forward' : 'backward'
    previousIndex.value = currentIndex.value
    currentIndex.value = newVal
  }
})
</script>

<style scoped lang="scss">
.hb-stepper {
  width: 100%;

  &__label {
    font-weight: var(--font-semibold);
    font-size: var(--text-lg);
    margin-bottom: var(--spacing-4);
    color: var(--gray-900);
  }

  &__progress-wrapper {
    margin-bottom: var(--spacing-4);
  }

  &__count {
    font-size: var(--text-sm);
    color: var(--gray-600);
    margin-bottom: var(--spacing-3);
    text-align: center;
  }

  // ===== STEPS CONTAINER =====
  &__steps {
    display: flex;
    margin-bottom: var(--spacing-6);

    &--horizontal {
      flex-direction: row;
      align-items: flex-start;
    }

    &--vertical {
      flex-direction: column;
    }
  }

  // ===== INDIVIDUAL STEP =====
  &__step {
    position: relative;
    display: flex;
    align-items: center;
    flex: 1;

    &--clickable {
      .hb-stepper__indicator {
        cursor: pointer;

        &:hover:not(:disabled) {
          .hb-stepper__number {
            transform: scale(1.05);
          }
        }
      }
    }
  }

  // ===== STEP INDICATOR =====
  &__indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: none;
    border: none;
    padding: 0;
    transition: all var(--transition-fast);

    &:disabled {
      cursor: not-allowed;
    }
  }

  &__number {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-full);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: var(--font-semibold);
    font-size: var(--text-sm);
    border: 2px solid var(--gray-300);
    background: var(--white);
    color: var(--gray-600);
    transition: all var(--transition-fast);
  }

  &__check {
    width: 20px;
    height: 20px;
  }

  // ===== STEP STATES =====
  &__step--active &__number {
    background: var(--primary-500);
    border-color: var(--primary-500);
    color: var(--white);
  }

  &__step--completed &__number {
    background: var(--success-500);
    border-color: var(--success-500);
    color: var(--white);
  }

  &__step--error &__number {
    background: var(--danger-500);
    border-color: var(--danger-500);
    color: var(--white);
  }

  &__step--disabled &__number {
    opacity: 0.5;
    cursor: not-allowed;
  }

  // ===== STEP CONTENT =====
  &__content {
    margin-top: var(--spacing-2);
    text-align: center;
  }

  &__title {
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    color: var(--gray-900);
  }

  &__description {
    font-size: var(--text-xs);
    color: var(--gray-600);
    margin-top: var(--spacing-1);
  }

  // ===== CONNECTOR =====
  &__connector {
    flex: 1;
    display: flex;
    align-items: center;
    padding: 0 var(--spacing-2);
  }

  &__connector-line {
    width: 100%;
    height: 2px;
    background: var(--gray-300);
    transition: background var(--transition-fast);

    &.is-completed {
      background: var(--success-500);
    }
  }

  // ===== VERTICAL ORIENTATION =====
  &--vertical {
    .hb-stepper__step {
      flex-direction: column;
      align-items: flex-start;
    }

    .hb-stepper__connector {
      width: 2px;
      height: 40px;
      flex: none;
      padding: var(--spacing-2) 0;
      margin-left: 19px; // Center with indicator
    }

    .hb-stepper__connector-line {
      width: 2px;
      height: 100%;
    }

    .hb-stepper__content {
      margin-top: 0;
      margin-left: var(--spacing-3);
      text-align: left;
    }
  }

  // ===== SIZE VARIANTS =====
  &--sm {
    .hb-stepper__number {
      width: 32px;
      height: 32px;
      font-size: var(--text-xs);
    }

    .hb-stepper__title {
      font-size: var(--text-xs);
    }
  }

  &--lg {
    .hb-stepper__number {
      width: 48px;
      height: 48px;
      font-size: var(--text-base);
    }

    .hb-stepper__title {
      font-size: var(--text-base);
    }
  }

  // ===== VARIANT: COMPACT =====
  &--compact {
    .hb-stepper__content {
      display: none;
    }
  }

  // ===== VARIANT: PILLS =====
  &--pills {
    .hb-stepper__number {
      border-radius: var(--radius-lg);
      width: auto;
      padding: 0 var(--spacing-3);
    }
  }

  // ===== BODY & FOOTER =====
  &__body {
    margin-top: var(--spacing-6);
    overflow-x: hidden;
  }

  &__footer {
    margin-top: var(--spacing-4);
    display: flex;
    justify-content: space-between;
    gap: var(--spacing-3);
  }

  // ===== BUILT-IN NAVIGATION =====
  &__navigation {
    // margin-top and padding-top moved to Tailwind classes in template
    // border-top moved to Tailwind classes in template
    display: flex;
    justify-content: space-between;
    gap: var(--spacing-3);
  }

  // ===== STATES =====
  &--disabled {
    opacity: 0.6;
    pointer-events: none;
  }

  &--loading {
    pointer-events: none;
  }

  // ===== BORDER STEPPER TYPE =====
  &--border {
    // Add gap between steps
    .hb-stepper__steps--border {
      gap: var(--spacing-4);
    }

    .hb-stepper__step {
      flex: 1 1 0;        // Flexible width calculation
      min-width: 0;       // Allow shrinking for equal distribution
    }

    .hb-stepper__border-step {
      width: 100%;
      display: flex;
      flex-direction: column;
      background: none;
      border: none;
      padding: 0;
      cursor: default;
      text-align: left;
      transition: all var(--transition-fast);

      &--clickable {
        cursor: pointer;

        &:hover:not(&--disabled) {
          opacity: 0.8;
        }
      }

      &--disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }

    .hb-stepper__border-top {
      height: 3px;        // 3px border (matching old design)
      width: 100%;
      background: var(--gray-300);
      margin-bottom: var(--spacing-3);
      transition: background var(--transition-fast);
    }

    // Active step - primary-500 color
    .hb-stepper__border-step--active .hb-stepper__border-top {
      background: var(--primary-500);
    }

    // Completed step - success color
    .hb-stepper__border-step--completed .hb-stepper__border-top {
      background: var(--success-500);
    }

    // Pending step - gray-300 color (default)
    .hb-stepper__border-step--pending .hb-stepper__border-top {
      background: var(--gray-300);
    }

    // Error step - danger color
    .hb-stepper__border-step--error .hb-stepper__border-top {
      background: var(--danger-500);
    }

    .hb-stepper__content {
      margin-top: 0;
      text-align: left;
    }

    .hb-stepper__title {
      font-size: var(--text-sm);
      font-weight: var(--font-medium);
      color: var(--gray-900);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .hb-stepper__description {
      font-size: var(--text-xs);
      color: var(--gray-600);
      margin-top: var(--spacing-1);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
    }
  }

  // ===== TRANSITION ANIMATIONS =====

  // Fade transition
  .stepper-fade-enter-active,
  .stepper-fade-leave-active {
    transition: opacity 0.3s ease;
  }
  .stepper-fade-enter-from,
  .stepper-fade-leave-to {
    opacity: 0;
  }

  // Zoom transition
  .stepper-zoom-enter-active,
  .stepper-zoom-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  .stepper-zoom-enter-from {
    opacity: 0;
    transform: scale(0.9);
  }
  .stepper-zoom-leave-to {
    opacity: 0;
    transform: scale(1.1);
  }

  // Slide left (forward) - content enters from RIGHT, exits to LEFT
  .slide-left-enter-active,
  .slide-left-leave-active {
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    position: absolute;
    width: 100%;
  }
  .slide-left-enter-from {
    opacity: 0;
    transform: translateX(100%);
  }
  .slide-left-leave-to {
    opacity: 0;
    transform: translateX(-100%);
  }

  // Slide right (backward) - content enters from LEFT, exits to RIGHT
  .slide-right-enter-active,
  .slide-right-leave-active {
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    position: absolute;
    width: 100%;
  }
  .slide-right-enter-from {
    opacity: 0;
    transform: translateX(-100%);
  }
  .slide-right-leave-to {
    opacity: 0;
    transform: translateX(100%);
  }

  // Slide-fade left (forward)
  .slide-fade-left-enter-active,
  .slide-fade-left-leave-active {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  }
  .slide-fade-left-enter-from {
    opacity: 0;
    transform: translateX(50px);
  }
  .slide-fade-left-leave-to {
    opacity: 0;
    transform: translateX(-50px);
  }

  // Slide-fade right (backward)
  .slide-fade-right-enter-active,
  .slide-fade-right-leave-active {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  }
  .slide-fade-right-enter-from {
    opacity: 0;
    transform: translateX(-50px);
  }
  .slide-fade-right-leave-to {
    opacity: 0;
    transform: translateX(50px);
  }
}
</style>
