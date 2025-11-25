<template>
  <HbCard
    variant="default"
    shadow="none"
    padding="none"
    :bg-color="backgroundColor"
    role="article"
    :aria-label="`${variant} gap: ${gap.title}`"
    class="gap-card gap-card--no-border"
  >
    <div class="gap-card__content">
      <!-- Title + Impact Header -->
      <header class="gap-card__header">
        <div class="gap-card__header-row">
          <h3
            :id="`gap-title-${gap.id}`"
            class="gap-card__title"
          >
            {{ gap.title }}
          </h3>
          <HbBadge
            :variant="impactBadgeVariant"
            size="sm"
            rounded
            :aria-label="`Impact level: ${gap.impact}`"
            class="gap-card__badge"
          >
            {{ gap.impact }}
          </HbBadge>
        </div>
      </header>

      <!-- Current/Required Grid (Critical & Important only) -->
      <div
        v-if="showGrid && (gap.current || gap.required)"
        class="gap-card__comparison"
        role="region"
        aria-label="Current vs Required comparison"
      >
        <div v-if="gap.current" class="gap-card__comparison-item">
          <span class="gap-card__comparison-label">
            Current
          </span>
          <p class="gap-card__comparison-value">
            {{ gap.current }}
          </p>
        </div>
        <div v-if="gap.required" class="gap-card__comparison-item gap-card__comparison-item--divider">
          <span class="gap-card__comparison-label">
            Required
          </span>
          <p class="gap-card__comparison-value">
            {{ gap.required }}
          </p>
        </div>
      </div>

      <!-- Description -->
      <p
        :id="`gap-desc-${gap.id}`"
        class="gap-card__description"
      >
        {{ gap.description }}
      </p>

      <!-- Metadata Badges (shown based on variant) -->
      <div
        v-if="showBadges && (gap.addressability || gap.timeframe_to_address)"
        class="gap-card__metadata"
        :class="`gap-card__metadata--${variant}`"
        role="region"
        aria-label="Gap addressability and resolution timeline"
      >
        <span
          v-if="gap.addressability"
          class="gap-card__metadata-badge capitalize"
          :aria-label="`Addressability: ${gap.addressability}`"
        >
          {{ gap.addressability }}
        </span>
        <span
          v-if="gap.timeframe_to_address"
          class="gap-card__metadata-badge"
          :aria-label="`Timeframe: ${gap.timeframe_to_address}`"
        >
          {{ gap.timeframe_to_address }}
        </span>
      </div>
    </div>
  </HbCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
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
const VARIANT_TO_BADGE: Record<Props['variant'], BadgeVariant> = {
  'critical': 'danger',
  'important': 'warning',
  'nice-to-have': 'success',
  'logistical': 'gray'
}

// Variant to background color mapping - subtle tints
const VARIANT_TO_BG_COLOR: Record<Props['variant'], string> = {
  'critical': '#fef2f2',      // Very light red
  'important': '#fffbeb',     // Very light yellow/amber
  'nice-to-have': '#f0fdfa',  // Very light teal
  'logistical': '#f9fafb'     // Very light gray
}

/**
 * Background color based on gap variant
 */
const backgroundColor = computed(() => VARIANT_TO_BG_COLOR[props.variant])

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

<style scoped lang="scss">
// ============================================================================
// SPACING SYSTEM - Compact
// ============================================================================
$spacing-xs: 6px;
$spacing-sm: 8px;
$spacing-md: 12px;
$spacing-lg: 14px;
$spacing-xl: 16px;
$spacing-2xl: 20px;

// ============================================================================
// COLOR SYSTEM
// ============================================================================
$gray-200: #e5e7eb;
$gray-300: #d1d5db;
$gray-500: #6b7280;
$gray-600: #4b5563;
$gray-700: #374151;
$gray-900: #111827;

// Variant border colors
$border-critical: #fca5a5;     // red-300
$border-important: #fcd34d;    // amber-300
$border-nice-to-have: #5eead4; // teal-300
$border-logistical: #d1d5db;   // gray-300

// ============================================================================
// GAP CARD
// ============================================================================
.gap-card {
  // No animations
}

.gap-card--no-border {
  border: none !important;
}

.gap-card__content {
  padding: $spacing-xl;
}

// ============================================================================
// HEADER
// ============================================================================
.gap-card__header {
  margin-bottom: $spacing-lg;
}

.gap-card__header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: $spacing-md;
}

.gap-card__title {
  font-size: 1rem; // 16px
  font-weight: 600;
  line-height: 1.4;
  color: $gray-900;
  margin: 0;
  flex: 1;
}

.gap-card__badge {
  flex-shrink: 0;
}

// ============================================================================
// COMPARISON GRID - With vertical divider
// ============================================================================
.gap-card__comparison {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-lg;
  margin-bottom: $spacing-lg;
}

.gap-card__comparison-item {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
  position: relative;
  
  // Add vertical divider before "Required" column
  &--divider::before {
    content: '';
    position: absolute;
    left: -#{$spacing-lg / 2 + 1px}; // Center the line in the gap
    top: 0;
    bottom: 0;
    width: 0px;
    background-color: $gray-300;
  }
}

.gap-card__comparison-label {
  font-size: 0.6875rem; // 11px
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: $gray-500;
}

.gap-card__comparison-value {
  font-size: 0.8125rem; // 13px
  font-weight: 500;
  line-height: 1.5;
  color: $gray-900;
  margin: 0;
}

// ============================================================================
// DESCRIPTION
// ============================================================================
.gap-card__description {
  font-size: 0.8125rem; // 13px
  line-height: 1.5;
  color: $gray-700;
  margin: 0;
}

// ============================================================================
// METADATA - With variant-specific colored borders
// ============================================================================
.gap-card__metadata {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-md;
  margin-top: $spacing-lg;
  padding-top: $spacing-lg;
  border-top: 1px solid;
  
  &--critical {
    border-top-color: $border-critical;
  }
  
  &--important {
    border-top-color: $border-important;
  }
  
  &--nice-to-have {
    border-top-color: $border-nice-to-have;
  }
  
  &--logistical {
    border-top-color: $border-logistical;
  }
}

.gap-card__metadata-badge {
  font-size: 0.75rem; // 12px
  font-weight: 500;
  color: $gray-600;
  padding: 4px 10px;
  background-color: #fff;
  border: 1px solid transparent;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.8);
  }
}

// ============================================================================
// TYPOGRAPHY
// ============================================================================
.gap-card__title,
.gap-card__comparison-label,
.gap-card__comparison-value,
.gap-card__description,
.gap-card__metadata-badge {
  font-family: 'Gabarito', 'Arial', sans-serif;
  -moz-osx-font-smoothing: grayscale;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
</style>