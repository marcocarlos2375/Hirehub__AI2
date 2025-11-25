<template>
  <span
    class="hb-icon"
    :class="[
      `hb-icon--${size}`,
      { 'hb-icon--clickable': clickable }
    ]"
    :style="iconStyle"
    v-html="sanitizedSvgContent"
  ></span>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, watch } from 'vue'
import { sanitizeSvg } from '~/utils/sanitize'

interface Props {
  /** Name of the icon (without .svg extension) - Should match the filename in the icons directory */
  name: string
  /** Width of the icon (in pixels or any CSS unit) */
  width?: string | number | null
  /** Height of the icon (in pixels or any CSS unit) */
  height?: string | number | null
  /** Size preset (overrides width/height if set) */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl'
  /** Color of the icon (applies to stroke/fill) */
  color?: string
  /** Whether the icon should have pointer cursor */
  clickable?: boolean
  /** Custom class to apply to the icon */
  customClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  width: null,
  height: null,
  size: 'md',
  color: 'currentColor',
  clickable: false,
  customClass: ''
})

const svgContent = ref<string>('')

// Sanitized SVG content to prevent XSS attacks
const sanitizedSvgContent = computed(() =>
  svgContent.value ? sanitizeSvg(svgContent.value) : ''
)

const iconStyle = computed(() => {
  const style: Record<string, string> = {}

  // Apply custom width/height if provided
  if (props.width) {
    style.width = typeof props.width === 'number' ? `${props.width}px` : props.width
  }

  if (props.height) {
    style.height = typeof props.height === 'number' ? `${props.height}px` : props.height
  }

  // Apply color
  if (props.color) {
    style.color = props.color
  }

  return style
})

async function loadIcon(iconName: string): Promise<void> {
  try {
    // Try to import the SVG file dynamically
    const iconModule = await import(`~/assets/icons/${iconName}.svg?raw`)
    svgContent.value = iconModule.default || iconModule
  } catch (error) {
    svgContent.value = getFallbackIcon()
  }
}

function getFallbackIcon(): string {
  // Fallback icon (a simple question mark)
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"></circle>
    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
    <line x1="12" y1="17" x2="12.01" y2="17"></line>
  </svg>`
}

// Watch for name changes
watch(() => props.name, (newName) => {
  loadIcon(newName)
}, { immediate: true })
</script>

<style lang="scss" scoped>
.hb-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
  
  // Make sure SVG inherits the size
  :deep(svg) {
    width: 100%;
    height: 100%;
    display: block;
  }
  
  // Size presets
  &--xs {
    width: 1rem;
    height: 1rem;
  }
  
  &--sm {
    width: 1.25rem;
    height: 1.25rem;
  }
  
  &--md {
    width: 1.5rem;
    height: 1.5rem;
  }
  
  &--lg {
    width: 2rem;
    height: 2rem;
  }
  
  &--xl {
    width: 2.5rem;
    height: 2.5rem;
  }
  
  &--2xl {
    width: 3rem;
    height: 3rem;
  }
  
  &--3xl {
    width: 4rem;
    height: 4rem;
  }
  
  &--clickable {
    cursor: pointer;
    transition: opacity 0.2s ease;
    
    &:hover {
      opacity: 0.7;
    }
  }
}
</style>
