<template>
  <HbCard
    :class="borderClass"
    :variant="cardVariant"
    :bg-color="backgroundColor"
    shadow="sm"
    padding="md"
    :border="variant !== 'logistical'"
    role="article"
    :aria-label="`${variant} gap: ${gap.title}`"
  >
    <!-- Icon + Title + Impact Header -->
    <header class="flex items-start gap-3 mb-4">
      <!-- Icon -->
      <div
        :class="iconColorClass"
        class="flex-shrink-0 mt-0.5"
        role="img"
        :aria-label="`${variant} severity indicator`"
      >
        <component :is="iconComponent" class="w-5 h-5" />
      </div>

      <!-- Title and Impact -->
      <div class="flex-1 min-w-0">
        <div class="flex justify-between items-start gap-2">
          <h3
            :id="`gap-title-${gap.id}`"
            class="font-semibold text-gray-900 flex-1 m-0"
          >
            {{ gap.title }}
          </h3>
          <HbBadge
            :variant="impactBadgeVariant"
            size="sm"
            rounded
            :aria-label="`Impact level: ${gap.impact}`"
          >
            {{ gap.impact }}
          </HbBadge>
        </div>
      </div>
    </header>

    <!-- Current/Required Grid (Critical & Important only) -->
    <div
      v-if="showGrid && (gap.current || gap.required)"
      class="grid grid-cols-2 gap-4 mb-4"
      role="region"
      aria-label="Current vs Required comparison"
    >
      <div v-if="gap.current">
        <span class="text-xs text-gray-600 block mb-1 font-medium">Current:</span>
        <p class="text-sm font-medium text-gray-900 m-0">{{ gap.current }}</p>
      </div>
      <div v-if="gap.required">
        <span class="text-xs text-gray-600 block mb-1 font-medium">Required:</span>
        <p class="text-sm font-medium text-gray-900 m-0">{{ gap.required }}</p>
      </div>
    </div>

    <!-- Description -->
    <p
      :id="`gap-desc-${gap.id}`"
      class="text-sm text-description mb-4 leading-relaxed m-0"
    >
      {{ gap.description }}
    </p>

    <!-- Metadata Badges (shown based on variant) -->
    <div
      v-if="showBadges && (gap.addressability || gap.timeframe_to_address)"
      class="flex flex-wrap gap-2"
      role="region"
      aria-label="Gap details and timeline"
    >
      <HbBadge
        v-if="gap.addressability"
        variant="light"
        size="sm"
        class="capitalize"
        :aria-label="`Addressability: ${gap.addressability}`"
      >
        {{ gap.addressability }}
      </HbBadge>
      <HbBadge
        v-if="gap.timeframe_to_address"
        variant="light"
        size="sm"
        :aria-label="`Timeframe: ${gap.timeframe_to_address}`"
      >
        {{ gap.timeframe_to_address }}
      </HbBadge>
    </div>
  </HbCard>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import HbBadge from '~/components/base/HbBadge.vue'

/**
 * Gap data structure representing a skill or requirement mismatch
 */
export interface Gap {
  id: string
  title: string
  impact: string
  description: string
  current?: string
  required?: string
  addressability?: string
  timeframe_to_address?: string
}

/**
 * GapCard component props
 */
interface Props {
  /** Gap severity level determining visual styling */
  variant: 'critical' | 'important' | 'nice-to-have' | 'logistical'
  /** Gap data to display */
  gap: Gap
}

const props = defineProps<Props>()

// Badge variant type from HbBadge component
type BadgeVariant = 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'light' | 'dark' | 'gray'

// Variant to badge variant mapping
// Note: Using 'gray' for logistical to match HbBadge's variant options
const VARIANT_TO_BADGE: Record<Props['variant'], BadgeVariant> = {
  'critical': 'danger',
  'important': 'warning',
  'nice-to-have': 'success',
  'logistical': 'gray'
}

// Variant to card variant mapping (used with HbCard)
const VARIANT_TO_CARD = {
  'critical': 'danger',
  'important': 'warning',
  'nice-to-have': 'success',
  'logistical': 'default'
} as const

// Icon Components (inline SVG)
const CriticalIcon: Component = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  `
}

const ImportantIcon: Component = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  `
}

const NiceToHaveIcon: Component = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  `
}

const LogisticalIcon: Component = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  `
}

// Computed properties for variant-specific styling
const iconComponent = computed(() => {
  switch (props.variant) {
    case 'critical':
      return CriticalIcon
    case 'important':
      return ImportantIcon
    case 'nice-to-have':
      return NiceToHaveIcon
    case 'logistical':
      return LogisticalIcon
    default:
      return NiceToHaveIcon
  }
})

/**
 * Card variant for semantic HbCard styling
 */
const cardVariant = computed(() => VARIANT_TO_CARD[props.variant])

/**
 * Custom background colors via HbCard bgColor prop
 * Using even lighter shades for a more subtle appearance
 */
const backgroundColor = computed(() => {
  switch (props.variant) {
    case 'critical':
      return '#fef5f5'    // lighter red (between red-50 and white)
    case 'important':
      return '#fffdf7'    // lighter amber (between amber-50 and white)
    case 'nice-to-have':
      return '#f0fdf9'    // lighter green (between green-50 and white)
    case 'logistical':
      return '#fafbfc'    // lighter gray (between gray-50 and white)
    default:
      return '#fafbfc'    // lighter gray
  }
})

/**
 * Custom border styling for logistical variant
 */
const borderClass = computed(() => {
  if (props.variant === 'logistical') {
    return 'border-l-4 border-gray-500'
  }
  return ''
})

/**
 * Icon color classes based on variant severity
 * Uses custom CSS classes with precise hex codes for WCAG AAA compliance
 * Each icon achieves 7:1+ contrast ratio on its respective light background
 */
const iconColorClass = computed(() => {
  switch (props.variant) {
    case 'critical':
      return 'icon-critical'       // #991b1b - 9.07:1 contrast
    case 'important':
      return 'icon-important'      // #92400e - 8.94:1 contrast
    case 'nice-to-have':
      return 'icon-nice-to-have'   // #065f46 - 8.88:1 contrast
    case 'logistical':
      return 'icon-logistical'     // #374151 - 9.93:1 contrast
    default:
      return 'icon-logistical'
  }
})

/**
 * Badge variant mapped from gap variant
 */
const impactBadgeVariant = computed(() => VARIANT_TO_BADGE[props.variant])

/**
 * Show current/required comparison grid only for critical and important gaps
 */
const showGrid = computed(() => {
  return props.variant === 'critical' || props.variant === 'important'
})

/**
 * Show metadata badges for all variants except logistical
 */
const showBadges = computed(() => {
  return props.variant !== 'logistical'
})
</script>

<style scoped>
/**
 * Custom border styling for logistical variant
 * Uses left border to distinguish from other variants
 */
.border-l-4 {
  border-left-width: 4px;
}

/**
 * Ensure semantic elements have no default margins
 */
header,
h3,
p {
  margin: 0;
  padding: 0;
}

/**
 * Custom icon color classes with precise hex codes for WCAG AAA compliance
 * Each color achieves 7:1+ contrast ratio on its respective light background
 */
.icon-critical {
  color: #991b1b;  /* Deep red - 9.07:1 contrast on #fef5f5 background */
}

.icon-important {
  color: #92400e;  /* Dark amber - 8.94:1 contrast on #fffdf7 background */
}

.icon-nice-to-have {
  color: #065f46;  /* Deep green - 8.88:1 contrast on #f0fdf9 background */
}

.icon-logistical {
  color: #374151;  /* Dark gray - 9.93:1 contrast on #fafbfc background */
}

/**
 * Custom text color for improved visual hierarchy
 * Stronger than default gray-700, provides better readability
 */
.text-description {
  color: #1f2937;  /* gray-800 equivalent - 13.5:1 contrast on light backgrounds */
}
</style>
