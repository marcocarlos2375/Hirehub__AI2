/**
 * Composable for adaptive question flow using LangGraph.
 *
 * Handles:
 * - Starting adaptive question workflow (deep dive OR learning resources)
 * - Submitting structured inputs (deep dive answers)
 * - Refining answers based on quality feedback
 * - Getting learning resources for gaps
 * - Saving/retrieving learning plans
 */

import type {
  ExperienceLevel,
  DeepDivePrompt,
  LearningResource,
  TimelineStep,
  StartWorkflowResponse,
  SubmitInputsResponse,
  RefineAnswerResponse,
  LearningPlanItem
} from '~/types/adaptive-questions'

// Specific response types for this composable
interface LearningPath {
  timeline: TimelineStep[]
  total_days: number
  estimated_completion: string
  resources_in_path: number
}

interface LearningResourcesResponse {
  resources: LearningResource[]
  learning_path: LearningPath
  total_resources: number
  total_duration_days: number
  estimated_completion: string
  error?: string
}

interface LearningPlansResponse {
  plans: LearningPlanItem[]
  total: number
}

interface AnswerEvaluationResponse {
  success: boolean
  question_id: string
  answer_text: string
  quality_score: number
  quality_issues: string[]
  quality_strengths: string[]
  improvement_suggestions: string[]
  is_acceptable: boolean
  time_seconds: number
  model: string
  error?: string
}

export const useAdaptiveQuestions = () => {
  const config = useRuntimeConfig()

  /**
   * Start adaptive question workflow.
   *
   * @param questionId - Unique question identifier
   * @param questionText - The question text
   * @param questionData - Full question object
   * @param gapInfo - Gap information from scoring phase
   * @param userId - User identifier
   * @param parsedCV - Parsed CV data
   * @param parsedJD - Parsed job description data
   * @param experienceCheckResponse - "yes", "no", or "willing_to_learn"
   * @param language - Content language (default: "english")
   */
  const startAdaptiveQuestion = async (
    questionId: string,
    questionText: string,
    questionData: any,
    gapInfo: any,
    userId: string,
    parsedCV: any,
    parsedJD: any,
    experienceCheckResponse: ExperienceLevel,
    language: string = 'english'
  ): Promise<StartWorkflowResponse> => {
    try {
      const data = await $fetch<StartWorkflowResponse>('/api/adaptive-questions/start', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          question_id: questionId,
          question_text: questionText,
          question_data: questionData,
          gap_info: gapInfo,
          user_id: userId,
          parsed_cv: parsedCV,
          parsed_jd: parsedJD,
          experience_check_response: experienceCheckResponse,
          language
        }
      })

      return data
    } catch (error) {
      console.error('Error starting adaptive question:', error)
      throw error
    }
  }

  /**
   * Submit structured inputs (deep dive answers).
   *
   * @param questionId - Question identifier
   * @param structuredData - User's responses to deep dive prompts
   */
  const submitStructuredInputs = async (
    questionId: string,
    structuredData: Record<string, any>
  ): Promise<SubmitInputsResponse> => {
    try {
      const data = await $fetch<SubmitInputsResponse>('/api/adaptive-questions/submit-inputs', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          question_id: questionId,
          structured_data: structuredData
        }
      })

      return data
    } catch (error) {
      console.error('Error submitting structured inputs:', error)
      throw error
    }
  }

  /**
   * Refine answer based on quality feedback.
   *
   * @param questionId - Question identifier
   * @param questionText - The question text
   * @param questionData - Full question object
   * @param gapInfo - Gap information {title, description}
   * @param generatedAnswer - The current/previous answer
   * @param qualityIssues - Issues found in the current answer
   * @param refinementData - Additional data for answer improvement
   */
  const refineAnswer = async (
    questionId: string,
    questionText: string,
    questionData: any,
    gapInfo: { title: string; description: string },
    generatedAnswer: string,
    qualityIssues: string[],
    refinementData: Record<string, any>
  ): Promise<RefineAnswerResponse> => {
    try {
      const data = await $fetch<RefineAnswerResponse>('/api/adaptive-questions/refine-answer', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          question_id: questionId,
          question_text: questionText,
          question_data: questionData,
          gap_info: gapInfo,
          generated_answer: generatedAnswer,
          quality_issues: qualityIssues,
          additional_data: refinementData
        }
      })

      return data
    } catch (error) {
      console.error('Error refining answer:', error)
      throw error
    }
  }

  /**
   * Get learning resources for a gap.
   *
   * @param gap - Gap information
   * @param userLevel - User's current skill level (default: "intermediate")
   * @param maxDays - Maximum duration in days (default: 10)
   * @param costPreference - Cost filter (default: "any")
   * @param limit - Maximum number of resources (default: 5)
   */
  const getLearningResources = async (
    gap: any,
    userLevel: 'beginner' | 'intermediate' | 'advanced' = 'intermediate',
    maxDays: number = 10,
    costPreference: 'free' | 'paid' | 'any' = 'any',
    limit: number = 5
  ): Promise<LearningResourcesResponse> => {
    try {
      const data = await $fetch<LearningResourcesResponse>('/api/adaptive-questions/get-learning-resources', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          gap,
          user_level: userLevel,
          max_days: maxDays,
          cost_preference: costPreference,
          limit
        }
      })

      return data
    } catch (error) {
      console.error('Error getting learning resources:', error)
      throw error
    }
  }

  /**
   * Save a learning plan for the user.
   *
   * @param userId - User identifier
   * @param gap - Gap information
   * @param resourceIds - List of selected resource IDs
   * @param notes - Optional user notes
   */
  const saveLearningPlan = async (
    userId: string,
    gap: any,
    resourceIds: string[],
    notes?: string
  ): Promise<{ plan_id: string; success: boolean; error?: string }> => {
    try {
      const data = await $fetch<{ plan_id: string; success: boolean; error?: string }>('/api/adaptive-questions/save-learning-plan', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          user_id: userId,
          gap,
          resource_ids: resourceIds,
          notes
        }
      })

      return data
    } catch (error) {
      console.error('Error saving learning plan:', error)
      throw error
    }
  }

  /**
   * Get all learning plans for a user.
   *
   * @param userId - User identifier
   * @param status - Optional status filter
   */
  const getLearningPlans = async (
    userId: string,
    status?: 'suggested' | 'in_progress' | 'completed' | 'abandoned'
  ): Promise<LearningPlansResponse> => {
    try {
      const data = await $fetch<LearningPlansResponse>('/api/adaptive-questions/get-learning-plans', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          user_id: userId,
          status
        }
      })

      return data
    } catch (error) {
      console.error('Error getting learning plans:', error)
      throw error
    }
  }

  /**
   * Evaluate a single traditional text/voice answer.
   *
   * @param questionId - Question identifier
   * @param questionText - The question text
   * @param answerText - User's answer (text or transcribed voice)
   * @param gapInfo - Gap information {title, description}
   * @param language - Content language (default: "english")
   */
  const evaluateAnswer = async (
    questionId: string,
    questionText: string,
    answerText: string,
    gapInfo: { title: string; description: string },
    language: string = 'english'
  ): Promise<AnswerEvaluationResponse> => {
    try {
      const data = await $fetch('/api/evaluate-answer', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          question_id: questionId,
          question_text: questionText,
          answer_text: answerText,
          gap_info: gapInfo,
          language
        }
      })

      return data
    } catch (error) {
      console.error('Error evaluating answer:', error)
      throw error
    }
  }

  return {
    startAdaptiveQuestion,
    submitStructuredInputs,
    refineAnswer,
    getLearningResources,
    saveLearningPlan,
    getLearningPlans,
    evaluateAnswer
  }
}
