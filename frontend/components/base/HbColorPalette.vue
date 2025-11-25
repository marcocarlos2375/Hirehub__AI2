<template>
  <div class="hb-color-palette">
    <div class="color-container">
      <!-- Predefined colors -->
      <div v-for="(color, index) in colors" :key="index" class="color-item">
        <div 
          class="cursor-pointer color-swatch" 
          :class="[modelValue === color ? 'color-selected' : '']">
          <div 
            aria-hidden="true" 
            class="color-box" 
            :style="{ 
              backgroundColor: color,
              borderColor: color
            }" 
            @click="updateSelectedColor(color)">
            <div v-if="modelValue === color" class="color-checkmark">
              <svg viewBox="0 -65 512 512" width="12" fill="#fff" xmlns="http://www.w3.org/2000/svg">
                <path d="m444.175781 0-260.871093 242.011719-110.324219-117.734375-72.980469 68.386718 178.234375 190.207032 333.765625-309.351563zm0 0"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Custom color picker -->
      <div v-if="showCustomColor" class="color-item custom-color-container">
        <div class="custom-picker-wrapper">
          <!-- Custom styled overlay -->
          <div 
            class="color-box color-box-custom" 
            :style="{ backgroundColor: displayColor }"
            @click="openPicker">
            <div class="color-icon">
              <!-- Plus icon when no custom color selected -->
              <svg v-if="!isCustomColorSelected" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              <!-- Check icon when custom color is selected -->
              <svg v-else viewBox="0 -65 512 512" width="12" fill="#ffffff" xmlns="http://www.w3.org/2000/svg">
                <path d="m444.175781 0-260.871093 242.011719-110.324219-117.734375-72.980469 68.386718 178.234375 190.207032 333.765625-309.351563zm0 0"></path>
              </svg>
            </div>
          </div>
          <!-- Hidden color picker -->
          <HbColorPicker 
            ref="pickerRef"
            v-model="customColor" 
            @update:modelValue="updateSelectedColor"
            class="hidden-picker"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, watch, onMounted } from 'vue';
import HbColorPicker from './HbColorPicker.vue';

interface Props {
  modelValue?: string
  colors?: string[]
  showCustomColor?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '#24A4EC',
  colors: () => [
    '#24A4EC', // Primary blue - HireHub primary
    '#7E57C2', // Purple - HireHub secondary
    '#4CAF50', // Green - Success
    '#F44336', // Red - Error
  ],
  showCustomColor: true
});

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const emit = defineEmits<Emits>();

const customColor = ref<string>(props.modelValue || (props.colors.length > 0 ? props.colors[0] : '#24A4EC'));
const pickerRef = ref<any>(null);

// Get the current display color (always returns a valid color)
const displayColor = computed<string>(() => {
  return customColor.value || props.modelValue || props.colors[0] || '#24A4EC';
});

// Check if the selected color is a custom color (not in predefined list)
const isCustomColorSelected = computed<boolean>(() => {
  return !!props.modelValue && !props.colors.includes(props.modelValue);
});

// Calculate if color is light or dark (for icon contrast)
const isLightColor = (hexColor: string): boolean => {
  // Convert hex to RGB
  const hex = hexColor.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);

  // Calculate luminance (perceived brightness)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

  // Return true if light (luminance > 0.5)
  return luminance > 0.5;
};

// Get icon color based on background brightness
const iconColor = computed<string>(() => {
  const bgColor = displayColor.value;
  return isLightColor(bgColor) ? '#333333' : '#ffffff';
});

const updateSelectedColor = (color: string): void => {
  emit('update:modelValue', color);
  customColor.value = color;
};

const openPicker = (): void => {
  // Programmatically trigger the color picker by finding the trigger element
  if (pickerRef.value) {
    // Access the DOM element directly
    const pickerElement = pickerRef.value.$el || pickerRef.value;
    if (pickerElement) {
      const trigger = pickerElement.querySelector('.hb-color-picker__trigger');
      if (trigger) {
        (trigger as HTMLElement).click();
      }
    }
  }
};

watch(() => props.modelValue, (newValue: string) => {
  // Always sync customColor with modelValue changes
  customColor.value = newValue || props.colors[0] || '#24A4EC';
}, { immediate: true });

// Select the first color by default when component is mounted
onMounted(() => {
  // Always select default if no color is already selected
  if (!props.modelValue && props.colors.length > 0) {
    const defaultColor = props.colors[0];
    // Important: Emit the default color to the parent component
    emit('update:modelValue', defaultColor);
    customColor.value = defaultColor;
  }
});
</script>

<style scoped>
.hb-color-palette {
  margin-bottom: 3rem; /* Extra space for tooltip below */
  padding-top: 0.5rem; /* Extra space for tooltip above if needed */
}

.color-container {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 12px;
}

.color-item {
  transition: transform 0.2s ease;
  display: inline-flex;
  align-items: center;
}

.color-item:not(.custom-color-container):hover {
  transform: scale(1.1);
  z-index: 1;
}

.color-box {
  height: 32px;
  width: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid;
  transition: all 0.2s ease;
}

.color-box-custom {
  border: none;
  color: #666;
  position: relative;
  
  /* Transparent ring (spacing) using ::after */
  &::after {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 50%;
    border: 2px solid transparent;
    pointer-events: none;
    z-index: 1;
  }
  
  /* Rainbow gradient border using ::before */
  &::before {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    padding: 2px;
    background: conic-gradient(
      from 135deg,
      rgb(228, 58, 58) 0deg,
      rgb(224, 202, 83) 45deg,
      rgb(103, 199, 69) 95deg,
      rgb(66, 218, 163) 145deg,
      rgb(49, 187, 231) 190deg,
      rgb(56, 81, 214) 230deg,
      rgb(143, 0, 255) 280deg,
      rgb(231, 54, 160) 320deg,
      rgb(201, 73, 73) 360deg
    );
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
    pointer-events: none;
    z-index: 0;
  }
  
  &:hover {
    transform: scale(1.05);
  }
}

.color-checkmark {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.color-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  position: relative;
  z-index: 10;
  color: #ffffff;
  
  svg {
    filter: drop-shadow(0px 0px 2px rgba(0, 0, 0, 0.5));
  }
}

.custom-color-container {
  height: 32px;
  position: relative;
}

.custom-picker-wrapper {
  position: relative;
  width: 32px;
  height: 32px;
  
  .color-box-custom {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 10;
    cursor: pointer;
    transition: transform 0.2s ease;
    
    &:hover {
      transform: scale(1.1);
    }
  }
}

.hidden-picker {
  position: absolute;
  top: 0;
  left: 0;
  width: 32px;
  height: 32px;
  z-index: 1;
  
  :deep(.hb-color-picker__trigger) {
    opacity: 0;
    pointer-events: none;
  }
  
  /* Keep the popup visible when it opens */
  :deep(.hb-color-picker__container) {
    opacity: 1 !important;
    pointer-events: all !important;
  }
}
</style>