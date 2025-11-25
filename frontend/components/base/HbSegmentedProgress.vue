<template>
  <div class="hb-segmented-progress" :style="{ width: `${size}px`, height: `${size}px` }">
    <div class="progress-container">
      <svg 
        :width="size" 
        :height="size" 
        :viewBox="`0 0 ${size} ${size}`"
        class="progress-svg"
      >
        <!-- Render segments -->
        <g v-for="(segment, index) in segments" :key="index">
          <path
            :d="segment.path"
            :stroke="segment.isActive ? activeColor : inactiveColor"
            :stroke-width="strokeWidth"
            fill="none"
            stroke-linecap="round"
            class="segment"
            :class="{ 'segment-active': segment.isActive }"
            :style="{ 
              opacity: segment.isActive ? animatedOpacity : 1,
              transition: `opacity ${animationDuration}ms ease-out`
            }"
          />
        </g>
      </svg>
      
      <!-- Center Text -->
      <div class="progress-content">
        <div class="progress-value">{{ Math.round(animatedValue) }}</div>
        <div class="progress-label">{{ label }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-strict
import { ref, computed, onMounted, watch } from 'vue'

interface Segment {
  path: string
  isActive: boolean
}

interface CartesianCoord {
  x: number
  y: number
}

interface Props {
  value?: number
  label?: string
  size?: number
  segmentCount?: number
  strokeWidth?: number
  activeColor?: string
  inactiveColor?: string
  animationDuration?: number
}

const props = withDefaults(defineProps<Props>(), {
  value: 0,
  label: 'Qualified',
  size: 160,
  segmentCount: 40,
  strokeWidth: 8,
  activeColor: '#ff6b5a',
  inactiveColor: '#e6e6e6',
  animationDuration: 1500
})

// Animated values
const animatedValue = ref<number>(0)
const animatedOpacity = ref<number>(0)

// Computed values
const center = computed<number>(() => props.size / 2)
const radius = computed<number>(() => (props.size - props.strokeWidth) / 2 - 10)

// Calculate segment gap (in degrees)
const segmentGap = computed<number>(() => (360 / props.segmentCount) * 0.25) // 25% gap
const segmentLength = computed<number>(() => (360 / props.segmentCount) - segmentGap.value)

// Generate segments
const segments = computed<Segment[]>(() => {
  const result: Segment[] = []
  const activeSegmentCount = Math.round((animatedValue.value / 100) * props.segmentCount)

  for (let i = 0; i < props.segmentCount; i++) {
    const startAngle = i * (360 / props.segmentCount) - 90 // Start from top
    const endAngle = startAngle + segmentLength.value
    const isActive = i < activeSegmentCount

    result.push({
      path: describeArc(
        center.value,
        center.value,
        radius.value,
        startAngle,
        endAngle
      ),
      isActive
    })
  }

  return result
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

// Animate progress
const animateProgress = (): void => {
  const startTime = Date.now()
  const startValue = animatedValue.value
  const targetValue = props.value

  const animate = (): void => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / props.animationDuration, 1)

    // Easing function (ease-out cubic)
    const eased = 1 - Math.pow(1 - progress, 3)

    animatedValue.value = startValue + (targetValue - startValue) * eased
    animatedOpacity.value = eased

    if (progress < 1) {
      requestAnimationFrame(animate)
    } else {
      animatedValue.value = targetValue
      animatedOpacity.value = 1
    }
  }

  requestAnimationFrame(animate)
}

// Trigger animation on mount
onMounted(() => {
  animateProgress()
})

// Watch for value changes
watch(() => props.value, () => {
  animateProgress()
})
</script>

<style lang="scss" scoped>
.hb-segmented-progress {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.progress-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-svg {
  display: block;
  overflow: visible;
  transform: rotate(0deg);
}

.segment {
  transition: stroke 0.3s ease;
}

.segment-active {
  filter: drop-shadow(0 0 2px rgba(255, 107, 90, 0.3));
}

.progress-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  pointer-events: none;
}

.progress-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--gray-900);
  line-height: 1;
  font-family: var(--font-heading);
}

.progress-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--gray-500);
  margin-top: 0.375rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Responsive font sizes */
@media (max-width: 640px) {
  .progress-value {
    font-size: 1.5rem;
  }
  
  .progress-label {
    font-size: 0.625rem;
  }
}
</style>
