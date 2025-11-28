/**
 * Centralized component prop and emit interface definitions
 *
 * This file exports reusable TypeScript interfaces for all adaptive questions
 * components, enabling better type safety and IntelliSense support.
 */

import type { QuestionItem } from '~/composables/analysis/useAnalysisState'
import type { AnswerEvaluation, QuestionAnswer, RefinementData } from './question-state'
import type { ExperienceLevel, AdaptiveQuestionState, DeepDivePrompt } from './adaptive-questions'

// ============================================================================
// AnswerEvaluationModal Component
// ============================================================================

export interface AnswerEvaluationModalProps {
  modelValue: boolean
  question: QuestionItem | null
  userAnswer: string
  evaluation: AnswerEvaluation | null
}

export interface AnswerEvaluationModalEmits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'use-improved-answer', questionId: string, improvedText: string): void
}

// ============================================================================
// AnswerInput Component
// ============================================================================

export interface AnswerInputProps {
  modelValue?: string
  placeholder?: string
  disabled?: boolean
  submitButtonText?: string
}

export interface AnswerInputEmits {
  (e: 'update:modelValue', value: string): void
  (e: 'submit', value: string, type: 'text' | 'voice', transcriptionTime?: number): void
}

// ============================================================================
// AnswerQualityDisplay Component
// ============================================================================

export interface AnswerQualityDisplayProps {
  evaluation: AnswerEvaluation
  showImprovements?: boolean
}

// ============================================================================
// AdaptiveQuestionFlow Component
// ============================================================================

export interface AdaptiveQuestionFlowProps {
  questionId: string
  questionText: string
  questionData: Record<string, any>
  gapInfo: {
    title: string
    description: string
  }
  userId: string
  parsedCv: Record<string, any>
  parsedJd: Record<string, any>
  language?: string
  initialExperienceLevel?: ExperienceLevel | null
}

export interface AdaptiveQuestionFlowEmits {
  (e: 'complete', state: AdaptiveQuestionState): void
  (e: 'cancel'): void
}

// ============================================================================
// DeepDiveForm Component
// ============================================================================

export interface DeepDiveFormProps {
  prompts: DeepDivePrompt[]
  loading?: boolean
}

export interface DeepDiveFormEmits {
  (e: 'submit-inputs', data: Record<string, any>): void
}

// ============================================================================
// QuestionsResult Component
// ============================================================================

export interface QuestionsResultProps {
  questionsData: any  // GenerateQuestionsResult type
  parsedCV: any
  parsedJD: any
  originalScore: number
  timeSeconds: number
  language?: string
}

export interface QuestionsResultEmits {
  (e: 'answers-submitted', result: any, answers: QuestionAnswer[], updatedCV: any): void
}

// ============================================================================
// RefinementSlider Component
// ============================================================================

export interface RefinementSliderProps {
  modelValue: boolean
  question: QuestionItem | null
  userAnswer: string
  evaluation: AnswerEvaluation | null
}

export interface RefinementSliderEmits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'submit-refinement', data: RefinementData, questionId: string): void
  (e: 'use-improved', questionId: string, improvedText: string): void
}

// ============================================================================
// RefinementSlide Component
// ============================================================================

export interface RefinementSlideProps {
  evaluation: AnswerEvaluation
  hasRefinementData: boolean
  isRefining: boolean
}

export interface RefinementSlideEmits {
  (e: 'submit-refinement', data: RefinementData): void
  (e: 'next'): void
  (e: 'prev'): void
}

// ============================================================================
// QuestionSlider Component
// ============================================================================

export interface QuestionSliderProps {
  question: QuestionItem
  questionIndex: number
  isActive: boolean
  parsedCv: Record<string, any>
  parsedJd: Record<string, any>
  language?: string
}

export interface QuestionSliderEmits {
  (e: 'need-help', question: QuestionItem): void
  (e: 'navigate', direction: 'previous' | 'next'): void
  (e: 'submit-all'): void
  (e: 'slide-changed', questionId: string, slideIndex: number): void
  (e: 'refinement-submitted', questionId: string, refinementData: Record<string, any>): void
  (e: 'learning-choice', questionId: string, choice: 'learn-now' | 'open-later'): void
}

// ============================================================================
// OriginalQuestionSlide Component
// ============================================================================

export interface OriginalQuestionSlideProps {
  question: QuestionItem
  questionIndex: number
  isActive: boolean
  parsedCv: Record<string, any>
  parsedJd: Record<string, any>
  language?: string
  totalQuestions?: number
  allAnswered?: boolean
}

export interface OriginalQuestionSlideEmits {
  (e: 'need-help', question: QuestionItem): void
  (e: 'navigate', direction: 'previous' | 'next'): void
  (e: 'submit-all'): void
  (e: 'adaptive-complete', questionId: string, state: any): void
  (e: 'adaptive-cancel', questionId: string): void
}

// ============================================================================
// RefinementSuggestionCard Component
// ============================================================================

export interface RefinementSuggestionCardProps {
  issue: string
  suggestion: string
  priority: 'high' | 'medium' | 'low'
  index: number
}

// ============================================================================
// QuestionContextCard Component
// ============================================================================

export interface QuestionContextCardProps {
  question: QuestionItem
  userAnswer?: string
  showAnswer?: boolean
}

// ============================================================================
// QuestionCard Component (if exists)
// ============================================================================

export interface QuestionCardProps {
  question: QuestionItem
  questionIndex: number
  isActive?: boolean
}
