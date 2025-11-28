/**
 * Type-safe constants for question workflow
 *
 * Eliminates magic strings and provides compile-time safety for state values,
 * quality thresholds, and refinement limits.
 */

// ============================================================================
// State Constants
// ============================================================================

/**
 * Question step states - controls navigation locking
 */
export const QUESTION_STEP_STATES = {
  INITIAL: 'initial',
  FEEDBACK: 'feedback',
  FEEDBACK_SUBMITTED: 'feedback_submitted',
  NO_EXPERIENCE: 'no_experience'
} as const

/**
 * Modal states for answer evaluation modal
 */
export const MODAL_STATES = {
  LOADING: 'loading',
  SLIDER: 'slider',
  CLOSED: 'closed'
} as const

/**
 * Answer input types
 */
export const ANSWER_TYPES = {
  TEXT: 'text',
  VOICE: 'voice'
} as const

/**
 * Tab types for question view
 */
export const TAB_TYPES = {
  ORIGINAL: 'original',
  FOLLOWUP: 'followup'
} as const

// ============================================================================
// Quality Scoring Constants
// ============================================================================

/**
 * Quality score thresholds
 * - ACCEPTABLE: Minimum score for auto-acceptance (7/10)
 * - EXCELLENT: High-quality answer threshold (8/10)
 * - MIN_SCORE: Lowest possible score (0)
 * - MAX_SCORE: Highest possible score (10)
 */
export const QUALITY_THRESHOLDS = {
  ACCEPTABLE: 7,    // Score >= 7 is acceptable, no refinement needed
  EXCELLENT: 8,     // Score >= 8 is excellent quality
  MIN_SCORE: 0,
  MAX_SCORE: 10
} as const

// ============================================================================
// Refinement Workflow Constants
// ============================================================================

/**
 * Refinement iteration limits
 * - MAX_ITERATIONS: Maximum number of refinement attempts (2)
 * - SLIDE_TIMEOUT_WARNING: Time before showing timeout warning (10 seconds)
 */
export const REFINEMENT_LIMITS = {
  MAX_ITERATIONS: 2,              // Max 2 refinement cycles per question
  SLIDE_TIMEOUT_WARNING: 10000    // 10 seconds in milliseconds
} as const

/**
 * Refinement form field keys
 */
export const REFINEMENT_FIELDS = {
  DURATION_DETAIL: 'duration_detail',
  SPECIFIC_TOOLS: 'specific_tools',
  METRICS: 'metrics'
} as const

// ============================================================================
// Experience Level Constants
// ============================================================================

/**
 * Experience level options for adaptive questions
 */
export const EXPERIENCE_LEVELS = {
  YES: 'yes',
  NO: 'no',
  WILLING_TO_LEARN: 'willing_to_learn'
} as const

// ============================================================================
// Priority Levels
// ============================================================================

/**
 * Question priority levels
 */
export const PRIORITY_LEVELS = {
  CRITICAL: 'CRITICAL',
  HIGH: 'HIGH',
  MEDIUM: 'MEDIUM'
} as const
