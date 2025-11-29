/**
 * Centralized type definitions for question workflow state management
 *
 * This file contains all core types related to:
 * - Question step states ('initial' | 'feedback')
 * - Answer structures and evaluations
 * - Refinement data
 * - Submission results
 */

import type { ParsedCV } from './api-responses'
import type { ExperienceLevel, QualityFeedbackItem, ImprovementSuggestion } from './adaptive-questions'

// ============================================================================
// Core State Enums and Types
// ============================================================================

/**
 * Question step state - controls navigation locking and UI visibility
 * - 'initial': Normal state, navigation allowed
 * - 'feedback': Refinement mode, navigation locked until submission
 * - 'feedback_submitted': Showing formatted answer after refinement submission
 * - 'no_experience': User selected "I have no experience" option
 */
export type QuestionStepState = 'initial' | 'feedback' | 'feedback_submitted' | 'no_experience'

/**
 * Modal state for answer evaluation modal
 */
export type ModalState = 'loading' | 'slider' | 'closed'

/**
 * Type of answer input
 */
export type AnswerType = 'text' | 'voice'

/**
 * Active tab type in question view
 */
export type TabType = 'original' | 'followup'

// ============================================================================
// Answer Structures
// ============================================================================

/**
 * User's answer to a question
 * Consolidates duplicate definitions from useQuestionsStore and useAnalysisState
 */
export interface QuestionAnswer {
  question_id: string
  answer_text: string
  answer_type: AnswerType
  transcription_time?: number  // For voice answers, time taken to transcribe
  timestamp: string
}

/**
 * AI evaluation of answer quality
 * Includes quality score (0-10) and detailed feedback
 */
export interface AnswerEvaluation {
  question_id: string
  answer_text: string
  quality_score: number  // 0-10, >= 7 is acceptable
  quality_issues: QualityFeedbackItem[]
  quality_strengths: QualityFeedbackItem[]
  improvement_suggestions: ImprovementSuggestion[]
  is_acceptable: boolean  // true if quality_score >= 7
  time_seconds: number
  model: string  // AI model used for evaluation
}

// ============================================================================
// Refinement Data
// ============================================================================

/**
 * Refinement form data structure
 * Used when answer quality is not acceptable and user provides more details
 */
export interface RefinementData {
  duration_detail: string   // How long user worked on/with the skill
  specific_tools: string    // Specific tools, frameworks, or technologies used
  metrics: string          // Quantifiable metrics or results achieved
}

// ============================================================================
// Submission Results
// ============================================================================

/**
 * Result of submitting all answers for batch analysis
 * Includes updated CV and score improvements
 */
export interface SubmitAnswersResult {
  success: boolean
  score_improvement: {
    before: number
    after: number
    absolute_change: number
    percentage_change: number
  }
  category_improvements: Array<{
    category: string
    before: number
    after: number
    change: number
  }>
  uncovered_experiences?: string[]  // New experiences discovered from answers
  updated_cv: ParsedCV
  time_seconds: number
  model: string  // AI model used for analysis
}
