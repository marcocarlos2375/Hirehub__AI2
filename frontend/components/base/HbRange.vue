<template>
  <div class="hb-range" :class="{ 'has-error': error }">
    <div v-if="label" class="hb-range__label">
      {{ label }}<span v-if="required" class="required">*</span>
      <span v-if="showValue" class="hb-range__value">{{ displayValue }}</span>
    </div>
    <div v-if="helperText && !error" class="hb-range__helper hb-range__helper--top">{{ helperText }}</div>
    
    <div class="hb-range__container">
      <input
        type="range"
        :id="id"
        :min="min"
        :max="max"
        :step="step"
        :disabled="disabled"
        :value="modelValue"
        @input="updateValue"
        class="hb-range__input"
      />
      
      <div class="hb-range__track">
        <div 
          class="hb-range__progress" 
          :style="{ width: progressWidth }"
        ></div>
        <div 
          class="hb-range__thumb" 
          :style="{ left: progressWidth }"
        ></div>
      </div>
      
      <div class="hb-range__ticks" v-if="showTicks">
        <div 
          v-for="tick in ticks" 
          :key="tick.value" 
          class="hb-range__tick"
          :class="{ 'active': numericValue >= tick.value }"
          :style="{ left: `${calculateTickPosition(tick.value)}%` }"
        >
          <div class="hb-range__tick-mark"></div>
          <div v-if="tick.label" class="hb-range__tick-label">{{ tick.label }}</div>
        </div>
      </div>
    </div>
    
    <div class="hb-range__bottom-space" v-if="showTicks"></div>
    <div v-if="error" class="hb-range__error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { computed } from 'vue';

interface Tick {
  value: number
  label?: string
}

interface Props {
  modelValue?: number | string
  id?: string
  min?: number | string
  max?: number | string
  step?: number | string
  label?: string
  required?: boolean
  disabled?: boolean
  error?: string
  helperText?: string
  showValue?: boolean
  valueFormat?: (value: number) => string | number
  showTicks?: boolean
  ticks?: Tick[]
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: 0,
  id: () => `range-${Math.random().toString(36).substring(2, 9)}`,
  min: 0,
  max: 100,
  step: 1,
  label: '',
  required: false,
  disabled: false,
  error: '',
  helperText: '',
  showValue: true,
  valueFormat: (value: number) => value,
  showTicks: false,
  ticks: () => []
});

interface Emits {
  (e: 'update:modelValue', value: number): void
}

const emit = defineEmits<Emits>();

const numericValue = computed<number>(() => {
  return Number(props.modelValue);
});

const displayValue = computed<string | number>(() => {
  return props.valueFormat(numericValue.value);
});

const progressWidth = computed<string>(() => {
  const percentage = ((numericValue.value - Number(props.min)) / (Number(props.max) - Number(props.min))) * 100;
  return `${percentage}%`;
});

const updateValue = (event: Event): void => {
  const target = event.target as HTMLInputElement;
  emit('update:modelValue', Number(target.value));
};

const calculateTickPosition = (value: number): number => {
  return ((value - Number(props.min)) / (Number(props.max) - Number(props.min))) * 100;
};
</script>

<style lang="scss" scoped>
.hb-range {
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
  
  &__value {
    font-weight: var(--font-medium);
    color: var(--gray-700);
  }
  
  &__container {
    position: relative;
    height: 36px;
    display: flex;
    align-items: center;
  }
  
  &__input {
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
      
      & + .hb-range__track {
        opacity: 0.6;
      }
    }
    
    &:focus + .hb-range__track {
      /* Focus styles removed as requested */
    }
  }
  
  &__track {
    position: relative;
    width: 100%;
    height: 6px;
    background-color: var(--gray-200);
    border-radius: var(--radius-full);
    transition: box-shadow var(--transition-fast) var(--transition-ease);
  }
  
  &__progress {
    position: absolute;
    height: 100%;
    background-color: var(--primary-500);
    border-radius: var(--radius-full);
    transition: width var(--transition-fast) var(--transition-ease);
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
    transition: left var(--transition-fast) var(--transition-ease), transform var(--transition-fast) var(--transition-ease);
    z-index: 1;
    
    &:hover {
      transform: translate(-50%, -50%) scale(1.1);
    }
    
    .has-error & {
      border-color: var(--danger-500);
    }
  }
  
  &__ticks {
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    margin-top: var(--spacing-2);
    height: 30px; /* Fixed height for ticks area */
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
      
      .active & {
        background-color: var(--primary-500);
      }
    }
    
    &-label {
      margin-top: var(--spacing-1);
      font-size: var(--text-xs);
      color: var(--gray-500);
      white-space: nowrap;
      
      .active & {
        color: var(--primary-700);
        font-weight: var(--font-medium);
      }
    }
  }
  
  &__error {
    margin-top: var(--spacing-1);
    font-size: var(--text-xs);
    color: var(--danger-500);
  }
  
  &__helper {
    margin-top: var(--spacing-1);
    font-size: var(--text-xs);
    color: var(--gray-500);
    
    &--top {
      margin-top: var(--spacing-1);
      margin-bottom: var(--spacing-2);
    }
  }
  
  &__bottom-space {
    height: 30px; /* Space for ticks */
  }
  
  &.has-error {
    .hb-range__track {
      /* Error focus styles removed as requested */
    }
    
    .hb-range__progress {
      background-color: var(--danger-500);
    }
  }
}

// Custom thumb styles for different browsers
@mixin thumb-styles {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--white);
  border: 2px solid var(--primary-500);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all var(--transition-fast) var(--transition-ease);
  
  &:hover {
    transform: scale(1.1);
  }
  
  .has-error & {
    border-color: var(--danger-500);
  }
}

// Apply thumb styles to different browsers
.hb-range__input {
  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    @include thumb-styles;
    margin-top: -6px;
  }
  
  &::-moz-range-thumb {
    @include thumb-styles;
  }
  
  &::-ms-thumb {
    @include thumb-styles;
  }
}
</style>
