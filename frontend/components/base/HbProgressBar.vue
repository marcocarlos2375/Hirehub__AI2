<template>
  <div class="hb-progress-bar" :style="{ width: width + 'px' }">
    <!-- Show label with percentage on top if label text provided -->
    <div v-if="showLabel && label" class="progress-label-top">
      <span class="label-text">{{ label }}</span>
      <span class="label-percentage">{{ Math.round(animatedProgress) }}%</span>
    </div>
    
    <!-- Show only percentage on top if no label text provided -->
    <div v-else-if="showLabel && !label && !showPercentageInside" class="progress-label-top">
      <span class="label-percentage">{{ Math.round(animatedProgress) }}%</span>
    </div>
    
    <div class="progress-track" :style="trackStyle">
      <div 
        class="progress-fill" 
        :style="fillStyle"
      >
        <span v-if="showPercentageInside" class="progress-text-inside">
          {{ Math.round(animatedProgress) }}%
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, onMounted, watch } from 'vue'
import type { CSSProperties } from 'vue'

interface SizeConfig {
  height: number
  width: number
  fontSize: string
}

interface RadiusConfig {
  [key: string]: string
}

interface Props {
  progress?: number
  sizeVariant?: 'xxs' | 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  customWidth?: number | null
  customHeight?: number | null
  backgroundColor?: string
  progressColor?: string
  label?: string
  showLabel?: boolean
  showPercentageInside?: boolean
  radius?: 'sm' | 'md' | 'lg' | 'full'
  animationDuration?: number
  striped?: boolean
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  progress: 0,
  sizeVariant: 'md',
  customWidth: undefined,
  customHeight: undefined,
  backgroundColor: 'var(--primary-100)',
  progressColor: 'var(--primary-500)',
  label: '',
  showLabel: true,
  showPercentageInside: false,
  radius: 'full',
  animationDuration: 1500,
  striped: false,
  animated: false
})

// Animated progress value
const animatedProgress = ref<number>(0)

// Size configurations (height and default width)
const sizeConfig: Record<string, SizeConfig> = {
  xxs: { height: 4, width: 160, fontSize: '0.5rem' },
  xs: { height: 6, width: 200, fontSize: '0.625rem' },
  sm: { height: 8, width: 240, fontSize: '0.75rem' },
  md: { height: 12, width: 280, fontSize: '0.875rem' },
  lg: { height: 16, width: 320, fontSize: '1rem' },
  xl: { height: 24, width: 360, fontSize: '1.125rem' }
}

// Border radius configurations
const radiusConfig: RadiusConfig = {
  sm: '0.25rem',
  md: '0.375rem',
  lg: '0.5rem',
  full: '9999px'
}

// Computed values
const height = computed<number>(() =>
  props.customHeight || sizeConfig[props.sizeVariant].height
)

const width = computed<number>(() =>
  props.customWidth || sizeConfig[props.sizeVariant].width
)

const fontSize = computed<string>(() =>
  sizeConfig[props.sizeVariant].fontSize
)

const borderRadius = computed<string>(() =>
  radiusConfig[props.radius] || radiusConfig.full
)

// Track style
const trackStyle = computed<CSSProperties>(() => ({
  width: `${width.value}px`,
  height: `${height.value}px`,
  backgroundColor: props.backgroundColor,
  borderRadius: borderRadius.value
} as CSSProperties))

// Fill style
const fillStyle = computed<CSSProperties>(() => {
  const baseStyle: CSSProperties = {
    width: `${animatedProgress.value}%`,
    backgroundColor: props.progressColor,
    borderRadius: borderRadius.value,
    fontSize: fontSize.value
  }

  // Add striped background if enabled
  if (props.striped) {
    baseStyle.backgroundImage = `linear-gradient(
      45deg,
      rgba(255, 255, 255, 0.15) 25%,
      transparent 25%,
      transparent 50%,
      rgba(255, 255, 255, 0.15) 50%,
      rgba(255, 255, 255, 0.15) 75%,
      transparent 75%,
      transparent
    )`
    baseStyle.backgroundSize = '1rem 1rem'
  }

  return baseStyle
})

// Animate progress with easing
const animateProgress = (): void => {
  const startTime = Date.now()
  const startProgress = animatedProgress.value
  const targetProgress = props.progress

  const animate = (): void => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / props.animationDuration, 1)

    // Easing function (ease-out cubic)
    const eased = 1 - Math.pow(1 - progress, 3)

    animatedProgress.value = startProgress + (targetProgress - startProgress) * eased

    if (progress < 1) {
      requestAnimationFrame(animate)
    } else {
      animatedProgress.value = targetProgress
    }
  }

  requestAnimationFrame(animate)
}

// Trigger animation on mount
onMounted(() => {
  animateProgress()
})

// Watch for progress changes
watch(() => props.progress, () => {
  animateProgress()
})
</script>

<style lang="scss" scoped>
.hb-progress-bar {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.progress-label-top {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1;
  margin-bottom: 0.25rem;
  width: 100%;
  
  /* When there's both label and percentage, space them apart */
  &:has(.label-text) {
    justify-content: space-between;
  }
}

.label-text {
  color: var(--gray-700);
  font-weight: 500;
}

.label-percentage {
  color: var(--gray-900);
  font-weight: 700;
  font-family: var(--font-heading);
  font-size: 0.75rem;
}

.progress-track {
  position: relative;
  overflow: hidden;
  background-color: var(--gray-200);
  transition: all 0.3s ease;
}

.progress-fill {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 0.5rem;
  transition: width 0.3s ease, background-color 0.3s ease;
  position: relative;
  overflow: hidden;
}

.progress-fill.striped-animated {
  animation: progress-stripes 1s linear infinite;
}

.progress-text-inside {
  color: white;
  font-weight: 700;
  font-size: inherit;
  line-height: 1;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  white-space: nowrap;
  padding-right: 0.25rem;
}

@keyframes progress-stripes {
  0% {
    background-position: 1rem 0;
  }
  100% {
    background-position: 0 0;
  }
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .hb-progress-bar {
    width: 100%;
  }
  
  .progress-track {
    width: 100% !important;
  }
}
</style>
