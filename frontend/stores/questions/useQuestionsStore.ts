/**
 * Pinia store for managing question state across the application.
 *
 * This store replaces the Map-based state management in QuestionsResult.vue
 * and provides a centralized, type-safe way to manage:
 * - User answers
 * - Answer evaluations
 * - Active adaptive flows
 * - Refinement data
 * - UI state (tabs, loading, etc.)
 */

import { defineStore } from 'pinia'
import type { ExperienceLevel } from '~/types/adaptive-questions'

/**
 * Answer types
 */
export interface QuestionAnswer {
  question_id: string
  answer_text: string
  answer_type: 'text' | 'voice'
  transcription_time?: number
  timestamp: string
}

export interface AnswerEvaluation {
  question_id: string
  answer_text: string
  quality_score: number
  quality_issues: string[]
  quality_strengths: string[]
  improvement_suggestions: string[]
  is_acceptable: boolean
  time_seconds: number
  model: string
}

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
  uncovered_experiences?: string[]
  updated_cv: any
  time_seconds: number
  model: string
}

export const useQuestionsStore = defineStore('questions', {
  state: () => ({
    // Answer storage
    answers: new Map<string, QuestionAnswer>(),

    // Evaluation results
    answerEvaluations: new Map<string, AnswerEvaluation>(),

    // Adaptive flow tracking
    activeAdaptiveFlows: new Map<string, ExperienceLevel>(),

    // Refinement data for each question
    refinementData: new Map<string, Record<string, string>>(),

    // UI state: active tab for each question ('original' | 'followup')
    activeQuestionTab: new Map<string, 'original' | 'followup'>(),

    // Submission state
    isSubmitting: false,
    hasSubmitted: false,
    answersResult: null as SubmitAnswersResult | null,

    // Evaluation state
    evaluatingQuestionId: null as string | null,

    // Adaptive modal state
    showAdaptiveModal: false,
    currentAdaptiveQuestion: null as any | null, // QuestionItem type from component

    // Refinement iteration tracking
    refinementIterations: new Map<string, number>(),
  }),

  getters: {
    /**
     * Get answer by question ID
     */
    getAnswerById: (state) => (questionId: string) => {
      return state.answers.get(questionId)
    },

    /**
     * Get evaluation by question ID
     */
    getEvaluationById: (state) => (questionId: string) => {
      return state.answerEvaluations.get(questionId)
    },

    /**
     * Check if question has been answered
     */
    isQuestionAnswered: (state) => (questionId: string) => {
      return state.answers.has(questionId)
    },

    /**
     * Check if all questions have been answered
     */
    allQuestionsAnswered: (state) => (totalQuestions: number) => {
      return state.answers.size === totalQuestions
    },

    /**
     * Get all answers as array
     */
    answersArray: (state) => {
      return Array.from(state.answers.values())
    },

    /**
     * Get refinement data for question
     */
    getRefinementData: (state) => (questionId: string) => {
      return state.refinementData.get(questionId)
    },

    /**
     * Check if refinement data has content
     */
    hasRefinementData: (state) => (questionId: string) => {
      const refinement = state.refinementData.get(questionId)
      if (!refinement) return false
      return Object.values(refinement).some(v => v && v.trim())
    },

    /**
     * Get active tab for question
     */
    getActiveTab: (state) => (questionId: string) => {
      return state.activeQuestionTab.get(questionId) || 'original'
    },

    /**
     * Get refinement iteration count
     */
    getRefinementIteration: (state) => (questionId: string) => {
      return state.refinementIterations.get(questionId) || 0
    },

    /**
     * Check if question is in adaptive flow
     */
    isInAdaptiveFlow: (state) => (questionId: string) => {
      return state.activeAdaptiveFlows.has(questionId)
    },

    /**
     * Get experience level for adaptive flow
     */
    getAdaptiveExperienceLevel: (state) => (questionId: string) => {
      return state.activeAdaptiveFlows.get(questionId)
    },
  },

  actions: {
    /**
     * Set answer for a question
     *
     * @param questionId - Unique identifier for the question
     * @param answerText - The answer text provided by the user
     * @param answerType - Type of answer: 'text' or 'voice'
     * @param transcriptionTime - Optional transcription time for voice answers (in seconds)
     *
     * @example
     * ```ts
     * questionsStore.setAnswer('q1', 'I have 5 years experience', 'text')
     * questionsStore.setAnswer('q2', 'Transcribed voice answer', 'voice', 1.5)
     * ```
     */
    setAnswer(questionId: string, answerText: string, answerType: 'text' | 'voice', transcriptionTime?: number) {
      this.answers.set(questionId, {
        question_id: questionId,
        answer_text: answerText,
        answer_type: answerType,
        transcription_time: transcriptionTime,
        timestamp: new Date().toISOString()
      })
    },

    /**
     * Set evaluation result for an answer
     *
     * Stores the evaluation result and automatically initializes refinement data
     * if the answer quality is not acceptable (< 7/10).
     *
     * @param questionId - Unique identifier for the question
     * @param evaluation - The evaluation result from the API
     *
     * @example
     * ```ts
     * questionsStore.setEvaluation('q1', {
     *   question_id: 'q1',
     *   answer_text: 'Improved answer',
     *   quality_score: 8,
     *   quality_issues: [],
     *   quality_strengths: ['Specific examples', 'Metrics included'],
     *   improvement_suggestions: [],
     *   is_acceptable: true,
     *   time_seconds: 2.5,
     *   model: 'gemini-2.0-flash'
     * })
     * ```
     */
    setEvaluation(questionId: string, evaluation: AnswerEvaluation) {
      this.answerEvaluations.set(questionId, evaluation)
      this.evaluatingQuestionId = null

      // Initialize refinement data if not acceptable
      if (!evaluation.is_acceptable && !this.refinementData.has(questionId)) {
        this.refinementData.set(questionId, {
          duration_detail: '',
          specific_tools: '',
          metrics: ''
        })
      }
    },

    /**
     * Start evaluation for a question
     *
     * Sets the evaluating state to show loading UI for the specified question.
     *
     * @param questionId - Unique identifier for the question being evaluated
     */
    startEvaluation(questionId: string) {
      this.evaluatingQuestionId = questionId
    },

    /**
     * Clear evaluation state
     *
     * Removes the evaluating state to hide loading UI.
     * Used when evaluation completes or encounters an error.
     */
    clearEvaluation() {
      this.evaluatingQuestionId = null
    },

    /**
     * Set refinement data for a question
     */
    setRefinementData(questionId: string, data: Record<string, string>) {
      this.refinementData.set(questionId, data)
    },

    /**
     * Update refinement field
     */
    updateRefinementField(questionId: string, field: string, value: string) {
      const current = this.refinementData.get(questionId) || {}
      this.refinementData.set(questionId, {
        ...current,
        [field]: value
      })
    },

    /**
     * Increment refinement iteration
     */
    incrementRefinementIteration(questionId: string) {
      const current = this.refinementIterations.get(questionId) || 0
      this.refinementIterations.set(questionId, current + 1)
    },

    /**
     * Accept answer (clear refinement state)
     */
    acceptAnswer(questionId: string) {
      this.refinementData.delete(questionId)
      this.refinementIterations.set(questionId, 0)
    },

    /**
     * Set active tab for question
     */
    setActiveTab(questionId: string, tab: 'original' | 'followup') {
      this.activeQuestionTab.set(questionId, tab)
    },

    /**
     * Start adaptive flow for a question
     *
     * Initiates the LangGraph adaptive workflow for users with zero/some experience.
     * Tracks the experience level to determine the workflow path (deep dive vs learning).
     *
     * @param questionId - Unique identifier for the question
     * @param experienceLevel - User's experience level: 'none', 'some', or 'intermediate'
     *
     * @example
     * ```ts
     * questionsStore.startAdaptiveFlow('q1', 'none') // Starts learning path
     * questionsStore.startAdaptiveFlow('q2', 'some') // Starts deep dive path
     * ```
     */
    startAdaptiveFlow(questionId: string, experienceLevel: ExperienceLevel) {
      this.activeAdaptiveFlows.set(questionId, experienceLevel)
    },

    /**
     * Complete adaptive flow
     *
     * Removes the adaptive flow tracking when the user completes the workflow
     * or cancels the adaptive question flow.
     *
     * @param questionId - Unique identifier for the question
     */
    completeAdaptiveFlow(questionId: string) {
      this.activeAdaptiveFlows.delete(questionId)
    },

    /**
     * Show adaptive modal
     *
     * Opens the experience check modal that asks users about their experience level.
     * This is triggered when users click "I have zero experience" button.
     *
     * @param question - The question object to pass to the modal
     */
    openAdaptiveModal(question: any) {
      this.showAdaptiveModal = true
      this.currentAdaptiveQuestion = question
    },

    /**
     * Close adaptive modal
     *
     * Closes the experience check modal without starting the adaptive workflow.
     */
    closeAdaptiveModal() {
      this.showAdaptiveModal = false
      this.currentAdaptiveQuestion = null
    },

    /**
     * Set submission state
     */
    setSubmitting(value: boolean) {
      this.isSubmitting = value
    },

    /**
     * Set answers result after batch submission
     */
    setAnswersResult(result: SubmitAnswersResult) {
      this.answersResult = result
      this.hasSubmitted = true
      this.isSubmitting = false
    },

    /**
     * Clear all answers
     */
    clearAnswers() {
      this.answers.clear()
      this.answerEvaluations.clear()
      this.refinementData.clear()
      this.activeQuestionTab.clear()
      this.refinementIterations.clear()
      this.activeAdaptiveFlows.clear()
      this.evaluatingQuestionId = null
    },

    /**
     * Clear all state (including submission)
     */
    resetStore() {
      this.clearAnswers()
      this.isSubmitting = false
      this.hasSubmitted = false
      this.answersResult = null
      this.showAdaptiveModal = false
      this.currentAdaptiveQuestion = null
    },

    /**
     * Clear specific question state
     */
    clearQuestionState(questionId: string) {
      this.answers.delete(questionId)
      this.answerEvaluations.delete(questionId)
      this.refinementData.delete(questionId)
      this.activeQuestionTab.delete(questionId)
      this.refinementIterations.delete(questionId)
      this.activeAdaptiveFlows.delete(questionId)
    },
  }
})
