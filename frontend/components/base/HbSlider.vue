<template>
  <div class="hb-slider" :class="{ 'is-disabled': disabled }">
    <div v-if="label" class="hb-slider__label">
      {{ label }}
    </div>
    
    <div class="hb-slider__container">
      <div class="hb-slider__track">
        <div 
          class="hb-slider__progress" 
          :style="{ width: `${percentage}%` }"
        ></div>
        
        <!-- Vertical tick marks -->
        <div class="hb-slider__ticks">
          <div 
            v-for="tick in ticks" 
            :key="tick" 
            class="hb-slider__tick"
            :style="{ left: `${calculateTickPosition(tick)}%` }"
          ></div>
        </div>
      </div>
      
      <div 
        class="hb-slider__thumb" 
        :style="{ left: `${percentage}%` }"
        @mousedown="startDrag"
        @touchstart="startDrag"
      ></div>
      
      <input 
        type="range" 
        class="hb-slider__input" 
        :min="min" 
        :max="max" 
        :step="step" 
        v-model="localValue"
        :disabled="disabled"
      >
    </div>
    
    <div class="hb-slider__value-container">
      <div v-if="showMinMax" class="hb-slider__min">{{ minLabel || min }}</div>
      <div class="hb-slider__current-value">{{ displayValue }}</div>
      <div v-if="showMinMax" class="hb-slider__max">{{ maxLabel || max }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, watch } from 'vue';

interface Props {
  modelValue?: number | string
  min?: number
  max?: number
  step?: number
  label?: string
  disabled?: boolean
  showMinMax?: boolean
  minLabel?: string
  maxLabel?: string
  unit?: string
  tickCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: 0,
  min: 0,
  max: 100,
  step: 1,
  label: '',
  disabled: false,
  showMinMax: true,
  minLabel: '',
  maxLabel: '',
  unit: '',
  tickCount: 5
});

interface Emits {
  (e: 'update:modelValue', value: number): void
}

const emit = defineEmits<Emits>();

// Local value to handle the slider state
const localValue = ref<number>(Number(props.modelValue));

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue: number | string) => {
  localValue.value = Number(newValue);
});

// Watch for local changes and emit updates
watch(localValue, (newValue: number) => {
  emit('update:modelValue', newValue);
});

// Calculate percentage for visual positioning
const percentage = computed<number>(() => {
  const range = props.max - props.min;
  return ((localValue.value - props.min) / range) * 100;
});

// Format the display value with unit if provided
const displayValue = computed<string | number>(() => {
  return props.unit ? `${localValue.value}${props.unit}` : localValue.value;
});

// Generate tick marks based on step value
const ticks = computed<number[]>(() => {
  const tickArray: number[] = [];
  const step = props.step;

  // Generate ticks for each possible value based on step
  for (let value = props.min; value <= props.max; value += step) {
    // Ensure we don't have floating point issues
    const roundedValue = Math.round(value * 1000) / 1000;
    tickArray.push(roundedValue);
  }

  return tickArray;
});

// Calculate position for each tick
const calculateTickPosition = (tickValue: number): number => {
  const range = props.max - props.min;
  return ((tickValue - props.min) / range) * 100;
};

// Handle drag interactions
const startDrag = (event: MouseEvent | TouchEvent): void => {
  if (props.disabled) return;

  event.preventDefault();

  const handleMove = (e: MouseEvent | TouchEvent): void => {
    const target = e.target as HTMLElement;
    const container = target.closest('.hb-slider__container') as HTMLElement | null;
    if (!container) return;

    const rect = container.getBoundingClientRect();
    const clientX = (e as TouchEvent).touches ? (e as TouchEvent).touches[0].clientX : (e as MouseEvent).clientX;

    // Calculate position as percentage of container width
    let percentage = ((clientX - rect.left) / rect.width) * 100;
    percentage = Math.max(0, Math.min(percentage, 100));

    // Convert percentage to value within range
    const range = props.max - props.min;
    let value = (percentage / 100) * range + props.min;

    // Apply step
    if (props.step > 0) {
      value = Math.round(value / props.step) * props.step;
    }

    localValue.value = Number(value.toFixed(2));
  };

  const stopDrag = (): void => {
    document.removeEventListener('mousemove', handleMove as EventListener);
    document.removeEventListener('mouseup', stopDrag);
    document.removeEventListener('touchmove', handleMove as EventListener);
    document.removeEventListener('touchend', stopDrag);
  };

  document.addEventListener('mousemove', handleMove as EventListener);
  document.addEventListener('mouseup', stopDrag);
  document.addEventListener('touchmove', handleMove as EventListener);
  document.addEventListener('touchend', stopDrag);

  // Initial move to handle the first click position
  handleMove(event);
};
</script>

<style lang="scss" scoped>
.hb-slider {
  width: 100%;
  margin-bottom: var(--spacing-4);
  
  &__label {
    font-family: var(--font-heading);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    margin-bottom: var(--spacing-2);
    color: var(--gray-700);
    text-transform: uppercase;
  }
  
  &__container {
    position: relative;
    height: 24px;
    display: flex;
    align-items: center;
    padding: 10px 0;
  }
  
  &__track {
    position: absolute;
    width: 100%;
    height: 2px;
    background-color: var(--gray-200);
    border-radius: 2px;
    overflow: visible; /* Changed to visible to show ticks */
  }
  
  &__progress {
    position: absolute;
    height: 100%;
    background-color: var(--primary-500);
    border-radius: 2px;
    transition: width 0.1s ease;
  }
  
  &__ticks {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
  }
  
  &__tick {
    position: absolute;
    width: 2px;
    height: 10px;
    background-color: var(--gray-300);
    transform: translateX(-50%);
    top: -4px; /* Position above the track */
    pointer-events: none; /* Ensure ticks don't interfere with clicks */
  }
  
  &__thumb {
    position: absolute;
    width: 16px;
    height: 16px;
    background-color: var(--primary-500); /* Full circle */
    border-radius: 50%;
    transform: translateX(-50%);
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: transform 0.1s ease;
    z-index: 1;
    
    &:hover {
      transform: translateX(-50%) scale(1.1);
      box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
    }
    
    &:active {
      transform: translateX(-50%) scale(1.2);
      box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2);
    }
  }
  
  &__input {
    position: absolute;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
    z-index: 0;
  }
  
  &__value-container {
    display: flex;
    justify-content: space-between;
    margin-top: var(--spacing-2);
    font-size: var(--text-xs);
    color: var(--gray-600);
  }
  
  &__current-value {
    font-weight: var(--font-medium);
    color: var(--gray-800);
  }
  
  &.is-disabled {
    opacity: 0.6;
    cursor: not-allowed;
    
    .hb-slider__thumb {
      cursor: not-allowed;
      background-color: var(--gray-300);
      border-color: var(--gray-400);
    }
    
    .hb-slider__progress {
      background-color: var(--gray-400);
    }
  }
}
</style>
