<template>
  <div class="hb-color-picker" ref="colorPickerRoot">
    <div 
      class="hb-color-picker__container" 
      v-if="isOpen" 
      ref="pickerContainer"
      tabindex="-1"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
    >
     
      <div class="hb-color-picker__body">
        <!-- Color saturation area -->
        <div 
          class="hb-color-picker__saturation"
          ref="saturationEl"
          @mousedown="startSaturationDrag"
          @touchstart="startSaturationDrag"
        >
          <div 
            class="hb-color-picker__saturation-white"
            :style="{ backgroundColor: `hsl(${hue}, 100%, 50%)` }"
          ></div>
          <div class="hb-color-picker__saturation-black"></div>
          <div 
            class="hb-color-picker__saturation-pointer"
            :style="{ 
              left: `${saturation}%`, 
              top: `${100 - brightness}%`,
              backgroundColor: currentColor
            }"
          ></div>
        </div>
        
        <!-- Hue slider -->
       <div class="hb-color-picker__hue-container">

        <div 
          class="hb-color-picker__hue"
          ref="hueSlider"
          @mousedown="startHueDrag"
          @touchstart="startHueDrag"
        >
          <div 
            class="hb-color-picker__hue-pointer"
            :style="{ 
              left: `${hue / 360 * 100}%`,
              backgroundColor: currentColor,
              transform: 'translate(-50%, -25%)'
            }"
          ></div>
        </div>
       </div>
      </div>
      
      <div class="hb-color-picker__value-container">
        <div class="hb-color-picker__input-wrapper">
          <span class="hb-color-picker__hash">#</span>
          <input 
            class="hb-color-picker__input" 
            type="text" 
            :value="hexInput"
            @input="handleHexInput($event)"
            maxlength="6"
            placeholder="24A4EC"
          />
        </div>
      </div>
      

    </div>
    
    <div 
      class="hb-color-picker__trigger"
      ref="triggerEl"
      :style="{ backgroundColor: modelValue || '#ffffff' }"
      @click="open"
    >
      <div class="hb-color-picker__icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';

interface Props {
  modelValue?: string
  presetColors?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '#24A4EC',
  presetColors: () => [
    '#24A4EC', // Primary blue - HireHub primary
    '#7E57C2', // Purple - HireHub secondary
    '#4CAF50', // Green - Success
    '#F44336', // Red - Error
    '#000000'  // Black - Text
  ]
});

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const emit = defineEmits<Emits>();

const isOpen = ref<boolean>(false);
const currentColor = ref<string>(props.modelValue || '#24A4EC');
const hue = ref<number>(210); // Default hue (blue)
const saturation = ref<number>(70);
const brightness = ref<number>(60);
const saturationEl = ref<HTMLElement | null>(null);
const hueSlider = ref<HTMLElement | null>(null);
const colorPickerRoot = ref<HTMLElement | null>(null);
const triggerEl = ref<HTMLElement | null>(null);
const pickerContainer = ref<HTMLElement | null>(null);
const isMouseOver = ref<boolean>(false);
const hexInput = ref<string>(currentColor.value.replace('#', ''));

interface HSB {
  h: number
  s: number
  b: number
}

// Convert hex to HSB
function hexToHsb(hex: string): HSB {
  // Remove # if present
  hex = hex.replace(/^#/, '');

  // Parse r, g, b values
  let r: number, g: number, b: number;
  if (hex.length === 3) {
    r = parseInt(hex[0] + hex[0], 16) / 255;
    g = parseInt(hex[1] + hex[1], 16) / 255;
    b = parseInt(hex[2] + hex[2], 16) / 255;
  } else {
    r = parseInt(hex.substring(0, 2), 16) / 255;
    g = parseInt(hex.substring(2, 4), 16) / 255;
    b = parseInt(hex.substring(4, 6), 16) / 255;
  }

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h: number, s: number, v = max;

  const d = max - min;
  s = max === 0 ? 0 : d / max;

  if (max === min) {
    h = 0; // achromatic
  } else {
    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break;
      case g: h = (b - r) / d + 2; break;
      case b: h = (r - g) / d + 4; break;
      default: h = 0;
    }
    h /= 6;
  }

  return {
    h: h * 360,
    s: s * 100,
    b: v * 100
  };
}

// Convert HSB to hex
function hsbToHex(h: number, s: number, b: number): string {
  h = h / 360;
  s = s / 100;
  b = b / 100;

  let r: number, g: number, bl: number;

  if (s === 0) {
    r = g = bl = b;
  } else {
    const i = Math.floor(h * 6);
    const f = h * 6 - i;
    const p = b * (1 - s);
    const q = b * (1 - f * s);
    const t = b * (1 - (1 - f) * s);

    switch (i % 6) {
      case 0: r = b; g = t; bl = p; break;
      case 1: r = q; g = b; bl = p; break;
      case 2: r = p; g = b; bl = t; break;
      case 3: r = p; g = q; bl = b; break;
      case 4: r = t; g = p; bl = b; break;
      case 5: r = b; g = p; bl = q; break;
      default: r = g = bl = 0;
    }
  }

  const toHex = (x: number): string => {
    const hex = Math.round(x * 255).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };

  return `#${toHex(r)}${toHex(g)}${toHex(bl)}`;
}

// Update color from HSB values
function updateColorFromHsb(): void {
  currentColor.value = hsbToHex(hue.value, saturation.value, brightness.value);
  emit('update:modelValue', currentColor.value);
}

// Handle saturation area interaction
function startSaturationDrag(e: MouseEvent | TouchEvent): void {
  e.preventDefault();

  const handleSaturationMove = (e: MouseEvent | TouchEvent): void => {
    if (!saturationEl.value) return;
    const rect = saturationEl.value.getBoundingClientRect();
    const clientX = (e as TouchEvent).touches ? (e as TouchEvent).touches[0].clientX : (e as MouseEvent).clientX;
    const clientY = (e as TouchEvent).touches ? (e as TouchEvent).touches[0].clientY : (e as MouseEvent).clientY;

    let x = clientX - rect.left;
    let y = clientY - rect.top;

    x = Math.max(0, Math.min(x, rect.width));
    y = Math.max(0, Math.min(y, rect.height));

    saturation.value = Math.round((x / rect.width) * 100);
    brightness.value = Math.round(100 - (y / rect.height) * 100);

    updateColorFromHsb();
  };

  const stopSaturationDrag = (): void => {
    document.removeEventListener('mousemove', handleSaturationMove);
    document.removeEventListener('mouseup', stopSaturationDrag);
    document.removeEventListener('touchmove', handleSaturationMove);
    document.removeEventListener('touchend', stopSaturationDrag);
  };

  document.addEventListener('mousemove', handleSaturationMove);
  document.addEventListener('mouseup', stopSaturationDrag);
  document.addEventListener('touchmove', handleSaturationMove);
  document.addEventListener('touchend', stopSaturationDrag);

  handleSaturationMove(e);
}

// Handle hue slider interaction
function startHueDrag(e: MouseEvent | TouchEvent): void {
  e.preventDefault();

  const handleHueMove = (e: MouseEvent | TouchEvent): void => {
    if (!hueSlider.value) return;
    const rect = hueSlider.value.getBoundingClientRect();
    const clientX = (e as TouchEvent).touches ? (e as TouchEvent).touches[0].clientX : (e as MouseEvent).clientX;

    let x = clientX - rect.left;
    x = Math.max(0, Math.min(x, rect.width));

    hue.value = Math.round((x / rect.width) * 360);
    updateColorFromHsb();
  };

  const stopHueDrag = (): void => {
    document.removeEventListener('mousemove', handleHueMove);
    document.removeEventListener('mouseup', stopHueDrag);
    document.removeEventListener('touchmove', handleHueMove);
    document.removeEventListener('touchend', stopHueDrag);
  };

  document.addEventListener('mousemove', handleHueMove);
  document.addEventListener('mouseup', stopHueDrag);
  document.addEventListener('touchmove', handleHueMove);
  document.addEventListener('touchend', stopHueDrag);

  handleHueMove(e);
}

// Select a preset color
function selectColor(color: string): void {
  currentColor.value = color;
  const hsb = hexToHsb(color);
  hue.value = hsb.h;
  saturation.value = hsb.s;
  brightness.value = hsb.b;
  hexInput.value = color.replace('#', '');
  emit('update:modelValue', color);
}

// Open color picker
function open(event?: MouseEvent): void {
  // Prevent event from bubbling up
  if (event) {
    event.stopPropagation();
    event.preventDefault();
  }

  // If already open, don't do anything
  if (isOpen.value) return;

  isOpen.value = true;
  selectColor(props.modelValue || '#24A4EC');

  // Position the picker after it's rendered
  setTimeout(() => {
    positionPicker();

    // Focus the container to help with keyboard accessibility
    // and to maintain focus within the picker
    if (pickerContainer.value) {
      pickerContainer.value.focus();
    }
  }, 50);
}

interface Position {
  top: number
  left: number
  score: number
  fits: boolean
}

type PositionKey = 'bottom' | 'top' | 'right' | 'left';

// Position the color picker dynamically with smart tooltip-like positioning
function positionPicker(): void {
  if (!isOpen.value || !triggerEl.value || !pickerContainer.value) return;

  const triggerRect = triggerEl.value.getBoundingClientRect();
  const containerRect = pickerContainer.value.getBoundingClientRect();
  const gap = 8; // Gap between trigger and picker
  const edgeMargin = 8; // Margin from viewport edges

  // Calculate available space in all directions
  const spaceAbove = triggerRect.top;
  const spaceBelow = window.innerHeight - triggerRect.bottom;
  const spaceLeft = triggerRect.left;
  const spaceRight = window.innerWidth - triggerRect.right;

  // Calculate all possible positions
  const positions: Record<PositionKey, Position> = {
    // Below (default)
    bottom: {
      top: triggerRect.bottom + gap,
      left: triggerRect.left + (triggerRect.width / 2) - (containerRect.width / 2),
      score: spaceBelow,
      fits: spaceBelow >= containerRect.height + gap
    },
    // Above
    top: {
      top: triggerRect.top - containerRect.height - gap,
      left: triggerRect.left + (triggerRect.width / 2) - (containerRect.width / 2),
      score: spaceAbove,
      fits: spaceAbove >= containerRect.height + gap
    },
    // Right
    right: {
      top: triggerRect.top + (triggerRect.height / 2) - (containerRect.height / 2),
      left: triggerRect.right + gap,
      score: spaceRight,
      fits: spaceRight >= containerRect.width + gap
    },
    // Left
    left: {
      top: triggerRect.top + (triggerRect.height / 2) - (containerRect.height / 2),
      left: triggerRect.left - containerRect.width - gap,
      score: spaceLeft,
      fits: spaceLeft >= containerRect.width + gap
    }
  };

  // Find the best position that fits, prioritizing: bottom -> top -> right -> left
  const priority: PositionKey[] = ['bottom', 'top', 'right', 'left'];
  let bestPosition: Position | null = null;

  // First, try to find a position that fits
  for (const key of priority) {
    if (positions[key].fits) {
      bestPosition = positions[key];
      break;
    }
  }

  // If none fit perfectly, choose the one with most space
  if (!bestPosition) {
    const sortedBySpace = Object.values(positions).sort((a, b) => b.score - a.score);
    bestPosition = sortedBySpace[0];
  }

  let { top, left } = bestPosition;

  // Ensure the picker stays within viewport bounds
  // Horizontal constraints
  if (left + containerRect.width > window.innerWidth - edgeMargin) {
    left = window.innerWidth - containerRect.width - edgeMargin;
  }
  if (left < edgeMargin) {
    left = edgeMargin;
  }

  // Vertical constraints
  if (top + containerRect.height > window.innerHeight - edgeMargin) {
    top = window.innerHeight - containerRect.height - edgeMargin;
  }
  if (top < edgeMargin) {
    top = edgeMargin;
  }

  // Apply the position with smooth transition
  pickerContainer.value.style.top = `${top}px`;
  pickerContainer.value.style.left = `${left}px`;
}

// Close color picker
function close(): void {
  isOpen.value = false;
}

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
  if (newValue && !isOpen.value) {
    selectColor(newValue);
  }
});

// Watch for changes to currentColor to update hexInput
watch(() => currentColor.value, (newValue) => {
  hexInput.value = newValue.replace('#', '');
});

// Initialize color from props and set up event listeners
onMounted(() => {
  if (props.modelValue) {
    selectColor(props.modelValue);
  }

  // Add event listeners for window resize and scroll
  window.addEventListener('resize', handleWindowChange);
  window.addEventListener('scroll', handleWindowChange, true);
  document.addEventListener('mousedown', handleClickOutside, true);

  // Use capture phase for mousedown to ensure we get it before other handlers
  // This helps prevent the flickering issue
});

// Clean up event listeners
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleWindowChange);
  window.removeEventListener('scroll', handleWindowChange, true);
  document.removeEventListener('mousedown', handleClickOutside);
});

// Handle clicks outside the color picker
function handleClickOutside(event: MouseEvent): void {
  // Only close if we're clicking outside the picker root
  if (isOpen.value && colorPickerRoot.value &&
      !colorPickerRoot.value.contains(event.target as Node)) {
    // We need to check if the click was on the trigger element
    // If it was, we don't want to close the picker
    if (triggerEl.value && triggerEl.value.contains(event.target as Node)) {
      return;
    }

    // Don't close if mouse is over the picker (prevents flickering)
    if (isMouseOver.value) {
      return;
    }

    close();
  }
}

// Handle window resize or scroll
function handleWindowChange(): void {
  if (isOpen.value) {
    positionPicker();
  }
}

// Handle mouse enter
function handleMouseEnter(): void {
  isMouseOver.value = true;
}

// Handle mouse leave
function handleMouseLeave(): void {
  isMouseOver.value = false;
}

// Handle hex input changes
function handleHexInput(event: Event): void {
  // Get the input value from the event
  const inputValue = (event.target as HTMLInputElement).value;

  // Ensure only valid hex characters
  const cleanValue = inputValue.replace(/[^0-9A-Fa-f]/g, '');

  // Update the hexInput ref
  hexInput.value = cleanValue;

  // If we have a valid hex color (3 or 6 characters), update the color
  if (cleanValue.length === 6 || cleanValue.length === 3) {
    const newColor = `#${cleanValue}`;
    currentColor.value = newColor;
    const hsb = hexToHsb(newColor);
    hue.value = hsb.h;
    saturation.value = hsb.s;
    brightness.value = hsb.b;
    emit('update:modelValue', newColor);
  }
}
</script>

<style lang="scss" scoped>
.hb-color-picker {
  position: relative;
  display: inline-block;
  
  &__trigger {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:hover {
      transform: translateY(-2px);
    }
  }
  
  &__no-color {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
  }
  
  &__icon {
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    color: white;
    opacity: 1;
    z-index: 1;
  }
  
  svg {
    filter: drop-shadow(0px 0px 1px rgba(0, 0, 0, 0.8));
  }
  
  &__container {
    position: fixed;
    width: 240px;
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    z-index: 9999;
    overflow: hidden;
    transition: top 0.2s ease, left 0.2s ease, opacity 0.15s ease;
    opacity: 0;
    animation: fadeInPicker 0.2s ease forwards;
  }
  
  @keyframes fadeInPicker {
    from {
      opacity: 0;
      transform: scale(0.95);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
  
  &__header {
    display: flex;
    align-items: center;
    
    .hb-color-picker__preview {
      width: 24px;
      height: 24px;
      border-radius: 4px;
      border: 2px solid rgba(255, 255, 255, 0.5);
    }
    

    
    .hb-color-picker__close {
      background: transparent;
      border: none;
      color: white;
      cursor: pointer;
      font-size: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 4px;
      
      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }
    }
  }
  
  &__body {
    width: 100%;
    background-color: #111;
  }
  
  &__value-container {
    padding: 12px;
    border-top: 1px solid var(--gray-200);
    background-color: #111;
    height: 60px;
    color: white;
    font-size: 12px;

  }
  
  &__input-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-lg);
    padding: 4px 8px;
    margin: 0 auto;
    width: 80px !important;
  }
  
  &__hash {
    font-family: monospace;
    font-size: 14px;
    color: white;
    margin-right: 2px;
  }
  
  &__input {
    font-family: monospace;
    font-size: 14px;
    color: white;
    background: transparent;
    border: none;
    outline: none;
    width: 100%;
    text-align: left;
    
    &::placeholder {
      color: rgba(255, 255, 255, 0.5);
    }
  }
  
  &__saturation {
    position: relative;
    width: 100%;
    height: 120px;
    border-radius: var(--radius-md);
    cursor: crosshair;
    overflow: hidden;
    
    &-white {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
    }
    
    &-black {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(to bottom, transparent, black);
    }
    
    &-pointer {
      position: absolute;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      box-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
      transform: translate(-6px, -6px);
      pointer-events: none;
    }
  }
  
  &__hue-container {
    
    padding-bottom: 0px;
  }

  &__hue {
    position: relative;
    width: 100%;
    height: 30px;
    background: linear-gradient(to right, 
      #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff, #ff0000);
    cursor: pointer;
    
    &-pointer {
      position: absolute;
      width: 40px;
      height: 40px;
      top: 5px;
      border: 3px solid white;
      background-color: v-bind(currentColor);
      border-radius: 50%;   
      z-index: 1000;  
      transform: translateY(-20px);
      pointer-events: none;
    }
  }
  
}
</style>
