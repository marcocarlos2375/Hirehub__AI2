<template>
  <div class="hb-semicircle-progress">
    <div class="progress-container">
      <svg 
        :width="size" 
        :height="size / 2 + 20" 
        :viewBox="`0 0 ${size} ${size / 2 + 20}`"
        class="progress-svg"
      >
        <!-- Background Arc (Light Gray) -->
        <path
          :d="describeArc(center, center, radius, -90, 90)"
          :stroke="backgroundColor"
          :stroke-width="calculatedStrokeWidth"
          fill="none"
          stroke-linecap="round"
          class="progress-bg"
        />
        
        <!-- Progress Arc (Blue) -->
        <path
          :d="describeArc(center, center, radius, -90, progressAngle)"
          :stroke="progressColor"
          :stroke-width="calculatedStrokeWidth"
          fill="none"
          stroke-linecap="round"
          class="progress-bar"
          :style="{ strokeDasharray, strokeDashoffset: animatedOffset }"
        />
      </svg>
      
      <!-- Percentage Text (Inside the circle) -->
      <div class="progress-text">
        <span class="progress-value" :style="{ fontSize }">{{ Math.round(animatedProgress) }}%</span>
        <span v-if="label" class="progress-label" :style="{ fontSize: labelSize }">{{ label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, onMounted, watch } from 'vue'

interface SizeConfig {
  size: number
  stroke: number
  fontSize: string
  labelSize: string
}

interface CartesianCoord {
  x: number
  y: number
}

interface Props {
  progress?: number
  sizeVariant?: 'xxxs' | 'xxs' | 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  customSize?: number | null
  strokeWidth?: number | null
  backgroundColor?: string
  progressColor?: string
  label?: string
  animationDuration?: number
}

const props = withDefaults(defineProps<Props>(), {
  progress: 0,
  sizeVariant: 'md',
  customSize: undefined,
  strokeWidth: undefined,
  backgroundColor: 'var(--primary-100)',
  progressColor: 'var(--primary-500)',
  label: '',
  animationDuration: 1500
})

// Animated progress value
const animatedProgress = ref<number>(0)
const animatedOffset = ref<number>(0)

// Size configurations
const sizeConfig: Record<string, SizeConfig> = {
  xxxs: { size: 40, stroke: 4, fontSize: '0.625rem', labelSize: '0.375rem' },
  xxs: { size: 60, stroke: 5, fontSize: '0.875rem', labelSize: '0.4375rem' },
  xs: { size: 80, stroke: 6, fontSize: '1rem', labelSize: '0.5rem' },
  sm: { size: 120, stroke: 8, fontSize: '1.25rem', labelSize: '0.625rem' },
  md: { size: 160, stroke: 10, fontSize: '1.5rem', labelSize: '0.625rem' },
  lg: { size: 200, stroke: 12, fontSize: '1.875rem', labelSize: '0.75rem' },
  xl: { size: 240, stroke: 14, fontSize: '2.25rem', labelSize: '0.875rem' }
}

// Computed values
const size = computed<number>(() => props.customSize || sizeConfig[props.sizeVariant].size)
const calculatedStrokeWidth = computed<number>(() => props.strokeWidth || sizeConfig[props.sizeVariant].stroke)
const fontSize = computed<string>(() => sizeConfig[props.sizeVariant].fontSize)
const labelSize = computed<string>(() => sizeConfig[props.sizeVariant].labelSize)

const center = computed<number>(() => size.value / 2)
const radius = computed<number>(() => (size.value - calculatedStrokeWidth.value) / 2)

// Calculate progress angle (-90° to +90° = 180° total)
const progressAngle = computed<number>(() => {
  const angle = -90 + (animatedProgress.value / 100) * 180
  return Math.min(angle, 90) // Cap at 90°
})

// Calculate stroke dash for smooth animation
const strokeDasharray = computed<string>(() => {
  const circumference = Math.PI * radius.value // Half circle circumference
  return `${circumference} ${circumference}`
})

// Helper function to describe SVG arc path
const describeArc = (x: number, y: number, radius: number, startAngle: number, endAngle: number): string => {
  const start = polarToCartesian(x, y, radius, endAngle)
  const end = polarToCartesian(x, y, radius, startAngle)
  const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1'

  return [
    'M', start.x, start.y,
    'A', radius, radius, 0, largeArcFlag, 0, end.x, end.y
  ].join(' ')
}

// Convert polar coordinates to cartesian
const polarToCartesian = (centerX: number, centerY: number, radius: number, angleInDegrees: number): CartesianCoord => {
  const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0
  return {
    x: centerX + (radius * Math.cos(angleInRadians)),
    y: centerY + (radius * Math.sin(angleInRadians))
  }
}

// Animate progress on mount and when progress changes
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
.hb-semicircle-progress {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.progress-container {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.progress-svg {
  display: block;
  overflow: visible;
}

.progress-bg {
  opacity: 1;
}

.progress-bar {
  transition: stroke-dashoffset 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -20%);
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1;
}

.progress-value {
  font-weight: 700;
  color: var(--gray-900);
  line-height: 1;
  font-family: var(--font-heading);
  transition: font-size 0.3s ease;
}

.progress-label {
  font-weight: 600;
  color: var(--gray-500);
  margin-top: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: font-size 0.3s ease;
}
</style>
