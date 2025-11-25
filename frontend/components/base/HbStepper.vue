<template>
  <div class="hb-stepper" :class="[`hb-stepper--${orientation}`, `hb-stepper--${size}`]">
    <!-- Horizontal Stepper -->
    <div v-if="orientation === 'horizontal'" class="hb-stepper__container">
      <div class="hb-stepper__steps">
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="hb-stepper__step"
          :class="{
            'hb-stepper__step--active': index === activeStep,
            'hb-stepper__step--completed': index < activeStep,
            'hb-stepper__step--disabled': index > activeStep && !allowSkip
          }"
          @click="handleStepClick(index)"
        >
          <div class="hb-stepper__step-indicator">
            <div class="hb-stepper__step-icon">
              <template v-if="index < activeStep">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path fill-rule="evenodd" d="M19.916 4.626a.75.75 0 01.208 1.04l-9 13.5a.75.75 0 01-1.154.114l-6-6a.75.75 0 011.06-1.06l5.353 5.353 8.493-12.739a.75.75 0 011.04-.208z" clip-rule="evenodd" />
                </svg>
              </template>
              <template v-else>
                {{ index + 1 }}
              </template>
            </div>
          </div>
          <div class="hb-stepper__step-content">
            <div class="hb-stepper__step-title">{{ step.title }}</div>
            <div v-if="step.description" class="hb-stepper__step-description">
              {{ step.description }}
            </div>
          </div>
          <div v-if="index < steps.length - 1" class="hb-stepper__connector"></div>
        </div>
      </div>
      
      <!-- Content Area -->
      <div v-if="showContent" class="hb-stepper__content">
        <slot :step="steps[activeStep]" :index="activeStep"></slot>
      </div>
      
      <!-- Navigation Buttons -->
      <div v-if="showNavigation" class="hb-stepper__navigation">
        <HbButton 
          v-if="activeStep > 0" 
          @click="prev" 
          :variant="navigationButtonVariant"
          :size="navigationButtonSize"
        >
          {{ backLabel }}
        </HbButton>
        <div class="hb-stepper__spacer"></div>
        <HbButton 
          @click="next" 
          :variant="activeStep === steps.length - 1 ? finishButtonVariant : navigationButtonVariant"
          :size="navigationButtonSize"
        >
          {{ activeStep === steps.length - 1 ? finishLabel : nextLabel }}
        </HbButton>
      </div>
    </div>
    
    <!-- Vertical Stepper -->
    <div v-else class="hb-stepper__container">
      <div class="hb-stepper__layout">
        <div class="hb-stepper__steps hb-stepper__steps--vertical">
          <div
            v-for="(step, index) in steps"
            :key="index"
            class="hb-stepper__step hb-stepper__step--vertical"
            :class="{
              'hb-stepper__step--active': index === activeStep,
              'hb-stepper__step--completed': index < activeStep,
              'hb-stepper__step--disabled': index > activeStep && !allowSkip
            }"
            @click="handleStepClick(index)"
          >
            <div class="hb-stepper__step-indicator">
              <div class="hb-stepper__step-icon">
                <template v-if="index < activeStep">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path fill-rule="evenodd" d="M19.916 4.626a.75.75 0 01.208 1.04l-9 13.5a.75.75 0 01-1.154.114l-6-6a.75.75 0 011.06-1.06l5.353 5.353 8.493-12.739a.75.75 0 011.04-.208z" clip-rule="evenodd" />
                  </svg>
                </template>
                <template v-else>
                  {{ index + 1 }}
                </template>
              </div>
              <div v-if="index < steps.length - 1" class="hb-stepper__connector hb-stepper__connector--vertical"></div>
            </div>
            <div class="hb-stepper__step-content">
              <div class="hb-stepper__step-title">{{ step.title }}</div>
              <div v-if="step.description" class="hb-stepper__step-description">
                {{ step.description }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- Content Area -->
        <div v-if="showContent" class="hb-stepper__content hb-stepper__content--vertical">
          <slot :step="steps[activeStep]" :index="activeStep"></slot>
        </div>
      </div>
      
      <!-- Navigation Buttons -->
      <div v-if="showNavigation" class="hb-stepper__navigation">
        <HbButton 
          v-if="activeStep > 0" 
          @click="prev" 
          :variant="navigationButtonVariant"
          :size="navigationButtonSize"
        >
          {{ backLabel }}
        </HbButton>
        <div class="hb-stepper__spacer"></div>
        <HbButton 
          @click="next" 
          :variant="activeStep === steps.length - 1 ? finishButtonVariant : navigationButtonVariant"
          :size="navigationButtonSize"
        >
          {{ activeStep === steps.length - 1 ? finishLabel : nextLabel }}
        </HbButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { computed, watch } from 'vue'
import HbButton from './HbButton.vue'
import type { ButtonVariant, ButtonSize } from '~/types/components'

interface Step {
  title: string
  description?: string
}

interface Props {
  steps?: Step[]
  modelValue?: number
  orientation?: 'horizontal' | 'vertical'
  size?: 'sm' | 'md' | 'lg'
  allowSkip?: boolean
  showContent?: boolean
  showNavigation?: boolean
  navigationButtonVariant?: ButtonVariant
  finishButtonVariant?: ButtonVariant
  navigationButtonSize?: ButtonSize
  nextLabel?: string
  backLabel?: string
  finishLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  steps: () => [],
  modelValue: 0,
  orientation: 'horizontal',
  size: 'md',
  allowSkip: false,
  showContent: true,
  showNavigation: true,
  navigationButtonVariant: 'primary',
  finishButtonVariant: 'primary',
  navigationButtonSize: 'md',
  nextLabel: 'Next',
  backLabel: 'Back',
  finishLabel: 'Finish'
})

const emit = defineEmits<{
  'update:modelValue': [value: number]
  'step-change': [index: number]
  'complete': []
}>()

const activeStep = computed<number>({
  get: () => props.modelValue,
  set: (value: number) => emit('update:modelValue', value)
})

const handleStepClick = (index: number): void => {
  if (index > activeStep.value && !props.allowSkip) {
    return
  }

  activeStep.value = index
  emit('step-change', index)
}

const next = (): void => {
  if (activeStep.value < props.steps.length - 1) {
    activeStep.value++
    emit('step-change', activeStep.value)
  } else {
    emit('complete')
  }
}

const prev = (): void => {
  if (activeStep.value > 0) {
    activeStep.value--
    emit('step-change', activeStep.value)
  }
}

// Watch for external changes to steps
watch(() => props.steps.length, (newLength: number) => {
  if (activeStep.value >= newLength) {
    activeStep.value = Math.max(0, newLength - 1)
  }
})
</script>

<style>
.hb-stepper {
  width: 100%;
}

/* Container */
.hb-stepper__container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

/* Steps layout */
.hb-stepper__steps {
  display: flex;
  width: 100%;
  position: relative;
}

.hb-stepper__steps--vertical {
  flex-direction: column;
}

.hb-stepper__layout {
  display: flex;
  width: 100%;
  gap: var(--spacing-6);
}

/* Individual step */
.hb-stepper__step {
  display: flex;
  align-items: center;
  position: relative;
  flex: 1;
  min-width: 0;
}

.hb-stepper__step--vertical {
  flex-direction: row;
  flex: 0;
  margin-bottom: var(--spacing-6);
}

.hb-stepper__step:last-child {
  flex: 0;
}

.hb-stepper__step--disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.hb-stepper__step:not(.hb-stepper__step--disabled) {
  cursor: pointer;
}

/* Step indicator */
.hb-stepper__step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1;
}

/* Step icon */
.hb-stepper__step-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background-color: var(--gray-200);
  color: var(--gray-700);
  font-weight: var(--font-medium);
  transition: all 0.2s ease;
}

.hb-stepper--sm .hb-stepper__step-icon {
  width: 1.5rem;
  height: 1.5rem;
  font-size: var(--text-xs);
}

.hb-stepper--lg .hb-stepper__step-icon {
  width: 2.5rem;
  height: 2.5rem;
  font-size: var(--text-lg);
}

.hb-stepper__step--active .hb-stepper__step-icon {
  background-color: var(--primary-500);
  color: white;
}

.hb-stepper__step--completed .hb-stepper__step-icon {
  background-color: var(--success-500);
  color: white;
}

.hb-stepper__step-icon svg {
  width: 1rem;
  height: 1rem;
}

.hb-stepper--sm .hb-stepper__step-icon svg {
  width: 0.75rem;
  height: 0.75rem;
}

.hb-stepper--lg .hb-stepper__step-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}

/* Step content */
.hb-stepper__step-content {
  margin-left: var(--spacing-3);
}

.hb-stepper__step-title {
  font-weight: var(--font-medium);
  color: var(--gray-700);
  font-size: var(--text-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hb-stepper--sm .hb-stepper__step-title {
  font-size: var(--text-xs);
}

.hb-stepper--lg .hb-stepper__step-title {
  font-size: var(--text-base);
}

.hb-stepper__step--active .hb-stepper__step-title {
  color: var(--primary-700);
}

.hb-stepper__step-description {
  font-size: var(--text-xs);
  color: var(--gray-500);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hb-stepper--sm .hb-stepper__step-description {
  display: none;
}

.hb-stepper--lg .hb-stepper__step-description {
  font-size: var(--text-sm);
}

/* Connector */
.hb-stepper__connector {
  position: absolute;
  top: 1rem;
  left: calc(50% + 1rem);
  right: calc(50% - 1rem);
  height: 2px;
  background-color: var(--gray-200);
  z-index: 0;
}

.hb-stepper--sm .hb-stepper__connector {
  top: 0.75rem;
}

.hb-stepper--lg .hb-stepper__connector {
  top: 1.25rem;
}

.hb-stepper__connector--vertical {
  position: absolute;
  top: 2rem;
  left: 1rem;
  width: 2px;
  height: calc(100% - 1rem);
  background-color: var(--gray-200);
}

.hb-stepper--sm .hb-stepper__connector--vertical {
  top: 1.5rem;
  left: 0.75rem;
}

.hb-stepper--lg .hb-stepper__connector--vertical {
  top: 2.5rem;
  left: 1.25rem;
}

.hb-stepper__step--completed + .hb-stepper__step .hb-stepper__connector,
.hb-stepper__step--completed .hb-stepper__connector--vertical {
  background-color: var(--success-500);
}

/* Content area */
.hb-stepper__content {
  margin-top: var(--spacing-8);
  padding: var(--spacing-4);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-md);
  background-color: white;
}

.hb-stepper__content--vertical {
  margin-top: 0;
  flex: 1;
}

/* Navigation */
.hb-stepper__navigation {
  display: flex;
  justify-content: space-between;
  margin-top: var(--spacing-4);
}

.hb-stepper__spacer {
  flex: 1;
}
</style>
